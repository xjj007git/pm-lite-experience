# %%
# 测试lite类
import pymotion as pm
lite = pm.lite.connect(auth_token="123456")
print(type(lite))          # <class 'pymotion_lite.facade.Lite'>
isinstance(lite, pm.lite.Lite)   # isinstance 判断是否为类实例True



# %%
# 测试一下lite.control返回什么
import pymotion as pm
lite = pm.lite.connect(auth_token="123456")

with lite.control() as ctx:
    print(ctx)                 # <pymotion_lite.facade.LiteControlContext object at 0x7f8e4c3b1d30>
    print(type(ctx))

lite.close()  # 关闭连接    如果一次连接没有中断 那将导致下次连连接设备都找不到 因为板子还认为自己连着  用with管理上下文确实很保险



# %%
# 查找当前可见的 PyMotion Lite 设备
import pymotion as pm
devices = pm.lite.list_devices(timeout=6.25)
for device in devices:
    # print(device) #id和transport为全部属性
    print(device.device_id)
    print(device.transports)



# %%
# 查看 Lite 类的属性和方法
import pymotion as pm
import inspect

L = pm.lite.Lite

props = []
methods = []

for m in dir(L):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(L, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
#查看lite的motor()方法返回的motor类成员变量
import pymotion as pm
import inspect

motor = pm.lite.Motor

props = []
methods = []

for m in dir(motor):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(motor, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 获取电机对象
import pymotion as pm

with pm.lite.connect(transport="usb",auth_token="123456") as lite:
    motor = lite.motor(2)  # 返回一个motor类 参数范围1-4 越界报错 
    print(motor.port)
    print(type(motor))          # <class 'pymotion_lite.motors.Motor'>
    print(type(motor.port))     # int



# %%
# 电机开环
import pymotion as pm

with pm.lite.connect(auth_token="123456") as lite:
    motor = lite.motor(1)
    with lite.control():
        # motor.set_pwm(100, duration=5.0)  # duration必须按名字传 且严格设置了参数边界 越界报错 
        motor.set_pwm(100)  
        time.sleep(10.0)     #等待稳定

        #查看一下状态
        s = motor.status(max_age=0.5)
        print("control_mode:   ", s.control_mode)
        print("has_encoder:    ", s.has_encoder)
        print("feedback_valid: ", s.feedback_valid)
        print("target_rpm:     ", s.target_rpm)
        print("measured_rpm:   ", s.measured_rpm)
        print("output_saturated:", s.output_saturated)
        print("controller_enabled:", s.controller_enabled)

        motor.stop()



# %%
# 闭环控制
import pymotion as pm

with pm.lite.connect(auth_token="123456") as lite:
    motor = lite.motor(1)
    with lite.control():
        # motor.set_speed(360, duration=5.0)  #rpm边界-360 - 360
        motor.set_speed(360)    #设定为300rpm 那么电机在lite.control中就会一直维持 直到control关闭
        time.sleep(10.0)     #电机会维持上面转速

        #查看一下状态
        s = motor.status(max_age=0.5)
        print("control_mode:   ", s.control_mode)
        print("has_encoder:    ", s.has_encoder)
        print("feedback_valid: ", s.feedback_valid)
        print("target_rpm:     ", s.target_rpm)
        print("measured_rpm:   ", s.measured_rpm)
        print("output_saturated:", s.output_saturated)  #控制饱和指的似乎是pwm是否饱和
        print("controller_enabled:", s.controller_enabled)

        # motor.stop()  #电机两种情况会停下 motor.stop和退出control



# %%
# 绘制一下rpm曲线   
import time
import pymotion as pm
import matplotlib.pyplot as plt

with pm.lite.connect(auth_token="123456") as lite:
    with lite.control():
        m = lite.motor(1)
        m.set_speed(300)

        ts, rpms = [], []
        t0 = time.monotonic()
        while time.monotonic() - t0 < 5.0:
            count = time.monotonic()
            s = m.status(max_age=0.2)
            read_status_time = time.monotonic() - count
            # print(f"读取电机状态花费时间:{read_status_time}")

            ts.append(time.monotonic() - t0)
            rpms.append(s.measured_rpm)
            time.sleep(0.02)                     # 50 Hz 采样

        m.stop()

# print(f"采样时间{ts}")
plt.plot(ts, rpms)  #非常低下的采样效率
plt.axhline(300, color='r', ls='--', label='target')
plt.xlabel('time (s)'); plt.ylabel('RPM'); plt.legend()
plt.show()



# %%
# 超声波
# triger没有信号
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    while(1):
        reading = lite.ultrasonic()
        print("valid:  ", reading.valid)
        print("state:  ", reading.state)
        # print("age:    ", reading.age)
        print("distance:", reading.distance)



# %%
# 超声波例程
import pymotion as pm

with pm.lite.connect(transport="usb",auth_token="123456") as lite:
    while(1):
        reading = lite.ultrasonic()
        if reading.valid:
            print(reading.distance, "mm")  # 输出距离



# %%
# 循迹模块
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    while(1):
        line = lite.line_tracker()
        if line.valid:
            print(line.levels)    # 五路电平
            print(line.detected)  # 五路检测结果



# %%
# 多电机控制
import time
import pymotion as pm

with pm.lite.connect(transport="usb") as lite:
    with lite.control():
        lite.motors.set_pwms({1: 30, 2: -30})
        lite.motors.set_speeds({3: 80, 4: 80})
        time.sleep(2.0)
        lite.motors.stop()



# %%
# 查看一下lite类下面的motors属性
import inspect
import pymotion as pm

L = pm.lite.Motors

props = []
methods = []

for m in dir(L):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(L, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"类名: {L.__module__}.{L.__name__}")
print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 位置控制
import time
import pymotion as pm

with pm.lite.connect(transport="usb",auth_token="123456") as lite:
    motor = lite.motor(1)
    with lite.control():
        motor.stop()
        time.sleep(0.5)
        if motor.status().running:
            raise RuntimeError("确认电机静止后再建立零点")
        motor.zero_position()
        motor.move_to(90)   #绝对角度
        motor.move_by(-45)  #相对角度



# %%
# 位控特点
# 1.speed描述的是pwm上限
# 2.位控具有阻塞性——串行的必然性 执行完才执行下一条 stop和set_pwm不可中断
# 3.想要位控并行可以使用开线程？
import time
import pymotion as pm

with pm.lite.connect(transport="usb",auth_token="123456") as lite:
    m1 = lite.motor(1)
    m2 = lite.motor(2)
    with lite.control():
        m1.stop(); m2.stop(); time.sleep(1)
        m1.zero_position(); m2.zero_position()

        # m1.move_to(180)
        # m2.move_to(180) #多电机位控阻塞性

        m1.move_to(360)
        m1.set_pwm(100)
        time.sleep(10)



# %%
# 看一下位控的theta/rpm-t曲线
import time
import pymotion as pm
import matplotlib.pyplot as plt

ANGLE = 1500
SPEED = 100

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    # s = lite.status(max_age=2.0)
    # print("lite状态:", lite.status().state)
    with lite.control():
        m = lite.motor(1)

        # 必须先建零点
        m.stop()
        time.sleep(1.0)
        m.zero_position()
        time.sleep(0.2)

        # 用线程采集，因为 move_to 会阻塞
        import threading

        samples = []
        stop_flag = threading.Event()

        def collect():
            t0 = time.monotonic()
            while not stop_flag.is_set():
                try:
                    s = m.status(max_age=0.2)
                    # print(f"控制模式：{s.control_mode}")    # 位控是闭环控制
                    # print(f"cmd_pwm: {s.commanded_pwm}\n")  # 闭环控制下cmd_pwm为None
                    samples.append((
                        time.monotonic() - t0,
                        s.measured_angle,
                        s.measured_rpm
                    ))
                except Exception:
                    pass
                time.sleep(0.01)

        th = threading.Thread(target=collect)
        th.start()
        time.sleep(0.3)          # 先采一段静止

        t_start = time.monotonic()
        m.move_to(ANGLE, speed=SPEED, timeout=20.0)    # angle范围是(-3600,3600)
        # m.move_to(ANGLE, timeout=20.0)  # 不设速度情况下 不设置时间就超时 设置时间就encoder_stall
        t_end = time.monotonic()                   # 时间要设好 不然会卡死

        time.sleep(0.5)          # 到位后再采一会儿
        stop_flag.set()
        th.join()   # 等待线程结束

print(f"运动耗时: {(t_end - t_start)*1000:.0f} ms")
print(f"采样点数: {len(samples)}")

# 绘制曲线
times = [s[0] for s in samples]
angles = [s[1] for s in samples]
rpms = [s[2] for s in samples]

plt.figure(figsize=(12, 8)) # 新建画布

plt.subplot(2, 2, 1)
plt.plot(times, angles)
plt.xlabel("Time (s)")
plt.ylabel("Angle (deg)")
plt.title("Theta-T Curve")

plt.subplot(2, 2, 2)
plt.plot(times, rpms)
plt.xlabel("Time (s)")
plt.ylabel("RPM")
plt.title("RPM-T Curve")

plt.tight_layout()  # 自动调整子图间距
plt.show()



# %%
# 获取舵机对象
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    continuous = lite.pwm_servo(1, mode="speed")
    position = lite.pwm_servo(2, mode="position")
    print(continuous)
    print(type(continuous)) # <class 'pymotion_lite.actuators.PwmServo'>
    print(position)
    print(type(position))



# %%
# 看一下PwmServo类的属性和方法
import pymotion as pm
import inspect

cls = pm.lite.PwmServo

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 连续旋转舵机
# servo.set_speed(speed, *, duration=None)
# 连续旋转模式下 几乎完全的开环 没有反馈 不能实现精准控制
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    servo = lite.pwm_servo(2, mode="speed")
    with lite.control():
        servo.set_speed(40, duration=5.0) 
        servo.stop()                       # 关闭输出



# %%
# 查看函数完整签名
import inspect
import pymotion as pm

try:
    print(inspect.signature(pm.lite.PwmServo.set_speed))
except Exception as e:
    print("拿不到:", type(e).__name__, e)



# %%
# 查看一下PWM舵机的status返回啥 看看能不能读到速度
import inspect
import pymotion as pm

try:
    print(inspect.signature(pm.lite.PwmServo.status))   # 返回类PwmServoState 这个类没有测量值
except Exception as e:
    print("拿不到:", type(e).__name__, e)



# %%
# 查看PwmServoState类的属性和方法
import pymotion as pm
import inspect

cls = pm.lite.PwmServoState

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 位置舵机  
### 注意一下 速度舵机和位置舵机在实际物理器件上就是两个东西 接线记得找准 双边是速度 单边是位置 
# 红线－电源线　棕线－地线　黄线－信号线PWM输入
# 占空比控制转角 2.5%-12.5%的周期利用率
import time
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    servo = lite.pwm_servo(2, mode="position")
    with lite.control():
        servo.move_to(50)  # 没有阻塞性
        print("舵机转动中...")
        time.sleep(2.0)     
        print("舵机转动完成")
        servo.stop()       # 关闭输出



# %%
# 多舵机控制
import time
import pymotion as pm

# 连接设备并在 with 结束时自动关闭
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        lite.pwm_servos.set_speeds({1: 30, 2: -30}) # 速度舵机就会一直转
        lite.pwm_servos.move_to({3: 30, 4: 150})    # 位置舵机就转一下就停了
        time.sleep(2.0)
        lite.pwm_servos.stop()



# %%
# 下面看一下lite下面属性pwm_servos有什么方法
import pymotion as pm
import inspect

cls = pm.lite.PwmServos

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看一下单舵机status()
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    servo = lite.pwm_servo(1, mode="speed")
    # with lite.control():
    #     servo.set_speed(40, duration=5.0) 
    #     servo.stop()    
    state = servo.status()
    print(state)



# %%
# 多PWM舵机状态
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    states = lite.pwm_servos.status()   # 这是一个PwmServoState类组成的字典
    print(states)
    for port, state in states.items():
        print(port, state.mode, state.output_enabled)



# %%
# TTL总线舵机配置id
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        result = lite.ttl_servo.set_id(new_id=1)
    print(result.id, result.max_angle)
    ttl_servo = lite.ttl_servo
    print(type(ttl_servo))



# %%
# 下面继续看一下ttl_servo类
import pymotion as pm
import inspect
cls = pm.lite.TtlServo

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
import inspect
from pymotion_lite.actuators import TtlServoAccessor

cls = TtlServoAccessor

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# TTL位置模式
import time
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token = "123456") as lite:
    with lite.control():
        result = lite.ttl_servo.set_id(new_id=1)
        print(result.id, result.max_angle)

        # 就电机的位控有阻塞性 PWM和TTL均无阻塞性
        servo = lite.ttl_servo(1, mode="position")
        servo.move_to(min(90, servo.max_angle), duration=2.0)   # 无阻塞性
        time.sleep(2)

        status = servo.status()
        if status.online:
            print(status.angle, status.moving)

        servo.stop()



# %%
# 多测几组角度看看
# 大舵机角度误差大 小舵机时好时坏
import time
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token = "123456") as lite:
    with lite.control():
        result = lite.ttl_servo.set_id(new_id=1)
        print(result.id, result.max_angle)

        servo = lite.ttl_servo(1, mode="position")

        # 就电机的位控有阻塞性 PWM和TTL均无阻塞性
        for angle in [20, 45, 90, 135, 160]:
            servo.move_to(angle, duration=3.0)

            time.sleep(3)

            s = servo.status()
            # print(type(s))
            print(f"online: {s.online}")
            print(f"id: {s.id}")
            print(f"angle: {s.angle}")
            print(f"voltage: {s.voltage}")
            print(f"temperature: {s.temperature}")
            print(f"moving: {s.moving}")
            print(f"fault_code: {s.fault_code}\n")
            servo.stop()



