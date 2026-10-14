#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""joystick_46'nin GERCEK ZED karelerini serit dugumunden gecirip ic terimleri olcer."""
import sys, os, sqlite3, struct, argparse, json
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--set", default="mevcut")
ap.add_argument("--n", type=int, default=204)
ap.add_argument("--atla", type=int, default=40)
ap.add_argument("--bag", default="/media/neuravix/T7/neuravix/joystick_46/joystick_46_0.db3")
ap.add_argument("--topic", default="/zed/zed_node/rgb/image_rect_color")
A = ap.parse_args()

AYAR = {
 "mevcut":   {},                                               # imajdaki hal
 "kapisiz":  {"cift_paralel_tol": 0.0},                        # paralellik kapisi KAPALI
 "yon0":     {"heading_gain": 0.0},                            # yon terimi yok
 "yon0_egim3": {"heading_gain": 0.0, "fit_max_slope": 3.0},    # onerilen
 "egim3":    {"fit_max_slope": 3.0},
 "noflip":   {"heading_no_flip": True},
 "yon0_egim3_kapisiz": {"heading_gain": 0.0, "fit_max_slope": 3.0, "cift_paralel_tol": 0.0},
}[A.set]

args = ["prog", "--ros-args", "-p", "show_window:=false",
        "-p", "publish_debug_image:=false", "-p", "publish_bev_image:=false"]
for k, v in AYAR.items():
    args += ["-p", f"{k}:={v}"]

import rclpy
rclpy.init(args=args)
sys.path.insert(0, "src/neuravix_ros2")
from neuravix_ros2.lane_follower_node import LaneFollowerNode

BAG = A.bag
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image as ImageMsg, CompressedImage
from cv_bridge import CvBridge
_br = CvBridge()

nd = LaneFollowerNode()
yayin = []
_orj = nd.pub.publish
nd.pub.publish = lambda m: yayin.append(m.data)

c = sqlite3.connect(f"file:{BAG}?mode=ro", uri=True)
tid = dict(c.execute("select name,id from topics"))[A.topic]
kayit = []
k = 0
for (d,) in c.execute("select data from messages where topic_id=? order by timestamp", (tid,)):
    if k % A.atla == 0:
        yayin.clear()
        if "compressed" in A.topic:
            cm = deserialize_message(d, CompressedImage)
            nd.cb(_br.cv2_to_imgmsg(_br.compressed_imgmsg_to_cv2(cm, "bgr8"), "bgr8"))
        else:
            nd.cb(deserialize_message(d, ImageMsg))
        kayit.append({
            "steer": float(yayin[-1].split(",")[1]) if yayin else None,
            "durum": yayin[-1].split(",")[4] if yayin and len(yayin[-1].split(","))>=5 else None,
            "lat":  float(nd._lat_err), "head": float(nd._head_err),
            "err":  float(nd._lat_err) + float(nd._head_err),
            "lanew": float(nd.lane_w_px) if nd.lane_w_px else None,
            "cift": bool(getattr(nd, "_cift_ok", False)),
        })
        if len(kayit) >= A.n: break
    k += 1
c.close()
print(json.dumps({"set": A.set, "ayar": AYAR,
                  "paralel_red": int(getattr(nd, "_paralel_red", 0)),
                  "cift_red": int(getattr(nd, "_cift_red", 0)),
                  "kayit": kayit}))
