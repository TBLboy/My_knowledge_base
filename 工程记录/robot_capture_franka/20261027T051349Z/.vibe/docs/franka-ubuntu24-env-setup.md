# Franka FR3 系统环境配置（Ubuntu 24.04，libfranka，不装 ROS）

面向一台**全新的 Ubuntu 24.04 amd64 电脑**：从零装好 PREEMPT_RT 内核、实时权限、NVIDIA 驱动（可选）、libfranka，并验证能与 FR3 通信。

只保留主干操作链。历史调试过程、本机专属 UUID、备份文件路径不在此文档中。

---

## 0. 开工前先确定这些值

后面所有命令中的尖括号都从这里取值。

| 占位符 | 含义 | 示例 |
| --- | --- | --- |
| `<USER>` | 登录用户名 | `embody` |
| `<RT_VER>` | RT 内核版本号 | `6.8.0-rt8` |
| `<KREL>` | 编译后的内核 release（含 LOCALVERSION） | `6.8.0-rt8-franka` |
| `<NVIDIA_VER>` | NVIDIA 驱动版本 | `615.71.09` |
| `<ROBOT_IF>` | 直连机器人控制柜的网口名 | `eno1` |
| `<ROBOT_IP>` | 机器人 Shop Floor 地址 | `172.16.0.3` |
| `<HOST_IP>` | 该网口上给电脑的静态地址 | `172.16.0.101` |

确认机器人侧信息：Desk（`https://<ROBOT_IP>`）可打开、FCI 可激活、Robot System image 版本满足 libfranka 兼容表要求（Robot System ≥5.9.0 对应 libfranka ≥0.18.0）。

## 1. 前置条件

- BIOS 中 **Secure Boot 关闭**（自编译内核未签名）。
- 保留原有 generic 内核，RT 内核作为**新增**内核安装，不删除、不覆盖。
- 内核编译需要数十 GB 磁盘空间，先确认 `df -h` 余量。

## 2. 安装内核编译依赖

```bash
sudo apt-get update
sudo apt-get install -y build-essential bc curl debhelper dpkg-dev devscripts fakeroot \
  libssl-dev libelf-dev bison flex cpio kmod rsync libncurses-dev
```

## 3. 获取内核源码与 RT 补丁

```bash
mkdir -p ~/franka-rt/linux-<RT_VER>
cd ~/franka-rt/linux-<RT_VER>

curl -fLO https://mirrors.tuna.tsinghua.edu.cn/kernel/v6.x/linux-6.8.tar.xz
curl -fLO https://mirrors.tuna.tsinghua.edu.cn/kernel/v6.x/linux-6.8.tar.sign
curl -fLO https://mirrors.tuna.tsinghua.edu.cn/kernel/projects/rt/6.8/older/patch-6.8-rt8.patch.xz
curl -fLO https://mirrors.tuna.tsinghua.edu.cn/kernel/projects/rt/6.8/older/patch-6.8-rt8.patch.sign

xz -dk linux-6.8.tar.xz
xz -dk patch-6.8-rt8.patch.xz
```

验签（首次会缺公钥，先导入）：

```bash
gpg --keyserver hkps://keyserver.ubuntu.com --recv-keys \
  647F28654894E3BD457199BE38DBBDC86092693E \
  57892E705233051337F6FDD105641F175712FA5B

gpg --verify linux-6.8.tar.sign linux-6.8.tar
gpg --verify patch-6.8-rt8.patch.sign patch-6.8-rt8.patch
```

两份都应报“完好的签名”。换成其他内核/补丁版本时，密钥与路径需按上游重新核对。

## 4. 打补丁并配置内核

补丁只对**刚解包的干净源码**应用一次。

```bash
cd ~/franka-rt/linux-<RT_VER>
tar -xf linux-6.8.tar
cd linux-6.8
patch -p1 --batch < ../patch-6.8-rt8.patch
make kernelversion
```

从当前运行内核迁移配置，再改成 RT：

```bash
cp /boot/config-$(uname -r) .config

scripts/config --disable DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT
scripts/config --disable DEBUG_INFO_DWARF4
scripts/config --disable DEBUG_INFO_DWARF5
scripts/config --enable DEBUG_INFO_NONE

scripts/config --set-str SYSTEM_TRUSTED_KEYS ""
scripts/config --set-str SYSTEM_REVOCATION_KEYS ""

scripts/config --disable PREEMPT_NONE
scripts/config --disable PREEMPT_VOLUNTARY
scripts/config --disable PREEMPT
scripts/config --enable PREEMPT_RT

scripts/config --set-str LOCALVERSION "-franka"
scripts/config --disable LOCALVERSION_AUTO

make olddefconfig
```

必须核对：

