# Debugging History

## 2026-05-18 - E-Stop Disabled During Motion

- **Issue**: E-Stop and Stop Motion buttons were disabled during World Jog operation.
- **Investigation**: Found `_run_async` at `arm_hand.py:379-381` disables all buttons in `self._buttons`. E-Stop was added to this list.
- **Fix**: Separated safe buttons into `self._safe_buttons` list. Added `safe=True` parameter to `_add_button`. Marked E-Stop, Stop Motion (Arm Ops), and Stop (top bar) as safe.
- **Verification**: `python3 -m py_compile` passes. Code review confirms safe buttons excluded from disable loop.
- **Files Changed**: `pages/arm_hand.py` (lines 39-40, 134, 165, 167, 361-368)

## 2026-05-18 - Disable Does Not Prevent Motion

- **Issue**: After clicking Disable, arm still responds to motion commands.
- **Investigation**: Traced call chain: `set_enabled(False)` → `setPowerState(False)` (success). Then `world_jog` → `move_rt_cartesian_segment` → `_ensure_power_ready()` → `setPowerState(True)`. Backend auto-repowers.
- **Root Cause**: Backend design assumes caller ensures arm is ready; motion methods always call `setPowerState(True)`.
- **Decision**: User chose NOT to implement GUI-level state tracking. Only fixed safe-button issue. Disable behavior remains as-is (informational, not blocking).
- **Files Checked**: `lbot_robot_xcore.py:1229-1249`, `lbot_robot_xcore.py:1712-1731`, `lbot_robot_xcore.py:3111-3127`

## 2026-04-29 - Web GUI Login Cookie Not Set

- **Issue**: Login succeeded but cookie not sent to browser.
- **Investigation**: `auth.login(response, username)` modified response object but handler returned new JSONResponse.
- **Fix**: Inlined session creation and set_cookie in login handler.
- **Verification**: Server compiles clean; login flow works.

## 2026-04-29 - Web GUI WebSocket 403

- **Issue**: WebSocket handshake always returned 403.
- **Investigation**: httpOnly cookies not forwarded in WebSocket upgrade request.
- **Fix**: Token passed via URL query parameter, stored in sessionStorage, appended to WebSocket URL.
- **Verification**: Server compiles clean; WebSocket connects after IP set.

## 2026-04-29 - Web GUI update_me 500

- **Issue**: POST /api/me returned 500.
- **Investigation**: Sync handler called async `request.json()` without await.
- **Fix**: Changed to async def, added await.
- **Verification**: POST /api/me → 200 OK.

## 2026-04-30 - Logging Integration

- **Issue**: No unified logging across GUI layers.
- **Investigation**: Each layer used different logging approach (print, stderr, basicConfig).
- **Fix**: Created `services/logger.py` with TimedRotatingFileHandler. Integrated in all layers.
- **Verification**: All 8 modified files compile clean.
