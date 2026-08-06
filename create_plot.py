import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

# Set seaborn style for better aesthetics
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.5

def parse_markdown_table(filepath):
    """Parses the markdown file and extracts the summary table."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the table in the markdown file
    lines = content.split('\n')
    table_lines = [line for line in lines if line.strip().startswith('|')]
    
    # Skip header and separator
    data_lines = table_lines[2:]
    
    data = []
    for line in data_lines:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 4:
            name = parts[0]
            conf_year = parts[1]
            ps_short = parts[3]
            data.append({
                'Name': name,
                'Conf_Year_Raw': conf_year,
                'Categories': [t.strip() for t in ps_short.split(',') if t.strip()]
            })
    return data

def process_data(data):
    """Processes the raw data to extract Year and Conference."""
    df = pd.DataFrame(data)
    
    def extract_conf_year(raw_str):
        # We prefer the non-arXiv conference if available (usually the first part before '/')
        parts = raw_str.split('/')
        primary = parts[0].strip()
        
        # Regex to extract Conference (letters) and Year (4 digits)
        match = re.search(r'([A-Za-z\-]+(?: [A-Za-z\-]+)*)?.*?(\d{4})', primary)
        if match:
            conf = match.group(1).strip() if match.group(1) else "Unknown"
            year = int(match.group(2))
            
            # Unify conference names (e.g., SIGGRAPH Asia -> SIGGRAPH)
            if "SIGGRAPH" in conf:
                conf = "SIGGRAPH"
            
            return conf, year
        return "Unknown", 0

    # Apply extraction
    df[['Conference', 'Year']] = df['Conf_Year_Raw'].apply(lambda x: pd.Series(extract_conf_year(x)))
    return df

def create_plots(df, output_dir):
    """Generates a beautiful 2x2 grid of insightful plots based on the data."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a 2x2 grid for the subplots
    fig, axes = plt.subplots(2, 2, figsize=(22, 16))
    fig.suptitle('4D Vision & Generation: Literature Trends and Analysis', 
                 fontsize=26, fontweight='black', y=0.98, color='#1a1a1a')
    
    # ---------------------------------------------------------
    # 1. Category Distribution (Top Left)
    # ---------------------------------------------------------
    ax1 = axes[0, 0]
    all_categories = [cat for sublist in df['Categories'] for cat in sublist]
    cat_counts = Counter(all_categories)
    sorted_cats = cat_counts.most_common()
    
    sns.barplot(x=[count for _, count in sorted_cats], y=[cat for cat, _ in sorted_cats], 
                palette="viridis", ax=ax1, edgecolor="black", linewidth=1.5)
    ax1.set_title('Distribution of Problem Statement Categories', fontsize=18, fontweight='bold', pad=15)
    ax1.set_xlabel('Number of Papers', fontsize=14, fontweight='semibold')
    ax1.set_ylabel('Category (PS-short)', fontsize=14, fontweight='semibold')
    ax1.tick_params(axis='both', labelsize=13)
    # Ensure x-axis only uses integers
    ax1.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # ---------------------------------------------------------
    # 2. Conference Distribution (Top Right)
    # ---------------------------------------------------------
    ax2 = axes[0, 1]
    conf_counts = df['Conference'].value_counts()
    sns.barplot(x=conf_counts.values, y=conf_counts.index, 
                palette="flare", ax=ax2, edgecolor="black", linewidth=1.5)
    ax2.set_title('Distribution of Papers by Venue', fontsize=18, fontweight='bold', pad=15)
    ax2.set_xlabel('Number of Papers', fontsize=14, fontweight='semibold')
    ax2.set_ylabel('Conference / Venue', fontsize=14, fontweight='semibold')
    ax2.tick_params(axis='both', labelsize=13)
    ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # ---------------------------------------------------------
    # 3. Publications Trend Over Time (Bottom Left)
    # ---------------------------------------------------------
    ax3 = axes[1, 0]
    year_counts = df['Year'].value_counts().sort_index()
    sns.barplot(x=year_counts.index.astype(int), y=year_counts.values, 
                palette="crest", ax=ax3, edgecolor="black", linewidth=1.5)
    ax3.set_title('Publication Trend Over Time', fontsize=18, fontweight='bold', pad=15)
    ax3.set_xlabel('Year', fontsize=14, fontweight='semibold')
    ax3.set_ylabel('Number of Papers', fontsize=14, fontweight='semibold')
    ax3.tick_params(axis='both', labelsize=14)
    ax3.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # ---------------------------------------------------------
    # 4. Evolution of Top Categories Over Time (Bottom Right)
    # ---------------------------------------------------------
    ax4 = axes[1, 1]
    # Get top 5 categories to keep the plot readable
    top_cats = [cat for cat, _ in cat_counts.most_common(5)]
    yearly_cat_counts = {year: {cat: 0 for cat in top_cats} for year in sorted(df['Year'].unique())}
    
    for _, row in df.iterrows():
        year = row['Year']
        for cat in row['Categories']:
            if cat in top_cats:
                yearly_cat_counts[year][cat] += 1
                
    cat_evolution_df = pd.DataFrame(yearly_cat_counts).T
    
    # Plot using pandas on ax4
    cat_evolution_df.plot(kind='line', marker='o', linewidth=4, markersize=10, 
                          colormap='Set1', ax=ax4, alpha=0.9)
    ax4.set_title('Evolution of Top Categories Over Time', fontsize=18, fontweight='bold', pad=15)
    ax4.set_xlabel('Year', fontsize=14, fontweight='semibold')
    ax4.set_ylabel('Number of Papers', fontsize=14, fontweight='semibold')
    ax4.set_xticks(cat_evolution_df.index)
    ax4.set_xticklabels(cat_evolution_df.index.astype(int), fontsize=13)
    
    # Force Y-axis to be integers only
    max_y = int(cat_evolution_df.max().max())
    ax4.set_yticks(range(0, max_y + 2))
    ax4.tick_params(axis='y', labelsize=13)
    
    ax4.legend(title='Category', loc='upper left', fontsize=12, title_fontsize=13, 
               frameon=True, shadow=True)
    ax4.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Adjust layout and save the combined grid plot
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Leave room for the suptitle
    out_path = os.path.join(output_dir, 'literature_trends_2x2.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Stunning 2x2 grid plot saved successfully to: {out_path}")

if __name__ == "__main__":
    filepath = "/data1/hemanth/4D/literature_review.md"
    output_dir = "/data1/hemanth/4D/plots"
    
    print(f"Reading data from {filepath}...")
    data = parse_markdown_table(filepath)
    
    if not data:
        print("No data found. Please check the markdown table parsing.")
    else:
        print(f"Successfully parsed {len(data)} papers.")
        df = process_data(data)
        
        print(f"Generating 2x2 grid plot in {output_dir}...")
        create_plots(df, output_dir)
