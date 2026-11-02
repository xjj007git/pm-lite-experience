# PyMotion Lite 使用手册

本手册适用于 `pymotion-lite 1.0.1`，面向第一次使用 PyMotion Lite 的用户，也可作为项目开发时的 API 查询手册。内容覆盖产品概览、Windows 与 Ubuntu 环境安装、首次连接、执行器控制、传感器读取、实时功能、完整例程、安全操作和常见问题。

第一次使用时，建议先完成安装、在终端设置出厂 Token 并通过 USB 验证连接；需要使用 Wi-Fi 时，再完成配网并设置用户 Token。只需查询某个接口时，可直接查看第六部分的 API 速查。

Python 程序统一使用以下入口：

```python
import pymotion as pm
```

## 1 快速入门

### 1.1 手册概览

#### 1.1.1 阅读路线

如果是第一次使用，建议按以下顺序阅读和操作：

1. 完成第 1 章的 SDK 安装，在终端设置设备 Token，并优先通过 USB 验证连接。全新设备使用出厂 Token，不要求先完成 Wi-Fi 配网。
2. 使用第 2 章的连接示例确认电脑能够发现并连接设备。
3. 阅读第 3 章，理解控制权、停止、急停以及 `timeout`、`max_age`、`duration` 和 `valid_for` 的区别。
4. 根据实际硬件阅读第 2～3 部分。每节都给出对象入口、方法语法、参数含义、返回值和最小示例。
5. 在需要连续接收数据或持续更新运动目标时，再阅读第 4 部分的实时功能。
6. 开始编写项目时查看第 5.1 节；程序出现异常时先查看第 5.2～5.3 节；需要快速查找方法签名时查看第 6.1 节。

只想尽快确认设备是否可用时，完成第 1.2～1.4 节后，直接运行 Quick Start 示例即可。涉及电机或舵机的示例必须先接好外部执行器电源，并让车轮悬空、舵臂周围没有障碍物。

#### 1.1.2 功能概览

| 功能 | 主要入口 | 典型用途 | 是否需要控制权 |
| --- | --- | --- | --- |
| 发现和连接 | `pm.lite.list_devices()`、`pm.lite.connect()` | 查找设备，建立 USB 或 Wi-Fi 连接 | 否 |
| 设备安全 | `lite.stop()`、`lite.emergency_stop()` | 正常停止、危险情况下急停 | 否 |
| 直流电机 | `lite.motor()`、`lite.motors` | 开环 PWM、闭环速度、位置控制 | 写入目标时需要 |
| PWM 舵机 | `lite.pwm_servo()`、`lite.pwm_servos` | 连续旋转或角度控制 | 写入目标时需要 |
| TTL 舵机 | `lite.ttl_servo()`、`lite.ttl_servos` | 带反馈的位置或速度控制 | 写入和配置时需要 |
| 普通传感器 | `lite.sensors()`、`lite.imu()` 等 | 偶尔读取一份当前数据 | 否 |
| 雷达和里程计 | `lite.lidar`、`lite.odometry` | 距离扫描和底盘位姿估计 | 读取不需要，配置需要 |
| OLED | `lite.oled` | 显示文字、状态和动态数据 | 否 |
| 实时数据 | `lite.realtime.open()` | 连续接收传感器和状态事件 | 只读会话不需要 |
| 实时命令 | `session.commands` | 以最高约 20 Hz 更新执行器目标 | 需要 |

#### 1.1.3 API 说明的阅读方法

本手册按统一格式说明 API：

1. **用途**说明什么时候应该使用该接口。
2. **语法**给出可直接复制的调用形式。
3. **参数**说明类型、默认值、有效范围以及填写方法。
4. **返回值**说明成功后得到什么对象或数值。
5. **示例**展示最小可运行用法。
6. **使用说明**解释阻塞行为、控制权要求、安全限制和常见误区。

API 表格中的常见写法：

| 写法 | 用户应该怎样理解 |
| --- | --- |
| `str \| None` | 可以是字符串，也可以是 `None` |
| `tuple[...]` | 一组固定顺序的数据，只读取，不要直接修改 |
| `Mapping[int, ...]` | 类似字典，通过端口号或舵机 ID 查找对应值 |
| `-100～100` | 两端数值都可以使用，即最小值为 -100，最大值为 100 |
| `*` 后的参数 | 调用时必须写出参数名，例如 `duration=1.0` |
| `None` 默认值 | 用户没有为该参数指定值；具体行为以对应接口说明为准 |

文中的长度默认使用 mm，角度使用度，时间使用秒。字段名带 `_ms`、`_mm_s2`、`_rad_s` 等后缀时，以字段后缀标明的单位为准。

`timeout=5.0` 表示本次操作最多等待 5 秒，并不表示执行器一定运动 5 秒。控制方法成功时通常返回 `None`；读取方法通常返回带属性的结果对象，例如通过 `state.measured_rpm` 读取电机实测转速。

#### 1.1.4 普通 API 与实时 API

| 用户需求 | 推荐方式 | 原因 |
| --- | --- | --- |
| 启停一次电机、移动一次舵机、读取一次传感器 | 普通 API | 调用直接，适合顺序执行和教学示例 |
| 一次设置多个同类执行器 | 批量 API | 一次提交多个端口，程序更简洁 |
| 以 10～20 Hz 连续更新运动目标 | 实时命令 | 始终优先发送最新目标，适合连续控制 |
| 连续接收一种或多种传感器数据 | 实时数据 | 不需要反复调用单次读取方法 |
| 一边读取循迹或姿态，一边连续控制电机 | 同一个实时会话同时开启数据和命令 | 数据与命令使用同一会话管理 |

普通 API 和实时 API 使用同一个 `Lite` 连接。一个程序不应同时创建多个实时会话；实时会话关闭后，可以继续使用普通 API。

#### 1.1.5 第一个可运行程序

下面的程序只连接设备并读取状态，不会让执行器动作。第一次运行时建议先使用 USB，并按第 1.2.6 节在运行程序的终端中提供设备 Token：

```python
import pymotion as pm


with pm.lite.connect(transport="usb") as lite:
    status = lite.status(max_age=1.0)
    print("设备 ID:", status.device_id)
    print("连接方式:", lite.connection.transport)
    print("设备状态:", status.state)
```

运行成功后，应看到设备 ID、`usb` 和当前设备状态。出现异常时不要跳过错误信息，可按第 5.2～5.3 节逐项检查。

#### 1.1.6 手册结构

| 部分 | 包含内容 | 适合什么时候阅读 |
| --- | --- | --- |
| 第一部分 快速入门 | 概览、安装、首次使用、发现、连接和安全基础 | 第一次使用时按顺序阅读 |
| 第二部分 执行器控制 | 数字输出、直流电机、PWM 舵机和 TTL 舵机 | 接好对应执行器后阅读 |
| 第三部分 传感与设备信息 | 常规传感器、电源、雷达、里程计、OLED 和设备状态 | 读取数据或制作仪表盘时阅读 |
| 第四部分 实时功能 | 实时数据与实时命令 | 需要连续采集或连续控制时阅读 |
| 第五部分 示例与问题排查 | 学习路线、完整程序结构、异常处理和常见问题 | 开始做项目或遇到问题时阅读 |
| 第六部分 API 参考 | 正式公开 API 的签名、参数和返回类型 | 已熟悉功能并需要快速查询时阅读 |

### 1.2 安装与首次使用

**本节内容包括：** 开发环境要求、Windows 环境搭建、Ubuntu 环境搭建、Raspberry Pi 5 环境搭建、首次 AP 配网、Token 配置和板载指示灯。

#### 1.2.1 开发环境要求

- CPython 3.10～3.14。
- Windows 10/11 x64，或 Ubuntu 24.04 LTS amd64。Ubuntu 22.04 和 Ubuntu arm64 不受支持。
- USB 使用需要系统能够识别设备串口。
- Wi-Fi 使用需要电脑和设备位于能够互相访问的局域网。
- 电机和舵机必须使用符合硬件要求的外部电源；USB 供电不能代替执行器电源。

#### 1.2.2 Windows 环境搭建

Windows 用户使用 Windows 版 SDK 包。不要把 Ubuntu 包中的脚本和 Windows 包混在同一个目录，也不要只复制 `install.bat`；安装程序需要交付包中的完整文件结构。

##### 1.2.2.1 第一步：打开 Windows SDK 下载页面

在浏览器地址栏输入 `https://github.com/PyMotion-OS/PyMotion_windows.git`，进入 PyMotion Lite Windows SDK 下载页面。

##### 1.2.2.2 第二步：下载并解压 SDK 代码和例程

按照下图选择 **Code**，再选择 **Download ZIP**，下载 SDK 代码以及配套例程。

![Windows 版 SDK 下载位置](assets/user_manual/windows-download.png)

下载完成后，将 ZIP 完整解压到本地磁盘。建议使用路径较短、拥有写权限的目录，例如 `D:\PyMotionLiteSDK`。进入解压后的 SDK 目录，确认能够看到 `install.bat`、`open-sdk-vscode.bat`、`open-sdk-terminal.bat`、`docs`、`examples`、`runtime` 和 `wheels` 等内容。

##### 1.2.2.3 第三步：下载并安装 VS Code

在浏览器地址栏输入 `https://code.visualstudio.com/`，进入 VS Code 官网，下载 Windows 版本并完成安装。VS Code 用于查看和运行例程，但不是 SDK 与设备通信的必要条件。

![VS Code 下载页面](assets/user_manual/vscode-download.png)

##### 1.2.2.4 第四步：安装 Python 相关扩展

首次打开 VS Code 后，点击左侧扩展图标，在搜索框中输入 `Python`，按照下图依次安装红框中的四个 Python 相关扩展。通过 SDK 的专用启动脚本打开工程时，如果工作区提示其他推荐扩展，按提示安装即可，不需要自行更改 Python 路径。

![VS Code Python 扩展](assets/user_manual/vscode-python-extensions.jpeg)

##### 1.2.2.5 第五步：运行安装脚本

打开已经下载并解压的 SDK 代码文件夹，双击 `install.bat`，一键完成 SDK 安装。也可以在该目录打开 PowerShell 后运行：

```powershell
.\install.bat
```

![Windows 安装脚本位置](assets/user_manual/windows-install-script.png)

安装程序会校验 SDK 包，并为当前 Windows 用户准备隔离的 Python 环境。等待窗口显示 `Installation completed.` 后再关闭窗口。重复运行该脚本可以检查并更新同一套 SDK 环境。

![Windows 安装完成后的终端提示](assets/user_manual/windows-install-result.png)

如果窗口一闪而过，可在文件夹地址栏输入 `cmd` 并回车，再运行 `install.bat`，这样可以保留完整错误信息。

##### 1.2.2.6 第六步：打开 SDK 工程

安装完成后，双击 `open-sdk-vscode.bat`，打开已经选择好 SDK Python 的工程环境。没有安装 VS Code 时，可双击 `open-sdk-terminal.bat`，在 SDK 专用终端中运行例程。

![Windows 打开 SDK 工程](assets/user_manual/windows-open-vscode.png)

![Windows 中打开的 PyMotion Lite SDK 工作区](assets/user_manual/windows-workspace.png)

在专用终端中依次运行：

```powershell
pymotion doctor --offline
python examples\quick-start\01-pymotion-lite.py
```

第一条命令检查本机安装环境，不要求连接设备。第二条命令确认 Python 能够导入 SDK。准备连接设备时，再按本章后续内容设置 Token 并运行连接例程。

##### 1.2.2.7 Windows 验证结果和常见问题

- 出现 `ModuleNotFoundError: No module named 'pymotion'` 时，通常是程序使用了系统 Python。关闭当前窗口，通过 `open-sdk-vscode.bat` 或 `open-sdk-terminal.bat` 重新打开。
- 安装程序提示文件校验失败时，不要跳过校验。重新下载并完整解压原始 SDK 包。
- 找不到串口时，先确认 USB 线支持数据传输，并关闭串口助手、烧录工具等可能占用端口的软件。

#### 1.2.3 Ubuntu 环境搭建

Ubuntu 用户使用 Ubuntu 版 SDK 包。下列步骤仅适用于 Ubuntu 24.04 LTS amd64。Ubuntu 22.04 和 Ubuntu arm64 不受支持；树莓派 5 请使用下一节所述的 Debian 13 ARM64 专用 SDK 包。

##### 1.2.3.1 第一步：打开 Ubuntu SDK 下载页面

在浏览器地址栏输入 `https://github.com/PyMotion-OS/PyMotion_ubuntu.git`，进入 PyMotion Lite Ubuntu SDK 下载页面。

##### 1.2.3.2 第二步：下载并解压 SDK 代码和例程

按照下图选择 **Code** 和 **Download ZIP**，下载 SDK 代码以及配套例程，再将文件解压到当前用户有写权限的目录。

![Ubuntu 版 SDK 下载位置](assets/user_manual/ubuntu-download.png)

解压后应能看到 `setup-ubuntu.sh`、`open-sdk-vscode.sh`、`install.sh`、`docs`、`examples`、`udev` 和 `wheels` 等内容。

##### 1.2.3.3 第三步：安装 VS Code

如果已经安装 VS Code，可跳过本节。需要安装时，打开终端并执行：

```bash
sudo apt update
sudo apt install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
  | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
sudo apt update
sudo apt install code
code --version
```

##### 1.2.3.4 第四步：安装 Python 相关扩展

打开 VS Code 后，点击左侧扩展图标，在搜索框中输入 `Python`，按照下图依次安装红框中的四个 Python 相关扩展。也可以不安装 VS Code，直接在终端中运行 SDK 示例。

![Ubuntu 中安装 VS Code Python 扩展](assets/user_manual/vscode-python-extensions.jpeg)

##### 1.2.3.5 第五步：运行 Ubuntu 安装脚本

解压已经下载的 SDK 代码文件，打开该文件夹并启动终端，然后执行：

```bash
bash ./setup-ubuntu.sh
```

![Ubuntu 安装脚本及执行位置](assets/user_manual/ubuntu-setup-script.png)

请以普通桌面用户运行脚本，不要在整条命令前加 `sudo`。脚本需要安装系统依赖或 USB 规则时，会在具体步骤请求管理员权限。安装完成后，终端会显示 SDK Python、诊断命令和工程启动命令。

![Ubuntu 安装完成后的环境诊断](assets/user_manual/ubuntu-setup-diagnostics.jpeg)

如果运行安装脚本时设备尚未通过 USB 连接，诊断中的 `device_connection` 可能显示 `FAIL`，这只表示当时没有发现可验证的设备，不表示 SDK 安装失败。完成 USB 权限步骤、重新连接设备并重新登录后再执行诊断即可。

##### 1.2.3.6 补充：USB 权限和重新登录

首次安装 USB 规则或加入 `dialout` 用户组后，应完成以下操作：

1. 拔下并重新连接 PyMotion Lite 的 USB 线。
2. 注销当前 Ubuntu 用户并重新登录，使用户组变更生效。
3. 关闭占用串口的终端、串口助手或烧录工具。

##### 1.2.3.7 第六步：打开 SDK 工程

在 SDK 目录的终端中输入 `./open-sdk-vscode.sh`，打开已经配置好 Python 环境的工程。也可以使用下面的等效写法：

```bash
bash ./open-sdk-vscode.sh
```

![Ubuntu 中打开的 PyMotion Lite SDK 工作区](assets/user_manual/ubuntu-workspace.png)

在打开的 VS Code 终端中运行：

```bash
pymotion doctor --offline
python examples/quick-start/01-pymotion-lite.py
```

如果不使用 VS Code，可根据安装完成时打印的 SDK Python 路径运行例程。连接全新设备时，在终端设置出厂 Token 后即可通过 USB 验证；需要使用 Wi-Fi 时再完成 AP 配网。

##### 1.2.3.8 Ubuntu 验证结果和常见问题

- `Permission denied` 通常表示 USB 规则或用户组尚未生效。拔插设备并重新登录后再试。
- `code: command not found` 只影响 VS Code 启动，不影响 SDK 本身。可先在终端中运行例程。
- 不要用 `sudo python` 或 `sudo pip` 运行 SDK；这会绕过安装脚本创建的用户环境。

