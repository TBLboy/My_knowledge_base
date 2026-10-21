# Blocked: enable data upload

The active balanced Task `data-upload-enable-20261021` is blocked before configuration change. In `robot_capture_franka-data_uplload/config.yaml`, upload is currently disabled and configured for local `/mnt/nas/forge/franka/raw`. `/mnt/nas` is not mounted and the destination does not exist. Enabling it now is unsafe because the local sink code creates missing paths and could save data to an unintended host-local directory. Resume when the NAS is mounted and verified, or the user provides an approved SSH destination.
