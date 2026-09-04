# Proposed Method

# Language-Guided Spatial Affordance Refinement for Language-Driven Grasp Detection

> Baseline status 2026-09-02: the baseline is now confirmed to be the
> diffusion-based `LGDM` model, not `lgrconvnet3`. Real-sample smoke evidence:
> `EV-20260902-diffusion-smoke`.

## 0. Overview

This document describes the proposed method for the Language-Driven Grasp Detection project based on the Grasp-Anything++ dataset.

The project starts from the official Language-driven Grasp Detection (LGD) framework, which formulates grasp detection as a conditional generation problem:

\[
(image, language instruction) \rightarrow grasp pose
\]

The original LGD method introduces a diffusion-based grasp generation framework with vision-language conditioning.

Our proposed method aims to improve the spatial grounding ability between language instructions and grasp regions while preserving the original generation pipeline.

The main idea is:

> Existing vision-language fusion methods provide semantic alignment between images and instructions, but they may lack fine-grained spatial affordance reasoning required for robotic grasping.

Therefore, we introduce a lightweight:

**Language-conditioned Spatial Affordance Refinement Module (LSAR)**

to refine the language-guided grasp region before grasp generation.


---

# 1. Motivation

## 1.1 Problem of Existing LGD

The original LGD pipeline:


Image
|
Vision Encoder

Language Instruction
|
Text Encoder

    ↓

Vision-Language Fusion (ALBEF)

    ↓

Language-guided attention map

    ↓

Diffusion-based grasp generation

    ↓

5D grasp rectangle


The existing framework successfully introduces language conditions into grasp generation.

However, the vision-language fusion module is originally designed for general image-text alignment.

Its attention response mainly represents:

"Which region is related to the language description?"

while grasp detection requires:

"Which specific region provides the best grasp affordance?"

These two objectives are related but not identical.


Example:

Instruction:

"Grasp the handle of the knife."


A generic vision-language model may identify:

- the knife object

but grasping requires:

- the handle region

rather than the blade or other regions.


Therefore, we hypothesize:

Improving language-conditioned spatial affordance representation can improve grasp localization.


---

# 2. Proposed Framework Overview


The proposed framework keeps the original LGD generation pipeline and introduces a spatial refinement module.


Overall pipeline:


             Image
               |
               ↓
        Vision Encoder


      Language Instruction
               |
               ↓
         Text Encoder


               ↓

    Vision-Language Fusion

         (Original LGD)

               ↓

    Language-conditioned
    Spatial Attention Map

               ↓

 =================================

  Language-conditioned Spatial
  Affordance Refinement Module

 =================================

               ↓

    Refined Grasp Guidance

               ↓

    Diffusion Grasp Generator

               ↓

      5D Grasp Rectangle

    (x, y, w, h, θ)


The proposed method only modifies the conditioning branch.

The original grasp representation, diffusion process, and evaluation protocol remain unchanged.


---

# 3. Language-conditioned Spatial Affordance Refinement Module (LSAR)


## 3.1 Input

The module receives:


### Vision-language attention feature

From the original LGD fusion module:

\[
A_{vl}
\]

where:

\[
A_{vl}\in R^{H\times W}
\]


This represents the spatial relevance between:

- image regions;
- language instruction.


### Visual feature map

Optional:

\[
F_v
\]

from the vision encoder.


The visual feature provides local spatial information.


---

## 3.2 Refinement Operation


The refinement module learns:


\[
A_{ref}=LSAR(A_{vl},F_v)
\]


where:

\[
A_{ref}
\]

is the refined grasp affordance map.


The goal is:

\[
A_{ref}
\rightarrow
ground-truth grasp region
\]

Compared with the original attention map:

\[
A_{vl}
\]

the refined representation should contain:

- stronger response on graspable regions;
- weaker response on irrelevant regions.


---

# 4. Possible Module Implementations


The first implementation should prioritize simplicity and robustness.