#### 1.2.4 Raspberry Pi 5 环境搭建

树莓派 5 使用单独的 Debian 13 ARM64 SDK 包。开始前请确认系统为 64 位 Debian 13（Trixie），已经安装 CPython 3.13，并确保树莓派能够稳定访问 GitHub。网络访问受限时，请按照所在网络的管理要求配置可用的代理或镜像服务。

##### 1.2.4.1 第一步：打开树莓派 SDK 下载页面

在浏览器地址栏输入 `https://github.com/PyMotion-OS/PyMotion_Raspberry.git`，进入 PyMotion Lite 树莓派 5 SDK 下载页面。

##### 1.2.4.2 第二步：下载并解压 SDK 代码和例程

按照下图选择 **Code** 和 **Download ZIP**，下载 SDK 代码以及配套例程。下载完成后，将 ZIP 文件解压到当前树莓派用户有写权限的目录。

![树莓派 5 SDK 下载位置](assets/user_manual/raspberry-pi-5-download.png)

##### 1.2.4.3 第三步：运行树莓派安装脚本

打开已经解压的 SDK 文件夹，在包含 `setup-debian.sh` 的目录中启动终端，然后执行：

```bash
bash ./setup-debian.sh
```

请使用普通用户运行，不要在整条命令前添加 `sudo`。脚本会检查 Debian 13、ARM64 和 Python 3.13，并创建 PyMotion Lite 专用 Python 环境；如果某个系统步骤需要管理员权限，脚本会在对应步骤单独提示。

![树莓派 5 中运行安装脚本](assets/user_manual/raspberry-pi-5-setup.png)

##### 1.2.4.4 第四步：设置设备 Token

安装完成后，在同一个终端中设置设备 Token。全新设备使用出厂 Token `123456`；已经修改过 Token 的设备应使用当前保存的值：

```bash
export PYMOTION_AUTH_TOKEN='123456'
```

不要把真实 Token 写入准备分享的代码、截图或公开仓库。关闭终端后，这个临时环境变量需要重新设置。

##### 1.2.4.5 第五步：运行第一个连接例程

连接 PyMotion Lite 的 USB 数据线并确认设备供电正常，然后在 SDK 解压目录中执行：

```bash
SDK_PYTHON="$HOME/.local/share/pymotion-lite/venv-cp313-debian13/bin/python"
"$SDK_PYTHON" examples/lite-learning-course/01-usb-connection.py
```

例程应显示设备 ID、`usb` 连接方式和设备状态，不会驱动电机或舵机。如果提示 USB 权限不足，请在 SDK 目录运行 `bash ./install-udev.sh`，然后拔插设备并重新登录当前用户。

#### 1.2.5 首次 AP 配网

AP 配网只在需要使用 Wi-Fi、修改用户 Token 或更换网络时进行。全新设备通过 USB 首次连接时不需要先完成本节操作。配置 Wi-Fi 时：

1. 给设备上电。
2. 电脑连接 `PyMotion-Lite-XXXX` 热点，出厂热点密码为 `pymotionlite`。
3. 若热点没有出现，单次按下并释放板上的 `CFG` 按键，等待设备重新进入配网模式。
4. 浏览器打开 `http://192.168.4.1:8787/wifi/setup`。
5. 填写 2.4 GHz Wi-Fi 名称、Wi-Fi 密码、设备 Token 和运行 SDK 的电脑地址。
6. 保存配置，等待设备加入目标网络。

服务器地址填写电脑在目标局域网中的地址，例如 `http://192.168.1.100:8787`。电脑 IP 改变后，需要重新进入配网页面更新该地址。

若要修改设备热点密码，请在页面中连续输入两遍相同的新密码；不修改时保持两个密码框为空。

修改热点密码是可选的安全措施，适合多人或公开环境，可避免他人使用公开的出厂默认密码进入设备热点。新密码应为 8～63 个可打印 ASCII 字符，并应妥善保存。板上的 `CFG` 按键只会让设备重新进入配网模式，不会清除或绕过已经设置的热点密码。如果忘记自定义热点密码，将无法通过按键直接恢复出厂默认密码，需要联系官方技术支持按恢复流程重新初始化设备。因此，如果没有可靠的密码保存方式，建议暂时保留出厂热点密码，并通过设备 Token 控制 SDK 访问权限。

#### 1.2.6 Token 配置

Token 是授权电脑连接和控制设备的访问口令。全新设备可直接使用出厂 Token `123456`，因此在终端设置该 Token 后即可通过 USB 连接，不需要先配网。通过配网页面设置新 Token 后，设备会记住新值，USB 与 Wi-Fi 随后都使用该用户 Token。

| 名称 | 用途 | 示例 |
| --- | --- | --- |
| Wi-Fi 密码 | 让设备加入路由器或手机热点 | 目标 Wi-Fi 的密码 |
| 设备热点密码 | 进入设备配网页面 | 出厂默认 `pymotionlite` |
| 设备 ID | 区分不同设备 | `90E5B1D51380` |
| 设备 Token | 授权 SDK 连接设备 | 出厂默认 `123456`；可改为用户设置的 1～16 字节口令 |

Token 长度为 1～16 个 UTF-8 字节，建议使用容易正确输入的英文字母和数字。电脑端提供的值必须与设备当前有效值完全一致，包括大小写。普通固件更新会保留用户设置的 Token；只有完整擦除设备存储后，设备才会重新使用出厂 Token。

SDK 按以下顺序取得 Token：

1. 如果 `pm.lite.connect(auth_token=...)` 明确传入了 Token，使用该值。
2. 如果没有传入 `auth_token`，读取环境变量 `PYMOTION_AUTH_TOKEN`。
3. 两处都没有提供时，连接失败并抛出 `AuthenticationError`。

推荐使用环境变量，避免把真实 Token 写入代码或提交到 Git 仓库。下面几种方式可以按使用场景选择。

##### 1.2.6.1 在当前终端临时设置

该方式只对当前终端及从该终端启动的 Python 程序有效。关闭终端后需要重新设置。

Windows PowerShell：

```powershell
$env:PYMOTION_AUTH_TOKEN = "123456"
```

Windows 命令提示符（CMD）：

```bat
set "PYMOTION_AUTH_TOKEN=123456"
```

Ubuntu、macOS 或其他 Bash 终端：

```bash
export PYMOTION_AUTH_TOKEN='123456'
```

设置后，在同一个终端中运行 Python 程序。程序可以省略 `auth_token`：

```python
with pm.lite.connect(transport="usb") as lite:
    print(lite.connection.device_id)
```

##### 1.2.6.2 在 Windows 用户环境中持久保存

如果不希望每次新开 PowerShell 都重新输入，可以在 PowerShell 中执行一次：

```powershell
[Environment]::SetEnvironmentVariable(
    "PYMOTION_AUTH_TOKEN",
    "123456",
    "User"
)
```

执行后应重新打开终端；如果程序从 VS Code 运行，也应重新启动 VS Code，使它读取新的用户环境变量。该方式会把 Token 保存到当前 Windows 用户的环境中，仅建议在受信任的个人电脑上使用。

如果换用另一台 Token 不同的设备，再次执行上述命令并填写新 Token，会覆盖当前 Windows 用户保存的默认值。新值只对之后启动的终端、VS Code 和 Python 进程生效；已经打开的程序仍可能继续使用旧值。需要在当前 PowerShell 立即切换时，可以同时执行：

```powershell
$env:PYMOTION_AUTH_TOKEN = "新设备的 Token"
```

一个 `PYMOTION_AUTH_TOKEN` 环境变量只能提供一个默认 Token。如果需要频繁连接多台且 Token 不同的设备，建议在当前终端按设备临时设置，或由程序从安全配置中读取并通过 `auth_token=` 明确传入。如果多台设备使用同一个 Token，则无需切换。

##### 1.2.6.3 通过连接参数传入

也可以只为某一次连接直接传入：

```python
with pm.lite.connect(
    transport="usb",
    auth_token="设备的 Token",
) as lite:
    print(lite.connection.device_id)
```

直接传入的 `auth_token` 优先于环境变量。这种方式适合临时测试或由程序从安全配置中读取 Token；不要把真实 Token 写入准备分享的示例、截图或公开仓库。

无论选择哪一种方式，都不需要每次运行时创建新 Token；只需向 SDK 提供设备当前使用的同一个值。全新设备使用出厂 Token，设置用户 Token 后改用用户值。Token 缺失或不匹配时会抛出 `AuthenticationError`。

#### 1.2.7 板载指示灯

| 指示灯 | 正常含义 | 使用时要注意 |
| --- | --- | --- |
| 电源灯 | 板上电源已经接通 | 亮起只说明板上已有供电，不能证明电池电压、带载能力、固件或网络一定正常；设备频繁断连时仍应检查带载电压 |
| SDK 通信/控制状态灯 | 已建立经过认证的 USB 或 Wi-Fi SDK 连接，或当前存在有效控制会话 | 它是连接/控制状态提示，不是每收到一个数据包就闪烁的流量灯；熄灭时先检查连接、Token 和供电 |

这两只灯用于设备状态提示，不应当作用户可自由控制的数字输出。不同硬件批次的灯位和丝印可能不同，应以板上丝印为准。

### 1.3 发现与连接

**本节内容包括：** 查找设备、USB 连接、Wi-Fi 连接、`connect()` 参数和连接生命周期。

#### 1.3.1 查找设备

**用途：** 在连接前查看当前电脑能够发现哪些 PyMotion Lite 设备，以及每台设备可使用 USB、Wi-Fi 中的哪一种连接方式。查找设备不会取得控制权，也不会让执行器动作。

**语法：**

```python
devices = pm.lite.list_devices(timeout=6.25)
```

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `timeout` | `float` | `6.25` | 大于 0 且不超过 30 秒 | 最多花多少时间等待 USB 和 Wi-Fi 发现结果；网络环境较慢时可适当增大 |

**返回值：** `tuple[LiteDeviceInfo, ...]`。没有发现设备时返回空元组，不返回 `None`。

```python
devices = pm.lite.list_devices(timeout=6.25)

for device in devices:
    print(device.device_id)
    print(device.transports)
```

发现多台设备时，应先打印 `device_id`，再把目标设备 ID 传给 `connect()`：

```python
devices = pm.lite.list_devices()
if not devices:
    raise RuntimeError("没有发现 PyMotion Lite")

for item in devices:
    print(item.device_id, item.transports)
```

`LiteDeviceInfo` 属性：

| 属性 | 含义 |
| --- | --- |
| `device_id` | 12 位设备 ID |
| `transports` | 本次扫描发现该设备的通信通道；可能为 `("usb",)`、`("wifi",)` 或 `("usb", "wifi")` |

`transports` 只表示本次扫描发现了哪些连接方式，不表示设备已经连接、Token 已通过认证或执行器控制一定可用。USB 表示电脑已发现设备的 USB 接口；Wi-Fi 表示当前局域网中发现了该设备。如果电脑 IP 地址变化，而设备仍保存着原来的 SDK 服务地址，设备可能仍能以 `"wifi"` 被扫描到，但实际执行 `connect(..., transport="wifi")` 时会超时。此时应进入设备配网页面，把 SDK 服务地址更新为电脑当前 IP；原 Token 没有变化时可以继续使用。

返回的每个 `LiteDeviceInfo` 至少包含一种发现通道；如果 USB 和 Wi-Fi 都没有发现某台设备，该设备不会出现在返回元组中，而不是返回一个 `transports=()` 的条目。连接是否真正可用，应以实际调用 `connect()` 的结果为准。

#### 1.3.2 USB 连接

**适用场景：** 首次使用、固定工位、调试和排查问题。USB 不要求设备完成配网或连接 Wi-Fi，但仍需要 Token 认证。全新设备按第 1.2.6 节在终端设置出厂 Token 后即可连接：

```python
with pm.lite.connect(
    transport="usb",
    timeout=15.0,
) as lite:
    print(lite.connection.device_id)
    print(lite.connection.transport)
```

只有一台设备时可以省略 `device_id`。连接多台设备时应明确指定：

```python
with pm.lite.connect(
    "90E5B1D51380",
    transport="usb",
) as lite:
    pass
```

#### 1.3.3 Wi-Fi 连接

**适用场景：** 移动机器人、无线调试和电脑不方便靠近设备的场景。使用前必须完成第 1.2.5～1.2.6 节的配网和 Token 设置。Token 的提供方式与 USB 相同：可以使用环境变量，也可以传入 `auth_token`。

```python
with pm.lite.connect(
    "90E5B1D51380",
    transport="wifi",
    timeout=15.0,
) as lite:
    print(lite.connection.transport)
```

Wi-Fi 连接失败时依次检查：

1. 设备和电脑是否连接到可互通的同一网络。
2. 当前终端是否设置了正确 Token。
3. 配网页面中的服务器地址是否仍是电脑当前 IP。
4. 是否有另一台电脑或另一个程序正在控制同一设备。

多数 Windows 个人电脑在专用网络中不需要手动添加防火墙规则。只有在上述项目均正确、设备与电脑可以互相访问，但连接仍在 TCP 阶段超时时，才检查 Windows 防火墙或第三方安全软件是否拦截 Python/SDK 接收入站连接。此时可仅在受信任的专用网络中允许 Python/SDK，或放行电脑端 TCP 8787，不建议关闭整个防火墙。实时数据使用电脑主动连接设备的 TCP 8789，通常不需要额外配置 Windows 入站规则。

#### 1.3.4 `connect()` 参数

```python
pm.lite.connect(
    device_id=None,
    *,
    timeout=15.0,
    auth_token=None,
    transport="usb",
)
```

| 参数 | 类型 | 默认值 | 可用值或范围 | 用户应该怎样填写 |
| --- | --- | --- | --- | --- |
| `device_id` | `str \| None` | `None` | 12 位设备 ID 或 `None` | 只有一台设备时通常可省略；发现多台设备或使用 Wi-Fi 时建议明确填写 |
| `timeout` | `float` | `15.0` | 大于 0 的秒数 | 整次连接允许等待的最长时间，不是后续每个 API 的超时时间 |
| `auth_token` | `str \| None` | `None` | 设备配置的 1～16 字节口令或 `None` | USB 与 Wi-Fi 都需要；明确传入时优先使用该值，省略时读取环境变量 `PYMOTION_AUTH_TOKEN` |
| `transport` | `str` | `"usb"` | `"usb"` 或 `"wifi"` | 选择本次实际使用的连接方式 |

Wi-Fi 所需的本机监听地址和端口由 SDK 自动管理，不属于用户参数。

**返回值：** `Lite`。这是整个程序访问设备功能的入口。`lite.connection.device_id` 是设备 ID，`lite.connection.transport` 是本次实际使用的连接方式。

**常见异常：** 找不到设备时抛出 `DeviceNotFoundError`；发现多台设备但没有指定 `device_id` 时抛出 `MultipleDevicesFoundError`；USB 或 Wi-Fi 的 Token 缺失、不正确时抛出 `AuthenticationError`；超过连接期限时抛出 `ConnectionTimeoutError`。

#### 1.3.5 连接生命周期

推荐始终使用 `with`：

```python
with pm.lite.connect() as lite:
    print(lite.is_closed)  # False

print(lite.is_closed)      # True
```

也可以手动调用 `lite.close()`。`close()` 可以重复调用；关闭后，之前取得的电机、舵机和功能对象不能继续使用。

`lite.connection` 提供本次连接的基本信息：

| 属性 | 含义 |
| --- | --- |
| `device_id` | 当前连接设备的 ID |
| `transport` | 当前使用的 `"usb"` 或 `"wifi"` |

建议在整个程序中只建立一次连接，并从这个 `lite` 对象取得需要的电机、舵机、传感器和实时功能对象。不要为每次读取或每条命令重复调用 `connect()`。

以下两种结构等价，但优先使用第一种：

```python
# 推荐：离开 with 时自动关闭
with pm.lite.connect() as lite:
    print(lite.status().state)

# 仅在需要自行管理生命周期时使用
lite = pm.lite.connect()
try:
    print(lite.status().state)
finally:
    lite.close()
```

