# Prepare Pose Selector Task List

## Goal

Build a new offline selector that chooses the best prepare pose for the next tofu-cutting phase.

Input:
- `target_prepare` 6D pose
- cut preview parameters
- current joint state `current_joints`

Output:
- `best_q_prepare`

The chosen prepare pose must satisfy the exact end-effector pose target, keep every joint away from limits, and be the most suitable starting state for future cutting motion.

This is not a path-comfort problem. The path from current pose to prepare pose is not the objective. The objective is: the prepare pose itself must be a good starting point for future cutting.

## Core Principles

1. Keep using the working target orientation construction.
2. Do not connect to real xCore hardware.
3. Do not use KDL, DH hand derivation, or StreamExecutor.
4. Do not stop at the first IK solution.
5. Do not optimize only `q - current_joints`.
6. Evaluate how each candidate behaves under future cut preview.

## Existing Building Blocks

- `offline_urdf_kinematics.py`
  - Offline URDF-based FK only.
  - Provides `fk_matrix(q)` and pose helpers.
- `demo_offline_ik_to_rviz.py`
  - Validated single-pose IK + RViz joint publishing.
  - Already supports `--plane-angle-deg`.

The new selector must build on these files, not replace them.

## New File

Create:

`src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py`

Responsibilities:
- Read current `/joint_states`
- Build `target_prepare_pose`
- Generate multiple prepare IK candidates
- Run cut preview rollout for each candidate
- Score each candidate by future cost
- Select the best candidate
- Publish `best_q_prepare` to `/joint_states`

## Target Pose Construction

Keep the current validated orientation logic:

```python
x_flange = [1, 0, 0]
z_flange = [0, sin(angle), cos(angle)]
y_flange = cross(z_flange, x_flange)
target_R = [x_flange, y_flange, z_flange]
```

Where:
- `angle = --plane-angle-deg`
- `angle = 90°` means `z_flange = base +Y`, i.e. downward in this robot base frame

## Proposed CLI

Example:

```bash
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --x 0.35 \
  --y 0.10 \
  --z 0.40 \
  --plane-angle-deg 90 \
  --base-link AR5-5_07R-W4C1C1_base \
  --tip-link AR5-5_07R-W4C1C1_link_tcp \
  --cut-depth 0.017 \
  --preview-steps 8 \
  --candidate-count 80 \
  --safety-margin-deg 15
```

Suggested arguments:
- `--x`, `--y`, `--z`: target prepare position in base frame
- `--plane-angle-deg`: line-plane angle of flange Z axis vs base XZ plane
- `--cut-depth`: preview down-cut depth in meters
- `--preview-steps`: discrete points for preview trajectory
- `--candidate-count`: number of target IK candidates to search
- `--safety-margin-deg`: hard safety margin from joint limits
- `--base-link`: URDF base link
- `--tip-link`: URDF tip link

## Step 1: Read Current Joint State

Implement:

```python
def get_current_joints_from_joint_states(joint_names, timeout_sec=1.0):
    ...
```

Requirements:
- Subscribe to `/joint_states`
- Extract positions in `joint_names` order
- Return `None` if timeout expires
- If no `/joint_states` is available, fall back to a default posture, not a hard failure

Fallback order:
1. `/joint_states` topic if available
2. `q_home` if defined
3. `np.zeros(7)` as a last fallback

Recommended default home posture:

```python
q_home = np.deg2rad([0, -30, 0, 60, 0, 45, 0])
```

## Step 2: Build Safe Joint Bounds

Read URDF joint bounds:

```python
lower, upper = kin.joint_bounds()
```

Apply a safety margin:

```python
margin = np.deg2rad(args.safety_margin_deg)
lower_safe = lower + margin
upper_safe = upper - margin
```

Hard rule:
- every joint must satisfy `lower_safe[i] < q[i] < upper_safe[i]`
- if a safe range becomes empty, fail immediately with a clear error

Print for every joint:
- raw limit
- safe limit
- safe range in degrees

## Step 3: Generate Prepare IK Candidates

Implement:

```python
def solve_prepare_candidates(
    kin,
    target_pos,
    target_R,
    current_joints,
    lower_safe,
    upper_safe,
    candidate_count=80,
):
    ...
```

Candidate seed pool should include:
- `current_joints`
- `q_home`
- joint-center posture `0.5 * (lower_safe + upper_safe)`
- noisy perturbations near `current_joints`
- random samples inside safe bounds

Suggested seed generation:

```python
seeds = []
seeds.append(current_joints)
seeds.append(q_home)
seeds.append(0.5 * (lower_safe + upper_safe))

for _ in range(20):
    seeds.append(current_joints + rng.normal(0, np.deg2rad(20), size=7))

for _ in range(candidate_count):
    seeds.append(rng.uniform(lower_safe, upper_safe))
```

Per-seed solver residual should keep the main pose exact first:

```python
residual = [
    100.0 * pos_err,
    10.0 * rot_err,
    0.005 * center_err,
]
```

Important:
- do not overweight `q - current_joints` here
- the main objective is not the shortest move, but a good prepare pose for future cutting

Candidate acceptance rules:
- `pos_error < 1e-4 m`
- `rot_error < np.deg2rad(0.06)`
- `min_joint_margin >= safety_margin`

Deduplicate near-identical IK solutions:

```python
if np.linalg.norm(wrap_to_pi(q_new - q_old)) < np.deg2rad(3):
    duplicate = True
```

