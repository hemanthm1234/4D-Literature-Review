# Analysis of Motion Representations in 4D Vision

Based on the literature review, representing motion (dynamics) in 4D scenes is one of the most heavily researched areas. Because 4D reconstruction and generation are highly ill-posed, researchers have developed various ways to constrain and represent motion. 

Here is a breakdown of the different categories of motion representation found across the papers:

## 1. Explicit 3D Trajectory Fields & Scene Flow
Instead of modeling how a whole scene deforms, these methods model the explicit path of individual points or pixels over time.
*   **Methodology:** Predicts dense per-pixel 3D trajectories or 3D scene flow vectors. 
*   **Examples:**
    *   **OmniX (ECCV 2026):** Parameterizes motion using a compact set of "dynamic tokens." It uses Sparse Spatiotemporal Attention to generate dense trajectory fields for every pixel across all frames in a single feed-forward pass.
    *   **World from Motion (arXiv 2026):** Conditions its generative model directly on dense 4D buffers, which explicitly include **3D scene flow** alongside RGB and depth.
*   **Pros:** Captures arbitrary, long-range motion; easy to query where a specific point goes.
*   **Cons:** Can be memory-intensive; doesn't inherently guarantee physical plausibility or rigidity.

## 2. Low-Dimensional SE(3) Motion Bases
Instead of predicting independent trajectories for millions of points, motion is constrained to a combination of a few global rigid transformations.
*   **Methodology:** The entire scene's motion is defined by a small, global set of SE(3) (translation + rotation) matrices/bases. Every point (or 3D Gaussian) assigns itself a weight/coefficient to these bases, and its final motion is a linear combination of them.
*   **Examples:**
    *   **Shape of Motion (ICCV 2025):** Employs this exact strategy. By forcing 3D Gaussians to move according to a shared set of SE(3) bases, it heavily constrains the optimization, allowing it to reconstruct long-range trajectories from single casual videos.
*   **Pros:** Highly robust to noise; guarantees structural rigidity; extremely parameter-efficient.
*   **Cons:** Struggles with highly non-rigid, fluid, or topologically changing motions that cannot be decomposed into rigid SE(3) components.

## 3. Deformation Fields & Canonical Spaces
This is the classic approach inherited from D-NeRF. It splits the problem into two parts: a static "canonical" space, and a motion space.
*   **Methodology:** An MLP (Deformation Network) takes a coordinate $(x, y, z)$ and a timestamp $t$, and outputs a displacement (e.g., $\Delta x$, $\Delta \text{rotation}$, $\Delta \text{scale}$). This maps the point back to a static canonical space where its color and density are evaluated.
*   **Examples:**
    *   **Deformable 3D Gaussians (CVPR 2024):** Learns a canonical set of 3D Gaussians and an MLP that predicts how their positions, rotations, and scales deform at each frame.
    *   **DeGO (ICML 2026):** Explicitly decouples rigid-body motion (using frame-to-frame offsets) from non-rigid motion (which is distilled into a deformation model).
*   **Pros:** Excellent for objects with consistent topology (like humans or faces); conceptually simple.
*   **Cons:** Struggles with severe topological changes (e.g., objects breaking apart, water splashing) because the mapping to a single canonical space becomes impossible.

## 4. Physics-Grounded Force Fields
Instead of modeling kinematics (how things move), this approach models dynamics (why things move).
*   **Methodology:** Predicts explicit physical forces over a graph of scene elements. An Ordinary Differential Equation (ODE) solver then integrates these forces over time to update the positions and velocities of the elements (like 3D Gaussians).
*   **Examples:**
    *   **Neural Gaussian Force Fields (ICLR 2026):** Uses a Neural Dynamics Simulator to predict object-centric force fields over a relational graph of 3D Gaussians, successfully simulating both rigid and soft bodies.
*   **Pros:** Ensures completely physically realistic motion; allows for interactive prompting (e.g., "push this object").
*   **Cons:** Computationally heavy due to the ODE solvers; difficult to extract ground-truth physical properties from pure visual data.

## 5. Implicit Spatiotemporal Latent Modeling (Diffusion/Transformers)
In these pure generative models, motion isn't explicitly defined by geometry or math equations. It is implicitly learned in the latent space of a neural network.
*   **Methodology:** Uses attention mechanisms across time (temporal attention) to ensure that the generated latents evolve coherently. 
*   **Examples:**
    *   **Sculpt4D (arXiv 2026):** Uses "Block Sparse Attention" (anchoring to the first frame and using time-decaying sparse masks) in the DiT block to implicitly ensure temporal consistency without explicit motion parameters.
    *   **MoRe (arXiv 2026):** Disentangles motion from the static background by applying "attention-forcing" during training (penalizing attention to dynamic regions), teaching the network the concept of motion without hardcoding it.
*   **Pros:** Can generate highly complex, non-rigid, and stochastic motions (like smoke or fire).
*   **Cons:** Lacks 3D geometric rigor; motion cannot be easily edited, extracted, or controlled explicitly.

## 6. Object-Centric Layouts & Scene Graphs
Motion is represented at a macro, semantic level rather than per-pixel or per-point.
*   **Methodology:** Represents motion as bounding boxes and abstract trajectories in a scene graph.
*   **Examples:**
    *   **LiDARCrafter (AAAI 2026):** Uses an LLM to generate an explicit 4D layout (scene graph with bounding boxes and trajectories) which then conditions the generation of the LiDAR point clouds.
*   **Pros:** Highly controllable via text prompts; great for structured environments like autonomous driving.
*   **Cons:** Does not capture fine-grained internal deformations (e.g., a pedestrian waving their arms).

## 7. Discretized Token Sequences
Treats motion exactly like language tokens.
*   **Methodology:** Continuous motion signals (like camera trajectories or human kinematics) are quantized into discrete tokens using VQ-VAEs, and motion generation becomes a sequence prediction task.
*   **Examples:**
    *   **ReViV (ECCV 2026):** Discretizes human gaze, hand pose, and camera ego-motion into tokens and uses a Masked Generative Transformer to predict them.
*   **Pros:** Allows for holistic, unified modeling of completely heterogeneous signals (e.g., predicting an image token from a motion token).
*   **Cons:** Quantization inherently loses high-frequency, continuous precision.