# %%
# 查看一下status类
import pymotion as pm
import inspect
from pymotion_lite.models import BusServoStatus

cls = BusServoStatus    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# TTL速度模式
# 关于掉线：这是最需要查清的问题，我先给出明确判断：大概率跟供电有关，但也可能是 USB 线本身；要靠数据排除
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token = "123456") as lite:
    with lite.control():
        result = lite.ttl_servo.set_id(new_id=1)
        print(result.id, result.max_angle)

        servo = lite.ttl_servo(1, mode="speed")
        servo.set_speed(-50, duration=2.0)   # 速度会阻塞

        print("会阻塞吗")



# %%
# 分别配置id
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token = "123456") as lite:
    with lite.control():
        # result = lite.ttl_servo.set_id(new_id=1)
        result = lite.ttl_servo.set_id(new_id=2)
        print(result.id, result.max_angle)



# %%
# 多TTL舵机位置控制
import time
import pymotion as pm

# 获取指定 ID 的 TTL 舵机对象
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        left = lite.ttl_servo(1, mode="position")
        right = lite.ttl_servo(2, mode="position")
        lite.ttl_servos.move_to({
            left: min(90, left.max_angle),
            right: min(180, right.max_angle),
        }, duration=2.0)
        time.sleep(2.5)
        lite.ttl_servos.stop()



