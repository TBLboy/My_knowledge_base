# Paper Revision V2 Execution

## Status

- Completed 2026-09-04.
- research/paper/main.tex and official CVPR template both compile to 2 pages.
- Bolin_Tao.pdf updated from the revised official template build.

## Task List

1. Fact and statistics check: convert raw counts to success rates; verify
   table values against repeated-eval json files.
2. Abstract: remove repair/bug-report story; emphasize semantic alignment vs
   spatial affordance; report success rates.
3. Introduction: scientific gap framing; neutral clean baseline description.
4. Related Work: dense-map grasp detection, language-driven grasp detection,
   vision-language grounding transition.
5. Method: clarify clean baseline objective, y_view, LSAR small residual,
   fixed scale, auxiliary loss sensitivity.
6. Experiments: success-rate table; sampling mean/std wording; seed 43 as
   independent LSAR training; 50-step sensitivity; qualitative wording.
7. Conclusion: core finding, result, limitation.
8. Compile research/paper/main.tex and official CVPR template; check 2 pages.
9. Update project log and commit.

## Frozen Facts

- Dataset: 10,000 unique scenes, 8,000 train / 2,000 validation.
- Training: 15 epochs, batch 2, lr 1e-3, weight decay 1e-4.
- LSAR: scale 0.01, final lambda_aff 0.05.
- Eval: 10-step respaced diffusion sampling main; 50-step sensitivity.
- Correct threshold: IoU > 0.25 and angle error < 30 degrees.
- Repeated means are over three stochastic diffusion sampling runs of the
  same checkpoint unless otherwise stated.
- Seed 43 is an independently trained LSAR run; there is no paired seed-43
  baseline experiment.

## Exact Success Rates

| Method | lambda_aff | Count /2000 | Success % |
|---|---:|---:|---:|
| LGDM | - | 470.0 | 23.5 +- 0.5 |
| LSAR | 0 | 653.7 | 32.7 +- 0.3 |
| LSAR | 0.10 | 605.3 | 30.3 +- 0.9 |
| LSAR | 0.05 seed42 | 678.0 | 33.9 +- 0.8 |
| LSAR | 0.05 seed43 | 661.7 | 33.1 +- 0.7 |

Note: success-rate std is raw count std divided by 2000 and multiplied by 100.
