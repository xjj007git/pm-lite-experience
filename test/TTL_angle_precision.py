import time
import statistics
import csv
from pathlib import Path
from datetime import datetime

import pymotion as pm

SERVO_ID = 1
ROUNDS = 10
DURATION = 1.5
SETTLE = 0.5
TOLERANCE = 1.0
SAMPLE_DT = 0.02

RESULT_DIR = Path(__file__).parent / "../results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

rows = []

with pm.lite.connect(transport="usb", auth_token="123456") as lite:

    # s = lite.status(max_age=2.0)
    # print(f"初始状态: {s.state}  fault={s.fault_latched}")
    # if s.state != "IDLE":
    #     raise RuntimeError(f"设备不在 IDLE: {s.state}")

    with lite.control():
        result = lite.ttl_servo.set_id(new_id=SERVO_ID) # 同时连接两个舵机不能进行id配置
        # print(result.id, result.max_angle)

        servo = lite.ttl_servo(SERVO_ID, mode="position")

        st = servo.status()
        print(f"ID={st.id}  online={st.online}  angle={st.angle:.2f}°  "
              f"max={servo.max_angle}°")
        if not st.online:
            raise RuntimeError("舵机离线")

        lo, hi = servo.max_angle * 0.1, servo.max_angle * 0.9
        TARGETS = [round(lo + (hi - lo) * i / 5, 1) for i in range(6)]
        print(f"测试角度: {TARGETS}\n")

        for rnd in range(1, ROUNDS + 1):
            for target in TARGETS:
                row = {
                    "test_id": "TTL角度精度测试", "round": rnd, "target_deg": target,
                    "measured_deg": None, "error_deg": None,
                    "max_dev_deg": None, "elapsed_s": None,
                    "n_samples": 0, "ok": False, "error_type": None,
                }

                ang_vals = []

                try:
                    t0 = time.monotonic()
                    servo.move_to(target, duration=DURATION)      # 不阻塞，立即返回

                    deadline = time.monotonic() + DURATION + 3.0    # 停止后继续采样3s
                    while time.monotonic() < deadline:
                        s_ = servo.status()
                        if s_.angle is not None:
                            ang_vals.append(s_.angle)
                        if not s_.moving:
                            break
                        time.sleep(SAMPLE_DT)

                    elapsed = time.monotonic() - t0
                    time.sleep(SETTLE)  # 稳定

                    # 最终状态
                    st = servo.status()
                    row["measured_deg"] = round(st.angle, 2)
                    row["error_deg"] = round(st.angle - target, 2)
                    row["elapsed_s"] = round(elapsed, 3)
                    row["n_samples"] = len(ang_vals)
                    row["ok"] = True

                    if ang_vals:
                        row["max_dev_deg"] = round(
                            max(ang_vals, key=lambda a: abs(a - target)), 2)

                    print(f"[{rnd:2d}/{ROUNDS}] {target:6.1f}° → "
                          f"{st.angle:7.2f}°  误差 {row['error_deg']:+6.2f}°  "
                          f"{elapsed:.2f}s  n={len(ang_vals)}")

                except Exception as e:
                    row["error_type"] = type(e).__name__
                    print(f"[{rnd:2d}/{ROUNDS}] {target:6.1f}° → "
                          f"失败: {type(e).__name__}: {e}")

                rows.append(row)
                if not row["ok"]:
                    print("出错，停止")
                    break

            if not rows[-1]["ok"]:
                break

        servo.stop()

if rows:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = RESULT_DIR / f"TTL舵机角度_{ts}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n已保存 {len(rows)} 行: {path.resolve()}")