# %%
# 多TTL舵机速度控制
import time
import pymotion as pm

# 获取指定 ID 的 TTL 舵机对象
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        left = lite.ttl_servo(1, mode="speed")
        right = lite.ttl_servo(2, mode="speed")
        lite.ttl_servos.set_speeds({
            left: 50,
            right: 50,
        }, duration=2.0)
        time.sleep(2.5)
        lite.ttl_servos.stop()



# %%
# 看一下ttl_servos下面方法
import pymotion as pm
import inspect

cls = pm.lite.TtlServos

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 传感器
import pymotion as pm
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    lite.sensors(max_age=0.5)



# %%
# 看一下SensorObservation
import pymotion as pm
import inspect

cls = pm.lite.SensorObservation    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看下环境光
import pymotion as pm
import inspect

cls = pm.lite.AmbientLightReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看下颜色
import pymotion as pm
import inspect

cls = pm.lite.ColorReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看下imu
import pymotion as pm
import inspect

cls = pm.lite.ImuReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看下循迹
import pymotion as pm
import inspect

cls = pm.lite.LineTrackerReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看下超声波
import pymotion as pm
import inspect

cls = pm.lite.UltrasonicReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# imu使用
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    reading = lite.imu()
    if reading.valid:
        print(type(reading.state))
        print(reading.state)



