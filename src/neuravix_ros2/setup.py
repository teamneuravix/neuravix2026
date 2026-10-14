from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'neuravix_ros2' # DIŞTAKİ KLASÖR ADI


setup(
    name=package_name,
    version='0.0.0',
    # Bu tanım, src/neuravix_ros2 içindeki neuravix_ros2 Python modülünü kesin olarak bulmalıdır.
    #packages=find_packages(include=[package_name, package_name + '.*']), 
    packages=[package_name], # Sadece ana paketi listeye ekleyin

    data_files=[
        # AMENT Resource dosyası
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # package.xml dosyası
        ('share/' + package_name, ['package.xml']),
        
        # Model dosyalarını kurulum dizinine kopyalar
        (os.path.join('share', package_name, 'models'), glob('models/*.pt')),
        
        (os.path.join('share', package_name, 'tabela'), glob('tabela/*.png') + glob('tabela/*.json')),

        # route_planner veri dosyalari (graf / GNSS datum / ornek geojson).
        # Toplam 34 KB. Node bunlari share dizininden bulur; yarisma gunu
        # geojson'u -p geojson:=... ile disaridan verilir.
        (os.path.join('share', package_name, 'data'),
            glob('data/*.json') + glob('data/*.npz') + glob('data/*.geojson')),
    ],
    install_requires=['setuptools', 'numpy', 'ultralytics', 'opencv-python','ament_index_python'],
    zip_safe=True,
    maintainer='Nursena',
    maintainer_email='nursena@neuravix.com',
    description='ROS 2 Humble için Neuravix Otonom Sürüş Düğümleri',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Çalıştırılabilir adı = Modül adı . Dosya adı : main fonksiyonu
            'lane_follower = neuravix_ros2.lane_follower_node:main',
            'tabela_tespit = neuravix_ros2.tabela_tespit_node:main',
            'neuravix_control = neuravix_ros2.neuravix_control_node:main',
            'neuravix_control_real = neuravix_ros2.neuravix_control_node_real:main',
            'tabela_overlay = neuravix_ros2.camera_overlay_node:main',
            'obstacle_lidar = neuravix_ros2.obstacle_lidar_node:main',
            'mjpeg_server = neuravix_ros2.mjpeg_server:main',
            'route_planner = neuravix_ros2.route_planner_node:main',
        ],
    },
)

