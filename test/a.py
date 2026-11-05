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
import pymotion as pm

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    reading = lite.ultrasonic()
    print("valid:  ", reading.valid)
    print("state:  ", reading.state)
    print("age:    ", reading.age)
    print("distance:", reading.distance)



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