# %%
# 测试电源测量
import pymotion as pm

# 读取电压与分组电流
with pm.lite.connect(transport="usb",auth_token="123456") as lite:
    power = lite.power()
    if power.voltage is not None:
        print(type(power))
        print(power.voltage, "V")
    current = power.current(3)
    if current is not None:
        print(current, "A")



# %%
# 看下lite.power返回什么
import pymotion as pm
import inspect

cls = pm.lite.PowerReading    # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# OLED文字
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    lite.oled.show([
        "PyMotion Lite",
        "Motor ready",
        "test1",
        "test2",                # 超过4行报错 超过长度也报错
    ], duration_seconds=10.0)   # 时间默认5s



# %%
# 多页轮播
import time
import pymotion as pm

# 配置两个页面并自动轮播
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    lite.oled.show_pages({
        "network": ["Wi-Fi IP", "{wifi.ip}"],
        "sensors": ["Time", "123456"],
    })      # 默认轮播
    # print("是否阻塞")       # 不会阻塞 仅仅设置状态
    time.sleep(6.0)
    # lite.oled.show(page="sensors")  # 固定播放某一页
    # time.sleep(3.0)
    # lite.oled.show(slide=True)  # 恢复轮播
    # time.sleep(6.0)
    lite.oled.show()    # 返回默认页
    # time.sleep(6.0)



