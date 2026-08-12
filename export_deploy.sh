#!/usr/bin/env bash
# Bu script'in amacı: gerçek araca giden Docker image'ının kaynağını
# (~/robotaksi_deploy/src) bu workspace'in src/'inden GÜNCEL tutmak.
#
# Neden var: daha önce ~/robotaksi_deploy elle kopyalanmış ve 7 Temmuz'da
# kalmıştı (decision_brain.py, neuravix_control_node_real.py yoktu). Bu
# script'i her Docker image build etmeden ÖNCE çalıştırarak o sorunu önler.
#
# Kullanım:
#   ./export_deploy.sh          # gerçekten kopyalar
#   ./export_deploy.sh --dry-run  # sadece ne değişecek gösterir, kopyalamaz
set -euo pipefail
WS_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/src"
DEPLOY_SRC="$HOME/robotaksi_deploy/src"
# Yarış günü gerçek araca giden paketler (bkz. CLAUDE.md "Path to real hardware").
# bee1_description 2026-07-10'da eklendi: gerçek lokalizasyon zinciri
# (can_odom rev3 + pist_slam_real / pist_localization_real launch'ları).
# Dockerfile'a gerekli apt paketleri de aynı gün eklendi (xacro,
# robot_state_publisher, joint_state_publisher, tf2_ros, slam_toolbox,
# pointcloud_to_laserscan, sensor_msgs_py).
# NOT: bee1_description KOMPLE kopyalanıyor (CARLA-only script'ler dahil)
# çünkü setup.py entry_points o dosyalara işaret ediyor; dışlamak kırık
# entry point üretir. Araçta sadece can_odom / lidar_echo çalıştırılır.
PACKAGES=(neuravix_ros2 smart_can_msgs bee1_description)
RSYNC_FLAGS=(-a --delete
  --exclude 'build/' --exclude 'install/' --exclude 'log/'
  --exclude '__pycache__/' --exclude '.pytest_cache/')
if [[ "${1:-}" == "--dry-run" ]]; then
  RSYNC_FLAGS+=(--dry-run -v)
  echo "== KURU ÇALIŞTIRMA: hiçbir şey kopyalanmayacak, sadece önizleme =="
fi
echo "Kaynak : $WS_SRC"
echo "Hedef  : $DEPLOY_SRC"
echo
mkdir -p "$DEPLOY_SRC"
for pkg in "${PACKAGES[@]}"; do
  echo ">>> $pkg"
  rsync "${RSYNC_FLAGS[@]}" "$WS_SRC/$pkg/" "$DEPLOY_SRC/$pkg/"
  echo
done
if [[ "${1:-}" != "--dry-run" ]]; then
  echo "Bitti. Şimdi image'ı yeniden build edin:"
  echo "  cd ~/robotaksi_deploy && docker build -t robotaksi_humble:latest ."
fi
