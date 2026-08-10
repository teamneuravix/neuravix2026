#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hiz Geri Besleme Topic Relay (GERCEK ARAC)
==========================================
Aracin CAN koprusu (smart_can_stuff/can2ros) hiz feedback'ini
/beemobs/FB_VehicleSpeed olarak yayinlar (canli, 07-13'te iki kez echo'landi).
Aracin kendi speed_pid_node'u ise feedback'i /beemobs/fbvehiclespeed'den
BEKLER (smart_can_stuff/launch/pid_params.yaml: feedback_value_topic:
"/beemobs/fbvehiclespeed"). Isimler tutmadigi icin PID feedback alamaz,
/beemobs/rcthrtdata (gaz) uretmez -> arac gaz vermez.

  /beemobs/FB_VehicleSpeed  (can2ros yayini, Fbvehiclespeed)
        |
        v  [relay: sadece topic adini kopruler, icerik AYNEN gecer]
        |
  /beemobs/fbvehiclespeed  --> speed_pid_node feedback girdisi

NEDEN RELAY (pid_params.yaml duzenlemek yerine): pid_params.yaml ve
speed_pid_node ARAC EKIBININ dosyasidir; ona dokunmuyoruz. Relay tamamen
bizim tarafta calisir, onlarin config'ine sifir dokunus. odom_relay.py /
gps_relay.py ile ayni desen (sadece isim kopruleme).

DUZELTME (2026-07-18, aracta): Ayni isim tuzagi CIKIS tarafinda da VAR ->
speed_pid_node /beemobs/rcthrtdata basar, can_handler /beemobs/RC_THRT_DATA
bekler (ros2 node info /can_handler ile dogrulandi). Onceki "cikis tarafinda
yok" varsayimi YANLISTI (kaynaktaki .cpp parola korumaliydi). Cikis halkasi
throttle_relay.py ile kapatilir. Heartbeat (AutonomousHeardBit) ise gercekten
arac->biz yonunde (can2ros publisher'i), gonderilecek bir enable degil. Bu
relay sadece speed-feedback (giris) halkasini kapatir.

KULLANIM (araCta, container icinde tmux'ta, CAN koprusu calisirken):
  ros2 run bee1_description speed_fb_relay
  # Isimler farkli cikarsa:
  ros2 run bee1_description speed_fb_relay \
      --ros-args -p input_topic:=/beemobs/FB_VehicleSpeed \
                 -p output_topic:=/beemobs/fbvehiclespeed

ONCE DOGRULA:
  ros2 topic info /beemobs/fbvehiclespeed -v   # 0 publisher ise relay gerekli
  ros2 topic info /beemobs/FB_VehicleSpeed -v  # 1 publisher (can2ros) + QoS
Kaynak topic best_effort cikarsa: -p best_effort:=true
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from smart_can_msgs.msg import Fbvehiclespeed


class SpeedFbRelay(Node):
    def __init__(self):
        super().__init__('speed_fb_relay')

        self.declare_parameter('input_topic', '/beemobs/FB_VehicleSpeed')
        self.declare_parameter('output_topic', '/beemobs/fbvehiclespeed')
        # can2ros feedback'i reliable yayinlar (can_odom_node default reliable
        # QoS ile okuyup calisiyor) -> varsayilan reliable. Arac tarafi
        # best-effort'a gecerse -p best_effort:=true ile abonelik eslesir.
        self.declare_parameter('best_effort', False)

        self.in_topic = self.get_parameter('input_topic').value
        self.out_topic = self.get_parameter('output_topic').value
        best_effort = self.get_parameter('best_effort').value

        qos = QoSProfile(depth=10)
        if best_effort:
            qos.reliability = ReliabilityPolicy.BEST_EFFORT

        # Cikis: PID'in bekledigi topic. PID aboneligiyle eslessin diye
        # yayin da ayni QoS ile yapilir.
        self.pub = self.create_publisher(Fbvehiclespeed, self.out_topic, qos)
        self.sub = self.create_subscription(
            Fbvehiclespeed, self.in_topic, self._cb, qos)

        self._count = 0
        self.get_logger().info(
            f'Speed feedback relay: {self.in_topic} -> {self.out_topic} '
            f'(reliability={"best_effort" if best_effort else "reliable"})')

    def _cb(self, msg: Fbvehiclespeed):
        # Icerigi degistirmeden aynen yeniden yayinla
        self.pub.publish(msg)
        self._count += 1
        if self._count == 1:
            self.get_logger().info(
                f'Ilk mesaj alindi ve {self.out_topic}\'e kopruleniyor.')


def main(args=None):
    rclpy.init(args=args)
    node = SpeedFbRelay()
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