# %%
# 动态字段
import time
import pymotion as pm

# 动态字段单独占一行
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    # pages = [["Time", str(time.monotonic_ns())]]    # 这里不会对ultrasonic.distance进行解析
    pages = [["Votage", "{power.voltage}"],
             ["wifi_rssi","{wifi.rssi}"]]   # 只能用它给的

    lite.oled.show_pages(pages)
    time.sleep(6.0)
    # lite.oled.show()



# %%
# 数字输出
import time
import pymotion as pm

# 丝印-真实
# 4 - 6
# 6 - 4        
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    output = lite.output(3)
    with lite.control():
        output.on()
        time.sleep(5.0)
        output.off()



# %%
# 实时数据
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.realtime.open(
        data_sources=("imu", "power", "motors"),
        # data_sources=("imu", "power", "lidar"),
        frequency="medium",
        data_queue_size=32,
    ) as session:
        print(type(session))
        print(type(session.data))
        event = session.data.read(timeout=1.0)
        print(type(event))
        if event is None:
            print("No data received within 1 second.")
        else:
            print(event.source, event.data)  # 来源和数据



# %%
# 看一下<class 'pymotion_lite.realtime.RealtimeSession'>类  session
import pymotion as pm
import inspect

cls = pm.lite.RealtimeSession   # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看一下<class 'pymotion_lite.realtime.RealtimeData'>类 data
import pymotion as pm
import inspect

cls = pm.lite.RealtimeData   # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看一下<class 'pymotion_lite.realtime.RealtimeDataEvent'>
import pymotion as pm
import inspect

