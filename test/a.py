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
# 2.位控具有阻塞性——穿行的必然性 执行完才执行下一条 stop和set_pwm不可中断
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
# 看一下位控的theta-t曲线
import time
import pymotion as pm
import matplotlib.pyplot as plt

THETA = 3600
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
        m.move_to(THETA, speed=SPEED, timeout=20.0)    # angle范围是(-3600,3600)
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