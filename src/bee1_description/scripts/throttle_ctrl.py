#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GAZ KONTROLCÜSÜ (GERÇEK ARAÇ) — aracın speed_pid_node'unun YERİNE geçer.
================================================================
NEDEN: Aracın kendi speed PID'i (smart_can_stuff) anti-windup'sız (ki=1.0).
2026-07-20 bag analizi: araç dururken integral şişip pedalı **255 (tam gaz)**
yapıyor, araç 1.5 sn'de 0->10 km/h fırlıyordu. Kullanılamaz.

BU NODE: /beemobs/speed_target_value (km/h) + /beemobs/FB_VehicleSpeed geri
beslemesi -> /beemobs/RC_THRT_DATA (pedal). İleri-besleme AĞIRLIKLI, küçük P/I
ve SIKI anti-windup ile.

ÖLÇÜLEN PEDAL->HIZ MODELİ (2026-07-20, semantik_6 bag'i, DRIVE viteste):
    pedal 60 -> 2 km/h (rpm 23)
    pedal 80 -> 5 km/h (rpm 53)
    => egim ~0.15 km/h / birim  =>  1/egim ~6.67 birim / (km/h)
    => olu bolge (hiz=0) ~47   (bu yuzden pedal<=40'ta arac HIC kimildamadi)
İleri-besleme:  pedal = 47 + 6.67 * hedef_kmh
Dogrulama: hedef 2 -> 60.3 ✓   hedef 5 -> 80.3 ✓
Surucu notu: 60 "guzel kalkis", 80 "bir tik hizli" -> ideal 65-70 (~3 km/h).

KULLANIM (aracin kendi PID'i KAPALI olmali!):
  pkill -9 -f speed_pid_node
  ros2 run bee1_description throttle_ctrl
  # daha yavas/hizli tavan:  -p max_pedal:=75

!! GUVENLIK: bu node gaz verir. max_pedal varsayilan 85 (~5.7 km/h) ile
   sinirli. Hedef 0 veya fren -> pedal 0 (aninda).
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from smart_can_msgs.msg import Rcthrtdata, Fbvehiclespeed


class ThrottleCtrl(Node):
    def __init__(self):
        super().__init__('throttle_ctrl')
        # --- olculen model (semantik_6) ---
        self.declare_parameter('pedal_deadband', 47.0)   # hiz=0 esigi
        self.declare_parameter('pedal_per_kmh', 6.67)    # 1/egim
        # --- geri besleme duzeltmesi (ileri-besleme agirlikli, kucuk tut) ---
        self.declare_parameter('kp', 3.0)                # pedal / (km/h hata)
        self.declare_parameter('ki', 0.5)
        self.declare_parameter('i_max', 10.0)            # ANTI-WINDUP: I katkisi tavani
        # --- guvenlik ---
        self.declare_parameter('max_pedal', 85.0)        # ~5.7 km/h
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('target_timeout', 0.5)    # hedef bayatsa gaz kes
        self.declare_parameter('speed_topic', '/beemobs/FB_VehicleSpeed')

        gp = lambda n: self.get_parameter(n).get_parameter_value()
        self.db = gp('pedal_deadband').double_value
        self.ppk = gp('pedal_per_kmh').double_value
        self.kp = gp('kp').double_value
        self.ki = gp('ki').double_value
        self.i_max = gp('i_max').double_value
        self.max_pedal = gp('max_pedal').double_value
        self.timeout = gp('target_timeout').double_value
        rate = gp('rate_hz').double_value

        self.target = 0.0
        self.speed = 0.0
        self.integral = 0.0
        self._last_target_t = None

        self.pub = self.create_publisher(Rcthrtdata, '/beemobs/RC_THRT_DATA', 10)
        self.create_subscription(Float64, '/beemobs/speed_target_value',
                                 self._target_cb, 10)
        self.create_subscription(Fbvehiclespeed, gp('speed_topic').string_value,
                                 self._speed_cb, 10)
        self.timer = self.create_timer(1.0 / rate, self._loop)
        self.get_logger().info(
            f"Throttle ctrl (aracin speed PID'i YERINE): pedal = {self.db:.0f} + "
            f"{self.ppk:.2f}*hedef_kmh + P/I, max_pedal={self.max_pedal:.0f}, {rate:.0f}Hz")

    def _target_cb(self, msg):
        self.target = float(msg.data)
        self._last_target_t = self.get_clock().now()

    def _speed_cb(self, msg):
        self.speed = float(msg.fb_reelvehiclespeed_kmh)

    def _loop(self):
        now = self.get_clock().now()
        stale = (self._last_target_t is None or
                 (now - self._last_target_t).nanoseconds * 1e-9 > self.timeout)
        # Hedef yok/bayat ya da ~0 -> gaz KES, integrali sifirla
        if stale or self.target <= 0.05:
            self.integral = 0.0
            self._publish(0)
            return

        err = self.target - self.speed
        # ANTI-WINDUP: integrali sinirli tut (aracin PID'inin yapmadigi sey)
        self.integral += err * 0.05
        lim = self.i_max / self.ki if self.ki > 0 else 0.0
        self.integral = max(-lim, min(lim, self.integral))

        pedal = self.db + self.ppk * self.target + self.kp * err + self.ki * self.integral
        # Doyma varsa integrali daha fazla sisirme (ek anti-windup)
        if pedal > self.max_pedal or pedal < 0.0:
            self.integral -= err * 0.05
        self._publish(int(max(0.0, min(self.max_pedal, pedal))))

    def _publish(self, pedal):
        m = Rcthrtdata()
        m.rc_thrt_pedal_position = int(pedal)
        m.rc_thrt_pedal_press = 0      # 2026-07-20: arac press=0 ile hareket etti
        self.pub.publish(m)


def main(args=None):
    rclpy.init(args=args)
    node = ThrottleCtrl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node._publish(0)           # cikarken gazi kes
        except Exception:
            pass
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
