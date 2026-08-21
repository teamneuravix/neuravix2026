#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MJPEG goruntu sunucusu — monitorsuz sahada goruntuyu LAPTOP TARAYICISINDAN
izlemek icin. Laptopta ROS/RViz/kurulum GEREKMEZ; sadece tarayici yeter.

Node'larimiz zaten sikistirilmis (JPEG) debug goruntusu yayinliyor:
  /neuravix/lane_debug/compressed    (lane_follower)
  /neuravix/tabela_debug/compressed  (tabela_tespit)
Bu script o JPEG'leri oldugu gibi bir HTTP MJPEG akisina cevirir.

KULLANIM (konteyner icinde, --network host oldugu icin port disari acik):
  ros2 run neuravix_ros2 mjpeg_server --ros-args \
      -p topic:=/neuravix/lane_debug/compressed -p port:=8081
  # ikinci goruntu icin ayri terminalde:
  ros2 run neuravix_ros2 mjpeg_server --ros-args \
      -p topic:=/neuravix/tabela_debug/compressed -p port:=8082

LAPTOPTA tarayiciya yaz:
  http://192.168.30.100:8081     (rb1)  /  http://192.168.10.100:8081  (rb2)

NOT: Ham (sikistirilmamis) Image topigi izlemek icin raw:=true verin
(orn. ZED'in kendisi: -p topic:=/zed/zed_node/rgb/image_rect_color
 -p raw:=true) — bu modda cv2 ile JPEG'e cevrilir, biraz daha CPU yer.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image

_BOUNDARY = "neuravixframe"

_INDEX_HTML = ("<html><head><title>NeuraVix Canli Goruntu</title></head>"
               "<body style='margin:0;background:#111;text-align:center'>"
               "<img src='/stream' style='max-width:100%;height:auto'/>"
               "</body></html>")


class _Shared:
    def __init__(self):
        self.cond = threading.Condition()
        self.jpeg = None
        self.seq = 0

    def put(self, data: bytes):
        with self.cond:
            self.jpeg = data
            self.seq += 1
            self.cond.notify_all()


SHARED = _Shared()


class MjpegNode(Node):
    def __init__(self):
        super().__init__('mjpeg_server')
        self.declare_parameter('topic', '/neuravix/lane_debug/compressed')
        self.declare_parameter('port', 8081)
        self.declare_parameter('raw', False)

        self.topic = self.get_parameter('topic').value
        self.port = int(self.get_parameter('port').value)
        self.raw = bool(self.get_parameter('raw').value)

        # sensor_data QoS (best-effort): raw modda ZED gibi gercek suruculer
        # best-effort yayinlar; reliable abonelik onlarla HIC eslesmez
        # (sessizce goruntu gelmez). Best-effort abonelik bizim reliable
        # debug publisher'larimizla da eslesir — iki mod icin de guvenli.
        if self.raw:
            import cv2  # sadece raw modda gerekli
            import numpy as np
            self._cv2, self._np = cv2, np
            self.sub = self.create_subscription(
                Image, self.topic, self._raw_cb, qos_profile_sensor_data)
        else:
            self.sub = self.create_subscription(
                CompressedImage, self.topic, self._jpeg_cb,
                qos_profile_sensor_data)

        self.get_logger().info(
            f"MJPEG sunucu: {self.topic} -> http://<arac_ip>:{self.port}  "
            f"(raw={self.raw})")

    def _jpeg_cb(self, msg: CompressedImage):
        SHARED.put(bytes(msg.data))

    def _raw_cb(self, msg: Image):
        np, cv2 = self._np, self._cv2
        # msg.step uzerinden satir satir oku: bazi suruculer satir sonuna
        # dolgu (padding) koyar; duz reshape(h, w, ch) o durumda patlar.
        buf = np.frombuffer(bytes(msg.data), dtype=np.uint8)
        step = msg.step if msg.step > 0 else len(msg.data) // max(1, msg.height)
        ch = max(1, step // max(1, msg.width))
        img = (buf[:msg.height * step]
               .reshape(msg.height, step)[:, :msg.width * ch]
               .reshape(msg.height, msg.width, ch))
        enc = msg.encoding.lower()
        if enc in ('rgb8',):
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif enc in ('rgba8',):
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif enc in ('bgra8',):
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        ok, jpg = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ok:
            SHARED.put(jpg.tobytes())


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # istek loglariyla terminali kirletme
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            body = _INDEX_HTML.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path != '/stream':
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Age', '0')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Type',
                         f'multipart/x-mixed-replace; boundary={_BOUNDARY}')
        self.end_headers()
        last_seq = -1
        try:
            while True:
                with SHARED.cond:
                    SHARED.cond.wait_for(lambda: SHARED.seq != last_seq,
                                         timeout=5.0)
                    frame = SHARED.jpeg
                    last_seq = SHARED.seq
                if frame is None:
                    continue
                self.wfile.write(
                    (f"--{_BOUNDARY}\r\nContent-Type: image/jpeg\r\n"
                     f"Content-Length: {len(frame)}\r\n\r\n").encode())
                self.wfile.write(frame)
                self.wfile.write(b"\r\n")
        except (BrokenPipeError, ConnectionResetError):
            pass  # tarayici kapandi — normal


def main(args=None):
    rclpy.init(args=args)
    node = MjpegNode()
    server = ThreadingHTTPServer(('0.0.0.0', node.port), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
