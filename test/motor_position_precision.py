import time
import statistics
import csv
import threading
from pathlib import Path
from datetime import datetime

import pymotion as pm

PORT = 1
TARGETS = [0, 90, 180, 270, 360]
ROUNDS = 20                # 每个角度 20 次
SPEED = 80                  # 不要用默认 20，力矩不够会 stall
TIMEOUT = 20.0
SETTLE = 0.8                # move_to 返回后再等，让反馈稳定
TOLERANCE = 2.0             # 判据

RESULT_DIR = Path(__file__).parent / "../results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

rows = []

with pm.lite.connect(transport="usb", auth_token="123456") as lite:

    # s = lite.status(max_age=2.0)
    # print(f"初始状态: {s.state}  fault={s.fault_latched}")
    # if s.state != "IDLE":
    #     raise RuntimeError(f"设备不在 IDLE 状态: {s.state}")

    with lite.control():
        m = lite.motor(PORT)

        # 建零点
        m.stop()
        time.sleep(1.5)
        if m.status(max_age=0.5).running:
            raise RuntimeError("电机未停稳，无法建立零点")
        m.zero_position()
        time.sleep(0.8)

        s = m.status(max_age=1.0)
        print(f"零点后: zeroed={s.zeroed}  valid={s.feedback_valid}  angle={s.measured_angle}")
        if not s.feedback_valid:
            print("feedback_valid=False,位置反馈可能不可用,可能需要额外开一个线程")

        for rnd in range(1, ROUNDS + 1):
            for target in TARGETS:
                row = {
                    "test_id": "电机位控精度",
                    "round": rnd,
                    "target_deg": target,
                    "measured_deg": None,
                    "error_deg": None,
                    "elapsed_s": None,
                    "final_deg": None,
                    "peak_deg": None,
                    "overshoot_deg": None,          
                    "n_samples": 0,
                    "fv_true_ratio": None,
                    "ok": False,
                    "error_type": None,
                }

                # ---- 每轮开一个采集线程 ----
                samples = []
                stop_flag = threading.Event()

                def collect():
                    t0 = time.monotonic()
                    while not stop_flag.is_set():
                        try:
                            st = m.status(max_age=0.5)
                            samples.append((
                                time.monotonic() - t0,
                                st.measured_angle,
                                st.measured_rpm,
                                st.feedback_valid,
                            ))
                        except Exception:
                            pass
                        time.sleep(0.02)      # 50 Hz

                th = threading.Thread(target=collect, daemon=True)
                th.start()
                time.sleep(0.2)               # 采一小段基线

                try:
                    t0 = time.monotonic()
                    m.move_to(target, speed=SPEED, timeout=TIMEOUT)
                    elapsed = time.monotonic() - t0

                    time.sleep(SETTLE)        # 到位后等反馈稳定
                    st = m.status(max_age=1.0)

                    # row["measured_deg"] = st.measured_angle     
                    # row["feedback_valid"] = st.feedback_valid   
                    print(f"电机停下来以后的fv是{st.feedback_valid}")
                    print(f"电机停下来以后的deg是{st.measured_angle}")  # 这里是看得到值得 所以电机的fv和measured_angle只有在切换成速度是才无效吗
                    row["elapsed_s"] = round(elapsed, 3)
                    row["ok"] = True

                except Exception as e:
                    row["error_type"] = type(e).__name__
                    print(f"[{rnd:2d}/{ROUNDS}] {target:4d}° → 失败: {type(e).__name__}: {e}")

                finally:
                    stop_flag.set()
                    th.join(timeout=3.0)

                # ---- 从采集数据里补统计 ----  从samples来的都是线程采到的 但是线程开着的时候并不意味着在执行move_to 线程显然包含了move_to全程
                row["n_samples"] = len(samples)
                ang_vals = [x[1] for x in samples if x[1] is not None]  # x[1]是测量角度
                fv_vals = [x[3] for x in samples]   # x[3]是feedback_valid
                if ang_vals:
                    row["final_deg"] = round(ang_vals[-1], 2)
                    peak = max(ang_vals)
                    row["peak_deg"] = round(peak, 2)
                    row["overshoot_deg"] = max(0, peak - target)
                    row["measured_deg"] = round(ang_vals[-1], 2)     # 最后一次有效角度
                    row["error_deg"] = round(ang_vals[-1] - target, 2)

                    row["fv_true_ratio"] = round(sum(fv_vals) / len(fv_vals), 3) if fv_vals else None

                rows.append(row)

                if row["ok"]:
                    meas = row["measured_deg"]
                    if meas is not None:
                        print(f"[{rnd:2d}/{ROUNDS}] {target:4d}° → "
                              f"{meas:8.2f}°  误差 {row['error_deg']:+6.2f}°  "
                              f"峰值 {row['peak_deg']}  {row['elapsed_s']}s  "
                              f"n={row['n_samples']}")
                    else:
                        print(f"[{rnd:2d}/{ROUNDS}] {target:4d}° → "
                              f"angle=None  {row['elapsed_s']}s  n={row['n_samples']}")

                if not row["ok"]:
                    print("出现错误，停止测试")
                    break

            if not rows[-1]["ok"]:
                break

        m.stop()

if rows:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = RESULT_DIR / f"电机位置精度_{ts}.csv"

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\n已保存 {len(rows)} 行: {path.resolve()}")
else:
    print("没有数据可保存")