## Option 1: Lightweight CNN Refinement (Recommended Baseline)


Structure:



Attention Map

  ↓

Conv 3×3

  ↓

ReLU

  ↓

Conv 3×3

  ↓

Sigmoid

  ↓

Refined Attention



Advantages:

- simple;
- low computational cost;
- easy ablation.


---

## Option 2: Spatial Attention Refinement


Use attention mechanism:


\[
A_{ref}=Attention(Q,K,V)
\]


Advantages:

- stronger spatial modeling;
- closer to transformer-based vision-language models.


---

## Option 3: Lightweight Transformer Refinement


Input:

patch features + language embedding


Output:

refined spatial representation.


Advantages:

- strongest expressive ability.


Disadvantage:

- higher implementation complexity.


---

# 5. Training Objective


The original LGD objective:


\[
L_{total}
=
L_{diffusion}
+
L_{contrastive}
\]


is preserved.


The proposed method introduces an additional spatial refinement loss.


## 5.1 Affordance Refinement Loss


If grasp region supervision is available:

\[
L_{aff}
=
BCE(A_{ref},M_{grasp})
\]


where:

- \(A_{ref}\): refined affordance map;
- \(M_{grasp}\): grasp region target.


Final objective:


\[
L
=
L_{diffusion}
+
\lambda_1L_{contrastive}
+
\lambda_2L_{aff}
\]


---

# 6. Expected Contribution


The proposed method contributes:


## Contribution 1

A language-conditioned spatial affordance refinement module for fine-grained grasp localization.


## Contribution 2

A simple plug-in improvement compatible with existing language-driven grasp detection frameworks.


## Contribution 3

Improved alignment between:

language instruction

and

robot graspable regions.


---

# 7. Experimental Plan


## Stage 0: Baseline Verification

Completed:

- official data pipeline;
- environment;
- batch smoke test.


---

# Stage 1: Training Sanity Check


Dataset size:

100 samples


Purpose:

- verify training stability;
- confirm loss decreasing;
- confirm gradients.


No performance claim.


---

# Stage 2: Small-scale Experiment


Dataset:

5k samples


Compare:


| Method | Description |
|-|-|
| LGD baseline | Original framework |
| LGD + LSAR | Proposed method |


Metrics:

- IoU success rate;
- angle accuracy;
- grasp success.


---

# Stage 3: Final Experiment


Dataset:

20k-50k samples


Evaluation:

- validation set;
- qualitative visualization;
- quantitative comparison.


---

# 8. Ablation Study


Required ablations:


## Ablation 1

Effect of refinement module


|Model|LSAR|
|-|-|
|Baseline|No|
|Ours|Yes|


---

## Ablation 2

Different refinement designs


|Method|
|-|
|CNN refinement|
|Attention refinement|
|Transformer refinement|


---

# 9. Future Extension: Flow Matching Grasp Generator


## Motivation

Diffusion models require iterative denoising.

For robotic applications, inference efficiency is important.


Flow Matching models learn:


\[
\frac{dx_t}{dt}=v_\theta(x_t,t,c)
\]


and directly model the transport path from noise to grasp.


---

## Extension Idea


Replace only the final generation head:


Original:


Refined condition

  ↓

Diffusion Denoiser

  ↓

Grasp Pose



Extension:


Refined condition

  ↓

Flow Matching Generator

  ↓

Grasp Pose



All other components remain unchanged:

- dataset;
- language encoder;
- visual encoder;
- LSAR module;
- evaluation.


---

# 10. Final Research Roadmap



Official LGD Baseline

    ↓

Language-conditioned Spatial
Affordance Refinement (LSAR)

    ↓

Improved Grasp Localization

    ↓

(Optional)

Flow Matching Generation Head

    ↓

Efficient Language-driven Grasp Detection



---

# Main Research Hypothesis


The main hypothesis of this project is:


"Improving the spatial affordance alignment between language instructions and visual regions can enhance la