If fewer than 2 valid candidates are found:
- do not crash immediately
- print a warning
- still continue if possible

## Step 4: Generate Cut Preview Poses

First version only previews a single down-cut.

Use the robot base convention already validated:
- `base +Y` is downward

Implement:

```python
def generate_cut_preview_poses(target_pos, target_R, cut_depth, preview_steps):
    poses = []
    cut_dir_base = np.array([0.0, 1.0, 0.0])

    for i in range(preview_steps + 1):
        s = i / preview_steps
        pos_i = target_pos + s * cut_depth * cut_dir_base
        R_i = target_R
        poses.append((pos_i, R_i))

    return poses
```

First-stage preview only:
- prepare → down

Do not implement full multi-cycle cutting yet.

## Step 5: Roll Out Preview IK From Each Candidate

Implement:

```python
def rollout_cut_preview(
    kin,
    preview_poses,
    q_prepare,
    lower_safe,
    upper_safe,
):
    ...
```

Rules:
- use `q_prev = q_prepare`
- for each preview pose, solve IK using `q_prev` as the seed
- preserve continuity between preview steps
- keep joint_1 stable relative to `q_prepare`
- keep wrists from over-twisting

Suggested preview residual:

```python
residual = [
    100.0 * pos_err,
    10.0 * rot_err,
    0.05 * (q - q_prev),
    0.3 * np.array([q[0] - q_prepare[0]]),
    0.02 * center_err,
]
```

Reject rollout if:
- any preview IK fails
- any preview pose exceeds final error tolerance
- any joint margin violates the 15° safety margin

## Step 6: Score Each Candidate by Future Cost

Implement:

```python
def score_preview_trajectory(q_traj, lower_safe, upper_safe, q_prepare, current_joints):
    ...
```

Suggested score terms:
- `path_cost`: total joint motion along preview trajectory
- `jump_cost`: maximum single-step joint jump
- `joint1_cost`: joint_1 stability across preview
- `limit_cost`: penalty for approaching safe bounds
- `wrist_cost`: over-twisting penalty for joints 6 and 7
- `current_cost`: distance from current joints, low weight only

Suggested structure:

```python
total = (
    1.0 * path_cost
    + 5.0 * jump_cost
    + 3.0 * joint1_cost
    + 0.001 * limit_cost
    + 0.02 * wrist_cost
    + 0.01 * current_cost
)
```

Important:
- do not use only `q - current_joints`
- the prepare pose must be chosen for future cutting quality

## Step 7: Choose the Best Prepare Pose

Implement selection logic:

1. discard failed preview rollouts
2. discard candidates with `min_margin_deg < safety_margin_deg`
3. sort by `score["total"]`
4. choose the first candidate

Print top 5 candidates with:
- rank
- total score
- path_cost
- jump_cost
- joint1_range_deg
- min_margin_deg
- wrist_cost
- current_cost
- `q_prepare` in degrees

## Step 8: Publish Best Prepare Pose to RViz

Use the same JointState publishing approach already used in `demo_offline_ik_to_rviz.py`:

```python
JointState.name = ACTIVE_JOINT_NAMES
JointState.position = best_q_prepare
```

Run RViz with:

```bash
ros2 launch ar5_07r_w4c1c1_description display.launch.py use_joint_gui:=false
```

The selector should publish `best_q_prepare` to `/joint_states` so RViz updates the robot model.

## Required Final Output

The script must print at least:

- `current_joints` in degrees
- `target_prepare` position and rotation setup
- candidate summary:
  - seeds tried
  - valid prepare candidates
  - preview success candidates
- best candidate:
  - `q_prepare` in degrees
  - prepare position error in mm
  - prepare rotation error in deg
  - minimum joint margin in deg
- future preview score:
  - total
  - path_cost
  - jump_cost
  - joint1_range_deg
  - min_margin_deg
  - wrist_cost
  - current_cost
- constraint check:
  - `x_flange dot base_X`
  - actual plane angle in deg

## Failure Modes to Report Clearly

If the pipeline fails, print the reason explicitly:

1. No IK solution for `target_prepare` inside safe bounds
2. Prepare IK exists, but cut preview cannot be executed
3. Preview executes, but no candidate satisfies the 15° margin rule
4. No `/joint_states` received, fallback posture was used

## Acceptance Criteria

### Prepare pose
- position error < 0.1 mm
- rotation error < 0.06 deg

### Safety
- all joints maintain at least 15 deg distance from their limits

### Preview quality
- all preview points must solve successfully
- joint_1 should remain as stable as possible during the cut preview
- max single-step jump should not be abnormally large

### RViz
- robot model must display the selected `best_q_prepare`

## Non-goals for First Version

Do not implement:
- real xCore SDK integration
- real cutting execution
- StreamExecutor
- trajectory cache
- full multi-cycle cutting preview
- path comfort as the only metric
- first-solution-only IK

## Recommended Implementation Order

1. Implement `/joint_states` reader with fallback posture
2. Implement safe bound builder with 15° margin
3. Implement multi-seed prepare candidate search
4. Implement one-step down-cut preview
5. Implement preview rollout IK
6. Implement future-cost scoring
7. Implement candidate ranking and selection
8. Publish `best_q_prepare` to RViz

## Notes

This module is a prepare-pose selector, not a path optimizer for approach motion.

The key question is:

> Which prepare pose makes the upcoming tofu cut the smoothest, most stable, and least prone to wrist twisting or limit proximity?

That is the objective of this stage.