连接对象不是跨程序共享句柄。另一个程序需要访问设备时，应先让当前程序离开 `lite.control()`；如果当前程序已经结束，确保它正常关闭连接。

### 1.4 控制权、时间参数与安全

**本节内容包括：** 取得控制权、时间参数、停止与急停。

#### 1.4.1 取得控制权

**用途：** 在一个明确的代码范围内取得执行器控制权。电机、舵机和数字输出的写操作必须位于这个范围内，读取状态和传感器通常不需要。

**语法：**

```python
with lite.control(timeout=5.0):
    # 在这里发送执行器命令
    pass
```

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `timeout` | `float` | `5.0` | 大于 0 的秒数 | 最多等待多久取得控制权；不是执行器运动时间 |

**返回值：** 控制上下文对象，应与 `with` 一起使用，不需要保存。

所有会改变电机、舵机或数字输出的操作都应放在控制上下文中：

```python
with pm.lite.connect() as lite:
    with lite.control(timeout=5.0):
        lite.motor(1).set_pwm(20, duration=1.0)
```

`timeout` 表示最多等待控制权的时间，不是电机运行时间。同一设备同一时间只能由一个程序取得控制权；同一个连接不能嵌套多个 `lite.control()`。

离开控制上下文时，SDK 会停止本次控制的执行器并释放控制权。

哪些操作需要控制权：

| 操作 | 是否需要 `lite.control()` |
| --- | --- |
| 读取设备状态、传感器、电源、雷达、里程计 | 否 |
| 读取电机或舵机状态 | 否 |
| 设置电机、PWM 舵机、TTL 舵机、数字输出 | 是 |
| 配置里程计、设置 TTL 舵机 ID 或创建 TTL 舵机对象 | 是 |
| 打开只含数据源的实时会话 | 否 |
| 打开含实时命令的实时会话 | 是 |

可以先在控制上下文外读取状态，再在控制上下文中执行动作：

```python
with pm.lite.connect() as lite:
    print(lite.power().voltage)

    with lite.control(timeout=5.0):
        lite.motor(1).set_pwm(20, duration=1.0)
```

`lite.control()` 不是后台常驻开关。它只覆盖对应的 `with` 代码块；代码块结束后，不应继续假设执行器仍保持原目标。

#### 1.4.2 时间参数

| 参数 | 影响对象 | 用户应该怎样理解 | 到期后的结果 |
| --- | --- | --- | --- |
| `timeout` | 连接、配置、等待事件或位置动作 | 本次操作最多等多久 | 抛出对应的超时异常；不能据此断定设备一定没有执行命令 |
| `max_age` | 普通状态和传感器读取 | 数据最多允许多旧，同时也是本次读取的等待预算 | 预算内没有满足要求的数据时抛出超时、过旧或不可用异常 |
| `duration` | 普通执行器动作 | 目标保持多久；是否阻塞由对应接口决定 | 到期后停止本次涉及的端口 |
| `valid_for` | 实时命令 | 如果后续更新中断，这条目标还能保持多久 | 到期后设备不再继续保持该实时目标 |

`max_age=0.5` 表示 API 最多用 0.5 秒取得数据，并且返回时数据年龄也不能超过 0.5 秒。USB 和 Wi-Fi 的通信等待由 SDK 自动管理，普通读取不再要求用户同时填写 `timeout`。

时间参数的典型组合：

```python
# 最多用 0.5 秒拿到一份年龄不超过 0.5 秒的状态
status = lite.status(max_age=0.5)

# 电机运行 1 秒；该方法在定时动作结束并完成停止后返回
with lite.control():
    lite.motor(1).set_pwm(20, duration=1.0)

# 最多等 1 秒接收下一条实时数据；超时返回 None
event = session.data.read(timeout=1.0)
```

`duration=None` 表示方法本身不安排定时停止。目标会保持到下一条同类命令、显式停止、安全停止或控制上下文结束。对持续运动使用 `duration=None` 时，程序必须有明确的停止路径。

#### 1.4.3 停止与急停

正常停止：

```python
report = lite.stop()
print(report.succeeded)
```

`lite.stop(timeout=None)` 不需要先进入控制上下文。返回 `ActionResult`，公开字段只有：

| 字段 | 含义 |
| --- | --- |
| `succeeded` | 设备是否成功处理本次整体停止 |

`report.succeeded=True` 表示设备端成功处理了本次停止请求，属于“命令执行成功”，不等于已经独立测得所有机构完全静止。如果 `report.succeeded` 为 `False`，应保持人员远离运动范围，必要时立即切断执行器电源或调用 `emergency_stop()`，不要继续发送运动命令。编码器电机还可以继续读取 `measured_rpm`，确认其接近 0；PWM 位置舵机没有实际位置反馈，因此必须现场观察舵臂或机构是否静止。

单独停止某类执行器时，使用 `motor.stop()`、`lite.motors.stop()`、`pwm.stop()` 或 `ttl.stop()`。

发生危险或控制失去可信度时使用锁存急停：

```python
report = lite.emergency_stop()
print(report.succeeded)
```

确认现场安全后复位：

```python
report = lite.reset_estop()
```

复位不会恢复之前的运动。故障原因排除后，使用 `lite.clear_fault()` 清除故障锁存。

停止接口的选择：

| 场景 | 应使用的接口 |
| --- | --- |
| 停止一个电机或舵机 | 对象的 `stop()` |
| 停止同类全部端口 | `lite.motors.stop()`、`lite.pwm_servos.stop()` 或 `lite.ttl_servos.stop()` |
| 正常停止整台设备的执行器 | `lite.stop()` |
| 发生危险、控制程序失去可信度 | `lite.emergency_stop()` |

急停建议流程：

```python
report = lite.emergency_stop(timeout=3.0)
if not report.succeeded:
    raise RuntimeError("设备未确认急停")

# 人工检查机械、电源和现场环境
status = lite.status(max_age=1.0)
print(status.state, status.estop_reason)

# 仅在确认安全后复位；复位后仍需重新取得控制权和重新发送目标
lite.reset_estop(timeout=3.0)
```

`lite.stop()` 是正常操作，不会代替急停。急停锁存后，普通执行器命令会被拒绝，直到安全条件满足并成功调用 `reset_estop()`。

## 2 执行器控制

### 2.1 数字输出

本章说明 OUTPUT1～OUTPUT6、输出对象的创建方法、高低电平控制以及使用限制。

板卡提供六路数字输出，丝印为 OUTPUT1～OUTPUT6。用户只需要使用端口号 1～6，
无需了解或填写 ESP32 GPIO 编号。

```python
with pm.lite.connect() as lite:
    output = lite.output(1)
    with lite.control():
        output.on()
        output.off()
```

| 接口 | 作用 |
| --- | --- |
| `lite.output(port)` | 取得指定 OUTPUT 端口的数字输出对象 |
| `output.port` | OUTPUT 端口号 |
| `output.on()` | 输出高电平 |
| `output.off()` | 输出低电平 |

数字输出适合指示灯、逻辑使能等低功耗信号，不能直接驱动电机、舵机或超过引脚电流能力的负载。OUTPUT1 与板载模拟采集电路相邻；需要同时可靠读取电流和电压时，建议优先使用 OUTPUT2～OUTPUT6。

完整用法：

```python
output = lite.output(port)
output.port
output.on()
output.off()
```

| 项目 | 说明 |
| --- | --- |
| `port` 类型 | `int` |
| 可用值 | 1～6，对应板卡丝印 OUTPUT1～OUTPUT6 |
| 返回值 | `lite.output()` 返回 `DigitalOutput`；设置方法返回 `None` |
| 控制权 | `on()`、`off()` 需要 |
| 状态读取 | 当前公开接口不提供输入读取或电平回读 |

同一个 OUTPUT 端口可以多次取得对象，建议程序中保存并复用一个对象。离开控制上下文时，应把外接电路设计成即使控制程序停止也处于安全状态。

### 2.2 直流电机

**本节内容包括：** 取得对象、开环 PWM、闭环速度、多电机控制、位置控制和电机状态。

#### 2.2.1 取得对象

```python
motor = lite.motor(1)  # M1～M4
print(motor.port)
```

标配电机已经配置闭环参数。更换其他型号电机时，可以先在车轮悬空、低输出的条件下使用 `set_pwm()` 验证方向；闭环转速、位置控制和里程计是否可用，还取决于电机、编码器和机械参数是否匹配。

电机对象入口：

```python
motor = lite.motor(port)
all_motors = lite.motors
```

| 入口 | 参数 | 返回对象 | 适用场景 |
| --- | --- | --- | --- |
| `lite.motor(port)` | `port` 为 1～4 | `Motor` | 控制或读取一只电机 |
| `lite.motors` | 无 | `Motors` | 批量控制或读取 M1～M4 |

`motor.port` 返回创建对象时使用的端口号。取得对象不会让电机动作，也不需要控制权。

#### 2.2.2 开环 PWM

```python
with lite.control():
    motor.set_pwm(30)
    motor.set_pwm(-30, duration=1.0)
    motor.stop()
```

`motor.set_pwm(pwm, *, duration=None)`：

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `pwm` | `float` | 无 | `-100～100` | 开环 PWM 百分比；正负号表示方向，0 表示零目标 |
| `duration` | `float \| None` | `None` | `None` 或大于 0 秒 | 指定时长时，方法等待到期、停止该电机后返回 |

**返回值：** 成功时返回 `None`。

开环百分比不等于实际转速。负载、供电和摩擦变化都会影响实际速度。

调用行为：

- `duration=None`：设置目标后立即返回，电机继续运行。
- `duration>0` 且 `pwm!=0`：方法等待指定时间，停止该电机后返回。
- `pwm=0`：选择开环零目标并立即返回；等价于本次目标为零，但需要明确停止时仍建议使用 `stop()`。
- `stop()`：只停止当前端口，不改变其他三路电机。

因为带 `duration` 的调用会占用当前 Python 执行流程，所以需要同时安排其他动作时，应使用批量 API、实时命令，或由应用程序自行调度时间。

#### 2.2.3 闭环速度

```python
with lite.control():
    motor.set_speed(120)
    print(motor.status().measured_rpm)
    motor.stop()
```

`motor.set_speed(rpm, *, duration=None)`：

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `rpm` | `int` | 无 | `-360～360` | 整数目标转速；正负号表示方向，0 表示闭环零转速目标 |
| `duration` | `float \| None` | `None` | `None` 或大于 0 秒 | 指定时长时，方法等待到期并把本路目标转速归零 |

**返回值：** 成功时返回 `None`。

`set_pwm()` 和 `set_speed()` 可以直接交替调用，不需要另外选择模式。方法名称即表示控制语义：前者使用开环百分比，后者使用闭环 RPM。

`rpm` 只接受整数，例如 `120`；`120.0` 和 `120.5` 都不是合法输入。`360 RPM` 是 SDK 允许设置的目标上限，不是电机保证能够达到的转速。实际最高转速取决于电机额定转速、减速比、电池电压、负载、摩擦、编码器配置和控制输出上限。闭环 RPM 依赖编码器反馈，应从较低目标开始测试，并结合 `measured_rpm`、`feedback_valid` 和 `output_saturated` 判断实际效果；持续饱和但实测转速仍低于目标，通常表示当前硬件和负载达不到该目标，而不是 SDK 把电机限制在错误转速。

```python
with lite.control():
    motor.set_speed(100)
    state = motor.status(max_age=0.5)

    if not state.feedback_valid:
        motor.stop()
        raise RuntimeError("编码器反馈不可用")

    print("target:", state.target_rpm)
    print("measured:", state.measured_rpm)
```

带 `duration` 的 `set_speed()` 同样会等待到期并停止本路后返回。`rpm=0` 时不会额外等待 `duration`。

#### 2.2.4 多电机控制

```python
with lite.control():
    lite.motors.set_pwms({1: 30, 3: -20})
    lite.motors.set_speeds({2: 80, 4: 80}, duration=2.0)
    lite.motors.stop()
```

| 接口 | 参数 |
| --- | --- |
| `lite.motors.set_pwms(pwms, *, duration=None)` | 1～4 个端口到 `-100～100%` 的映射 |
| `lite.motors.set_speeds(speeds, *, duration=None)` | 1～4 个端口到整数 `-360～360 RPM` 的映射 |
| `lite.motors.stop()` | 停止 M1～M4 |

只改变字典中列出的电机。任何参数不合法时，本次调用不会只执行其中一部分。

批量接口规则：

| 项目 | 规则 |
| --- | --- |
| 字典键 | 电机端口 1～4 |
| 字典值 | `set_pwms()` 使用数字百分比；`set_speeds()` 使用整数 RPM |
| 字典大小 | 1～4 项 |
| 未列出的端口 | 保持原状态 |
| `duration` | 到期后只停止本次字典中列出的端口 |
| 返回值 | 成功时为 `None` |

一个程序可以让不同电机采用不同控制方式：

```python
with lite.control():
    lite.motors.set_pwms({1: 25, 2: -25})
    lite.motors.set_speeds({3: 80, 4: 80})
```

这时 M1/M2 使用开环百分比，M3/M4 使用闭环 RPM。后续只更新 `{3: 60}` 不会改变 M1、M2、M4。

#### 2.2.5 位置控制

先在电机静止时建立当前位置零点：

```python
with lite.control():
    motor.zero_position()
    motor.move_to(
        90,
        speed=20,
        tolerance=2,
        timeout=8.0,
    )
    motor.move_by(-45, speed=15)
```

| 接口 | 含义 |
| --- | --- |
| `zero_position()` | 将当前静止位置设为 0° |
| `move_to(angle, ...)` | 移动到相对零点的绝对角度 |
| `move_by(angle, ...)` | 从当前位置继续移动指定角度 |

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `angle` | `float` | 无 | `-3600～3600` 度 | `move_to()` 表示相对零点的目标角度；`move_by()` 表示从当前位置增加的角度 |
| `speed` | `float` | `20` | 大于 0 且不超过 100 | 位置运动的输出上限百分比，不是 RPM |
| `tolerance` | `float` | `2` | 大于 0 且不超过 30 度 | 最终位置落在目标正负该角度内时，可以判定进入允许范围 |
| `timeout` | `float` | `8.0` | 0.1～60 秒 | 整个位置动作最多等待多久，包括运动、减速和到位确认 |

**返回值：** `None`。`move_to()` 和 `move_by()` 都是阻塞方法：方法会一直等待动作成功完成、发生故障或超过 `timeout`。正常返回表示设备已经确认动作完成；未确认完成时会抛出异常，不会用布尔值静默表示失败。

位置控制推荐流程：

1. 架空或固定机构，确认运动范围安全。
2. 调用 `motor.stop()` 并等待电机完全静止。
3. 调用 `zero_position()` 建立应用所需的参考零点。
4. 先用较低 `speed` 和较宽松 `tolerance` 验证方向。
5. 再根据负载和机械间隙调整速度与允许误差。

`speed` 是位置运动的输出上限，不是 RPM。`tolerance` 过小可能因机械间隙或负载波动导致动作无法确认。`timeout` 应覆盖完整运动时间，并留出减速和到位确认时间。

如果位置运动尚未结束，又对同一电机调用 `set_pwm()`、`set_speed()` 或 `stop()`，新命令会立即成为当前命令，原位置运动随之结束。之后要继续位置控制，应确认电机静止并重新调用 `zero_position()`。

软件零点在设备重新启动后恢复默认；重新建立电脑连接不会改变零点。

如果 `zero_position()` 报告电机尚未静止，应等待轮子或机构完全停稳后重试。不要在自由滑行过程中建立零点。

#### 2.2.6 电机状态

```python
state = motor.status(max_age=0.5)
all_states = lite.motors.status(max_age=0.5)
```

只查看一只电机时使用 `motor.status()`；一次查看 M1～M4 时使用 `lite.motors.status()`。