cls = pm.lite.RealtimeDataEvent   # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 三档频率测试
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.realtime.open(
        data_sources=("imu", "line_tracker", "power"),
        frequency="high",
    ) as session:
        print(session.effective_rate_hz)  # 各数据源的目标频率
        # print(type(session.data.read(timeout=1.0).source))

        # 数据统计
        # event = session.data.read(timeout=1.0)
        # stats = session.data.stats()
        # print(event.source if event else None)
        # print(stats.received, stats.dropped)

# %%
# 订阅pwm / ttl 状态
import pymotion as pm

# 打开实时数据会话
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        result = lite.ttl_servo.set_id(new_id=1)  # 设置 ID
        pwm = lite.pwm_servo(1, mode="speed")
        ttl = lite.ttl_servo(1, mode="position")

    with lite.realtime.open(
        data_sources=("pwm_servos", "ttl_servos"),
        pwm_servos=(pwm,),
        ttl_servos=(ttl,),
        frequency="medium",
    ) as session:
        for _ in range(4):
            event = session.data.read(timeout=1.0)
            if event is not None:
                print(event.source, event.data)


# %%
# 不带载-测试各传感器频率
import time
import statistics
import csv
from pathlib import Path
from datetime import datetime

import pymotion as pm

FREQS = ["low", "medium", "high"]
SOURCES = ["imu", "ultrasonic", "line_tracker", "power", "motors"]
DURATION = 30.0
RESULT_DIR = Path(__file__).parent / "../results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

rows = []

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    s = lite.status(max_age=2.0)
    print(f"初始状态: {s.state}  fault={s.fault_latched}")
    if s.state != "IDLE":
        raise RuntimeError(f"设备不在 IDLE: {s.state}")

    with lite.control():
        for freq in FREQS:
            print(f"\n===== frequency={freq} =====")

            try:
                with lite.realtime.open(
                    data_sources=tuple(SOURCES),
                    frequency=freq,
                    data_queue_size=256,
                ) as session:

                    target_hz = session.effective_rate_hz
                    print(f"目标频率: {target_hz} Hz")

                    per_source = {}
                    t0 = time.monotonic()
                    last_recv = t0

                    while time.monotonic() - t0 < DURATION:
                        ev = session.data.read(timeout=0.5)
                        if ev is None:
                            continue
                        last_recv = time.monotonic()
                        src = ev.source
                        per_source.setdefault(src, []).append(
                            time.monotonic() - t0)

                    elapsed = time.monotonic() - t0
                    stats = session.data.stats()

                print(f"接收总事件: {sum(len(v) for v in per_source.values())}  "
                      f"dropped={stats.dropped}")

                for src in SOURCES:
                    ts = per_source.get(src, [])
                    n = len(ts)
                    hz = n / elapsed if elapsed > 0 else 0

                    if len(ts) > 2:
                        ivs = [ts[i+1] - ts[i] for i in range(len(ts)-1)]
                        mean_iv = statistics.mean(ivs) * 1000
                        std_iv = statistics.stdev(ivs) * 1000 if len(ivs) > 1 else 0
                        max_iv = max(ivs) * 1000
                    else:
                        mean_iv = std_iv = max_iv = None

                    print(f"  {src:14} n={n:5}  {hz:6.2f} Hz  "
                          f"间隔 均值{mean_iv:.1f} 标准差{std_iv:.1f} "
                          f"最大{max_iv:.1f} ms" if mean_iv else
                          f"  {src:14} n={n:5}  {hz:6.2f} Hz  (样本不足)")

                    rows.append({
                        "test_id": "C-01",
                        "frequency": freq,
                        "target_hz": target_hz,
                        "source": src,
                        "n_events": n,
                        "duration_s": round(elapsed, 2),
                        "actual_hz": round(hz, 2),
                        "iv_mean_ms": round(mean_iv, 2) if mean_iv else None,
                        "iv_std_ms": round(std_iv, 2) if std_iv else None,
                        "iv_max_ms": round(max_iv, 2) if max_iv else None,
                        "dropped": stats.dropped,
                    })

            except Exception as e:
                print(f"  ❌ {type(e).__name__}: {e}")
                rows.append({
                    "test_id": "C-01", "frequency": freq,
                    "target_hz": None, "source": "ALL", "n_events": 0,
                    "duration_s": 0, "actual_hz": 0,
                    "iv_mean_ms": None, "iv_std_ms": None, "iv_max_ms": None,
                    "dropped": None,
                    "error": f"{type(e).__name__}: {e}",
                })
                break

