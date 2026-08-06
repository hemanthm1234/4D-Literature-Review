#!/bin/bash
# Download script for 4D reconstruction papers

mkdir -p /data1/hemanth/4D/papers

download_paper() {
    local name="$1"
    local output_path="$2"
    local url="$3"
    
    if [ -f "$output_path" ]; then
        echo "Already downloaded: $name"
    else
        echo "Downloading $name..."
        wget -q -O "$output_path" "$url"
        echo "Finished downloading: $name"
    fi
}

download_paper "D-NeRF (CVPR 2021)" "/data1/hemanth/4D/papers/CVPR2021_D-NeRF.pdf" "https://arxiv.org/pdf/2011.13961.pdf" &
download_paper "TiNeuVox (SIGGRAPH Asia 2022)" "/data1/hemanth/4D/papers/SIGGRAPHAsia2022_TiNeuVox.pdf" "https://arxiv.org/pdf/2205.15285.pdf" &
download_paper "Deformable 3D Gaussians (CVPR 2024)" "/data1/hemanth/4D/papers/CVPR2024_Deformable_3D_Gaussians.pdf" "https://arxiv.org/pdf/2309.13101.pdf" &
download_paper "4D Gaussian Splatting for Real-Time Dynamic Scene Rendering (CVPR 2024)" "/data1/hemanth/4D/papers/CVPR2024_4D_Gaussian_Splatting_Real_Time.pdf" "https://arxiv.org/pdf/2310.08528.pdf" &
download_paper "Real-Time Photorealistic Dynamic Scene Representation and Rendering with 4D Gaussian Splatting (ICLR 2024)" "/data1/hemanth/4D/papers/ICLR2024_Real_Time_Photorealistic_4D_Gaussian.pdf" "https://arxiv.org/pdf/2310.10642.pdf" &
download_paper "SV4D (ICLR 2025)" "/data1/hemanth/4D/papers/ICLR2025_SV4D.pdf" "https://arxiv.org/pdf/2407.17470.pdf" &
download_paper "MoRe (CVPR 2026)" "/data1/hemanth/4D/papers/CVPR2026_MoRe.pdf" "https://arxiv.org/pdf/2603.05078.pdf" &
download_paper "OmniX (ECCV 2026)" "/data1/hemanth/4D/papers/ECCV2026_OmniX.pdf" "https://arxiv.org/pdf/2607.10840.pdf" &
download_paper "ReViV (ECCV 2026)" "/data1/hemanth/4D/papers/ECCV2026_ReViV.pdf" "https://arxiv.org/pdf/2607.17790.pdf" &
download_paper "Dream-in-4D (CVPR 2024)" "/data1/hemanth/4D/papers/CVPR2024_Dream_in_4D.pdf" "https://arxiv.org/pdf/2311.16854.pdf" &
download_paper "Shape of Motion (ICCV 2025)" "/data1/hemanth/4D/papers/ICCV2025_Shape_of_Motion.pdf" "https://arxiv.org/pdf/2407.13764.pdf" &
download_paper "Sculpt4D (2026)" "/data1/hemanth/4D/papers/ArXiv2026_Sculpt4D.pdf" "https://arxiv.org/pdf/2604.21592.pdf" &
download_paper "K-Planes (CVPR 2023)" "/data1/hemanth/4D/papers/CVPR2023_K_Planes.pdf" "https://arxiv.org/pdf/2301.08930.pdf" &
download_paper "Dynamic Neural Radiance Fields for Monocular 4D Facial Avatar Reconstruction (CVPR 2021)" "/data1/hemanth/4D/papers/CVPR2021_Dynamic_Facial_Avatar.pdf" "https://arxiv.org/pdf/2012.03065.pdf" &
download_paper "Spacetime Gaussian Feature Splatting (CVPR 2024)" "/data1/hemanth/4D/papers/CVPR2024_Spacetime_Gaussian.pdf" "https://arxiv.org/pdf/2312.16812.pdf" &
download_paper "World from Motion (CVPR 2026)" "/data1/hemanth/4D/papers/CVPR2026_World_from_Motion.pdf" "https://arxiv.org/pdf/2607.01202.pdf" &
download_paper "Streaming 4D Visual Geometry Transformer (ICLR 2025)" "/data1/hemanth/4D/papers/ICLR2025_Streaming_4D_VGGT.pdf" "https://arxiv.org/pdf/2507.11539.pdf" &
download_paper "Neural Gaussian Force Fields (ICLR 2026)" "/data1/hemanth/4D/papers/ICLR2026_Neural_Gaussian_Force_Fields.pdf" "https://arxiv.org/pdf/2602.00148.pdf" &
download_paper "CAGS (SIGGRAPH 2026)" "/data1/hemanth/4D/papers/SIGGRAPH2026_CAGS.pdf" "https://arxiv.org/pdf/2605.09279.pdf" &
download_paper "DeGO (ICML 2026)" "/data1/hemanth/4D/papers/ICML2026_DeGO.pdf" "https://arxiv.org/pdf/2605.28587.pdf" &
download_paper "VistaBot (ICRA 2026)" "/data1/hemanth/4D/papers/ICRA2026_VistaBot.pdf" "https://arxiv.org/pdf/2604.21914.pdf" &
download_paper "LiDARCrafter (AAAI 2026)" "/data1/hemanth/4D/papers/AAAI2026_LiDARCrafter.pdf" "https://arxiv.org/pdf/2508.03692.pdf" &

echo "Waiting for all downloads to finish..."
wait
echo "All downloads completed."