| 字段 | 含义 |
| --- | --- |
| `port` | 电机端口 1～4 |
| `control_mode` | `"open_loop"` 或 `"closed_loop"` |
| `has_encoder` | 是否配置了编码器 |
| `commanded_pwm` | 当前开环 PWM 百分比；闭环时为 `None` |
| `target_rpm` | 当前闭环目标 RPM；开环时为 `None` |
| `measured_rpm` | 编码器测得的 RPM；无有效反馈时为 `None` |
| `encoder_count` | 编码器累计计数 |
| `controller_enabled` | 当前电机输出控制是否启用 |
| `running` | 当前是否处于运动状态；判断堵转还要比较目标值和实测值 |
| `output_saturated` | 输出是否已到上限；持续为 `True` 时应降低目标并检查负载、供电或机械阻力 |
| `feedback_valid` | 编码器反馈是否有效 |
| `measured_angle` | 相对软件零点的当前位置角度，单位为度 |
| `zeroed` | 是否已经建立软件零点 |
| `position_active` | 是否正在执行位置运动 |
| `fault` | 无故障时为 `None`，否则为原因文本 |
| `age` | 数据距当前时刻的时间，单位为秒 |

`max_age` 范围为 0～10 秒。`max_age=0` 表示要求立即取得更新后的状态，适合动作前确认；周期显示通常使用默认值即可。

状态判断示例：

```python
state = motor.status(max_age=0.5)

if state.fault is not None:
    print("motor fault:", state.fault)
elif state.target_rpm and state.feedback_valid:
    error = state.target_rpm - (state.measured_rpm or 0)
    print("rpm error:", error)

if state.output_saturated:
    print("目标可能过高，或负载/供电需要检查")
```

`running=True` 只表示当前状态判断为正在运动，不能单独证明电机按目标正常运行。闭环应用还应检查编码器反馈和目标误差。

### 2.3 PWM 舵机

**本节内容包括：** 连续旋转舵机、位置舵机、多路控制与状态。

PWM 端口为 S1～S6。创建对象时必须说明实际接入的是连续旋转舵机还是位置舵机。

`PwmServo` 的 `port` 是端口号，`mode` 是创建对象时声明的类型。

```python
speed_servo = lite.pwm_servo(1, mode="speed")
position_servo = lite.pwm_servo(2, mode="position")
```

| 参数 | 类型 | 默认值 | 可用值 | 说明 |
| --- | --- | --- | --- | --- |
| `port` | `int` | 无 | 1～6 | 对应板上的 S1～S6 |
| `mode` | `str` | 无，必须填写 | `"speed"` 或 `"position"` | 必须与实际接入的舵机类型一致 |

**返回值：** `PwmServo`。创建对象不会输出 PWM，也不需要控制权。

模式是对实际舵机用途的声明。连续旋转舵机对象只能调用 `set_speed()`，位置舵机对象只能调用 `move_to()`；错误组合会抛出 `ValueError`。

#### 2.3.1 连续旋转舵机

```python
servo = lite.pwm_servo(1, mode="speed")

with lite.control():
    servo.set_speed(40)
    servo.set_speed(-30, duration=1.0)
    servo.stop()
```

`set_speed(speed, *, duration=None)` 的参数：

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `speed` | `float` | 无 | `-100～100` | 连续旋转速度百分比；正负号表示方向，0 表示停止输出 |
| `duration` | `float \| None` | `None` | `None` 或大于 0 秒 | 指定时长后自动关闭该端口输出 |

**返回值：** 成功时返回 `None`。

`duration=None` 时设置后立即返回；指定正数时，方法等待到期、关闭该端口输出后返回。`speed=0` 会直接关闭输出。

#### 2.3.2 位置舵机

```python
servo = lite.pwm_servo(2, mode="position")

with lite.control():
    servo.move_to(90)
```

`move_to(angle)` 的参数：

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `angle` | `float` | 无 | `0～180` 度 | 舵机目标角度；应同时满足实际舵机和机械结构的安全范围 |

**返回值：** 成功时返回 `None`。普通 PWM 位置舵机通常没有位置反馈，因此调用成功表示目标已经接受，不表示舵臂已经通过传感器确认到位。

`move_to()` 不提供运动时长参数。舵机实际到位时间由型号、负载、供电和角度变化决定。后续动作依赖舵机到位时，应用程序应根据舵机规格等待合适时间。

#### 2.3.3 多路控制与状态

```python
with lite.control():
    lite.pwm_servos.set_speeds({1: 30, 2: -30})
    lite.pwm_servos.move_to({3: 60, 4: 120})
    lite.pwm_servos.stop()

state = servo.status(max_age=0.5)
states = lite.pwm_servos.status(max_age=0.5)
```

字典中只填写本次要改变的端口。`set_speeds()` 用于连续旋转舵机，`move_to()` 用于位置舵机。

批量 API：

| API | 输入 | 行为 |
| --- | --- | --- |
| `set_speeds(mapping, duration=None)` | 1～6 路端口到 `-100～100` | 设置连续旋转速度；可定时关闭列出的端口 |
| `move_to(mapping)` | 1～6 路端口到 `0～180` | 设置位置目标 |
| `status(max_age=0.5)` | 无 | 返回 1～6 六路状态映射 |
| `stop()` | 无 | 关闭 S1～S6 输出 |

批量位置目标适合左右舵机、机械臂多个关节等联动场景，但不能把它理解为各舵机在完全相同的机械时刻到位。

`PwmServoState`：

| 字段 | 含义 |
| --- | --- |
| `port` | S1～S6 对应的端口号 |
| `mode` | `"speed"` 或 `"position"` |
| `commanded_speed` | 最近一次速度目标 |
| `commanded_angle` | 最近一次角度目标，单位为度 |
| `output_enabled` | 当前端口是否正在输出 PWM |

这些字段描述命令状态，不是舵机实测角度。

`output_enabled=False` 表示该端口当前没有输出。对于位置舵机，调用 `stop()` 是关闭输出，不是继续保持当前位置；承载重物时应评估机构是否会因失去保持力而移动。

### 2.4 TTL 总线舵机

**本节内容包括：** 首次设置 ID、创建对象、位置模式、速度模式、状态读取和多舵机控制。

#### 2.4.1 首次配置

首次安装或修改 ID 时：

1. 完全断电。
2. TTL 总线上只连接一只待配置舵机。
3. 重新上电并取得控制权。
4. 调用配置接口。

```python
with lite.control():
    result = lite.ttl_servo.set_id(new_id=1)

print(result.id)
print(result.max_angle)  # 单位：度
```

配置会写入舵机 ID 和运行所需参数，断电后仍然保留。`new_id` 范围为 1～253。SDK 会自动识别支持的 TTL 舵机，用户不需要选择或传入型号。

`TtlServoIdResult`：

| 字段 | 含义 |
| --- | --- |
| `old_id` | 配置前 ID |
| `id` | 配置后 ID |
| `max_angle` | SDK 自动识别出的最大允许角度，单位为度 |

配置接口正常返回表示 SDK 已写入并读回确认；验证失败时会抛出异常。

#### 2.4.2 位置模式

```python
with lite.control():
    servo = lite.ttl_servo(1, mode="position")
    servo.move_to(135, duration=2.0)

status = servo.status()
```

调用 `lite.ttl_servo(id, mode=...)` 时，SDK 会立即识别舵机并把真实舵机写入所声明的模式，因此创建对象也必须位于 `lite.control()` 内。对象创建成功后应保存并复用，不要在周期循环中重复创建。

`duration` 是舵机完成本次位置变化的目标时间，范围为 0.001～65.535 秒；省略时由舵机使用默认运动方式。方法会在目标被接受后返回。程序如需等待舵机接近目标位置，应根据 `duration` 留出适当时间并读取 `status()`。

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `angle` | `float` | 无 | 0 到 `servo.max_angle` | 目标角度 |
| `duration` | `float \| None` | `None` | 0.001～65.535 秒或 `None` | 舵机完成运动的目标时间；方法本身不会等到该时间结束 |

**返回值：** 成功时返回 `None`。需要确认是否到位时，在预留运动时间后读取 `servo.status().angle`，单位为度。

当前舵机支持的角度范围可以通过 `servo.max_angle` 读取：

```python
target = min(180.0, servo.max_angle)
with lite.control():
    servo.move_to(target, duration=2.0)
```

#### 2.4.3 速度模式

```python
with lite.control():
    servo = lite.ttl_servo(2, mode="speed")
    servo.set_speed(30, duration=2.0)
```

速度范围为 `-100～100%`。创建对象时已经完成模式设置，不需要再调用单独的模式配置 API。

| 参数 | 类型 | 默认值 | 有效范围 | 说明 |
| --- | --- | ---: | --- | --- |
| `speed` | `float` | 无 | `-100～100` | 速度百分比；正负号表示方向 |
| `duration` | `float \| None` | `None` | `None` 或大于 0 秒 | 指定时长后自动停止该舵机 |

`set_speed()` 的 `duration` 语义与直流电机相同：指定时长时，方法等待到期并停止该舵机后返回；省略时保持到新命令或停止。

#### 2.4.4 模式与状态

```python
print(servo.mode)  # "position" 或 "speed"
status = servo.status()
```

`TtlServo` 的常用属性：

| 属性 | 含义 |
| --- | --- |
| `id` | 舵机 ID |
| `mode` | 当前连接为该舵机设置的模式，值为字符串 `"position"` 或 `"speed"` |
| `max_angle` | 当前舵机允许的最大角度 |

| 字段 | 含义 |
| --- | --- |
| `online` | 舵机是否在线 |
| `id` | 舵机 ID |
| `angle` | 当前角度，单位为度 |
| `voltage` | 舵机报告的电压，单位为 V；不支持时为 `None` |
| `temperature` | 舵机报告的温度，单位为 ℃；不支持时为 `None` |
| `moving` | 是否正在运动 |
| `fault_code` | `0` 表示未报告故障 |

创建 `TtlServo` 对象时，SDK 已完成设备模式的读取、必要的切换和结果校验。用户直接读取 `servo.mode` 即可，不需要再调用单独的模式读取方法。同一连接中若再次用相同 ID 创建不同模式的对象，已有对象的 `mode` 也会更新为最近成功设置的模式。

状态使用示例：

```python
status = servo.status()
if not status.online:
    print("TTL 舵机不在线")
elif status.fault_code != 0:
    print("TTL fault:", status.fault_code)
else:
    print(status.angle, status.moving)
```

#### 2.4.5 多舵机控制

```python
with lite.control():
    servo1 = lite.ttl_servo(1, mode="position")
    servo2 = lite.ttl_servo(2, mode="position")
    lite.ttl_servos.move_to(
        {
            servo1: 90,
            servo2: 180,
        },
        duration=2.0,
    )
```

速度模式使用 `lite.ttl_servos.set_speeds(mapping, *, duration=None)`。一个批量调用支持 1～8 只舵机；接入更多 ID 时可以分批调用。`lite.ttl_servos.status()` 返回通过当前 `lite` 对象创建的 TTL 舵机状态，`lite.ttl_servos.stop()` 停止这些舵机。

批量映射的键必须是 `TtlServo` 对象，不是整数 ID。这样可以保留每只舵机的 ID 和模式信息：

```python
with lite.control():
    left = lite.ttl_servo(1, mode="speed")
    right = lite.ttl_servo(2, mode="speed")
    lite.ttl_servos.set_speeds(
        {left: 25, right: -25},
        duration=2.0,
    )
```

`lite.ttl_servos.stop()` 和 `status()` 作用于当前程序已经通过 `lite.ttl_servo()` 取得的 TTL 舵机对象。若只想停止一只，使用该对象的 `stop()`。

## 3 传感与设备信息

### 3.1 传感器

**本节内容包括：** 综合读取与单项读取、有效性、IMU、HC-SR04 超声波、五路循迹、环境光与颜色。

#### 3.1.1 综合读取与单项读取

```python
data = lite.sensors(max_age=0.5)

print(data.imu)
print(data.ultrasonic)
print(data.line_tracker)
print(data.ambient_light)
print(data.color)
```

| 参数 | 默认值 | 含义 |
| --- | ---: | --- |
| `max_age` | `0.5` 秒 | 数据最大年龄和本次读取等待预算，范围 0～10 秒 |

只需要一种传感器时，可以使用：

```python
imu = lite.imu(max_age=0.5)
ultrasonic = lite.ultrasonic(max_age=0.5)
line = lite.line_tracker(max_age=0.5)
light = lite.ambient_light(max_age=0.5)
color = lite.color(max_age=0.5)
```

方法选择：

| 需求 | 推荐 API |
| --- | --- |
| 一次查看全部常用传感器 | `lite.sensors()` |
| 偶尔读取某一种传感器 | 对应的 `lite.imu()`、`lite.ultrasonic()` 等 |
| 持续接收一种或多种传感器 | `lite.realtime.open()` |

`sensors()` 返回 `SensorObservation`，包含 `imu`、`ultrasonic`、`line_tracker`、`ambient_light` 和 `color` 五个属性。某个传感器未接入时，对应属性仍然存在，但其 `valid=False`，数值字段通常为 `None`。

`sensors()` 一次返回五类传感器的当前读数。使用任何读数前，应先检查对应对象的 `valid`；如果该值为 `False`，表示当前读数不可用，不应参与显示、计算或控制。

#### 3.1.2 有效性

所有传感器读数都提供 `valid`、`state` 和 `age`。

| `state` | 含义 |
| --- | --- |
| `"valid"` | 数据有效 |
| `"no_echo"` | 超声波没有收到合适回波 |
| `"stale"` | 数据超过 `max_age` |
| `"unavailable"` | 传感器未连接、未启用或暂时不可用 |
| `"error"` | 传感器报告错误 |

只有 `valid=True` 时才应将数值用于控制计算。

推荐判断模板：

```python
reading = lite.ultrasonic(max_age=0.5)

if reading.valid:
    print("distance:", reading.distance, "mm")
elif reading.state == "no_echo":
    print("未收到有效回波")
elif reading.state == "stale":
    print("数据过旧")
else:
    print("当前不可用:", reading.state)
```

`age` 的单位为秒。其值为 `None` 时表示无法给出可靠年龄；此时 `valid` 会反映该数据能否使用。控制程序应把无效或过旧数据当作需要降速、停止或切换策略的条件，而不是沿用上一次数值。

#### 3.1.3 IMU

`ImuReading`：

| 字段 | 类型与单位 |
| --- | --- |
| `acceleration` | `Vector3`，单位 mm/s² |
| `angular_velocity` | `Vector3`，单位 rad/s |
| `orientation` | `Orientation`，单位 ° |

`Vector3` 提供 `x`、`y`、`z`；`Orientation` 提供 `roll`、`pitch`。

字段使用示例：

```python
imu = lite.imu(max_age=0.2)
if imu.valid:
    ax = imu.acceleration.x
    yaw_rate = imu.angular_velocity.z
    roll = imu.orientation.roll
    pitch = imu.orientation.pitch
```

姿态角适合显示倾斜和进行低速姿态辅助，不应在没有额外参考的情况下把它当作长期绝对航向。安装方向改变后，X/Y/Z 和 Roll/Pitch 的物理含义也会随传感器朝向变化。

#### 3.1.4 HC-SR04 超声波

`UltrasonicReading.distance` 返回距离，单位为 mm。API 只返回数值，不在字段名或数值中附加单位。

接线如下，电源和地线位置以板上丝印为准：

| HC-SR04 引脚 | PyMotion Lite 连接 |
| --- | --- |
| `VCC` | 板上 `5V` 电源引脚 |
| `GND` | 板上 `GND`，与设备共地 |
| `TRIG` | `GPIO5` |
| `ECHO` | 经 5 V 转 3.3 V 分压或电平转换后接 `GPIO6` |

常见 HC-SR04 的 `ECHO` 是 5 V 信号，不能直接接到 ESP32 的 3.3 V GPIO。必须使用分压或电平转换，并且不要用普通 GPIO 给传感器供电。

HC-SR04 的典型有效量程约为 2～400 cm。软质、倾斜、过小或超出量程的目标可能产生 `no_echo`。为减少相邻回波互相影响，连续有效测距通常按约 15～16.7 Hz 使用更稳妥。

避障时不要只比较单次距离。更稳妥的做法是连续取得多次有效数据，并为“无回波”设置明确策略：

```python
reading = lite.ultrasonic(max_age=0.2)
if not reading.valid:
    safe_to_move = False
else:
    safe_to_move = reading.distance >= 250
```

