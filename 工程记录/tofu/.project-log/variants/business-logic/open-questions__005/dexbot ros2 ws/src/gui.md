# Open Business Logic Questions

## Active Questions

### Q-20260518-001

- Related node: C
- Related edge: B->C
- Question: Disable button does not prevent motion — all motion methods (move_rt_cartesian_segment, move_joints, etc.) internally call _ensure_power_ready() which auto-repowers the arm. Should GUI-level state tracking be added to block motion when disabled, or should the backend be modified?
- Why it matters: Safety — operator expects Disable to prevent motion.
- Options:
  - A: Add _enabled state flag in ArmControlService, check before each motion method
  - B: Modify lbot_robot_xcore.py to check power state before motion
  - C: Use E-Stop instead of Disable for motion blocking (current workaround)
- Current status: Open — user chose not to implement state tracking, only fixed safe-button disabling bug

### Q-20260518-002

- Related node: B
- Related edge: A->B
- Question: Should the web GUI worker.py implement the same safe-button logic (E-Stop/Stop Motion always available) as the Tkinter GUI?
- Why it matters: Consistency between Tkinter and Web modes.
- Options:
  - A: Add safe-button equivalent in web/app.js (E-Stop and Stop buttons always enabled)
  - B: No change — web UI handles busy state differently
- Current status: Open

### Q-20260518-003

- Related node: A
- Related edge: A->B
- Question: Single process for dual-arm vs two separate instances — should the GUI control both arms in one process or require two separate GUI instances?
- Why it matters: Architecture and resource allocation.
- Options:
  - A: Single process with side selection (current implementation)
  - B: Two separate processes, one per arm
- Current status: Open — user has not confirmed

## Resolved Questions

### Q-20260429-001

- Related node: A
- Question: Should each web user have a login/password, or is config.yaml sufficient?
- Answer: Username + password, server-side SQLite per user.
- Resolved: 2026-04-29

### Q-20260429-002

- Related node: A
- Question: Should the Tkinter GUI remain independently runnable alongside the web server?
- Answer: Yes, both runnable, same service layer.
- Resolved: 2026-04-29

### Q-20260429-003

- Related node: A
- Question: Preferred frontend framework (plain HTML/JS vs React/Vue)?
- Answer: Plain HTML + vanilla JS, no framework.
- Resolved: 2026-04-29

### Q-20260429-004

- Related node: A
- Question: Admin UI for user management — page or direct SQLite edits?
- Answer: Self-registration page, users register themselves.
- Resolved: 2026-04-29
