#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaz (throttle) Topic Relay (GERCEK ARAC)
========================================
Aracin speed_pid_node'u gaz cikisini /beemobs/rcthrtdata'ya yayinlar
(smart_can_stuff/launch/pid_params.yaml: output_topic "/beemobs/rcthrtdata").
Aracin CAN koprusu (can_handler / ros2can) ise gaz komutunu
/beemobs/RC_THRT_DATA'dan (BUYUK harf) BEKLER. ROS2 topic isimleri
case-sensitive oldugu icin rcthrtdata != RC_THRT_DATA -> can_handler PID
ciktisini almaz, /to_can_bus'a Frame gitmez -> arac gaz vermez.

  /beemobs/rcthrtdata  (speed_pid_node ciktisi, Rcthrtdata)
        |
        v  [relay: sadece topic adini kopruler, icerik AYNEN gecer]
        |
  /beemobs/RC_THRT_DATA  --> can_handler subscribe --> /to_can_bus (CAN)

DOGRULANDI (2026-07-18, aracta): ros2 node info /can_handler ->
Subscribers'da /beemobs/RC_THRT_DATA var; ros2 topic info
/beemobs/rcthrtdata -v -> Publisher 1 (speed_pid) / Subscription 0.
Bu, feedback tarafindaki FB_VehicleSpeed->fbvehiclespeed tuzaginin
CIKIS tarafi ikizidir (bkz. speed_fb_relay.py). Kaynaktaki .cpp parola
korumali oldugu icin bu isim once yanlislikla "eslesir" varsayilmisti.

NEDEN RELAY: pid_params.yaml ve speed_pid_node/can_handler ARAC EKIBININ
dosyalaridir; onlara dokunmuyoruz. Relay tamamen bizim tarafta calisir.
odom_relay.py / gps_relay.py / speed_fb_relay.py ile ayni desen.

!! GUVENLIK: Bu relay + speed_fb_relay birlikte calisirken ve kontrol
node'u speed_target_value yayinlarken GAZ ZINCIRI TAMAMEN KAPANIR ve arac
gercekten hareket eder. En son, alan bosken, surucu frendeyken baslat.

KULLANIM (aracta, container icinde tmux'ta, CAN koprusu + PID calisirken):
  ros2 run bee1_description throttle_relay
  # Isimler farkli cikarsa:
  ros2 run bee1_description throttle_relay \
      --ros-args -p input_topic:=/beemobs/rcthrtdata \
                 -p output_topic:=/beemobs/RC_THRT_DATA

DOGRULA (relay calisirken):
  ros2 topic info /beemobs/RC_THRT_DATA -v   # Publisher 1 (relay) + Sub 1 (can_handler)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from smart_can_msgs.msg import Rcthrtdata


class ThrottleRelay(Node):
    def __init__(self):
        super().__init__('throttle_relay')

        self.declare_parameter('input_topic', '/beemobs/rcthrtdata')
        self.declare_parameter('output_topic', '/beemobs/RC_THRT_DATA')
        # speed_pid_node ciktisi ve can_handler aboneligi RELIABLE (07-18:
        # rcthrtdata publisher RELIABLE/VOLATILE goruldu) -> varsayilan reliable.
        self.declare_parameter('best_effort', False)

        self.in_topic = self.get_parameter('input_topic').value
        self.out_topic = self.get_parameter('output_topic').value
        best_effort = self.get_parameter('best_effort').value

        qos = QoSProfile(depth=10)
        if best_effort:
            qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self.pub = self.create_publisher(Rcthrtdata, self.out_topic, qos)
        self.sub = self.create_subscription(
            Rcthrtdata, self.in_topic, self._cb, qos)

        self._count = 0
        self.get_logger().info(
            f'Throttle relay: {self.in_topic} -> {self.out_topic} '
            f'(reliability={"best_effort" if best_effort else "reliable"})')

    def _cb(self, msg: Rcthrtdata):
        # Icerigi degistirmeden aynen yeniden yayinla
        self.pub.publish(msg)
        self._count += 1
        if self._count == 1:
            self.get_logger().info(
                f'Ilk gaz mesaji alindi ve {self.out_topic}\'e kopruleniyor.')


def main(args=None):
    rclpy.init(args=args)
    node = ThrottleRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
