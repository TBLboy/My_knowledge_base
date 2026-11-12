# Koopman lifted-space tracking review

## Identity and purpose

- Reading level: L4 transfer review.
- Purpose: verify whether weighting only the physical-state block of a lifted Koopman state is standard, and identify a tracking-MPC formulation that does not require a prescribed reference input.
- User-provided paper: Z. M. Manaa, A. M. Abdallah, M. A. Abido, and S. S. A. Ali, “Koopman-LQR Controller for Quadrotor UAVs from Data,” IEEE International Conference on Smart Mobility, 2024.

## Confirmed transfer points

### User-provided Koopman-LQR paper

Section II-D, p. 4, replaces the original-state LQR cost by a lifted-state cost using a block weight \(\bar Q=\operatorname{diag}(Q,0)\): only the original physical-state coordinates are penalized; the additional observables receive zero weight. The input remains unlifted and keeps \(R\). This is a regulation/LQR example, not a time-varying tracking-MPC proof, but it directly supports the proposed weighting convention.

### SE(3) Koopman-MPC

S. S. K. S. Narayanan et al., “SE(3) Koopman-MPC: Data-driven Learning and Control of Quadrotor UAVs,” arXiv:2305.03868, Sec. 2.4, Eqs. (5)–(9), https://arxiv.org/html/2305.03868.

The paper defines \(z_{k+1}=Az_k+Bu_k\), \(x_k=\mathcal C z_k\), lifts the reference trajectory, and uses \(\bar Q=\operatorname{diag}(Q,0)\) in the lifted tracking cost. The zero block leaves pure observables unpenalized while the physical coordinates retain the tracking weight. The resulting condensed problem is a QP in the input sequence. This is the closest precedent for the current design choice.

### Data-driven Predictive Tracking Control based on Koopman Operators

Y. Wang, Y. Yang, Y. Pu, and C. Manzie, “Data-driven Predictive Tracking Control based on Koopman Operators,” arXiv:2208.12000v2, Secs. III-B–III-C and IV, https://arxiv.org/html/2208.12000.

This paper does not require a prescribed reference input as an external interface. It introduces online optimal reachable steady output/input variables, computes them from lifted steady manifolds, and uses a lifted-state/input cost plus an output offset cost. Its robust constraint tightening and ISS-to-a-neighborhood analysis provide a more relevant theoretical template than simply deleting \(u_t^r\) from the current theorem.

## Decision for this project

For the full measured reference \(x_t^r\), use the existing state-preserving lift but penalize only the physical block:

\[
\ell_t(p,u)=\|C_xE_z^Tp-x_t^r\|_{Q_x}^2
 +\|u-E_{\rm prev}p\|_S^2+\|u\|_R^2.
\]

Equivalently, if \(z=\operatorname{col}(x,\psi)\), use \(\bar Q_z=\operatorname{diag}(Q_x,0)\). No reference input or reference input cache is required by the controller. For a partial output reference, replace \(C_x\) by the physical-output selector.

The zero latent block is standard and must not be presented as a contribution. The main theoretical consequence is that strict convexity should be established through \(S\succ0\) on the input-increment map (or an independent \(R\succ0\)), not through a positive-definite full-state tracking weight. IV-B must be rebuilt; the old full-augmented-state/reference-input theorem cannot be reused by notation substitution.

## Limitations

- The user-provided paper is an LQR regulation example; it supports the cost-weighting convention but not the proposed time-varying Frozen-LTV tracking theorem.
- The cited tracking-MPC papers use different model structures and assumptions; they are transfer references, not proof of the present model.
- No project source or experiment was modified during this review.
