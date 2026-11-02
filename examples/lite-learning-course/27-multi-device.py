"""同时连接三台 PyMotion Lite，读取电压并控制三台设备的 M1 电机。
"""

import time

import pymotion as pm


# 第一台设备：USB 连接。
DEVICE_1_ID = "90E5B1AA2CEC"
DEVICE_1_TOKEN = "123456"
DEVICE_1_TRANSPORT = "usb"

# 第二台设备：Wi-Fi 连接。
DEVICE_2_ID = "90E5B1AA2CE0"
DEVICE_2_TOKEN = "123456"
DEVICE_2_TRANSPORT = "wifi"

# 第三台设备：运行前将 000000000000 改为真实设备 ID。
DEVICE_3_ID = "000000000000"
DEVICE_3_TOKEN = "123456"
DEVICE_3_TRANSPORT = "usb"

# 三台设备使用相同的电机测试参数。
MOTOR_PORT = 1
MOTOR_PWM_PERCENT = 50
RUN_SECONDS = 5.0


def show_discovered_devices():
    """显示当前发现的板卡及其可用连接方式。"""

    devices = pm.lite.list_devices(timeout=1.0)
    if not devices:
        print("未发现设备")
        return

    print("发现以下设备：")
    for device in devices:
        links = ", ".join(device.transports)
        print(f"- ID: {device.device_id}, link: {links}")


def show_device_status(number, device):
    """显示一台设备的连接信息和电源电压。"""

    device_id = device.connection.device_id
    transport = device.connection.transport
    voltage = device.power().voltage

    print(f"设备 {number} 已连接: {device_id}, link: {transport}")
    print(f"设备 {number} 电压: {voltage} V")


def run_three_motors(device_1, device_2, device_3):
    """同时运行三台设备的 M1，经过指定时间后停止。"""

    motor_1 = device_1.motor(MOTOR_PORT)
    motor_2 = device_2.motor(MOTOR_PORT)
    motor_3 = device_3.motor(MOTOR_PORT)

    # 假设三台设备都可以正常取得控制权。
    with device_1.control(), device_2.control(), device_3.control():
        motor_1.set_pwm(MOTOR_PWM_PERCENT)
        motor_2.set_pwm(MOTOR_PWM_PERCENT)
        motor_3.set_pwm(MOTOR_PWM_PERCENT)

        print(
            f"三台设备的 M{MOTOR_PORT} 已启动: "
            f"PWM={MOTOR_PWM_PERCENT}%, 时间={RUN_SECONDS}s"
        )
        time.sleep(RUN_SECONDS)

        # 假设三个停止命令都可以正常执行。
        motor_1.stop()
        motor_2.stop()
        motor_3.stop()
        print("三台设备的电机已停止")


def main():
    show_discovered_devices()

    # 使用逗号分隔三个连接，退出 with 时自动关闭三台设备。
    with pm.lite.connect(
        DEVICE_1_ID,
        auth_token=DEVICE_1_TOKEN,
        transport=DEVICE_1_TRANSPORT,
    ) as device_1, pm.lite.connect(
        DEVICE_2_ID,
        auth_token=DEVICE_2_TOKEN,
        transport=DEVICE_2_TRANSPORT,
    ) as device_2, pm.lite.connect(
        DEVICE_3_ID,
        auth_token=DEVICE_3_TOKEN,
        transport=DEVICE_3_TRANSPORT,
    ) as device_3:
        show_device_status(1, device_1)
        show_device_status(2, device_2)
        show_device_status(3, device_3)
        run_three_motors(device_1, device_2, device_3)


if __name__ == "__main__":
    try:
        main()
    except pm.lite.LiteError as exc:
        print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
