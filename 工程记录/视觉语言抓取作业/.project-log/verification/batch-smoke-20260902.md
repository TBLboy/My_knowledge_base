# Batch Smoke Evidence 2026-09-02

Stage 0 gate: run 10 real Grasp-Anything++ stems from 10 different scenes
through the `lgrconvnet3` engineering pipeline.

Command:

```bash
PYTHONNOUSERSITE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python \
  research/scripts/batch_smoke.py \
  --stems research/smoke-data/stems.txt \
  --image-dir processed/grasp-anything/images \
  --cpu
```

Result: `10/10 OK, 0 SKIP-RGB, 0 FAIL`.

Artifacts:

- `outputs/batch_smoke/metrics.json`
- `outputs/batch_smoke/summary.txt`
- `outputs/batch_smoke/qualitative/*.png`

Interpretation:

- All stems completed image loading, instruction loading, positive GT loading,
  dense map generation, `lgrconvnet3` forward, loss, backward, post-process,
  and IoU evaluation.
- The model is randomly initialized; `correct=True` on 1 of 10 is not a
  quality result and is expected by the smoke-test gate.
- Only `.jpg` files needed for the 10 stems are extracted, not the full 60 GiB
  image archive.