```bash
grep -E '^CONFIG_PREEMPT_RT=|^CONFIG_DEBUG_INFO_NONE=|^CONFIG_SYSTEM_(TRUSTED|REVOCATION)_KEYS=' .config
make kernelrelease   # 应输出 <KREL>
```

`olddefconfig` 出现少量新旧配置类型警告属正常，以这两条命令的实际输出为准。

## 5. 编译并安装内核

普通用户执行，不要 sudo：

```bash
set -o pipefail
make -j$(nproc) bindeb-pkg 2>&1 | tee ../build.log
ls -lh ../*.deb
```

只安装 image 与 headers，**不要**安装本次构建产生的 `linux-libc-dev`：

```bash
sudo dpkg -i \
  linux-image-<KREL>_*.deb \
  linux-headers-<KREL>_*.deb
```

## 6. 实时权限

```bash
sudo groupadd -f realtime
sudo usermod -aG realtime "$USER"

sudo tee /etc/security/limits.d/99-franka-realtime.conf >/dev/null <<'EOF'
@realtime soft rtprio 99
@realtime hard rtprio 99
@realtime soft memlock unlimited
@realtime hard memlock unlimited
EOF
```

注销重新登录后生效（`memlock` 也可按需写成固定 KiB 值）。

## 7. NVIDIA 驱动适配 RT 内核（无独显可跳过）

机器人控制不需要显卡；只有机器需要驱动显示器/GPU 时才做。原有驱动模块是针对 generic 内核编译的，RT 内核必须重新构建。

安装同版本 DKMS 包（`IGNORE_PREEMPT_RT_PRESENCE=1` 仅用于绕过构建检查，不代表任何版本组合都兼容）：

```bash
sudo env IGNORE_PREEMPT_RT_PRESENCE=1 \
  apt-get install -y nvidia-dkms-<NVIDIA_VER>-server-open
```

DKMS 通常只给当前运行的内核装模块，需显式指定 RT 内核：

```bash
sudo env IGNORE_PREEMPT_RT_PRESENCE=1 \
  dkms install -m nvidia -v <NVIDIA_VER> -k <KREL>

sudo update-initramfs -u -k <KREL>
```

核对：

```bash
dkms status
modinfo -k <KREL> -F filename nvidia
```

## 8. GRUB 启动菜单

默认项可以不改，但要保证能手动选到 RT 内核。文本菜单最稳：

```bash
sudo mkdir -p /etc/default/grub.d
sudo tee /etc/default/grub.d/99-franka.cfg >/dev/null <<'EOF'
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=15
GRUB_TERMINAL_OUTPUT=console
EOF

sudo update-grub
sudo grub-script-check /boot/grub/grub.cfg
```

重启后在 `Advanced options for Ubuntu` 里选 `<KREL>`，**不要选 recovery mode**；起不来就回退原来的 generic 内核。

## 9. RT 启动后验收

```bash
uname -r                 # <KREL>
cat /sys/kernel/realtime # 1
id                       # 含 realtime 组
ulimit -r                # 99
ulimit -l                # 与 limits 配置一致
nvidia-smi               # 有独显时应正常加载
```

四项都符合才继续往下做。

## 10. 安装 libfranka

用官方 Ubuntu noble amd64 预编译包，不装 ROS：

```bash
mkdir -p ~/franka/libfranka-packages
cd ~/franka/libfranka-packages

curl -fLO https://github.com/frankarobotics/libfranka/releases/download/0.19.0/libfranka_0.19.0_noble_amd64.deb
curl -fLO https://github.com/frankarobotics/libfranka/releases/download/0.19.0/libfranka_0.19.0_noble_amd64.deb.sha256
sha256sum -c libfranka_0.19.0_noble_amd64.deb.sha256

sudo apt-get install -y ./libfranka_0.19.0_noble_amd64.deb
```

核对：

```bash
dpkg-query -W libfranka
ldd /usr/lib/libfranka.so | grep "not found"   # 应无输出
```

开发依赖：

```bash
sudo apt-get install -y cmake git libeigen3-dev libpoco-dev libfmt-dev
```

**版本必须与机器人系统匹配**，换机器人或升级 Robot System 时按官方兼容表重新选包。

## 11. 最小只读验证程序

```bash
mkdir -p ~/franka/read-state && cd ~/franka/read-state
```

`CMakeLists.txt`：

```cmake
cmake_minimum_required(VERSION 3.16)
project(franka_read_state LANGUAGES CXX)
find_package(Franka 0.19 REQUIRED)
add_executable(read_state main.cpp)
target_compile_features(read_state PRIVATE cxx_std_17)
target_link_libraries(read_state PRIVATE Franka::Franka)
```

`main.cpp`：

