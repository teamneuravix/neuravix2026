#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEKERLEK ODOMETRISI -> odom->base_link TF
=========================================
Aracta hazir bir tekerlek odometrisi var: /odometry/can_wheel (nav_msgs/Odometry,
50 Hz, frame odom -> base_link, IMU yaw'i zaten fuzyonlanmis). Bu node onu
dogrudan TF'e cevirir; can_odom'un yerine gecer.

NEDEN (2026-08-20 olcumu, lokal_0820_* bag'leri):
  can_odom odometriyi CAN hizindan KENDI turetiyor. CAN hizi uint8 km/h
  cozunurlukte ve olculdu: kat edilen yolu %25 eksik veriyor. /odometry/can_wheel
  ayni mesafede %6-9 eksik.

    HAREKET HALINDEKI medyan hata    can_odom   /odometry/can_wheel
      lokal_0820_0719                  3.67 m         1.45 m
      lokal_0820_0722                  2.27 m         1.83 m

  Bu olcum GNSS'e hic dokunmuyor (gozetmen esigi gibi dairesel degil).

⚠️ TEK YAYINCI KURALI: odom->base_link'i ayni anda iki node surerse AMCL kacar
(2026-08-18'de olculdu: medyan hata 52 m). Bu yuzden launch, use_wheel_odom
true iken can_odom'u HIC baslatmaz.

⚠️ TOPIC YOKSA: bu node TF uretmez, AMCL'in odom->base_link'i hic olmaz ve
lokalizasyon calismaz. Sessizce olmemek icin ilk mesaji bekler ve gelmezse
duzenli araliklarla HATA basar. Temmuz bag'lerinde bu topic YOK -- eski bag'le
denerken use_wheel_odom:=false birak.
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros


class TekerlekOdomTF(Node):
    def __init__(self):
        super().__init__('tekerlek_odom_tf')
        self.declare_parameter('odom_topic', '/odometry/can_wheel')
        self.declare_parameter('uyari_saniye', 5.0)
        top = self.get_parameter('odom_topic').value
        self.uyari = float(self.get_parameter('uyari_saniye').value)

        self.br = tf2_ros.TransformBroadcaster(self)
        self.n = 0
        self.create_subscription(Odometry, top, self.cb, 50)
        self.create_timer(self.uyari, self.denetle)
        self.get_logger().info(f'tekerlek_odom_tf: {top} -> TF odom->base_link')

    def cb(self, m):
        t = TransformStamped()
        t.header = m.header
        t.header.frame_id = m.header.frame_id or 'odom'
        t.child_frame_id = m.child_frame_id or 'base_link'
        t.transform.translation.x = m.pose.pose.position.x
        t.transform.translation.y = m.pose.pose.position.y
        t.transform.translation.z = 0.0
        t.transform.rotation = m.pose.pose.orientation
        self.br.sendTransform(t)
        self.n += 1

    def denetle(self):
        # Sessiz olum en tehlikeli hata: TF hic uretilmezse AMCL calismaz ama
        # kimse fark etmez. Yuksek sesle sikayet et.
        if self.n == 0:
            self.get_logger().error(
                f"{self.uyari:.0f} s'dir tekerlek odometrisi GELMEDI -- odom->base_link TF "
                "URETILMIYOR, AMCL calismaz. Topic akiyor mu bak; akmiyorsa "
                "use_wheel_odom:=false ile can_odom'a don.")


def main():
    rclpy.init()
    n = TekerlekOdomTF()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    except rclpy.executors.ExternalShutdownException:
        pass
    finally:
        n.destroy_node(); rclpy.ok() and rclpy.shutdown()


if __name__ == '__main__':
    main()