对着天花板、墙角或斜面时，声波可能反射到其他方向；即使模块已经完成一次测量，也不保证每次都有有效距离。

#### 3.1.5 五路循迹

调用 `lite.line_tracker()` 读取五路循迹状态。使用检测结果前，应先确认本次读数有效：

```python
line = lite.line_tracker(max_age=0.5)

if line.valid:
    print("Levels:", line.levels)
    print("Detected:", line.detected)
else:
    print("Line tracker unavailable:", line.state)
```

`LineTrackerReading`：

| 字段 | 含义 |
| --- | --- |
| `levels` | 从左到右五路原始电平，值为 0 或 1 |
| `detected` | 从左到右五路是否检测到目标线 |
| `black_is_low` | `True` 表示低电平代表黑线 |

OUT1～OUT5 应从左到右依次连接 GPIO14、15、16、17、18。

默认 `black_is_low=True` 时：

- 探头位于黑线上方：红外反射较弱，`levels` 对应位置为 0，`detected` 为 `True`，模块对应指示灯通常不亮。
- 探头位于浅色地面上方：红外反射较强，`levels` 对应位置为 1，`detected` 为 `False`，模块对应指示灯通常亮起。

控制程序通常优先使用 `detected`。

典型解释如下：

| `detected` 情况 | 常见含义 | 建议动作 |
| --- | --- | --- |
| 中间一路或中间多路为 `True` | 车体大致在线上 | 保持或小幅修正 |
| 左侧为 `True` | 线位于探头左侧 | 向左修正 |
| 右侧为 `True` | 线位于探头右侧 | 向右修正 |
| 五路均为 `False` | 可能丢线或位于间隙 | 减速，并按应用策略搜索 |
| 五路均为 `True` | 可能是宽线、路口或全黑区域 | 按赛道规则处理 |

循迹判断应结合模块离轮轴的前置距离、车速、转弯半径和 20 Hz 最高数据更新频率调参。车速越高或探头越靠前，越需要平滑转向、弯道降速和限制单次差速变化。

#### 3.1.6 环境光与颜色

调用 `lite.ambient_light()` 读取环境照度，调用 `lite.color()` 读取颜色传感器原始值：

```python
light = lite.ambient_light(max_age=0.5)
color = lite.color(max_age=0.5)

if light.valid:
    print("Illuminance:", light.illuminance, "lux")
```

`AmbientLightReading.illuminance` 是环境照度，单位 lux。

`ColorReading`：

| 字段 | 含义 |
| --- | --- |
| `red`、`green`、`blue` | RGB 原始计数 |
| `clear` | 未经过颜色滤光的总光强计数 |
| `chip_id` | 传感器识别值 |

RGB 数值不是已经校准好的颜色名称。环境光、安装距离和被测物表面都会影响结果。

建议先在实际光照和安装高度下采集样本，再用相对比例或阈值分类。示例：

```python
reading = lite.color(max_age=0.5)
if reading.valid and reading.clear:
    red_ratio = reading.red / reading.clear
    green_ratio = reading.green / reading.clear
    blue_ratio = reading.blue / reading.clear
```

环境光与颜色传感器共用安装资源时，应根据实际硬件接法启用相应设备；未接入的设备返回不可用状态属于正常情况。

### 3.2 电源测量

本章说明电池电压、两组电机电流和 PWM 舵机电流的读取方法，以及 `None`、压降和分组电流的含义。

```python
power = lite.power(max_age=1.0)

print(power.voltage)
print(power.current(1))
print(power.current(2))
print(power.current(3))
```

| 字段 | 单位 | 含义 |
| --- | --- | --- |
| `voltage` | V | 外部电池电压 |
| `current(1)` | A | M1/M2 供电组总电流 |
| `current(2)` | A | M3/M4 供电组总电流 |
| `current(3)` | A | S1～S6 PWM 舵机供电组总电流 |

这些读数反映当前供电状态，可能随负载变化，不是 1 秒平均值。`current()` 的参数表示供电组，而不是单个电机或舵机；只接受 1、2、3。某项无法读取时返回 `None`，不是 0。板载读数适合供电监视与保护判断，不应代替精密测量仪表。

`lite.power(max_age=1.0)` 不需要控制权；`max_age` 同时表示可接受的供电读数最大年龄和本次读取等待预算，范围为 0～10 秒。供电检查示例：

```python
power = lite.power(max_age=1.0)

if power.voltage is None:
    print("当前没有可用的电池电压读数")
else:
    print(f"battery={power.voltage:.2f} V")
```

电流字段是对应供电组的合计值，不能用来直接区分同组内某一只电机或舵机的电流。启动瞬间、堵转和多执行器同时动作可能造成电压下降；实际保护阈值应依据电池类型、允许放电电压和负载特性确定。

### 3.3 LD14P 雷达

**本节内容包括：** 单帧与整圈、连续扫描。

#### 3.3.1 单帧与整圈

```python
frame = lite.lidar.frame(max_age=0.5)
scan = lite.lidar.scan()
```

`frame()` 返回雷达的一帧，一帧通常包含 12 个点；`scan()` 返回一整圈。

| API | 是否等待完整一圈 | 适用场景 |
| --- | --- | --- |
| `frame(max_age=0.5)` | 否 | 快速查看局部原始测距点 |
| `scan()` | 是 | 一次性等待并获取用于避障或绘图的一圈新数据 |
| `stream()` | 连续提供整圈 | 长时间导航、绘图和记录 |

`frame()` 返回最近一帧雷达数据，使用 `max_age` 限制数据最大年龄，范围为 0～10 秒。`scan()` 等待下一圈完整扫描，因此不需要 `max_age`。雷达未接入、尚未产生数据或等待超时时会抛出相应异常，应用程序应捕获 `LiteError` 并进入安全状态。

`LidarFrame`：

| 字段 | 含义 |
| --- | --- |
| `sequence` | 帧序号 |
| `points` | `tuple[LidarPoint, ...]` |
| `age` | 数据年龄，秒 |
| `speed` | 雷达旋转速度，度/秒；不可用时为 `None` |

`LidarScan`：

| 字段 | 含义 |
| --- | --- |
| `sequence` | 扫描序号 |
| `points` | 一圈中的测量点 |
| `frame_count` | 组成这一圈的帧数 |
| `age` | 扫描年龄，秒 |
| `speed` | 平均旋转速度，度/秒 |

`scan()` 和 `next_scan()` 只返回完整的一圈。如果规定时间内无法组成完整扫描，接口会抛出超时异常，不会返回不完整的 `LidarScan`。

每个 `LidarPoint` 提供：

| 字段 | 含义 |
| --- | --- |
| `angle` | 相对雷达坐标系的角度，单位 °，约 -180～180° |
| `distance` | 距离，单位 mm；0 通常表示没有有效测量 |
| `confidence` | 置信度 0～255，越高通常越可靠 |

#### 3.3.2 连续扫描

```python
with lite.lidar.stream() as stream:
    while True:
        scan = stream.next_scan(timeout=3.0)
        print(scan.sequence, len(scan.points))
```

| 接口 | 作用 |
| --- | --- |
| `next_scan(timeout=3.0)` | 等待比上一次结果更新的完整扫描；超时会抛出异常 |
| `stats()` | 返回本次连续扫描的运行统计 |

连续扫描采用“最新数据优先”策略。SDK 只保留最近完成的一圈；如果程序处理速度慢于雷达更新速度，中间来不及处理的旧扫描会被新扫描覆盖，下一次 `next_scan()` 直接返回当时最新的一圈。这样可以避免避障和控制程序持续处理已经失去实时价值的历史数据。

`LidarStreamStats`：

| 字段 | 含义 |
| --- | --- |
| `is_active` | 连续扫描是否仍在运行 |
| `scan_count` | 本次连续扫描已经组成的完整圈数 |
| `point_count` | 本次连续扫描已经解析的测量点总数 |
| `missing_frame_count` | 根据帧序号检测到的缺失帧总数 |
| `decode_error_count` | 数据格式、长度或校验不正确而无法解码的次数 |
| `device_dropped_frame_count` | 设备端来不及处理而累计丢弃的帧数 |
| `last_data_age` | 距离电脑最近一次收到雷达数据的时间，单位为秒；尚未收到数据时为 `None` |

这些统计在每次进入新的 `stream()` 会话时从零开始。`last_data_age` 持续增大通常表示雷达停止上传或通信中断；它不是一圈扫描所需的时间。

长期处理雷达数据时使用 `stream()`；只偶尔查看一次时使用 `frame()` 或 `scan()`。

连续扫描典型处理：

```python
with lite.lidar.stream() as stream:
    for _ in range(20):
        scan = stream.next_scan(timeout=3.0)
        usable = [
            point
            for point in scan.points
            if point.distance > 0 and point.confidence >= 100
        ]
        nearest = min(usable, key=lambda p: p.distance, default=None)
        if nearest is not None:
            print(nearest.angle, nearest.distance)

    stats = stream.stats()
    print(stats.scan_count, stats.missing_frame_count)
```

### 3.4 里程计

**本节内容包括：** 使用条件、配置、左右轮端口与正方向限制、读取状态。

#### 3.4.1 使用条件

可靠使用里程计需要满足：

- 左右轮电机端口配置正确。
- 两个电机的编码器参数正确，反馈有效。
- 轮径和左右轮中心间距填写正确。
- 轮胎与地面接触良好，打滑较小。
- 左右轮方向与车体前进方向一致。

设备启动时从 `x=0`、`y=0`、`heading=0` 开始累计。重新建立电脑连接不会清零；成功调用 `configure()` 会把调用时的位置重新设为原点。

#### 3.4.2 配置

```python
with lite.control():
    config = lite.odometry.configure(
        left_motor_port=3,
        right_motor_port=4,
        wheel_diameter_mm=67.5,
        wheel_separation_mm=166.0,
    )
```

| 参数 | 范围 | 含义 |
| --- | --- | --- |
| `left_motor_port` | 1～4 | 左轮电机端口 |
| `right_motor_port` | 1～4 | 右轮端口，不能与左轮相同 |
| `wheel_diameter_mm` | 1～1000 mm | 轮子滚动直径 |
| `wheel_separation_mm` | 10～2000 mm | 左右驱动轮中心距离（轮距） |

默认配置为左轮 M3、右轮 M4、轮径 67.5 mm、轮距 166 mm。读取实际配置：

```python
config = lite.odometry.configuration()
```

`OdometryConfiguration`：

| 字段 | 含义 |
| --- | --- |
| `left_motor_port`、`right_motor_port` | 左右轮电机端口 |
| `wheel_diameter` | 轮径，单位为 mm |
| `wheel_separation` | 左右驱动轮中心距离（轮距），单位为 mm |
| `persistent` | 是否断电保存；`False` 表示重新启动后恢复默认配置 |

配置参数的测量方法：

- `wheel_diameter_mm` 应测量轮胎实际滚动直径，而不只使用轮毂标称直径。
- `wheel_separation_mm` 是左右驱动轮接地点中心之间的有效距离，也就是轮距。
- 左右轮端口必须不同，配置前应停止全部直流电机。

##### 3.4.2.1 左右轮端口与正方向限制

标准底盘使用 M3 左轮、M4 右轮，通常保持默认值即可。改接其他端口时，必须保证两个电机接收相同的正目标后，左右轮都驱动车体向前：

```python
LEFT_MOTOR = 3
RIGHT_MOTOR = 4

with lite.control():
    lite.motors.set_speeds(
        {LEFT_MOTOR: 20, RIGHT_MOTOR: 20},
        duration=0.5,
    )
```

首次验证应让车轮悬空并使用低转速。设备会自动处理各端口的编码器计数方向；如果某一路正目标实际让车轮向后，应检查端口、接线或机械安装，否则里程计方向会计算错误。

成功调用 `configure()` 后，返回值就是当前生效配置，同时里程计位姿从零重新开始。该配置不会永久保存；需要自定义几何参数的程序，应在每次设备启动后配置一次。

#### 3.4.3 读取状态

`lite.odometry` 是里程计功能入口；它本身不是一份数据。调用 `lite.odometry.status(max_age=0.5)` 才会读取当前里程计状态。`max_age` 同时表示允许的数据最大年龄和本次读取的等待预算，不是让设备额外累计 0.5 秒。

```python
odom = lite.odometry.status(max_age=0.5)

if odom.pose_valid:
    print(odom.x, odom.y, odom.heading)
```

坐标约定：

- X 轴正方向：车体前方。
- Y 轴正方向：车体左侧。
- 航向角正方向：从上方看逆时针左转。

`OdometryState` 常用字段：

| 字段 | 含义 |
| --- | --- |
| `x`、`y` | 相对当前原点的平面坐标，mm |
| `heading` | 航向角，度 |
| `linear_speed` | 车体线速度，mm/s |
| `angular_speed` | 车体角速度，度/s |
| `left_distance`、`right_distance` | 左右轮累计距离，mm |
| `configured` | 当前几何配置是否有效 |
| `pose_valid` | 当前位姿是否可用 |
| `left_encoder_valid`、`right_encoder_valid` | 左右编码器反馈是否有效 |
| `age` | 数据距当前时刻的时间，单位为秒 |

编码器里程计会受到轮胎打滑、地面不平、轮径误差和轮距误差影响。需要更高精度时，应在实际场地校正轮径与轮距。

校正建议：

1. 让车辆直行一段已知距离；实际距离与 `x` 成比例偏差明显时，优先校正轮径。
2. 让车辆原地旋转已知角度；航向比例偏差明显时，优先校正轮距。
3. 左右偏航但总距离接近时，检查两轮直径、摩擦、编码器参数和电机方向。
4. 急加速、急刹车或松软地面上的误差通常来自打滑，不能只靠修改几何参数消除。

`pose_valid=False` 时，不应使用 `x`、`y` 或 `heading` 进行闭环导航。先检查 `configured` 以及左右编码器有效性。

### 3.5 OLED

**本节内容包括：** 临时文字、多页仪表盘、动态字段。

OLED 支持文字和动态数值，不支持图片。最多 8 页，每页 1～4 行，每行最多 21 个可打印 ASCII 字符。

OLED 方法不需要控制权。文字超长、页数过多、行数不符合要求或使用不支持字符时会抛出参数错误。

#### 3.5.1 临时文字

```python
lite.oled.show(
    ["Welcome to", "PyMotion"],
    duration_seconds=5.0,
)
```

`duration_seconds` 范围为 0.1～60 秒，到时后恢复此前页面。

`lines` 可以是单个字符串，也可以是 1～4 个字符串的列表或元组：

```python
lite.oled.show("Ready", duration_seconds=2.0)
lite.oled.show(["Battery", "Check complete"], duration_seconds=3.0)
```

该方法用于临时提示，不会覆盖已经配置的多页仪表盘。

#### 3.5.2 多页仪表盘

```python
pages = {
    "device": [
        "PyMotion Lite",
        "{status.state}",
        "{wifi.ip}",
    ],
    "sensors": [
        "{ultrasonic.distance}",
        "{imu.orientation}",
        "{line_tracker.levels}",
    ],
    "power": [
        "{power.voltage}",
        "{power.current.1}",
        "{power.current.2}",
        "{power.current.3}",
    ],
}

lite.oled.show_pages(
    pages,
    refresh_interval_seconds=0.5,
    page_interval_seconds=3.0,
)
```

调用 `show_pages()` 后，设备会立即从第一页开始自动轮播，不需要再调用其他方法启动轮播。

| 参数 | 默认值 | 范围 |
| --- | ---: | --- |
| `refresh_interval_seconds` | `0.5` | 0.2～5 秒 |
| `page_interval_seconds` | `3.0` | 1～60 秒 |

```python
# 固定显示 sensors 页面，并暂停自动轮播
lite.oled.show(page="sensors")

# 从 device 页面开始轮播
lite.oled.show(page="device", slide=True)

# 从第一页开始轮播
lite.oled.show(slide=True)

# 恢复默认欢迎页
lite.oled.show()
```

使用命名字典配置页面后可以使用页面名；使用普通列表配置时使用从 0 开始的页码。