if rows:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = RESULT_DIR / f"C-01_实时频率_{ts}.csv"
    keys = sorted({k for r in rows for k in r})
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"\n已保存: {path.resolve()}")



# %%
# 电机实时命令
import time
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token='123456') as lite:
    with lite.control():
        with lite.realtime.open(
            # 这里命令通道只有4个电机两个 pwm舵机两个
            command_targets={"motor_pwms": (1, 2)},     
        ) as session:
            channel = session.commands.motor_pwms
            channel.write({1: 30, 2: 30}, valid_for=2)    # 命令有效时间
            print("是否阻塞")   # 不会阻塞
            print(type(session.commands))
            print(type(channel))
            print(channel.stats())  # RealtimeCommandStats(sent=0, replaced=0)
            print(channel.ports)    # (1, 2)
            time.sleep(10.0)
            channel.stop()



# %%
# 看一下commands
import pymotion as pm
import inspect

cls = pm.lite.RealtimeCommands  # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 看一下motor_pwms
import pymotion as pm
import inspect

cls = pm.lite.RealtimeMotorPwmCommands  # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# PWM舵机实时命令
import time
import pymotion as pm

# 打开实时命令会话
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        with lite.realtime.open(
            command_targets={"pwm_position_servos": (1, 2)},
        ) as session:
            channel = session.commands.pwm_position_servos
            channel.write({1: 180, 2: 0}, valid_for=1.2)
            print(channel.stats())
            time.sleep(1.0)
            channel.stop()
            channel.write({1: 0, 2: 180}, valid_for=1.2)
            print(channel.stats())
            time.sleep(1.0)
            print(channel.stats())



# %%
# 数据于命令合一块
import pymotion as pm

# 同时打开实时数据与命令通道
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        with lite.realtime.open(
            data_sources=("line_tracker",),
            command_targets={"motor_speeds": (1, 2)},
            frequency="high", data_queue_size=32,
        ) as session:
            channel = session.commands.motor_speeds
            try:
                for _ in range(100):
                    event = session.data.read(timeout=0.1)
                    if event is None:
                        channel.stop()
                        continue
                    if event.source != "line_tracker":
                        channel.stop()
                        continue
                    reading = event.data
                    if (not reading.valid or event.age is None
                            or event.age > 0.2):
                        channel.stop()
                        continue
                    channel.write({1: 45, 2: 45}, valid_for=0.3)
            finally:
                channel.stop()



# %%
# 里程计
import pymotion as pm

# 配置差速里程计参数
with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        config = lite.odometry.configure(
            left_motor_port=3, right_motor_port=4,
            wheel_diameter_mm=67.5, wheel_separation_mm=166.0,
        )
    print(type(lite.odometry))
    print(type(config))
    print(config)
    print(config.left_motor_port, config.right_motor_port)
    print(lite.odometry.status())



# %%
# 看一下里程计这个类的详细属性和方法
import pymotion as pm
import inspect

cls = pm.lite.Odometry  # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")



# %%
# 再看下configuration里面的东西
import pymotion as pm
import inspect

cls = pm.lite.OdometryConfiguration  # 取别名

props = []
methods = []

for m in dir(cls):
    if m.startswith('_'):
        continue
    try:
        attr = inspect.getattr_static(cls, m)
    except Exception:
        continue

    kind = type(attr).__name__
    if 'function' in kind or 'method' in kind or callable(attr):
        methods.append(m)
    else:
        props.append(m)

print(f"===== 属性 ({len(props)}) =====")
for m in props:
    print(f"  {m}")

print(f"\n===== 方法 ({len(methods)}) =====")
for m in methods:
    print(f"  {m}()")