```cpp
#include <iostream>
#include <franka/exception.h>
#include <franka/robot.h>

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " <robot-ip>\n";
    return 1;
  }
  try {
    franka::Robot robot(argv[1]);
    const auto state = robot.readOnce();
    std::cout << "Joint positions (rad):";
    for (const auto q : state.q) std::cout << ' ' << q;
    std::cout << '\n';
  } catch (const franka::Exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
```

编译并运行（只读，不发送运动命令）：

```bash
cmake -S ~/franka/read-state -B ~/franka/read-state/build -DCMAKE_BUILD_TYPE=Release
cmake --build ~/franka/read-state/build -j2
timeout 15s ~/franka/read-state/build/read_state <ROBOT_IP>
```

成功输出七个关节角即表示链路通。无参数启动输出 Usage、退出码 1 属正常。

## 12. 网络：直连机器人

### 12.1 确认物理接线

```bash
ip -br link                    # 找出接控制柜的网口 <ROBOT_IF>
sudo ethtool <ROBOT_IF> | grep -E "Speed|Link detected"
```

多台机器人时，**每个机器人单独一个网口**，不要依赖同一网段的默认路由，否则会走错出口。

### 12.2 配置静态地址

```bash
sudo nmcli connection add type ethernet ifname <ROBOT_IF> con-name franka-<ROBOT_IF> \
  ipv4.method manual \
  ipv4.addresses <HOST_IP>/24 \
  ipv4.never-default yes \
  ipv6.method ignore
sudo nmcli connection up franka-<ROBOT_IF>
```

给机器人加 `/32` 主机路由，确保精确出口：

```bash
sudo nmcli connection modify franka-<ROBOT_IF> \
  +ipv4.routes "<ROBOT_IP>/32"
sudo nmcli connection up franka-<ROBOT_IF>
```

### 12.3 验证

```bash
ip route get <ROBOT_IP>        # 出口应为 <ROBOT_IF>，源地址 <HOST_IP>
ping -c 3 <ROBOT_IP>
```

### 12.4 常见坑：连接反复“激活失败”

现象：网口每几十秒 DHCP 超时重试，即使静态地址已配好。

原因：`/etc/netplan/50-cloud-init.yaml` 里该网口的 `dhcp4: true` 在合并配置时仍然生效，覆盖或干扰 NetworkManager 的 manual 设置。只改 `90-NM-*.yaml` 往往会被下次保存覆盖。

处理：在 cloud-init 的 netplan 文件中把该网口的 `dhcp4` 关掉，保留 MAC 匹配与 `set-name`：

```yaml
network:
  version: 2
  ethernets:
    <ROBOT_IF>:
      match:
        macaddress: "<该网口 MAC>"
      dhcp4: false
      set-name: "<ROBOT_IF>"
```

立即生效，不需重启电脑或整体重启网络：

```bash
sudo netplan generate
sudo nmcli connection reload
sudo nmcli connection up franka-<ROBOT_IF>
```

若之后 cloud-init 或其他工具重写了该文件，需要重新核对。

## 13. 日常启动与验收

1. GRUB 选 `Advanced options for Ubuntu → Ubuntu, with Linux <KREL>`。
2. 浏览器打开 `https://<ROBOT_IP>`，在 Desk 中激活 FCI。
3. 依次检查：

```bash
uname -r
cat /sys/kernel/realtime
ulimit -r; ulimit -l
ip route get <ROBOT_IP>
timeout 15s ~/franka/read-state/build/read_state <ROBOT_IP>
```

预期：内核为 `<KREL>`、实时标志 `1`、`rtprio 99`、路由走 `<ROBOT_IF>`、最后打印七个关节角。

## 14. 常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `Connection to FCI refused` | Desk 中未激活 FCI | 在 Desk 激活后重试，不要重装 libfranka |
| 开机进的是 generic 内核 | GRUB 默认项未变 | 手动在 Advanced options 选择，或改 `GRUB_DEFAULT` |
| `modinfo -k <KREL> nvidia` 为空 | DKMS 未给新内核构建 | `dkms install -m nvidia -v <NVIDIA_VER> -k <KREL>` |
| 网口反复激活失败 | cloud-init 的 `dhcp4: true` | 见 12.4 |
| 链接库缺失 | 未装运行依赖 | `ldd /usr/lib/libfranka.so` 查看缺失项 |

## 15. 本文档未覆盖

- RT 延迟调优与验收（`cyclictest`、`isolcpus`/`nohz_full`、关闭 `irqbalance`、CPU governor、C-state）。
- 1 kHz 实时控制回路与运动测试。
- GPU 负载下的控制性能。

上述项目完成前，只能认为“环境就绪、可只读通信”，**不等于实时控制已验证**。