| 调用形式 | 显示行为 |
| --- | --- |
| `show()` | 恢复默认欢迎页，并清除当前页面名称记录 |
| `show(page=...)` | 固定显示指定页面 |
| `show(slide=True)` | 从第一页开始自动轮播 |
| `show(page=..., slide=True)` | 从指定页面开始自动轮播 |

`slide` 只接受布尔值。临时文字参数 `lines` 不能与 `page` 或 `slide=True` 同时使用。

#### 3.5.3 动态字段

| 占位符 | 显示内容 |
| --- | --- |
| `"{ultrasonic.distance}"` | 超声波距离数值，单位 mm |
| `"{ambient_light.illuminance}"` | 环境光数值，单位 lux |
| `"{color.rgb_raw}"` | RGB 原始数值，以 `/` 分隔 |
| `"{color.clear_raw}"` | Clear 原始数值 |
| `"{imu.orientation}"` | Roll/Pitch 数值，单位 ° |
| `"{line_tracker.levels}"` | 五路循迹电平值 |
| `"{wifi.ip}"` | Wi-Fi IP 值 |
| `"{wifi.rssi}"` | Wi-Fi 信号强度数值，单位 dBm |
| `"{system.uptime}"` | 设备运行时间数值，单位秒 |
| `"{status.state}"` | 设备状态值 |
| `"{motors.1.measured_rpm}"`～`"{motors.4.measured_rpm}"` | 电机实测转速数值，单位 RPM |
| `"{power.voltage}"` | 电池电压数值，单位 V |
| `"{power.current.1}"` | M1/M2 组电流数值，单位 A |
| `"{power.current.2}"` | M3/M4 组电流数值，单位 A |
| `"{power.current.3}"` | PWM 舵机组电流数值，单位 A |

这些动态占位符只显示对应的值，不自动附加字段标签、单位或说明文字；如需在 OLED 上提示单位，可另外添加一行普通文本。页面配置在设备重新启动后恢复默认值。

动态字段会按 `refresh_interval_seconds` 更新，页面切换按 `page_interval_seconds` 进行。动态值暂时不可用时，页面仍会保留，但对应字段不会产生可用于控制的传感器读数；控制逻辑应从传感器 API 获取并检查有效性，不要从 OLED 显示结果反推状态。

### 3.6 设备状态

本章说明 `lite.status()` 的参数、返回字段以及 `IDLE`、`CONTROLLED`、`ESTOP`、`FAULT` 等状态应如何处理。

```python
status = lite.status(max_age=1.0)

print(status.device_id)
print(status.state)
print(status.age)
```

参数：

| 参数 | 默认值 | 含义 |
| --- | ---: | --- |
| `max_age` | `1.0` | 状态最大年龄和本次读取等待预算，范围 0～10 秒 |

`status()` 不需要控制权，适合在动作前后和异常处理中调用。`max_age` 越小，对状态新鲜度要求越高，但网络临时抖动时也更容易触发超时或过旧异常。

| 字段/属性 | 含义 |
| --- | --- |
| `device_id` | 设备 ID |
| `state` | 当前汇总状态 |
| `age` | 电脑收到这份状态后已经过去的秒数；越小表示越新 |
| `lease_active` | 当前是否有程序取得控制权 |
| `estop_latched` | 急停是否锁存 |
| `fault_latched` | 故障是否锁存 |
| `estop_reason` | 急停原因 |
| `fault_reason` | 故障原因 |

`state`：

| 状态 | 含义 |
| --- | --- |
| `IDLE` | 已连接，当前没有程序控制执行器 |
| `CONTROLLED` | 某个程序已经取得控制权 |
| `STOPPING` | 正在完成停止操作 |
| `MAINTENANCE` | 正在执行需要独占设备的配置操作 |
| `ESTOP` | 急停已锁存，需要确认安全后复位 |
| `FAULT` | 故障已锁存，需要排除原因后清除 |

`lite.stop()`、`lite.emergency_stop()`、`lite.reset_estop()` 和 `lite.clear_fault()` 返回统一的 `ActionResult`：

| 字段 | 含义 |
| --- | --- |
| `succeeded` | 本次动作是否成功 |

动作后如需查看急停、故障等锁存状态，应重新调用 `lite.status()`。

安全状态处理建议：

| 当前 `state` | 应用程序建议 |
| --- | --- |
| `IDLE` | 可以尝试取得控制权 |
| `CONTROLLED` | 当前已有控制者；本程序未持有时不要强行发送动作 |
| `STOPPING` | 等待停止完成后重新读取状态 |
| `MAINTENANCE` | 等待配置操作完成 |
| `ESTOP` | 检查现场与原因，安全后调用 `reset_estop()` |
| `FAULT` | 排除故障原因，停止输出后调用 `clear_fault()` |

`reset_estop()` 和 `clear_fault()` 只清除已经满足复位条件的锁存状态，不会重新播放先前的执行器目标。复位成功后，应用程序必须重新进入 `lite.control()` 并明确发送新的安全目标。

## 4 实时功能

### 4.1 实时数据

实时数据适合仪表盘、记录、循迹、姿态反馈和多传感器联动。

**本节内容包括：** 可用数据源、打开会话并读取、三档频率、数据事件与统计、订阅 PWM 与 TTL 状态。

#### 4.1.1 可用数据源

| 名称 | 内容 |
| --- | --- |
| `status` | 设备运行状态 |
| `imu` | IMU |
| `ultrasonic` | 超声波 |
| `line_tracker` | 五路循迹 |
| `ambient_light` | 环境光 |
| `color` | 颜色 |
| `lidar` | 雷达整圈扫描 |
| `power` | 电压和电流 |
| `motors` | M1～M4 状态 |
| `pwm_servos` | PWM 舵机状态 |
| `ttl_servos` | 指定 TTL 舵机状态 |

一次会话可以订阅一个或多个来源。每个来源仍按自身支持的速度产生事件，不会因为同时订阅三个约 20 Hz 来源就把单个传感器变成 60 Hz；程序只是可能每秒合计收到约 60 条不同来源的事件。

订阅选择示例：

```python
# 单一来源：适合循迹控制
data_sources = ("line_tracker",)

# 多来源：适合仪表盘或记录
data_sources = ("imu", "ultrasonic", "power", "motors")
```

只订阅实际需要的数据有助于让程序更容易及时处理最新事件。

#### 4.1.2 打开会话并读取

```python
with lite.realtime.open(
    data_sources=("imu", "ultrasonic", "power"),
    frequency="medium",
    data_queue_size=32,
) as session:
    while True:
        event = session.data.read(timeout=1.0)
        if event is None:
            continue
        print(event.source, event.data, event.age)
```

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `data_sources` | 空 | 要连续接收的数据源 |
| `command_targets` | `None` | 要启用的实时命令，见第 4.2 节 |
| `frequency` | `"low"` | `low`、`medium` 或 `high` |
| `data_queue_size` | `32` | 最多暂存多少条尚未读取的数据，范围 1～1024 |
| `ttl_servos` | 空 | 订阅 TTL 状态时填写具体对象 |
| `pwm_servos` | 空 | 订阅 PWM 状态时填写具体对象 |

`data_queue_size` 决定实时会话最多保留多少条未读事件。如果程序处理速度长期低于数据到达速度，SDK 会丢弃最旧事件并增加 `dropped`。控制程序通常使用较小队列并持续读取，以便优先处理新数据；记录程序可以适当增大队列。

队列示意：假设同时订阅三种约 20 Hz 的来源，合计最多约 60 条事件/秒。`data_queue_size=32` 大约只能容纳半秒左右的未处理事件。如果程序暂停 2 秒，等待区会满，较旧事件被替换，`dropped` 增加。

| 程序类型 | 建议思路 |
| --- | --- |
| 循迹、遥控、闭环控制 | 队列 8～32，持续快速读取，优先新数据 |
| 一般仪表盘 | 队列 32～128，界面刷新与数据读取分开 |
| 短时记录 | 根据来源总频率增大队列，并确保写盘速度足够 |

未读事件只在当前实时会话中有效；关闭会话后不会保留。

#### 4.1.3 三档频率

| 数据源 | `low` | `medium` | `high` | 建议用途 |
| --- | ---: | ---: | ---: | --- |
| IMU | 约 5 Hz | 约 10 Hz | 最高约 20 Hz | 姿态显示与控制 |
| 超声波 | 约 5 Hz | 约 10 Hz | 最多约 20 次测距尝试/秒 | 有效距离通常低于 20 Hz |
| 五路循迹 | 约 5 Hz | 约 10 Hz | 最高约 20 Hz | 循迹优先使用 `high` |
| 环境光 | 约 5 Hz | 最高约 10 Hz | 最高约 10 Hz | 环境亮度判断 |
| 颜色 | 约 5 Hz | 最高约 10 Hz | 最高约 10 Hz | 颜色和反射强度判断 |
| 电源 | 约 5 Hz | 最高约 10 Hz | 最高约 10 Hz | 供电监视 |
| 电机状态 | 约 5 Hz | 约 10 Hz | 最高约 20 Hz | 转速和编码器反馈 |
| PWM 状态 | 约 5 Hz | 约 10 Hz | 最高约 20 Hz | 命令状态显示 |
| TTL 状态 | 取决于订阅数量 | 取决于订阅数量 | 取决于订阅数量 | 状态显示 |
| 雷达 | 约 6 Hz | 约 6 Hz | 约 6 Hz | 由雷达转速决定 |
| 设备状态 | 约 0.5 Hz | 约 0.5 Hz | 约 0.5 Hz | 状态栏与安全提示 |

档位表示希望接收数据的最高频率。传感器自身测量速度较低时，选择 `high` 也不会重复旧数值凑到 20 Hz。

- `low`：界面显示、低速记录、供电监视。
- `medium`：一般传感器联动。
- `high`：循迹、姿态反馈、电机状态等快速响应场景。

实际频率还会受订阅数量、传感器测量时间和程序处理速度影响。可以读取 `session.effective_rate_hz` 查看当前会话为各来源采用的目标频率：

```python
with lite.realtime.open(
    data_sources=("imu", "line_tracker", "power"),
    frequency="high",
) as session:
    print(session.effective_rate_hz)
```

`frequency` 只影响实时数据。普通的 `lite.imu()` 或 `motor.status()` 是按调用读取；实时命令则由程序调用 `write()` 的节奏决定。

#### 4.1.4 数据事件与统计

`session.data.read(timeout)` 返回 `RealtimeDataEvent`；超过等待时间仍没有数据时返回 `None`。

| 字段 | 含义 |
| --- | --- |
| `source` | 数据源名称 |
| `data` | 对应的返回对象 |
| `sequence` | 该数据源的事件序号 |
| `received_monotonic` | 电脑接收时刻，适合计算时间差 |
| `age` | 测量值距当前时刻的秒数；无法确定时为 `None` |

`session.data.stats()` 返回：

| 字段 | 含义 |
| --- | --- |
| `received` | 已进入等待区的数据总数 |
| `dropped` | 因等待区已满而丢弃的旧数据数 |

`dropped` 增加时，应提高读取速度、减少订阅源或适当增大 `data_queue_size`。

统计值从会话开始累计，到会话关闭为止。`received` 表示进入等待区的事件数量，不等于 `read()` 已经取走的数量。应用程序可以用下式了解当前尚未消费或已经丢弃的总体情况：

```python
stats = session.data.stats()
print("received:", stats.received)
print("dropped:", stats.dropped)
```

如果控制循环只关心某一种来源，应忽略其他事件，但仍要持续从队列中取出它们，避免队列长期堆积。

各来源的 `event.data`：

| `source` | 数据类型 | 主要内容 |
| --- | --- | --- |
| `status` | 运行状态对象 | `state` 等设备状态 |
| `imu` | `ImuReading` | 加速度、角速度、Roll/Pitch |
| `ultrasonic` | `UltrasonicReading` | 距离 |
| `line_tracker` | `LineTrackerReading` | 五路电平和检测结果 |
| `ambient_light` | `AmbientLightReading` | 照度 |
| `color` | `ColorReading` | RGBC 原始值 |
| `lidar` | `LidarScan` | 一整圈雷达点 |
| `power` | `PowerReading` | 电压和分组电流 |
| `motors` | `tuple[RealtimeMotorState, ...]` | M1～M4 状态 |
| `pwm_servos` | `tuple[RealtimePwmServoState, ...]` | 已声明 PWM 端口状态 |
| `ttl_servos` | TTL 状态元组 | 已声明 TTL 舵机状态 |

`RealtimeMotorState`：

| 字段 | 含义 |
| --- | --- |
| `port` | 电机端口 |
| `control_mode` | `open_loop` 或 `closed_loop` |
| `commanded_pwm` | 开环 PWM 目标 |
| `target_rpm`、`measured_rpm` | 闭环目标和实测 RPM |
| `encoder_count` | 编码器累计计数 |
| `feedback_valid` | 编码器反馈是否有效 |
| `running` | 是否处于运动状态 |
| `saturated` | 输出是否已经达到上限 |

`RealtimePwmServoState`：

| 字段 | 含义 |
| --- | --- |
| `port` | PWM 端口 |
| `mode` | `speed` 或 `position` |
| `commanded_speed` | 连续旋转速度目标 |
| `commanded_angle` | 位置角度目标，单位为度 |
| `output_enabled` | 当前端口是否正在输出 |

会话属性：

| 属性/方法 | 含义 |
| --- | --- |
| `session.sources` | 实际订阅的数据源 |
| `session.effective_rate_hz` | 各数据源在当前会话中的目标频率 |
| `session.command_ports(target)` | 指定命令类型允许使用的端口 |
| `session.motor_pwm_command_ports` | 开环 PWM 电机端口 |
| `session.motor_speed_command_ports` | 闭环速度电机端口 |
| `session.close()` | 关闭会话；通常由 `with` 自动完成 |

#### 4.1.5 订阅 PWM 与 TTL 状态

```python
s1 = lite.pwm_servo(1, mode="speed")
s2 = lite.pwm_servo(2, mode="position")

with lite.control():
    ttl1 = lite.ttl_servo(1, mode="position")

with lite.realtime.open(
    data_sources=("pwm_servos", "ttl_servos"),
    pwm_servos=(s1, s2),
    ttl_servos=(ttl1,),
    frequency="medium",
) as session:
    event = session.data.read(timeout=2.0)
```

这里只读取状态，不会让舵机动作。

`pwm_servos` 和 `ttl_servos` 参数用于明确要读取哪些对象及其模式。仅在 `data_sources` 包含相应来源时需要填写：

- 订阅 `pwm_servos` 时，应提供至少一个通过 `lite.pwm_servo()` 创建的对象。
- 订阅 `ttl_servos` 时，应提供至少一个通过 `lite.ttl_servo()` 创建的对象。
- 不要把整数端口或 ID 直接放入这两个参数。

实时会话使用规则：

- 使用 `with` 确保会话一定关闭。
- 同一个 `lite` 对象同一时间只打开一个实时会话。
- 订阅原生数据源时，进入 `with` 代码块即表示实时数据通道已经收到并验证第一批数据；启动失败会直接抛出连接异常，不会先返回一个尚无数据的会话。
- `session.data.read()` 可以按程序需要随时调用；不调用时数据仍可能到达等待区。
- `read(timeout=None)` 会持续等待；控制程序建议使用有限超时，以便检查退出条件。
- 会话关闭后，不要继续使用原来的 `session.data` 或 `session.commands` 对象。

### 4.2 实时命令

**本节内容包括：** 支持类型、电机示例、PWM 示例、使用规则、命令统计、数据与命令同时使用。

实时命令适合循迹、遥控、平滑速度曲线和多执行器联动。当前最高持续更新频率为 20 Hz。

#### 4.2.1 支持类型

| `command_targets` 键名 | 值范围 |
| --- | --- |
| `motor_pwms` | M1～M4，`-100～100%` |
| `motor_speeds` | M1～M4，整数 `-360～360 RPM` |
| `pwm_continuous_servos` | S1～S6，`-100～100%` |
| `pwm_position_servos` | S1～S6，`0～180°` |

