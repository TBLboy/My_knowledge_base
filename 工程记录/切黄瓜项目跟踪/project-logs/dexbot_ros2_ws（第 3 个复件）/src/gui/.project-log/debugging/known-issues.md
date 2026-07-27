# Known Issues

## Active Issues

### ISSUE-20260518-001: Disable Does Not Prevent Motion

- **Symptom**: After clicking Disable, arm still responds to World Jog and other motion commands.
- **Root Cause**: All motion methods in `lbot_robot_xcore.py` call `_ensure_power_ready()` which auto-repowers the arm via `setPowerState(True)`.
- **Affected Edge**: B->C (Execute Operation)
- **Workaround**: Use E-Stop instead of Disable to block motion.
- **Fix Status**: Not implemented — user chose not to add state tracking, only fixed safe-button issue.
- **Repro**: 1. Click Disable. 2. Click World Jog X+. 3. Arm moves.
- **Related Files**: `lbot_robot_xcore.py:1229-1249` (enable_arm), `lbot_robot_xcore.py:1712-1731` (move_rt_cartesian_segment), `lbot_robot_xcore.py:3111-3127` (_ensure_power_ready)

### ISSUE-20260429-001: Web GUI Login Cookie Not Set

- **Symptom**: Login returned 200 OK but subsequent requests redirected to /login.
- **Root Cause**: `auth.login(response, username)` called `response.set_cookie()` on the FastAPI response argument, but the handler returned a new `JSONResponse` instead of the modified response object.
- **Fix**: Inlined session creation and `set_cookie` directly in the `login` handler, returned the same response with cookie set.
- **Status**: Resolved 2026-04-29.

### ISSUE-20260429-002: Web GUI WebSocket 403

- **Symptom**: `/ws` always returned 403 because `websocket.cookies.get(auth.COOKIE_NAME)` was empty.
- **Root Cause**: httpOnly cookies cannot be read by JavaScript, so the browser cannot pass them in the WebSocket handshake URL.
- **Fix**: Changed login to redirect with `?token=<session_token>` query parameter; pages store token in sessionStorage; WebSocket connects with `ws://host/ws?token=<token>`.
- **Status**: Resolved 2026-04-29.

### ISSUE-20260429-003: Web GUI update_me 500 Error

- **Symptom**: `POST /api/me` → 500 `AttributeError: 'coroutine' object has no attribute 'get'`
- **Root Cause**: `update_me` was a sync `def` but called `request.json()` (which is a coroutine in FastAPI) without `await`.
- **Fix**: Changed `update_me` to `async def update_me` and added `await` on `request.json()`.
- **Status**: Resolved 2026-04-29.

### ISSUE-20260518-002: E-Stop Button Disabled During Motion

- **Symptom**: During World Jog or any motion operation, all buttons including E-Stop were disabled.
- **Root Cause**: `_run_async` disabled all buttons in `self._buttons` list, which included E-Stop and Stop Motion.
- **Fix**: Added `safe=True` parameter to `_add_button`; E-Stop and Stop Motion added to separate `_safe_buttons` list; `_run_async` only disables `_buttons`, not `_safe_buttons`.
- **Status**: Resolved 2026-05-18.
