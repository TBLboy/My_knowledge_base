# Diffusion LGDM Baseline Smoke Evidence 2026-09-02

Goal: prove the current `LGD-main` diffusion baseline can run on real
Grasp-Anything++ samples before using it as the baseline for LSAR work.

Command:

```bash
HF_ENDPOINT=https://hf-mirror.com \
PYTHONNOUSERSITE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python \
  research/scripts/diffusion_smoke.py \
  --max-stems 2 --sample-steps 10 \
  --out outputs/diffusion_smoke_2
```

Result: `2/2 OK, 0 FAIL`.

Relevant metric values:

- Device: CUDA (RTX 4090)
- Official diffusion steps: 1000
- Smoke sampling steps: 10 (respaced cosine)
- Sample shape: `(1, 1, 224, 224)`
- Sample finite: True for both stems
- Dense map GT shape: `(1, 1, 224, 224)` per map
- Backward gradients finite: True
- Peak GPU memory: ~2.51 GiB
- Untrained model IoU `correct`: False (expected; no quality claim)

Key implementation findings:

1. `LGDM` instantiates successfully with `transformers==4.28.1`,
   `timm==0.6.13`, `ruamel.yaml==0.17.21`, plus existing CLIP.
2. `train_network_diffusion.py` computes the diffusion loss but does not
   call `backward()` on it (line 242-244); the official update is driven by
   the dense-map loss from `LGDM.compute_loss`.
3. Official README uses `--network lgd`, but `get_network` only registers
   `lgdm`; smoke uses the `LGDM` model directly.
4. The `p_sample_loop` smoke used a 10-step respaced schedule over the
   1000-step cosine schedule. The full 1000-step sample path is intended for
   evaluation/training, not the smoke test.

Limitations:

- Only 2 real stems from 2 different scenes were used.
- Prediction correctness is not a criterion; the model is randomly initialized.
- Full 1000-step sampling was not run.
- `grasp_instructions/<stem>.pkl` is passed directly as the text query in this
  smoke adapter; official historical `queries[obj_id]` semantics remain
  `Unknown / To Verify`.