同一个电机不能同时声明在 `motor_pwms` 和 `motor_speeds` 中；同一个 PWM 端口不能同时声明为连续旋转和位置类型。

声明方式：

```python
command_targets = {
    "motor_pwms": (1, 2),
    "motor_speeds": (3, 4),
    "pwm_continuous_servos": (1, 2),
    "pwm_position_servos": (3, 4, 5, 6),
}
```

字典中的端口只声明本次会话允许控制的范围，不会在打开会话时自动让执行器动作。之后的 `write()` 必须为同一命令类型的全部已声明端口提供目标。

例如声明 `"motor_pwms": (1, 2)` 后：

```python
commands.write({1: 20, 2: 20}, valid_for=0.3)  # 正确
commands.write({1: 20}, valid_for=0.3)         # 错误：缺少 M2
commands.write({1: 20, 2: 20, 3: 20}, valid_for=0.3)  # 错误：M3 未声明
```

#### 4.2.2 电机示例

```python
import time

with lite.control():
    with lite.realtime.open(
        command_targets={
            "motor_pwms": (1, 2),
        },
    ) as session:
        commands = session.commands.motor_pwms

        for speed in range(0, 31):
            commands.write(
                {1: speed, 2: speed},
                valid_for=0.3,
            )
            time.sleep(0.05)

        commands.stop()
```

闭环 RPM 使用 `session.commands.motor_speeds`：

```python
with lite.control():
    with lite.realtime.open(
        command_targets={
            "motor_speeds": (1, 2, 3, 4),
        },
    ) as session:
        session.commands.motor_speeds.write(
            {1: 60, 2: 60, 3: 60, 4: 60},
            valid_for=0.3,
        )
        session.commands.motor_speeds.stop()
```

`session.commands` 下只有已经声明的命令类型可以使用。访问未声明的类型会报错。每个命令对象提供：

| 成员 | 含义 |
| --- | --- |
| `ports` | 本类型声明的端口元组 |
| `write(mapping, valid_for=...)` | 提交一组新目标 |
| `stop()` | 停止本类型声明的端口 |
| `stats()` | 返回发送和替换统计 |

#### 4.2.3 PWM 示例

```python
with lite.control():
    with lite.realtime.open(
        command_targets={
            "pwm_continuous_servos": (1, 2),
            "pwm_position_servos": (3, 4),
        },
    ) as session:
        session.commands.pwm_continuous_servos.write(
            {1: 20, 2: -20},
            valid_for=0.3,
        )
        session.commands.pwm_position_servos.write(
            {3: 60, 4: 120},
            valid_for=0.3,
        )
```

#### 4.2.4 使用规则

- `frequency` 只控制实时数据，不控制实时命令。
- 命令更新速度由程序调用 `write()` 的节奏决定。
- 每次 `write()` 必须包含该命令类型声明的全部端口。
- `valid_for` 必填，范围 0.05～2.0 秒。
- 建议以 10～20 Hz 更新连续运动目标，并让 `valid_for` 大于正常更新间隔。
- 程序可以偶尔调用，也可以短时间连续调用；不需要持续发送时可以暂时不调用。
- 同一目标在发送前收到多个新值时，只保留最新值，避免依次执行已经过时的中间目标。
- 会话关闭时会停止本次使用过的命令目标。

`valid_for` 是安全有效期，不是更新频率。例如以 20 Hz 更新时，正常间隔约 0.05 秒，可以设置 `valid_for=0.2` 或 `0.3` 秒，为偶发调度延迟留出余量；不应设置得很长来掩盖程序停止更新的问题。

推荐使用绝对节拍，避免“执行时间 + sleep”逐步拖慢循环：

```python
import time

period = 0.05  # 20 Hz
next_tick = time.monotonic()

for value in range(100):
    commands.write({1: value % 30, 2: value % 30}, valid_for=0.3)
    next_tick += period
    time.sleep(max(0.0, next_tick - time.monotonic()))
```

用户不必精确固定频率。事件触发式程序可以只在目标变化时调用，但在执行器持续运动期间，应确保下一次更新或停止发生在 `valid_for` 到期之前。

#### 4.2.5 命令统计

```python
stats = session.commands.motor_pwms.stats()
print(stats.sent, stats.replaced)
```

| 字段 | 含义 |
| --- | --- |
| `sent` | 已发送的目标更新次数 |
| `replaced` | 发送前被更新目标或停止操作替代的旧目标次数 |

`replaced` 不表示通信丢包。例如程序写入最终零目标后立即调用 `stop()`，停止操作可能直接替代尚未发送的零目标，此时 `replaced=1` 属于正常结果。

实时命令采用“最新目标优先”：如果前一目标仍在等待发送，程序又提交了新目标，旧目标没有继续执行的价值，因此会由新目标替换。这样可以避免车辆在恢复后依次执行已经过时的转向指令。

应关注的是：

- `sent` 是否持续增长；
- 执行器是否按最新目标响应；
- `replaced` 是否因程序提交速度长期明显高于支持速度而快速增长；
- 是否出现异常或安全停止。

偶尔出现少量 `replaced` 通常不影响控制。如果大量增长，应降低 `write()` 调用频率或只在目标真正变化时提交。

#### 4.2.6 数据与命令同时使用

```python
import time

with lite.control():
    with lite.realtime.open(
        data_sources=("line_tracker",),
        command_targets={
            "motor_speeds": (1, 2),
        },
        frequency="high",
        data_queue_size=16,
    ) as session:
        end_time = time.monotonic() + 10.0

        while time.monotonic() < end_time:
            event = session.data.read(timeout=0.05)
            if event is None or event.source != "line_tracker":
                continue

            left_rpm = 45
            right_rpm = 45
            # 根据 event.data.detected 调整左右轮目标
            session.commands.motor_speeds.write(
                {1: left_rpm, 2: right_rpm},
                valid_for=0.3,
            )

        session.commands.motor_speeds.stop()
```

控制算法应优先使用最新数据；当数据年龄超过应用允许值时，应停止运动或进入安全降级状态。

一个更完整的控制循环通常包含：

1. 用有限 `timeout` 等待下一条需要的数据。
2. 检查 `event.source`、读数 `valid` 和 `event.age`。
3. 根据当前读数计算目标，不累计执行旧事件。
4. 提交完整的端口映射和合适的 `valid_for`。
5. 无数据、数据无效或退出时调用 `stop()`。

实时命令最高约 20 Hz，意味着短时间内多次 `write()` 不会让每个中间值都逐条执行。对于运动控制，这种行为用于保持最新目标，而不是保存命令历史。

## 5 示例与问题排查

### 5.1 例程与程序结构

**本节内容包括：** 例程学习路线、Wi-Fi 程序起点、传感器控制程序起点、实时控制程序起点。

```python
import pymotion as pm


def main():
    with pm.lite.connect(
        transport="usb",
        timeout=15.0,
    ) as lite:
        print("Device:", lite.connection.device_id)
        print("Transport:", lite.connection.transport)

        imu = lite.imu()
        if imu.valid:
            print("Orientation:", imu.orientation)

        with lite.control():
            lite.motor(1).set_pwm(
                20,
                duration=1.0,
            )


if __name__ == "__main__":
    try:
        main()
    except pm.lite.LiteError as exc:
        print("PyMotion Lite error:", exc)
```

该结构清楚地区分连接、读取、控制和异常处理，适合作为新项目起点。

#### 5.1.1 例程学习路线

SDK 的公开例程分为 Quick Start 和完整学习课程。第一次使用时先运行 Quick Start，确认安装、连接和基本控制都正常，再按实际硬件选择学习课程。

| 学习阶段 | 推荐例程 | 学习目标 |
| --- | --- | --- |
| 认识 SDK | `01-quick-start/code/01-pymotion-lite.py` | 确认 Python 能导入 SDK，并了解程序入口 |
| 建立连接 | `01-quick-start/code/02-connection.py` | 设置出厂 Token 并通过 USB 快速连接；按需继续配置 Wi-Fi |
| 第一次控制 | `01-quick-start/code/03-motor.py` | 在安全条件下控制电机并可靠停止 |
| 传感与显示 | `01-quick-start/code/04-ultrasonic-oled.py` | 读取超声波并在 OLED 上显示 |
| 单项功能 | `02-lite-learning-course/code/03` 至 `22` | 按硬件类型学习执行器、传感器、状态和安全接口 |
| 实时功能 | `02-lite-learning-course/code/23` 至 `26` | 连续接收数据、发送实时命令并制作仪表盘 |

运行涉及电机或舵机的例程前，应让车轮悬空或固定机构，清空运动范围，并准备能够立即切断执行器电源。先阅读文件开头的说明，再修改端口、方向、速度或舵机 ID。

#### 5.1.2 Wi-Fi 程序起点

```python
import pymotion as pm


def main():
    with pm.lite.connect(
        "90E5B1D51380",
        transport="wifi",
        timeout=15.0,
    ) as lite:
        print("Connected:", lite.connection.device_id)
        print("State:", lite.status(max_age=1.0).state)


if __name__ == "__main__":
    try:
        main()
    except pm.lite.LiteError as exc:
        print("PyMotion Lite error:", exc)
```

#### 5.1.3 传感器控制程序起点

```python
import pymotion as pm


with pm.lite.connect() as lite:
    motor = lite.motor(1)

    with lite.control():
        reading = lite.ultrasonic(max_age=0.3)

        if reading.valid and reading.distance >= 300:
            motor.set_pwm(15, duration=0.5)
        else:
            motor.stop()
```

这个结构先判断读数有效性，再决定是否运动。任何无法确认安全的数据都进入停止分支。

#### 5.1.4 实时控制程序起点

```python
import time
import pymotion as pm


with pm.lite.connect(transport="usb") as lite:
    with lite.control():
        with lite.realtime.open(
            data_sources=("line_tracker",),
            command_targets={"motor_speeds": (3, 4)},
            frequency="high",
            data_queue_size=16,
        ) as session:
            commands = session.commands.motor_speeds
            end_time = time.monotonic() + 10.0

            try:
                while time.monotonic() < end_time:
                    event = session.data.read(timeout=0.2)
                    if event is None or event.source != "line_tracker":
                        commands.stop()
                        continue

                    line = event.data
                    if not line.valid or event.age is None or event.age > 0.2:
                        commands.stop()
                        continue

                    commands.write(
                        {3: 35, 4: 35},
                        valid_for=0.3,
                    )
            finally:
                commands.stop()
```

实际循迹程序应根据 `line.detected` 计算左右轮差速；这个模板主要展示连接、数据检查、命令有效期和退出停止的完整结构。

### 5.2 异常处理

**本节内容包括：** 常见异常、推荐异常结构、出错后是否可以重试。

推荐捕获 `pm.lite.LiteError`：

```python
import pymotion as pm

try:
    with pm.lite.connect() as lite:
        with lite.control():
            lite.motor(1).set_pwm(20, duration=1.0)
except pm.lite.LiteError as exc:
    print("PyMotion Lite error:", exc)
```

| 异常 | 常见原因 |
| --- | --- |
| `DeviceNotFoundError` | 没有找到指定设备 |
| `MultipleDevicesFoundError` | 发现多台设备但未指定 `device_id` |
| `AuthenticationError` | Token 不匹配 |
| `ConnectionTimeoutError` | 建立连接超时 |
| `ConnectionClosedError` | 连接关闭后继续调用 |
| `ControlUnavailableError` | 控制权被占用或重复进入控制上下文 |
| `DeviceBusyError` | 设备正在执行其他独占操作 |
| `EstopActiveError` | 急停锁存尚未复位 |
| `DeviceFaultError` | 设备处于故障状态 |
| `StaleStatusError` | 数据超过 `max_age` |
| `SensorUnavailableError` | 传感器未连接或当前不可用 |
| `CapabilityUnsupportedError` | 当前设备不支持所调用功能 |
| `RpcTimeoutError` | 普通读取或非动作操作等待超时 |
| `CommandOutcomeUnknownError` | 写命令可能已经执行，但程序无法确认最终结果 |

写操作正常返回（包括返回 `None`）表示设备已经返回命令级成功响应；设备明确拒绝时会抛出相应异常。命令级成功不等于机械机构已经物理到位，只有明确带有状态验证语义的结果才表示经过反馈确认。

遇到 `CommandOutcomeUnknownError` 时，不要直接重复运动命令。先保证现场安全并尝试停止输出；连接可用时重新读取最新状态，再决定是否重新执行。该异常不表示命令一定成功或一定失败，只表示 SDK 无法证明最终结果。

参数类型或范围错误通常抛出 `TypeError` 或 `ValueError`，应直接修正程序参数。

#### 5.2.1 推荐异常结构

```python
import pymotion as pm


try:
    with pm.lite.connect(transport="wifi") as lite:
        with lite.control():
            motor = lite.motor(1)
            motor.set_pwm(20)
            # 其他业务逻辑
            motor.stop()
except (TypeError, ValueError) as exc:
    print("程序参数错误:", exc)
except pm.lite.AuthenticationError as exc:
    print("请检查设备 Token:", exc)
except pm.lite.DeviceNotFoundError as exc:
    print("请检查设备连接和设备 ID:", exc)
except pm.lite.CommandOutcomeUnknownError as exc:
    print("命令结果无法确认，不要直接重复发送:", exc.operation)
except pm.lite.LiteError as exc:
    print("设备操作失败:", exc)
```

不要使用空的 `except:` 忽略所有错误。执行器程序至少应记录错误，并依靠控制上下文退出时的停止行为完成清理。

#### 5.2.2 出错后是否可以重试

| 情况 | 建议 |
| --- | --- |
| 参数错误 | 修正参数，不要原样重试 |
| 数据过旧或暂时不可用 | 可在有限次数内重新读取；运动控制应先进入安全状态 |
| 普通读取超时 | 检查连接状态后，可以有限次数重新读取 |
| `CommandOutcomeUnknownError` | 先停止并读取状态，确认现场后再决定 |
| `ESTOP` / `FAULT` | 排查原因并按安全流程复位，不要循环重试运动命令 |
| 控制权被占用 | 等待当前控制者释放，或结束重复运行的程序 |

### 5.3 常见问题

本章按实际现象说明排查顺序。遇到执行器异常时，应先停止输出并确认现场安全，再继续检查程序和连接。

#### 5.3.1 执行器没有动作

依次检查：

1. 是否连接外部电源，电压是否满足负载要求。
2. 是否进入 `with lite.control():`。
3. 设备是否处于 `ESTOP` 或 `FAULT`。
4. 电机、PWM 端口和 TTL ID 是否与接线一致。
5. PWM/TTL 舵机声明的模式是否与实际模式一致。

#### 5.3.2 数据不更新

检查：

- 传感器是否正确连接。
- `valid` 和 `state` 的值。
- `age` 是否超过设置的 `max_age`；两者单位均为秒。
- 实时会话是否持续调用 `session.data.read()`。
- `session.data.stats().dropped` 是否增长。

#### 5.3.3 Wi-Fi 可以发现但连接超时

先检查 Token、电脑当前 IP、配网页面的服务器地址，以及路由器或热点是否启用了访客/AP 隔离。多数 Windows 电脑不需要手动设置防火墙；只有设备和电脑已经确认能够互相访问、其他配置也正确，但 TCP 连接仍超时时，才检查防火墙或安全软件是否拦截 Python/SDK 接收设备发往电脑 TCP 8787 的入站连接。可以仅在受信任的专用网络中允许对应程序或端口，不要直接关闭整个防火墙。

Wi-Fi 实时数据还要求电脑能够主动连接设备的 TCP 8789；该方向通常不需要 Windows 入站规则。手机热点息屏、访客/AP 隔离或节能设置也可能影响连接稳定性。

#### 5.3.4 电机位置不准

检查编码器 `ppr`、`gear_ratio`、电机方向、供电、机械间隙和负载。执行位置运动前应在电机静止时调用 `zero_position()`。

#### 5.3.5 里程计偏差较大

在实际地面重新测量轮子滚动直径和左右轮中心距离，并检查轮胎打滑、左右轮速度差和编码器反馈。

#### 5.3.6 为什么指定 `duration` 后后面的代码晚执行

