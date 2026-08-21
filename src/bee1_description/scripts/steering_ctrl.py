#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DİREKSİYON KONTROLCÜSÜ (GERÇEK ARAÇ) — aracın steering_pid_node'unun YERİNE.
==========================================================================
NEDEN: Aracın kendi steering PID'i TEK YÖNLÜ. pid_params.yaml'da
`min_output: 0` olduğu için NEGATİF hatada çıkış 0'a saturе oluyor,
`pwm=0` ise motoru KAPATIYOR -> tekerlek serbest kalıp kayıyor ve PID onu
geri getiremiyor. 2026-07-20 bag kanıtı (debug_control): hedef sabit -2.30
iken feedback 3 -> 25'e kaçtı, 1700 örnekte pwm=0. Araç sürekli sağa kırıyordu.

ÇÖZÜLEN PWM SEMANTİĞİ (2026-07-20, semantik_1 bag'i):
    en=1  -> motor AKTIF   (en=0 ve en=2 -> motor OLU, hic hareket yok)
    pwm=0     -> motor KAPALI (serbest, tutmaz)
    pwm<127   -> feedback AZALIR  (fiziksel SOL)      orn. 100: -9 / 17s
    pwm>127   -> feedback ARTAR   (fiziksel SAG)      orn. 150: +9 / 12.6s
                                                      255: +22 / 19s (en hizli)
    => merkez ~127, merkeze uzaklik = donme hizi, olu bolge dar (~Delta 20-25 hareket ettiriyor)

BU NODE: /beemobs/steering_target_value (ham FeedbackSteeringAngle birimi) +
/beemobs/FeedbackSteeringAngle geri beslemesi -> /beemobs/AUTONOMOUS_SteeringMot_Control
CIFT YONLU P kontrol. Hedefe varinca pwm=0 (motor kapali, mekanik tutar).

KULLANIM (aracin kendi PID'i KAPALI olmali!):
  pkill -9 -f steering_pid_node
  ros2 run bee1_description steering_ctrl
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from smart_can_msgs.msg import Autonomoussteeringmotcontrol, Feedbacksteeringangle


class SteeringCtrl(Node):
    def __init__(self):
        super().__init__('steering_ctrl')
        # --- olculen semantik (semantik_1) ---
        self.declare_parameter('pwm_center', 127)     # notr
        self.declare_parameter('min_drive', 22.0)     # olu bolgeyi asmak icin min sapma
        self.declare_parameter('kp', 3.0)             # pwm sapmasi / birim hata
        self.declare_parameter('max_delta', 68.0)     # merkezden max sapma (hiz siniri)
        self.declare_parameter('tolerance', 1.0)      # +-bu kadar hata -> motor kapali
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('target_timeout', 0.5)

        gp = lambda n: self.get_parameter(n).get_parameter_value()
        self.center = gp('pwm_center').integer_value
        self.min_drive = gp('min_drive').double_value
        self.kp = gp('kp').double_value
        self.max_delta = gp('max_delta').double_value
        self.tol = gp('tolerance').double_value
        self.timeout = gp('target_timeout').double_value
        rate = gp('rate_hz').double_value

        self.target = None
        self.fb = None
        self._last_target_t = None

        self.pub = self.create_publisher(
            Autonomoussteeringmotcontrol, '/beemobs/AUTONOMOUS_SteeringMot_Control', 10)
        self.create_subscription(Float64, '/beemobs/steering_target_value',
                                 self._target_cb, 10)
        self.create_subscription(Feedbacksteeringangle, '/beemobs/FeedbackSteeringAngle',
                                 self._fb_cb, 10)
        self.timer = self.create_timer(1.0 / rate, self._loop)
        # CALISIRKEN AYAR (20.08.2026). Parametreler acilista BIR KEZ okunup
        # instance degiskenine yaziliyordu; `ros2 param set max_delta 110`
        # parametre sunucusunu guncelliyor ama kontrolcu eski degerle
        # calismaya devam ediyordu — yani "110'u denedim" diye kaydedilen bir
        # kosu aslinda 68 ile kosmus olurdu. (Ayni tuzak lane_follower'in
        # err_offset'inde de var, orada dokumante edilmis.)
        self.add_on_set_parameters_callback(self._on_params)
        self.get_logger().info(
            f"Steering ctrl (aracin steering PID'i YERINE): merkez={self.center}, "
            f"min_drive={self.min_drive:.0f}, kp={self.kp:.1f}, max_delta={self.max_delta:.0f}, "
            f"tol={self.tol:.1f}, {rate:.0f}Hz  [pwm>127=SAG, <127=SOL, 0=kapali]")

    def _on_params(self, params):
        """Bilinen parametreleri calisirken guncelle.

        Bilinmeyen isimler DOKUNULMADAN kabul edilir (use_sim_time gibi altyapi
        parametreleri reddedilirse launch/param gecisi kirilir — obstacle_lidar'da
        tam bu hata yasandi ve CLAUDE.md'de kayitli)."""
        from rcl_interfaces.msg import SetParametersResult
        ALAN = {'pwm_center': ('center', int), 'min_drive': ('min_drive', float),
                'kp': ('kp', float), 'max_delta': ('max_delta', float),
                'tolerance': ('tol', float), 'target_timeout': ('timeout', float)}
        for pr in params:
            if pr.name not in ALAN:
                continue
            alan, tip = ALAN[pr.name]
            try:
                d = tip(pr.value)
            except (TypeError, ValueError):
                return SetParametersResult(
                    successful=False, reason=f"{pr.name}: sayi olmali")
            if pr.name == 'max_delta' and not (0.0 < d <= 127.0):
                return SetParametersResult(
                    successful=False,
                    reason="max_delta 0..127 olmali (pwm merkezi 127)")
            if pr.name in ('min_drive', 'tolerance') and d < 0.0:
                return SetParametersResult(
                    successful=False, reason=f"{pr.name} negatif olamaz")
            setattr(self, alan, d)
            self.get_logger().info(f"{pr.name} -> {d}")
        return SetParametersResult(successful=True)

    def _target_cb(self, msg):
        self.target = float(msg.data)
        self._last_target_t = self.get_clock().now()

    def _fb_cb(self, msg):
        self.fb = float(msg.feedbacksteeringangle)

    def _loop(self):
        now = self.get_clock().now()
        stale = (self._last_target_t is None or
                 (now - self._last_target_t).nanoseconds * 1e-9 > self.timeout)
        if stale or self.target is None or self.fb is None:
            self._publish(0)           # veri yok -> motor kapali (guvenli)
            return

        err = self.target - self.fb    # + => feedback ARTMALI => pwm > center (SAG)
        if abs(err) <= self.tol:
            self._publish(0)           # hedefteyiz -> motoru birak (mekanik tutar)
            return

        delta = self.min_drive + self.kp * (abs(err) - self.tol)
        delta = min(self.max_delta, delta)
        pwm = self.center + (delta if err > 0 else -delta)
        self._publish(int(max(1, min(255, pwm))))   # 0 = kapali oldugu icin alt sinir 1

    def _publish(self, pwm):
        m = Autonomoussteeringmotcontrol()
        m.autonomous_steeringmot_en = 1      # 0 ve 2 motoru olduruyor
        m.autonomous_steeringmot_pwm = int(pwm)
        self.pub.publish(m)


def main(args=None):
    rclpy.init(args=args)
    node = SteeringCtrl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node._publish(0)           # cikarken motoru kapat
        except Exception:
            pass
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
