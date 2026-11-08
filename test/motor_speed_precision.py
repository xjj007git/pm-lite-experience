import time
import statistics
import csv
from datetime import datetime
from pathlib import Path

import pymotion as pm

PORT = 1
TARGETS = [10,40,80,200,280,360]
SETTLE_S = 2.0
MEASURE_S = 30.0
SAMPLE_HZ = 10
ROUNDS = 3

rows = []

with pm.lite.connect(transport="usb", auth_token="123456") as lite:
    with lite.control():
        m = lite.motor(PORT)

        for rnd in range(1, ROUNDS + 1):
            for target in TARGETS:
                print(f"第{rnd}轮  目标{target}RPM", end="  ", flush=True)

                m.set_speed(target)
                time.sleep(SETTLE_S)          # 等稳定

                samples = []
                t0 = time.monotonic()
                while time.monotonic() - t0 < MEASURE_S:
                    s = m.status(max_age=0.5)
                    if s.measured_rpm is not None:
                        samples.append(s.measured_rpm)
                    else:
                        # print("数据无效")
                        print(f"mode={s.control_mode}")
                        print(f"has_enc={s.has_encoder}")
                        print(f"feedback_valid是{s.feedback_valid}")    #用于位置反馈控制
                        print(f"running={s.running}")

                        print(f"count={s.encoder_count:8d}")
                        print(f"measured_rpm是{s.measured_rpm}\n")



                    time.sleep(1.0 / SAMPLE_HZ)

                m.stop()
                time.sleep(0.5)               # 间隔，避免上轮残留

                row = {
                    "test_id": "电机低速精度",
                    "round": rnd,
                    "target_rpm": target,
                    "采样数n": len(samples),
                    "mean_rpm": statistics.mean(samples) if samples else None,
                    "std_rpm": statistics.stdev(samples) if len(samples) > 1 else None,
                    "max_rpm": max(samples) if samples else None,
                    "min_rpm": min(samples) if samples else None,
                    "error_pct": None,
                    "是否饱和saturated": s.output_saturated,
                    "feedback_valid": s.feedback_valid,
                }
                if row["mean_rpm"] is not None:
                    row["error_pct"] = (row["mean_rpm"] - target) / target * 100

                rows.append(row)
                print(f"均值 {row['mean_rpm']:.2f} RPM  误差 {row['error_pct']:+.1f}%")

ts = datetime.now().strftime("%Y-%m-%d_%H%M")
path = Path(f"../results/电机低速精度_{ts}.csv")   # 按实际路径调整
path.parent.mkdir(parents=True, exist_ok=True) 
with open(path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("已保存:", path)