直流电机、连续旋转 PWM 舵机和速度模式 TTL 舵机的普通 API 在指定 `duration` 时，会等待这段时间并完成停止后才返回。这适合简单教学和顺序动作。需要多个动作同时进行时，应使用批量 API、实时命令，或由应用程序自行调度。

#### 5.3.7 为什么调用成功但 PWM 位置舵机没有准确到位

PWM 位置舵机接口没有实际角度反馈。调用成功只说明目标已接受。检查舵机供电、角度范围、舵臂是否受阻以及是否预留足够运动时间；需要角度反馈时应使用能够报告位置的 TTL 舵机。

#### 5.3.8 为什么 `replaced` 不是 0

它表示尚未发送的旧实时目标被更新目标或停止操作替换，不是数据包丢失。少量替换，特别是结束前零目标紧接 `stop()`，通常属于正常现象。持续大量增加时，应降低提交频率。

#### 5.3.9 为什么选择 `high` 仍达不到 20 Hz

`high` 是最高档位，不保证所有设备都是 20 Hz。环境光、颜色、电源、雷达、TTL 状态和超声波有效测距都有各自速度限制；同时订阅较多来源时，实际速度也可能低于目标。通过 `session.effective_rate_hz` 查看目标频率，并按第 4.1.3 节的适用范围设计程序。

#### 5.3.10 USB 与 Wi-Fi 应该怎么选

- USB：连接直接，适合首次使用、固定工位和排查问题；全新设备设置出厂 Token 后即可连接，不要求先配网或接入 Wi-Fi。
- Wi-Fi：适合移动机器人和无线控制；除正确 Token 外，还需要网络互通与稳定供电。
- 两种连接使用相同的用户 API；程序通常只需修改 `transport` 和必要的 Wi-Fi 参数。

无论使用哪种连接，实时控制都应设置有效期、检查数据新鲜度，并在退出时停止执行器。

#### 5.3.11 USB 和 Wi-Fi 都偶发超时或中断

如果 USB、Wi-Fi、实时数据和配网热点同时出现不稳定，不要只排查电脑网络。供电不足或电池内阻过大可能让设备在电机启动、快速换向或舵机动作时瞬间掉压，表现为连接超时、数据中断、设备重启或配网热点没有出现。

按以下顺序检查：

1. 停止全部执行器，确认电池类型、额定电压和接线符合硬件要求。
2. 读取设备电源状态，并观察电机启动和换向时的最低电压。
3. 如果电压字段不可用，使用万用表直接测量设备供电端，不要只测空载电池电压。
4. 更换已充满且能够提供足够电流的电池，再分别验证 USB 和 Wi-Fi。
5. 供电恢复正常后仍有问题，再检查 USB 线、串口占用、Token、电脑 IP、防火墙和网络隔离。

```python
import pymotion as pm


with pm.lite.connect(transport="usb") as lite:
    power = lite.power(max_age=0.5)
    print("电池电压:", power.voltage, "V")
```

板载电压用于运行状态监视，不能代替经过校准的测量仪表。执行器负载变化较大时，应重点观察动作瞬间的压降。

## 6 API 参考

### 6.1 API 速查

**本节内容包括：** 连接、状态与安全；电机与数字输出；舵机；传感器、雷达、里程计与 OLED；实时功能；返回类型索引。

#### 6.1.1 连接、状态与安全

| API | 作用 | 返回值 | 最小调用 |
| --- | --- | --- | --- |
| `pm.lite.list_devices(*, timeout=6.25)` | 查找当前可见设备 | `tuple[LiteDeviceInfo, ...]` | `devices = pm.lite.list_devices()` |
| `pm.lite.connect(device_id=None, *, timeout=15.0, auth_token=None, transport="usb")` | 建立 USB 或 Wi-Fi 连接 | `Lite` | `lite = pm.lite.connect()` |
| `lite.control(*, timeout=5.0)` | 在 `with` 范围内取得执行器控制权 | 控制上下文 | `with lite.control(): ...` |
| `lite.is_closed` | 连接是否已经关闭 | `bool` | `if lite.is_closed: ...` |
| `lite.close()` | 关闭连接并释放资源 | `None` | `lite.close()` |
| `lite.stop(*, timeout=None)` | 正常停止整台设备的执行器 | `ActionResult` | `report = lite.stop()` |
| `lite.status(*, max_age=1.0)` | 读取一份满足新鲜度要求的设备状态 | `ProductStatus` | `state = lite.status()` |
| `lite.emergency_stop(*, timeout=None)` | 锁存急停并停止输出 | `ActionResult` | `lite.emergency_stop()` |
| `lite.reset_estop(*, timeout=None)` | 在确认安全后解除急停锁存 | `ActionResult` | `lite.reset_estop()` |
| `lite.clear_fault(*, timeout=None)` | 在排除原因后清除故障锁存 | `ActionResult` | `lite.clear_fault()` |

#### 6.1.2 电机与数字输出

| API | 作用 | 返回值 | 最小调用 |
| --- | --- | --- | --- |
| `lite.output(port)` | 取得 OUTPUT1～OUTPUT6 中的一路数字输出 | `DigitalOutput` | `out = lite.output(1)` |
| `output.on()` / `output.off()` | 输出高电平或低电平 | `None` | `out.on()` |
| `lite.motor(port)` | 取得 M1～M4 中的一只电机对象 | `Motor` | `motor = lite.motor(1)` |
| `motor.set_pwm(pwm, *, duration=None)` | 设置开环输出百分比 | `None` | `motor.set_pwm(20)` |
| `motor.set_speed(rpm, *, duration=None)` | 设置整数闭环目标转速，范围 -360～360 RPM | `None` | `motor.set_speed(80)` |
| `motor.stop()` | 停止当前电机 | `None` | `motor.stop()` |
| `motor.status(*, max_age=0.5)` | 读取当前电机状态 | `MotorState` | `state = motor.status()` |
| `motor.zero_position()` | 把当前静止位置设为软件零点 | `None` | `motor.zero_position()` |
| `motor.move_to(angle, *, speed=20, tolerance=2, timeout=8)` | 移动到相对零点的目标角度 | `None` | `motor.move_to(90)` |
| `motor.move_by(angle, *, speed=20, tolerance=2, timeout=8)` | 从当前位置继续移动指定角度 | `None` | `motor.move_by(-45)` |
| `lite.motors.set_pwms(mapping, *, duration=None)` | 批量设置开环 PWM | `None` | `lite.motors.set_pwms({1: 20, 2: 20})` |
| `lite.motors.set_speeds(mapping, *, duration=None)` | 批量设置闭环 RPM | `None` | `lite.motors.set_speeds({3: 60, 4: 60})` |
| `lite.motors.status(*, max_age=0.5)` | 一次读取 M1～M4 状态 | 状态映射 | `states = lite.motors.status()` |
| `lite.motors.stop()` | 停止全部直流电机 | `None` | `lite.motors.stop()` |

#### 6.1.3 舵机

| API | 作用 | 返回值 | 最小调用 |
| --- | --- | --- | --- |
| `lite.pwm_servo(port, *, mode)` | 声明一个 PWM 舵机端口和类型 | `PwmServo` | `pwm = lite.pwm_servo(1, mode="speed")` |
| `pwm.set_speed(speed, *, duration=None)` | 设置连续旋转舵机速度 | `None` | `pwm.set_speed(30)` |
| `pwm.move_to(angle)` | 设置 PWM 位置舵机角度 | `None` | `pwm.move_to(90)` |
| `pwm.status(*, max_age=0.5)` | 读取该端口的命令状态 | `PwmServoState` | `state = pwm.status()` |
| `pwm.stop()` | 关闭该端口 PWM 输出 | `None` | `pwm.stop()` |
| `lite.pwm_servos.set_speeds(mapping, *, duration=None)` | 批量设置连续旋转舵机 | `None` | `lite.pwm_servos.set_speeds({1: 20, 2: -20})` |
| `lite.pwm_servos.move_to(mapping)` | 批量设置位置舵机角度 | `None` | `lite.pwm_servos.move_to({3: 60, 4: 120})` |
| `lite.pwm_servos.status(*, max_age=0.5)` | 读取六路 PWM 状态 | 状态映射 | `states = lite.pwm_servos.status()` |
| `lite.pwm_servos.stop()` | 关闭六路 PWM 输出 | `None` | `lite.pwm_servos.stop()` |
| `lite.ttl_servo(id, *, mode="position")` | 识别指定 ID、立即设置实际模式并返回对象；需控制权 | `TtlServo` | `with lite.control(): ttl = lite.ttl_servo(1)` |
| `ttl.move_to(angle, *, duration=None)` | 设置 TTL 舵机目标角度 | `None` | `ttl.move_to(135, duration=2)` |
| `ttl.set_speed(speed, *, duration=None)` | 设置速度模式目标 | `None` | `ttl.set_speed(25)` |
| `ttl.mode` | 读取当前连接为该舵机设置的模式 | `str` | `mode = ttl.mode` |
| `ttl.status()` | 读取在线、角度、温度等状态 | TTL 状态 | `state = ttl.status()` |
| `ttl.stop()` | 停止当前 TTL 舵机 | `None` | `ttl.stop()` |
| `lite.ttl_servo.set_id(*, new_id)` | 设置总线上唯一一只舵机的 ID；需控制权 | `TtlServoIdResult` | `lite.ttl_servo.set_id(new_id=1)` |
| `lite.ttl_servos.move_to(mapping, *, duration=None)` | 批量设置 TTL 位置目标 | `None` | `lite.ttl_servos.move_to({ttl: 90})` |
| `lite.ttl_servos.set_speeds(mapping, *, duration=None)` | 批量设置 TTL 速度目标 | `None` | `lite.ttl_servos.set_speeds({ttl: 20})` |
| `lite.ttl_servos.status()` | 读取当前程序已创建的 TTL 舵机状态 | 状态映射 | `states = lite.ttl_servos.status()` |
| `lite.ttl_servos.stop()` | 停止当前程序已创建的 TTL 舵机 | `None` | `lite.ttl_servos.stop()` |

#### 6.1.4 传感器、雷达、里程计与 OLED

| API | 作用 | 返回值 | 最小调用 |
| --- | --- | --- | --- |
| `lite.sensors(*, max_age=0.5)` | 一次读取五类常用传感器 | `SensorObservation` | `data = lite.sensors()` |
| `lite.imu(*, max_age=0.5)` | 读取加速度、角速度和姿态 | `ImuReading` | `imu = lite.imu()` |
| `lite.ultrasonic(*, max_age=0.5)` | 读取超声波距离 | `UltrasonicReading` | `distance = lite.ultrasonic()` |
| `lite.line_tracker(*, max_age=0.5)` | 读取五路循迹状态 | `LineTrackerReading` | `line = lite.line_tracker()` |
| `lite.ambient_light(*, max_age=0.5)` | 读取环境照度 | `AmbientLightReading` | `light = lite.ambient_light()` |
| `lite.color(*, max_age=0.5)` | 读取 RGBC 原始值 | `ColorReading` | `color = lite.color()` |
| `lite.power(*, max_age=1.0)` | 读取电池电压和三组供电电流 | `PowerReading` | `power = lite.power()` |
| `lite.lidar.frame(*, max_age=0.5)` | 读取一帧雷达点 | `LidarFrame` | `frame = lite.lidar.frame()` |
| `lite.lidar.scan()` | 等待并读取一整圈新的雷达扫描 | `LidarScan` | `scan = lite.lidar.scan()` |
| `lite.lidar.stream()` | 打开连续整圈扫描 | `LidarStream` | `with lite.lidar.stream() as stream: ...` |
| `stream.next_scan(*, timeout=3.0)` | 等待并返回当时最新的一圈新扫描 | `LidarScan` | `scan = stream.next_scan()` |
| `stream.stats()` | 查看连续扫描统计 | `LidarStreamStats` | `stats = stream.stats()` |
| `lite.odometry.configuration()` | 读取当前里程计配置 | `OdometryConfiguration` | `cfg = lite.odometry.configuration()` |
| `lite.odometry.configure(*, left_motor_port, right_motor_port, wheel_diameter_mm, wheel_separation_mm)` | 设置左右轮端口和底盘几何参数 | `OdometryConfiguration` | `lite.odometry.configure(left_motor_port=3, right_motor_port=4, wheel_diameter_mm=67.5, wheel_separation_mm=166)` |
| `lite.odometry.status(*, max_age=0.5)` | 读取位置、航向和速度 | `OdometryState` | `odom = lite.odometry.status()` |
| `lite.oled.show(lines, *, duration_seconds=5.0)` | 临时显示 1～4 行文字 | `None` | `lite.oled.show("Ready")` |
| `lite.oled.show()` | 恢复默认欢迎页 | `None` | `lite.oled.show()` |
| `lite.oled.show(*, page, slide=False)` | 固定指定页，或从该页开始轮播 | `None` | `lite.oled.show(page="power")` |
| `lite.oled.show(*, slide=True)` | 从第一页开始自动轮播 | `None` | `lite.oled.show(slide=True)` |
| `lite.oled.show_pages(pages, *, refresh_interval_seconds=0.5, page_interval_seconds=3.0)` | 配置多页动态显示并立即轮播 | `None` | `lite.oled.show_pages(pages)` |

#### 6.1.5 实时功能

```python
lite.realtime.open(
    *,
    data_sources=(),
    command_targets=None,
    frequency="low",
    data_queue_size=32,
    ttl_servos=(),
    pwm_servos=(),
)
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `data_sources` | `tuple[str, ...]` | 空元组 | 需要连续接收的数据源名称；可用值见第 4.1.1 节 |
| `command_targets` | `Mapping[str, tuple[int, ...]] \| None` | `None` | 需要启用的实时命令类型及端口；只读会话可省略 |
| `frequency` | `str` | `"low"` | 实时数据档位 `low`、`medium` 或 `high`；不控制命令发送频率 |
| `data_queue_size` | `int` | `32` | Python 端最多暂存的未读取事件数，范围 1～1024 |
| `ttl_servos` | `tuple[TtlServo, ...]` | 空元组 | 订阅 TTL 状态时列出已经创建的 TTL 舵机对象 |
| `pwm_servos` | `tuple[PwmServo, ...]` | 空元组 | 订阅 PWM 状态时列出已经创建的 PWM 舵机对象 |

**返回值：** `RealtimeSession`。应使用 `with` 打开和关闭，避免程序异常退出后会话仍占用资源。

数据：

- `session.data.read(timeout=None)`
- `session.data.stats()`
- `session.sources`
- `session.effective_rate_hz`

命令：

- `session.commands.motor_pwms.write(mapping, *, valid_for)`
- `session.commands.motor_speeds.write(mapping, *, valid_for)`
- `session.commands.pwm_continuous_servos.write(mapping, *, valid_for)`
- `session.commands.pwm_position_servos.write(mapping, *, valid_for)`
- 每个命令对象均提供 `stop()`、`stats()` 和只读 `ports`。

最小示例：

```python
with lite.realtime.open(
    data_sources=("imu",),
    frequency="medium",
) as session:
    event = session.data.read(timeout=1.0)
    if event is not None:
        print(event.source, event.data)
```

#### 6.1.6 常用返回类型索引

| 返回类型 | 详细说明位置 |
| --- | --- |
| `ConnectionInfo`、`LiteDeviceInfo` | 第 1.3 节 |
| `ProductStatus`、`ActionResult` | 第 1.4.3、3.6 节 |
| `MotorState` | 第 2.2.6 节 |
| `PwmServoState` | 第 2.3.3 节 |
| `TtlServoIdResult`、TTL 状态 | 第 2.4.1、2.4.4 节 |
| 五类传感器读数 | 第 3.1 节 |
| `PowerReading` | 第 3.2 节 |
| `LidarFrame`、`LidarScan`、`LidarStreamStats` | 第 3.3 节 |
| `OdometryConfiguration`、`OdometryState` | 第 3.4 节 |
| `RealtimeDataEvent`、实时数据与命令统计 | 第 4.1～4.2 节 |

所有返回对象都应通过属性读取，例如 `state.measured_rpm`，不要依赖对象打印文本的排版。带有 `None` 可能性的字段，使用前应明确判断。
