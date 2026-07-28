# Deployment

## Tkinter GUI (Local Mode)

### Requirements

- Python 3.10+
- ROS2 environment (Humble/Iron)
- `dexbot_toolbox` installed in workspace
- `linkerbot` package installed
- xCore SDK available at `src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12/`
- Network access to robot arm (192.168.2.160/161)
- CAN interface `can0` configured

### Start Command

```bash
cd ~/Project/dexbot_ros2_ws
source install/setup.bash
python3 src/gui/main.py
```

### Dependencies

- ROS2 launch: `ros2 launch dexbot_bringup dual_xcore_controllers.launch.py`
- Arm IPs: right=192.168.2.161, left=192.168.2.160

## Web GUI (Server Mode)

### Requirements

- Ubuntu 22.04 server
- Python 3.10+
- ROS2 environment
- `pip install fastapi uvicorn aiofiles`
- nginx (production)
- systemd (production)

### Development Mode

```bash
cd ~/Project/dexbot_ros2_ws
source install/setup.bash
cd src/gui/web
uvicorn server:app --host 0.0.0.0 --port 80 --workers 1
```

### Production Mode (systemd + nginx)

1. **systemd service**:
   ```bash
   sudo cp dexbot-web.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable dexbot-web
   sudo systemctl start dexbot-web
   ```

2. **nginx reverse proxy**:
   ```bash
   sudo apt install nginx
   sudo cp nginx.conf /etc/nginx/sites-available/dexbot-web
   sudo ln -s /etc/nginx/sites-available/dexbot-web /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

3. **Access**: `http://<server-ip>/`

### Deployment Files

| File | Purpose | Location |
|------|---------|----------|
| `dexbot-web.service` | systemd unit | gui/web/dexbot-web.service |
| `nginx.conf` | nginx reverse proxy | gui/web/nginx.conf |

### Scaling

- Single uvicorn process (--workers 1) handles all HTTP + WebSocket connections
- Each WebSocket connection spawns a separate worker.py subprocess
- One crash does not affect other users
- Suitable for < 50 concurrent users

## Log Locations

| Mode | Log File | Rotation |
|------|----------|----------|
| Tkinter | `src/gui/logs/tkinter_YYYY-MM-DD.log` | Midnight, 30-day retention |
| Web server | `src/gui/logs/web_YYYY-MM-DD.log` | Midnight, single file |
| Web worker | stderr (captured by server.py) | Per-session |

## Database

- SQLite: `src/gui/web/users.db`
- Tables: `users`, `sessions`
- Location: same directory as `web/server.py`
