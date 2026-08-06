import fitz  # PyMuPDF
import os
import json
import re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

def get_groq_client():
    if not GROQ_AVAILABLE:
        return None
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def is_body_text(text):
    text = text.strip()
    return len(text) > 60 or text.count('\n') >= 2

def get_column_bounds(rect, page_width):
    col_mid = (rect.x0 + rect.x1) / 2
    is_full_width = (0.35 * page_width < col_mid < 0.65 * page_width) or (rect.width > page_width * 0.6)
    
    if is_full_width:
        return 0, page_width
    else:
        if col_mid < page_width / 2:
            return 0, page_width / 2
        else:
            return page_width / 2, page_width

def cols_overlap(x0a, x1a, x0b, x1b):
    return max(0, min(x1a, x1b) - max(x0a, x0b)) > 0

def rect_area(r):
    if r.is_empty: return 0
    return max(0, r.x1 - r.x0) * max(0, r.y1 - r.y0)

def identify_architecture_figures_groq(client, captions):
    if not captions:
        return []
        
    prompt = """Given the following list of figure captions from an academic paper, identify which figures represent the overall method architecture, pipeline, system overview, or framework. 
Return a JSON object with a single key "architecture_figures" containing a list of figure IDs (strings). Do not include any other text.
Example: {"architecture_figures": ["Figure 1", "Figure 3"]}

Captions:
"""
    for cap in captions:
        prompt += f"[{cap['id']}]: {cap['text']}\n"
        
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("architecture_figures", [])
    except Exception as e:
        print(f"Groq API error: {e}")
        return None

def identify_architecture_figures_heuristic(caption_blocks):
    keywords = ['overview', 'architecture', 'pipeline', 'framework', 'method', 'approach', 'schematic', 'system', 'model']
    arch_figures = []
    for cap in caption_blocks:
        text = cap['text'].lower()
        if any(kw in text for kw in keywords):
            arch_figures.append(cap['id'])
    return arch_figures

def extract_architecture_diagrams(papers_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    client = get_groq_client()
    
    if client:
        print("Groq API key found! Using Llama 3 70B for robust semantic caption filtering.")
    else:
        print("Groq API not configured or module missing. Using keyword heuristics (fallback).")
        print("Hint: pip install groq && export GROQ_API_KEY='your-key'")

    for filename in os.listdir(papers_dir):
        if not filename.lower().endswith(".pdf"):
            continue
            
        pdf_path = os.path.join(papers_dir, filename)
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {pdf_path}: {e}")
            continue
        
        paper_name = os.path.splitext(filename)[0]
        print(f"\nProcessing {paper_name}...")
        
        all_captions = []
        caption_blocks = []
        
        # 1. Collect all figure captions
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[6] == 0:
                    text = block[4].strip()
                    match = re.match(r'^(?:Figure|Fig\.)\s*(\d+[a-zA-Z]?)', text, re.IGNORECASE)
                    if match:
                        fig_id = f"Figure {match.group(1)}"
                        cap_data = {
                            "id": fig_id,
                            "text": text.replace('\n', ' '),
                            "page_num": page_num,
                            "rect": fitz.Rect(block[:4]),
                            "block_tuple": block
                        }
                        all_captions.append({"id": fig_id, "text": text.replace('\n', ' ')})
                        caption_blocks.append(cap_data)
        
        # 2. Identify architecture figures
        arch_fig_ids = None
        if client and all_captions:
            arch_fig_ids = identify_architecture_figures_groq(client, all_captions)
        
        if arch_fig_ids is None:
            arch_fig_ids = identify_architecture_figures_heuristic(caption_blocks)
            
        print(f"  Identified architecture figures: {arch_fig_ids}")
        
        # 3. Extract the identified figures using tight geometrical bounds
        diagram_count = 0
        for cap_data in caption_blocks:
            if cap_data['id'] not in arch_fig_ids:
                continue
                
            page_num = cap_data['page_num']
            page = doc[page_num]
            blocks = page.get_text("blocks")
            caption_rect = cap_data['rect']
            
            page_width = page.rect.width
            col_x0, col_x1 = get_column_bounds(caption_rect, page_width)
            
            y_top = 0
            y_bottom = page.rect.height
            
            # Find semantic bounds (body text and other captions)
            for b in blocks:
                if b[6] != 0 or b == cap_data['block_tuple']: 
                    continue
                
                b_rect = fitz.Rect(b[:4])
                b_text = b[4].strip()
                b_col_x0, b_col_x1 = get_column_bounds(b_rect, page_width)
                
                if not cols_overlap(col_x0, col_x1, b_col_x0, b_col_x1):
                    continue
                
                is_body = is_body_text(b_text)
                is_other_caption = bool(re.match(r'^(?:Figure|Fig\.|Table|Tab\.)\s*\d+', b_text, re.IGNORECASE))
                
                if is_body or is_other_caption:
                    if b_rect.y1 <= caption_rect.y0 + 5:
                        y_top = max(y_top, b_rect.y1)
                    elif b_rect.y0 >= caption_rect.y1 - 5:
                        y_bottom = min(y_bottom, b_rect.y0)
            
            fig_region = fitz.Rect(col_x0, y_top, col_x1, y_bottom)
            tight_rect = fitz.Rect(caption_rect)
            
            # Union with images
            for img in page.get_image_info():
                img_rect = fitz.Rect(img["bbox"])
                intersect = img_rect & fig_region
                if not intersect.is_empty and rect_area(img_rect) < rect_area(page.rect) * 0.9:
                    tight_rect |= img_rect
                    
            # Union with drawings
            for path in page.get_drawings():
                path_rect = fitz.Rect(path["rect"])
                intersect = path_rect & fig_region
                if not intersect.is_empty:
                    tight_rect |= path_rect
                    
            # Union with non-body text
            for b in blocks:
                if b[6] != 0 or b == cap_data['block_tuple']:
                    continue
                b_rect = fitz.Rect(b[:4])
                b_text = b[4].strip()
                
                if not is_body_text(b_text) and not bool(re.match(r'^(?:Figure|Fig\.|Table|Tab\.)\s*\d+', b_text, re.IGNORECASE)):
                    intersect = b_rect & fig_region
                    if not intersect.is_empty and rect_area(intersect) > 0.5 * rect_area(b_rect):
                        tight_rect |= b_rect
            
            # Fallback if tightening failed or missed something crucial
            if rect_area(tight_rect) < rect_area(caption_rect) * 1.5:
                tight_rect = fig_region
                
            # Final padding
            pad = 10
            tight_rect.x0 = max(0, tight_rect.x0 - pad)
            tight_rect.y0 = max(0, tight_rect.y0 - pad)
            tight_rect.x1 = min(page_width, tight_rect.x1 + pad)
            tight_rect.y1 = min(page.rect.height, tight_rect.y1 + pad)
            
            if (tight_rect.y1 - tight_rect.y0) < 50:
                continue
                
            pix = page.get_pixmap(clip=tight_rect, dpi=300)
            diagram_count += 1
            output_path = os.path.join(output_dir, f"{paper_name}_arch_{diagram_count}.png")
            pix.save(output_path)
            print(f"  -> Saved {output_path}")

if __name__ == "__main__":
    papers_directory = "/data1/hemanth/4D/papers"
    output_directory = "/data1/hemanth/4D/architecture_diagrams"
    print(f"Starting extraction from {papers_directory}")
    extract_architecture_diagrams(papers_directory, output_directory)
    print("Done!")
