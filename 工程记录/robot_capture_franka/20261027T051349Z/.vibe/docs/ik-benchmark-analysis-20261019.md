# IK Benchmark Analysis

## Confirmed project evidence

- The opt-in continuous-IK → joint-impedance route reduced vibration during roll compared with Cartesian impedance, but Pico teleoperation became visibly discontinuous and was stopped as the main route.
- The current implementation performs synchronous worker-side IK for each TCP target. Its loop repeatedly evaluates native Franky FK and Jacobian, solves a damped least-squares step, and then publishes a joint target.
- The project already has an FR3 URDF and an isolated native libfranka model benchmark. The current RLinf Python environment does not provide Pinocchio, Pink, IKPy, CasADi, or Mink.
- The current benchmark must remain offline: no robot connection, Ray lifecycle, Pico service, camera service, gripper, or hardware motion.

## Decision

Benchmark a Pinocchio-based single-step differential IK path against the current native-model iterative IK path before changing runtime code.

The candidate path is:

```text
FR3 URDF → Pinocchio FK/Jacobian → one damped least-squares differential step
→ integrate q_target → offline continuity/error measurements
```

The benchmark must compare warm-started sequential targets, not isolated random IK calls.

## Rationale

The primary hypothesis is that a single-step differential IK controller is better suited to continuous Pico teleoperation than a per-frame solver that seeks full pose convergence. A library replacement can improve model/Jacobian cost, but it will not by itself remove synchronous RPC or outer-loop scheduling latency; those are separate measurements and are not silently changed by this benchmark.

## Candidates and boundaries

- **Primary:** Pinocchio with the existing FR3 URDF and a project-owned DLS update.
- **Secondary:** Pink only if constraints/task composition are needed after the Pinocchio baseline.
- **Not primary:** IKPy, because its documented SciPy optimization path is a poor fit for bounded high-rate warm-started control; TRAC-IK/IKFast require larger integration or generation work.
- No dependency is added to the official runtime during this benchmark.

## Required measurements

- solve latency mean, p95, and p99;
- per-target and cumulative joint step continuity;
- TCP position/orientation residuals;
- joint-limit margin and non-finite/failure counts;
- sequential target replay on the existing offline trajectory;
- model/tool-frame convention compatibility with the existing FR3 fixture.

## Acceptance boundary

The result is a recommendation only. It does not authorize replacing Cartesian control, enabling joint_ik in production, adding a dependency, or running hardware. A runtime change requires a separate decision and task.
