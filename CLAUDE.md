# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a ROS 2 Humble colcon workspace for **Team NeuraVix's TEKNOFEST 2026 Robotaksi** entry — an
autonomous vehicle stack that runs both in the CARLA simulator and on a real vehicle ("Bee1", a Beemobs
L7e-CU). The custom code lives in a handful of packages under `src/`; everything else is vendored
third-party middleware (CARLA bridge, LiDAR-inertial odometry, driver code).

Not a git repository at the workspace root — several `src/` subdirectories (`ros-bridge`, `FAST_LIO`,
`livox_ros_driver2`, `carla-msgs`) are their own git repos (vendored, effectively submodules without
`.gitmodules`). Treat those as third-party code; don't "fix" their conventions to match the rest of the
workspace.

## Workspace layout

Custom packages (this team's code — where almost all work happens):
- **`src/neuravix_ros2`** — perception + decision/control brain. `ament_python` package.
- **`src/bee1_description`** — robot URDF/xacro, TF bringup, SLAM/localization launch files, A* planner
  node, point-cloud/odom/GPS relays for the real vehicle. `ament_cmake` package (installs Python scripts
  directly, no `setup.py`).
- **`src/pcl_recorder`** — small C++ point-cloud recorder utility (currently has `COLCON_IGNORE`, not built).
- **`src/smart_can_msgs`** — CAN message definitions for the real vehicle. **This is the REAL package
  from the vehicle team** (swapped in 2026-07-11 from `~/Downloads/smart_can_msgs.zip`), no longer the
  hand-authored draft. Don't edit it to match our conventions — it's the vehicle's contract. See "Path
  to real hardware" below.

Vendored / third-party (avoid modifying unless fixing an integration bug):
- **`src/ros-bridge`** — CARLA ROS bridge (upstream `carla-simulator/ros-bridge`), providing the
  `carla_*` packages (msgs, ackermann control, waypoint publisher, spawn objects, etc.). Note that the
  `carla_*` packages are also installed as top-level entries under `install/` — they build from
  `src/ros-bridge/<pkg>`, not from a separate copy.
- **`src/carla-msgs`** — standalone CARLA message definitions repo (not currently built; `carla_msgs`
  from `ros-bridge` is what's actually used).
- **`src/FAST_LIO`** — FAST-LIO2 LiDAR-inertial odometry (real hardware sensor fusion).
- **`src/livox_ros_driver2`** — Livox LiDAR driver.
- **`navigation_msgs/`** (workspace root, *not* under `src/`) — nav2 message definitions; not part of the
  colcon build tree as laid out.

`src/docs/`, `src/README.md`, `src/CHANGELOG.md`, `src/Makefile`, `src/mkdocs.yml`, `src/packaging/`, and
the top-level `src/pcl_recorder`/`src/docker` are leftovers from the `ros-bridge` upstream repo's own root
being extracted directly into `src/`. They document the upstream bridge, not this workspace.

## Build / run commands

ROS 2 distro: **Humble**. Standard colcon workflow from the workspace root:

```bash
source /opt/ros/humble/setup.bash

# build one package (fast iteration) -- ALWAYS scope the build, see hygiene rules below
colcon build --symlink-install --base-paths src --packages-select neuravix_ros2
colcon build --symlink-install --base-paths src --packages-select bee1_description

source install/setup.bash
```

### Workspace hygiene — hard rules

- **Never run a bare `colcon build`** (no `--packages-select`). Some vendored packages under
  `src/` (leftover ROS1-era packages, e.g. `carla_ackermann_control`, `carla_ad_demo`) are broken in
  this tree and a full build hits them and breaks the rest of the chain, sometimes deleting already-built
  packages from `install/`. Always scope builds with `--packages-select` (or `--packages-skip` for the
  known-broken ones if a wider build is truly needed).
- **Never run `livox_ros_driver2`'s own `build.sh`.** It deletes the entire `build/`/`install/` directory
  and can stomp on unrelated packages. Build it via `colcon build --symlink-install --packages-select
  livox_ros_driver2 --cmake-args -DROS_EDITION=ROS2 -DDISTRO_ROS=humble` instead.
- Teammates working in the shared workspace sometimes drop `COLCON_IGNORE` files to hide packages
  they're mid-editing on, which can silently make `fast_lio`/`bee1_description`/`livox_ros_driver2`
  disappear from `ros2 pkg list`. Before assuming a package is missing, check for stray ignore files:
  `find src -name COLCON_IGNORE`. (`src/pcl_recorder` has one intentionally — it's unused.)
- Sanity check before starting work: `ros2 pkg list | grep -E "fast_lio|bee1_description|livox"` — if
  none show up, (re)build them.
- The track (pist) CARLA bridge must run with `synchronous_mode: true` (in that scenario's
  `bridge_params.yaml`, outside this repo). Async mode lets raw LiDAR/IMU timestamps drift (observed
  ~268s drift against `/clock`), which silently breaks FAST-LIO/SLAM input.
- **Always pass `--base-paths src` to `colcon build`/`colcon list`.** By default colcon recursively scans
  the whole current directory, not just `src/`. The vehicle deploy staging folder
  (`~/robotaksi_deploy` — Dockerfile + `src/neuravix_ros2` + `src/smart_can_msgs` + `src/bee1_description`, kept **outside** this
  workspace on purpose) must never be copied into the workspace root — its nested `src/` has packages
  with the *same names* as this workspace's real ones, and a bare `colcon build` errors with "Duplicate
  package names" the moment both exist side by side (this happened once already and was cleaned up).
  `--base-paths src` is cheap insurance regardless.
- **`~/robotaksi_deploy` is the single canonical vehicle-deploy staging folder** — run
  `./export_deploy.sh` (workspace root) before every `docker build` there to sync `neuravix_ros2` +
  `smart_can_msgs` + `bee1_description` from this workspace's `src/`, so the Docker image never goes stale again (it did once:
  the deploy copy was missing `decision_brain.py`/`neuravix_control_node_real.py` entirely). Use
  `./export_deploy.sh --dry-run` to preview before syncing.

The temporary `neuravix_ros2/test/test_safety_regressions.py` suite added during the rejected
2026-07-21 lane-validity/slew experiment was removed when the `sonclaude` 10:35 image sources were
restored. `neuravix_ros2` currently has no meaningful custom test suite; use a scoped build plus node
smoke test. `bee1_description` also has no meaningful custom test suite.

Launching the stack (simulation, with CARLA + ros-bridge already running):

```bash
# TF bringup: robot_state_publisher + joint_state_publisher from the xacro model
ros2 launch bee1_description bee1_bringup.launch.py

# SLAM / localization variants
ros2 launch bee1_description pist_slam.launch.py
ros2 launch bee1_description pist_localization.launch.py
ros2 launch bee1_description localization.launch.py   # or localization_local.launch.py

# A* planner
ros2 launch bee1_description astar_planner.launch.py

# perception + decision nodes (neuravix_ros2 console_scripts)
ros2 run neuravix_ros2 lane_follower
ros2 run neuravix_ros2 tabela_tespit       # sign/traffic-light detection
ros2 run neuravix_ros2 tabela_overlay      # camera overlay (own RGB+depth cams, for visualization)
ros2 run neuravix_ros2 obstacle_lidar
ros2 run neuravix_ros2 neuravix_control    # the decision/control FSM (see below)
```

`bee1_bringup.launch.py` defaults to `publish_ego_to_base:=false`, meaning **EKF (robot_localization)
drives `odom -> base_link`** per REP-105. Only pass `publish_ego_to_base:=true` (with
`ego_to_base_*` offsets) when testing FAST-LIO/URDF in isolation without the EKF running — `base_link`
cannot have two parents.

`src/neuravix_ros2/neuravix_kontrol.py` is a standalone script (not a console_script / not part of the
ROS graph) that drives the CARLA Python API directly with a hardcoded pure-pursuit waypoint route and no
perception/FSM. It conflicts with the bridge + control node if run at the same time — it's an alternate,
simpler mission runner, not part of the normal pipeline.

## TF/frame conventions and SLAM

- **`base_link` = front axle center**, at ground height (not rear axle) — chosen to match the vehicle's
  spec document, which measures sensor offsets from the front axle. Axes follow REP-103 (+x forward, +y
  left, +z up). Because the spec doc measures front-axle-*backwards*, sensor x-offsets in
  `bee1_robotaxi.urdf.xacro` are sign-flipped relative to the doc's numbers (e.g. LiDAR doc `-177mm` ->
  URDF `+0.177`; IMU/GNSS doc `+1440mm` -> URDF `-1.440`) — if URDF offsets ever look backwards, this is
  the first thing to check against the original spec doc, not a sign bug.
- There are **two separate, non-simultaneous SLAM setups** — don't run both at once, and don't assume
  code/config for one applies to the other:
  - **Town02 (open 3D world): FAST-LIO**, configured via `src/FAST_LIO/config/bee1.yaml`. Produced
    `bee1_map.pcd` (workspace root). Launch: `ros2 launch fast_lio mapping.launch.py
    config_file:=bee1.yaml use_sim_time:=true`. Saving the map requires calling
    `ros2 service call /map_save std_srvs/srv/Trigger` explicitly — Ctrl+C does **not** autosave.
  - **Custom flat/barriered/tunneled track: `slam_toolbox` (2D)**, via `bee1_description`'s
    `pist_slam.launch.py` (mapping) / `pist_localization.launch.py` (localization), configured by
    `config/slam_toolbox_pist*.yaml` and `config/pointcloud_to_laserscan_pist.yaml`. FAST-LIO was tried
    on the track first and **diverges on flat/sparse geometry**, hence the switch. The 3D LiDAR is
    flattened to 2D via `pointcloud_to_laserscan` with a height window (`min_height:-1.0,
    max_height:0.5`) tuned so the tunnel ceiling isn't seen as an obstacle. Frame chain:
    `/carla/ego_vehicle/lidar` -> `pointcloud_to_laserscan` -> `/scan`, and
    `/carla/ego_vehicle/odometry` -> `pist_odom_tf.py` -> `odom -> ego_vehicle` TF, feeding
    `slam_toolbox` (`map -> odom`). `pointcloud_filter` is **not** used on the track (it over-filters
    track geometry, e.g. ~4369 -> 277 points) — `slam_toolbox` consumes the raw track LiDAR topic.
  - **Known open issue**: the track's serialized `slam_toolbox` map (`pist_haritasi.*`, ~452 MB) is too
    large — scan-matching falls behind (`queue is full`) and drifts/aliases against the track's repeated
    barrier geometry once driving. A healthy 2D map for this track should be a few–tens of MB; the fix is
    re-recording a short, single, constant-speed mapping lap rather than tuning matcher parameters.
- `bee1.yaml`'s `extrinsic_T` (LiDAR->IMU offset for FAST-LIO) is a **simulation-only value**,
  `[-0.6, 0, -0.4]` (derived from CARLA's LIDAR `[0.4,0,1.6]` vs IMU `[1.0,0,2.0]`, both relative to
  `ego_vehicle`) — it must be physically remeasured on the real vehicle, not reused as-is.
- `odom_relay.py` and `gps_relay.py` (both in `bee1_description/scripts/`) exist purely to rename
  hardcoded frame ids so downstream `robot_localization` config doesn't need to change: FAST-LIO always
  publishes `camera_init`/`body`, relayed to `odom`/`base_link`; CARLA's GNSS sensor frame is relayed to
  `gnss_link` (both under `ego_vehicle/...` prefixed frame names otherwise). If a relay node isn't
  running, expect `robot_localization`/`slam_toolbox` to silently wait on TF that never arrives rather
  than error clearly.
- GPS global fusion (`ekf_global` + `navsat_transform`, wired up in `localization.launch.py` /
  `config/ekf_navsat.yaml`) is built but **not validated in sim** — CARLA's fake GNSS reports coordinates
  near `(0,0)` (equator/prime-meridian), which is degenerate for `navsat_transform`. This is deferred to
  the real vehicle's RTK GPS; `datum`, `magnetic_declination_radians`, and `yaw_offset` in
  `ekf_navsat.yaml` are placeholders that need real-world values.
- Orchestration GUIs `carla_arayuz.py` (Town02) and `carla_pist_arayuz.py` (track) live in `~/Desktop`,
  **outside this workspace** — they're Tkinter scripts that start the whole chain (CARLA, bridge, spawn,
  bringup, filter, FAST-LIO/SLAM, localization) with staggered delays. If a manual chain doesn't come up,
  check what order/delays these scripts use before assuming a launch file is broken.

## Path to real hardware (Bee1 vehicle)

The real vehicle (Bee1, Beemobs L7e-CU) runs an **Advantech MIC-770V3H (i9-12900TE) + MIC-75G20/RTX 3060,
Ubuntu 20.04, ROS 1 Noetic or ROS 2 Foxy (switchable via `.bashrc`, both present)**, vs. this dev
workspace's Ubuntu 22.04 + Humble. Real sensors: **Velodyne VLP-16 LiDAR, ZED2 stereo camera, XSENS
MTI-680-DK GPS/IMU**, all bridged through an **Advantech<->Vehicle-ECU CAN0 link**, wrapped in Docker for
easy ROS1/ROS2 switching. Full CAN contract confirmed from the official "2026 Araç Kullanıcı Dokümanı" /
"2026 Araç-Mimari" / "2026 Araç_Genel_Bilgilendirme" PDFs (kept at the workspace root) — this replaced
earlier guesswork:

- **Cross-distro ROS communication requires Cyclone DDS on both sides.** The default RMW does not see
  topics across a Noetic/Foxy or Humble/Foxy boundary even on the same host/network; switching both sides
  to `rmw_cyclonedds_cpp` (`apt install ros-<distro>-rmw-cyclonedds-cpp`, `export
  RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`) fixed it in testing, custom messages included — no bridge
  package needed. `ROS_DOMAIN_ID` must also match on both sides. Vehicle wifi: SSID `robotaxi_1`/`robotaxi_2`;
  **wifi password, host IPs and the SSH user are NOT recorded here — this repo is public.**
  Ask the vehicle team, or see the private team notes. (Redacted 2026-08-21 before the first
  push to `github.com/teamneuravix/neuravix2026`, which is a PUBLIC repository.)
- **Both message TYPE names and FIELD names must be rosidl-legal in ROS 2** — type names need
  `^[A-Z][A-Za-z0-9]*$` (no underscores) and field names need `^[a-z][a-z0-9_]*$` (snake_case). The
  vehicle's own CAN topic/field names (e.g. `RC_Ignition`, `AUTONOMOUS_SteeringMot_Control`) violate both
  rules — matching what the earlier Docker compatibility report already found for `RC_THRT_DATA`
  specifically. **The real package's renaming scheme is now known** (we have the package, see below):
  type names are the CAN name flattened to leading-capital-then-all-lowercase — `RC_UnittoOmux` ->
  **`Rcunittoomux`**, `AUTONOMOUS_BrakePedalControl` -> **`Autonomousbrakepedalcontrol`**,
  `FB_OMUX_to_AUTONOMOUS` -> **`Fbomuxtoautonomous`** (NOT CamelCase `RcUnittoOmux` — that was the old
  draft's guess) — while field names are snake_case (`rc_ignition`, `fb_brakepedal_voltage_en`) and
  **topic** names keep the original CAN style (`/beemobs/rc_unittoOmux`,
  `/beemobs/FB_OMUX_to_AUTONOMOUS`). Type name != topic name; don't infer one from the other.
- **The CAN bridge is package `smart_can_stuff`** (message defs are the separate `smart_can_msgs`
  package). Launch: ROS1 `roslaunch smart_can_stuff start_can_bus.launch` / ROS2 `ros2 launch
  smart_can_stuff can_launch.xml`. Per the user doc (§1.4/1.5) this single launch starts **CAN and all
  sensor drivers** (Velodyne VLP16 trio + ZED2 wrapper + XSENS) — there is no separate sensor launch;
  after any host-side `pkill` cleanup, this one command (in `tmux`) restores the whole sensor stack.
  Verify with `ros2 topic hz`, never with `node list` alone — stuck drivers stay in `node list`
  advertising topics while publishing nothing (proven 2026-07-13). It also ships a ready **PID layer**: publish a target to
  `/beemobs/steering_target_value` or `/beemobs/speed_target_value` (`std_msgs/Float32`, presumed) and
  the vehicle's own tuned PID (`steering_pid.yaml`/`thrt_pid.yaml`) computes the low-level PWM/pedal
  commands — no need to hand-compute `AUTONOMOUS_SteeringMot_Control` PWM or `RC_THRT_DATA` pedal
  position ourselves. **The PID disengages if its target topic doesn't receive a message for 3 loop
  ticks** — any publisher to these topics must publish continuously, not just on change. Brake and
  handbrake have **no PID layer** — those still go through raw CAN messages
  (`/beemobs/AUTONOMOUS_BrakePedalControl`, `/beemobs/AUTONOMOUS_HB_MotorControl`). Real vehicle's own CAN
  driver/PID source lives at `smart@192.168.30.100:Projects/ros2_ws/src/smart_can_stuff/` (or
  `Projects/ros_ws/src/...` for ROS1). We now have it as `~/Downloads/smart_can_stuff.zip` (received
  2026-07-11 alongside `smart_can_msgs.zip`), but it is **not extracted into this workspace** — only
  `smart_can_msgs` was. Read the zip for the authoritative PID topic names/units rather than guessing;
  the `smart_can_msgs` half of that delivery already replaced the old draft.
- **`AUTONOMOUS_EMERGENCY`** (a field inside `rc_unittoOmux`, not physical-button-only) can force-stop the
  vehicle (drive motor cut, gear forced to neutral) from software — the real node sets this whenever
  `/safety/emergency_stop` fires, in addition to zeroing throttle/setting brake internally.
- **CARLA-coupled control node has been split**: `neuravix_ros2/decision_brain.py` now holds the entire
  FSM/decision logic (`Alkar_Function4`, `DriveState`, `/master` id constants, sign-id table, the
  CARLA-pist-specific `ROUTE` — real competition routes arrive as a GEOJSON file with `start`/`gorev_N`/
  `park_giris` lat-lon points per the Şartname, not this hardcoded list) with zero CARLA dependency. Two
  thin ROS I/O wrappers both import it: `neuravix_control_node.py` (sim — CARLA pub/sub, `carla_msgs`,
  the CARLA-tuned feedforward+PI throttle controller) and **`neuravix_control_node_real.py`** (real
  vehicle — no `carla_msgs` import; console script `neuravix_control_real`). If you change FSM behavior,
  edit `decision_brain.py` once; don't duplicate logic into either node file.
  - The real node's odometry input is a declared ROS parameter `odom_topic` (default
    `/odometry/filtered`) — point it at whatever the real localization chain ends up publishing.
    **Decision (2026-07-08): the real vehicle will use `slam_toolbox` for localization** (matching the
    track/`pist` setup already built in `bee1_description`, not FAST-LIO/GPS).
  - **`bee1_description/scripts/can_odom_node.py`** (console script `can_odom`, **draft**) is the real
    vehicle's odometry source for that `slam_toolbox` chain — the real-hardware equivalent of the sim's
    `pist_odom_tf.py` (same role: feed raw `odom` into `slam_toolbox` directly, no EKF in between, mirroring
    how the sim `pist_*` setup already skips EKF). It integrates a bicycle/Ackermann model from CAN
    feedback (`/beemobs/FB_VehicleSpeed`, `/beemobs/FeedbackSteeringAngle`, `/beemobs/FB_MotorDriver` for
    gear/direction) into `odom -> base_link` (TF + `nav_msgs/Odometry` on `/odometry/can_wheel`).
    **Steering feedback calibrated on the vehicle 2026-07-13**: raw `feedbacksteeringangle` (int8) reads
    straight=2, full-left=-21, full-right=26; against the spec's mechanical limits (32.5°/30.0°
    inner/outer → ~31.25° equivalent bicycle angle) that gives `steer_feedback_gain=-0.02322` rad/unit
    (negative because raw-negative = physically left, and REP-103 positive steer = left turn) and
    `steer_feedback_offset=2.0` — now the defaults in the node and both `pist_*_real` launch files.
    Remaining check on first drive: turning left must produce positive `steer_rad`/leftward odom curve
    (if not, the sign assumption was wrong — flip the gain). `wheelbase` (1.86 m) is already confirmed
    from the spec doc and shouldn't need changing. Being pure dead-reckoning, yaw drifts over time by design — that's exactly what
    `slam_toolbox`'s scan-matching (`map -> odom`) is meant to correct on top of it; this node only needs
    to supply a reasonable-enough short-term `odom -> base_link`.
    **`max_dt` (0.5 s, 2026-08-22)**: `_integrate`'in adım süresi sınırsızdı ve bir saat sıçraması
    (ölçülen: `dt = 1.787.210.527 s`) yaw'ı rastgele bir değere atıyordu — AMCL'in `lokal_0820_0722`
    bag'inde hiç yakınsamamasının kök nedeni buydu. Aşan tik entegre edilmeden atlanır (bir kez WARN).
    Önce/sonra tablosu aşağıdaki AMCL bölümünde.
  - Until `can_odom_node` is wired up and launched, `odom_topic` in `neuravix_control_node_real.py`
    receives nothing and the real control node degrades gracefully to FSM-only driving (lane+sign+
    obstacle, no pure-pursuit/A* position updates) — no code branch needed for that "no odometry yet"
    phase.
  - **`src/smart_can_msgs` is the REAL package from the vehicle team** (swapped in wholesale
    2026-07-11 from `~/Downloads/smart_can_msgs.zip`; the old hand-authored draft is gone). Tells:
    16 `.msg` files (draft had 9), flat type names (`Rcunittoomux`), no inline CAN-name comments, and
    `package.xml` maintainer `smart@todo.todo`. **Treat these files as read-only** — they are the
    vehicle's contract, not ours to tidy. `.msg` files carry no value semantics, so field *encodings*
    (e.g. is `rc_lowbeam` 0/1?) still need confirming against live `FB_*` feedback on the vehicle.
  - **Stale draft artifacts still live in `install/smart_can_msgs`** — 9 orphaned CamelCase types
    (`RcUnittoOmux`, `AutonomousBrakePedalControl`, `FbOmuxToAutonomous`, …) generated before the swap
    and never cleaned. **This is a trap**: `from smart_can_msgs.msg import RcUnittoOmux` still imports
    fine from the stale install and then breaks on a clean rebuild. Only the 16 flat-named types exist
    in source. Clean with `rm -rf build/smart_can_msgs install/smart_can_msgs` + rebuild if in doubt.
  - `neuravix_control_node_real.py` publishes: `/beemobs/rc_unittoOmux` (ignition/gear/signal/emergency,
    `smart_can_msgs/Rcunittoomux`), `/beemobs/AUTONOMOUS_BrakePedalControl` (ham fren,
    `smart_can_msgs/Autonomousbrakepedalcontrol`), and `/beemobs/steering_target_value` /
    `/beemobs/speed_target_value` (`std_msgs/Float64` by default; `targets_float64:=false` is the legacy
    Float32 escape hatch) every control tick (20 Hz), regardless of FSM state, to satisfy the PID's
    3-tick keepalive requirement. Steering target is confirmed to use raw
    `FeedbackSteeringAngle` units (straight=2, left lock=-21, right lock=26); speed target is scaled by
    `speed_target_scale` and capped by `max_speed_kmh`. Brake
    `AUTONOMOUS_BrakePedalMotor_ACC`/`_PER` defaults are still placeholders; handbrake is unused;
    `auto_ignition` (default true) makes the node itself send `RC_Ignition=1` + gear=DRIVE at startup —
    flip it off via launch param if ignition should instead be a manual/joystick step first. Steering
    feedback is subscribed for observation/guarded auto-offset; speed feedback is not closed into this
    wrapper (the vehicle's PID owns that loop).
  - `camera_overlay_node.py` and `neuravix_kontrol.py` are confirmed **sim-only, not ported**: the
    former is a CARLA-sensor debug/visualization overlay (real detection already happens independently
    in `lane_follower`/`tabela_tespit`'s YOLO pipelines), the latter is a standalone `carla.Client`
    test script outside the ROS graph. Both now have a "SADECE CARLA SİMÜLASYONU" note at the top of the
    file.
  - Sensors differ from sim regardless of the above: camera input becomes Zed2 (not a CARLA RGB camera),
    LiDAR is a **Velodyne VLP16** (the workspace's `livox_ros_driver2` is present only because FAST-LIO's
    build depends on it — the real vehicle has no Livox hardware; also moot if the real localization
    path settles on `slam_toolbox` rather than FAST-LIO, per the decision above). `tabela_tespit_node.py`
    (`camera_topic` param) and `obstacle_lidar_node.py` (`lidar_topic` param) already accept the real
    topic name via a launch-time ROS parameter, no code change needed to repoint them. `lane_follower_node.py`
    had its camera topic hardcoded to the CARLA overlay output — it's now been given the same
    `camera_topic` parameter (default unchanged) so it can be repointed the same way.
- Deployment is via a Docker image (`robotaksi_humble:latest`, built from a separate `~/robotaksi_deploy`
  directory outside this workspace: `ros:humble-ros-base` + `neuravix_ros2` + vision deps +
  `smart_can_msgs` + `bee1_description` (added 2026-07-10, with `slam-toolbox`, `pointcloud-to-laserscan`,
  xacro/robot_state_publisher apt deps and a `/root/maps` dir for the serialized track map); default RMW
  is **Fast DDS** as of 2026-07-12 to match the vehicle host — Cyclone DDS
  is still installed as a fallback), transferred to the vehicle with `docker save`/`load` and run with
  `--gpus all --network host --ipc=host --privileged -v /dev:/dev
  -v /home/smart/Permanent/maps:/root/maps
  -v /home/smart/Permanent/neuravix_kayit:/root/neuravix_kayit
  -e ROS_DOMAIN_ID=<vehicle's>`
  (`--ipc=host` so Fast DDS's shared-memory transport shares `/dev/shm` with the host reliably; the maps
  volume so a map serialized to `/root/maps` lands directly in the overlayroot-safe `Permanent` folder
  and survives both container removal and host reboot).
- Full ROS 2 **Foxy rebuild/compat check is still needed** for `fast_lio`, `livox_ros_driver2`, and
  `robot_localization` before relying on them on the vehicle — development so far has only targeted
  Humble.

## Architecture: perception -> `/master` -> decision/control

The perception nodes and the decision brain are decoupled through a single `std_msgs/String` topic,
**`/master`**, carrying comma-separated values: `"<id>,<field1>,<field2>,..."`. This is the core
integration point in the stack — most cross-node bugs live at this boundary (field count/order
mismatches, stale data). Message ids (defined in `decision_brain.py`, shared by both sim and real nodes):

| id | publisher | payload |
|----|-----------|---------|
| 2 (`ID_LANE`) | `lane_follower_node.py` | `id, lane_angle` — restored `sonclaude` format; there is no `lane_valid` field or lane-validity brake override in this version |
| 3 (`ID_SIGN`) | `tabela_tespit_node.py` | `id, sign_class, distance, cx, cy, w, h` (bbox center + size in pixels; `distance` is a rough bbox-height estimate with an uncalibrated constant. `sign_class` is the **canonical** id from `decision_brain.py` (`DUR`=11, `KIRMIZI_ISIK`=15, …), **not** the YOLO model's class index — see the sign-id mapping section below. **Event-based**: published only per confirmed detection — no sign in view ⇒ no ID-3 traffic, unlike lane (every frame) and obstacle (10 Hz)) |
| 4 (`ID_OBSTACLE`) | `obstacle_lidar_node.py` | `id, front, left, right` — **all three are longitudinal clearance in metres from the front bumper** (rewritten 2026-07-21, see below): `front` = ego corridor, `left`/`right` = the corridor you'd enter by swerving that way. `99` = clear, `0` = blocked / no lidar data. Lidar frame, REP-103 (x forward, +y left) |
| 5 (`ID_PLANNER`) | — | `id, goal_x, goal_y` (A* grid goal update) |

`decision_brain.py`'s `Alkar_Function4` is the single decision brain (state machine, `DriveState`),
**CARLA-independent by design** — it only consumes `/master` events plus explicit method calls
(`emergency_event`, `update_position`). It knows nothing about ROS, CARLA, or the real vehicle; all of
that lives in the two node files that wrap it:
- **`neuravix_control_node.py`** (sim, console script `neuravix_control`) — subscribes to
  `/safety/emergency_stop`, `/carla/ego_vehicle/vehicle_status` (speed feedback) and
  `/carla/ego_vehicle/odometry` (position feedback, also used to keep the A* grid's current-position
  cell up to date). Publishes CARLA sim control (`/carla/ego_vehicle/vehicle_control_cmd`,
  `CarlaEgoVehicleControl`) via a feedforward+PI throttle controller closing the loop on
  `vehicle_status` speed feedback, alongside the Bee1 `/beemobs/*` topics below.
- **`neuravix_control_node_real.py`** (real vehicle, console script `neuravix_control_real`) — same
  `/master`/emergency subscriptions, no `carla_msgs` dependency; odometry comes from a declared
  `odom_topic` ROS parameter (default `/odometry/filtered`) instead of a hardcoded CARLA topic. See the
  "Path to real hardware" section above for what still needs to land before this is fully wired
  (real localization source, real CAN feedback messages).

Both nodes blend **pure-pursuit steering** against a hardcoded `ROUTE` waypoint list (CARLA-pist
coordinates, meaningless off that specific track) with the FSM's lane-follow steering output (55%/45%
blend when both are fresh), then publish:
- Bee1 vehicle topics: `/beemobs/RC_THRT_DATA`, `/beemobs/AUTONOMOUS_BrakePedalControl`,
  `/beemobs/RC_STR_DATA`, `/beemobs/RC_SIGNAL_STATUS` (currently plain `Float32`/`Int32` — placeholder
  types, see "Path to real hardware")
- Debug: `/neuravix/current_state`, `/neuravix/decision_dump`

Vehicle-day findings (2026-07-11, measured on the real vehicle): the Velodyne driver publishes
`/velodyne_points` as **RELIABLE** (not best-effort as typically assumed); an "obstacle always 99"
symptom there was **not** QoS but the driver logging `Velodyne poll() timeout` — no packets from the
sensor (Velodyne lives on a `192.168.1.x` ethernet segment that wasn't configured on the host; the
`RTNETLINK answers: Device or resource busy` message at SSH login is the failing setup script, and the
long-standing `ddsi_udp_conn_write to 192.168.1.77` DDS noise is almost certainly that same stale/broken
interface). `sonyaris.pt` (tabela model) is pickled with `dill` — the deploy image must bundle `dill`
(vehicle is offline, pip can't fetch it there); the Dockerfile now does. The ZED wrapper on the Foxy host
was up but publishing no image frames (even host-side `topic hz` saw nothing) while spamming
`zed_camera_center frame does not exist` — check the ZED launch/camera before blaming our nodes.

Vehicle-day findings (2026-07-12, second on-vehicle session — full log in `6.deneme.txt`):
- **All three sensors confirmed live on the Foxy host**: `/velodyne_points` ~10 Hz (yesterday's
  `192.168.1.x` ethernet problem no longer blocking), `/zed/zed_node/rgb/image_rect_color` ~28 Hz
  (yesterday's dead ZED also resolved), `/imu/data` ~200 Hz. CAN feedback also live:
  `ros2 topic echo /beemobs/FB_OMUX_to_AUTONOMOUS` streams (`fb_ignition: 1`, `fb_batterysoc: 97`, …) —
  so the **real `smart_can_msgs` uses snake_case field names** (`fb_ignition`, `fb_brakepedal_voltage_en`)
  while keeping original CAN style in **topic** names (`FB_OMUX_to_AUTONOMOUS`). (Since resolved: the
  real package was swapped into `src/smart_can_msgs` on 2026-07-11 — this bullet's "pull that package"
  action item is **done**. Note its *type* names are flat, e.g. `Fbomuxtoautonomous`, unlike the topic.)
- **Fast DDS worked host↔container this session**: every terminal (host Foxy and Humble container alike)
  exported `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, container ran with `--network host -e ROS_DOMAIN_ID=0`,
  and all sensor topics were visible inside the container (`/imu` 200 Hz, ZED ~23 Hz — slightly below the
  host's 28 Hz). So the earlier "Cyclone DDS required" finding is not absolute — same-host, same-RMW,
  same-domain-id worked with Fast DDS too; Cyclone remains the tested answer for cross-host (laptop↔vehicle)
  setups. Just make sure **both** sides use the same RMW. **Consequence (2026-07-12): the deploy image's
  default RMW was switched from Cyclone to Fast DDS** (`ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp` in the
  Dockerfile) so it matches the vehicle host's default out of the box and `docker exec` shells no longer
  need a manual export (which got typo'd on the vehicle once). Cyclone stays installed in the image as a
  fallback — override per-container with `docker run -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` if a
  cross-host setup turns out to need it. A laptop running `rqt_image_view` against the container must now
  also be on Fast DDS (Humble's default — so typically nothing to do, just don't export Cyclone there).
- **CUDA is dead inside the container**: the image's PyTorch build is newer than the host NVIDIA driver
  (`found version 12050`) → `torch.cuda.is_available() == False`, all YOLO inference ran on CPU. Vehicle
  is offline, so no pip fix on site. **Fixed in the deploy Dockerfile (2026-07-12)**: torch is now pinned
  to `torch==2.5.1+cu121` / `torchvision==0.20.1+cu121` from the PyTorch cu121 index, installed *before*
  `ultralytics` so pip doesn't pull a newer CUDA build — needs a fresh `docker build`/`save`/`load` cycle
  to reach the vehicle. Detection *does* work on CPU (`tabela_tespit` correctly tracked real
  `park`/`disabled_park`/`red_light` targets from the ZED feed), just at low frame rates.
- **`ultralytics` import hangs when offline**: first `lane_follower` start froze inside ultralytics'
  `is_online()` DNS check (`Temporary failure in name resolution` after a long stall) — looks like a hung
  node, needed repeated Ctrl+C; the retry ran fine. **Fixed in the deploy Dockerfile (2026-07-12)**:
  `ENV YOLO_OFFLINE=True` (skips the online check) and `ENV YOLO_CONFIG_DIR=/tmp/Ultralytics`
  (`/root/.config/Ultralytics` was not writable → "user config directory is not writable" warning).
- **`obstacle_lidar` crashed on real Velodyne clouds** (reproduced twice, node exited on first message):
  `read_points_numpy()` asserts `All fields need to have the same datatype` **even when `field_names`
  only requests x/y/z** — Velodyne's PointCloud2 mixes datatypes (x/y/z `float32` + `ring` `uint16`),
  unlike CARLA's all-`float32` clouds, so sim never showed it. **Fixed 2026-07-12** in
  `obstacle_lidar_node.py` (and the same latent bug in `bee1_description`'s `lidar_echo_node.py` and
  `pointcloud_filter.py`): read via `pc2.read_points(cloud, field_names=(...))` (structured array,
  datatype-mix safe) and the obstacle callback now catches parse errors instead of dying. Verified
  against a synthetic VLP-16-layout cloud (reproduced the exact assert with the old call, correct
  front/left/right with the new one) plus a CARLA-style all-float32 regression check.
- **Real-LiDAR geometry fixes (2026-07-12, post-session)**: (1) the Velodyne driver stamps clouds with
  frame_id `velodyne`, but the URDF only defined `lidar_link` — slam_toolbox would wait for a
  `base_link->velodyne` TF that never arrives, silently (no error). The URDF now has a `velodyne` alias
  link (identity joint under `lidar_link`); verify the actual frame_id on the vehicle before trusting it.
  (2) Height windows were tuned for CARLA's 1.6 m lidar mount, but the real mount is 0.62 m (URDF
  `lidar_z`): `pointcloud_to_laserscan_real.yaml` is now `min_height: -0.4 / max_height: 1.5` (ground
  excluded, same absolute ceiling cutoff as sim), and `obstacle_lidar` on the real vehicle **must** be
  run with `-p z_min:=-0.4` — its default `-1.3` is CARLA-tuned and on the real mount would count the
  ground as a permanent front obstacle (run line is in the node's docstring). **Obsolete since the
  2026-07-21 rewrite**: the height window is now derived from `lidar_height`, so the real vehicle needs
  no flag and it is **CARLA** that must pass `-p lidar_height:=1.6`.
  **(3) The 0.62 m mount height was WRONG — corrected to 1.35 m on 2026-07-21.** Ground returns in the
  5–20 m ring of five real track bags put the sensor at 1.29 / 1.31 / 1.39 / 1.41 m (teammate measured
  three, independently reproduced on `pist_17tem_2` and `pist_19_3tem`), i.e. roof mount, not the
  bonnet-height 0.62 the URDF claimed. The consequence was a **silent fail-open**: the window believed
  to be 0.22–2.12 m above ground actually sat at ~0.95–2.85 m, so cones, low barriers and vehicle
  underbodies were filtered out entirely — on one bag the ego corridor kept 38 points under the old
  window vs 81 under the new one. `bee1_robotaxi.urdf.xacro` `lidar_z` is now `1.350`,
  `pointcloud_to_laserscan_real.yaml` is `min_height: -1.13 / max_height: 0.77`, and
  `obstacle_lidar_node.py`'s `lidar_height` default is `1.35` (plus a startup check that estimates the
  mount height from ground returns and logs an ERROR on a >`mount_check_tol` mismatch — this is what
  catches a forgotten `-p lidar_height:=1.6` in CARLA). **Still to do: confirm with a tape measure**,
  and note this **invalidates `pist_haritasi_4`** and every earlier serialized map — they were built
  through the wrong window, so localization against them will not hold. Re-map before relying on one.
- **SSH-launched processes die with the wifi**: the vehicle wifi dropped the session every few minutes
  (`client_loop: send disconnect: Connection reset`). `ros2 launch smart_can_stuff pid_launch.py` started
  both PID nodes, but after the disconnect the node list showed `steering_pid_node` without
  `speed_pid_node`. Anything long-lived (PID layer especially, given its 3-tick keepalive) must run under
  `tmux`/`screen` or inside the container — never bare in an ssh session.
- **The host root filesystem is overlayroot** (read-only root + tmpfs overlay — visible in the login
  banner; that's why the image tar lives in `/home/smart/Permanent/`). Writes outside the persistent
  mount — potentially including `/var/lib/docker` — may vanish on reboot: after the next power cycle,
  verify `robotaksi_humble:latest` / `robotaksi_container` still exist before debugging "missing image"
  as something else, and re-`docker load` from `/home/smart/Permanent/robotaksi_humble.tar` if needed.

Vehicle-day findings (2026-07-12, third on-vehicle session — full log in `output7.txt`):
- **All three deploy-image fixes verified live on the vehicle**: `torch.cuda.is_available() == True` in the
  container (cu121 pin works against the real driver), `lane_follower` started instantly offline (no
  ultralytics DNS hang), and `obstacle_lidar` ran on real Velodyne clouds without crashing, publishing
  plausible `/master` ID-4 values that tracked a person approaching (front 6.7→0.87 m) and cleared to 99.
  Fast DDS default also confirmed: no manual RMW export needed in `docker exec` shells.
- **`lane_follower` published a constant/drifting garbage angle** (`2,15` pinned, then a slow 15→75 ramp,
  then pinned at 75) while its YOLO found **zero masks for 53k+ frames** (indoor test, no lanes visible).
  Root cause was threefold and is **fixed 2026-07-12**: (1) unbounded PID integral (windup) — now clamped
  so `Ki*integral` ≤ 10°, plus `reset()`; (2) stale `left_prev`/`right_prev` fits used forever — a single
  false detection poisoned steering permanently; (3) an angle was confidently published even with no lane
  info. New behavior: after `lane_lost_frames` (param, default 15) consecutive mask-less frames the fits
  and PID reset and neutral 45 is published (decision brain treats 45 as straight). Verified end-to-end by
  injecting the poisoned state and feeding 100 blank frames (recovers to constant 45 at frame 15).
- **The lane model found nothing on real ZED images** — partly explained by the indoor setting, but
  `best_yolo11.pt` and the BEV homography (`src_pts` calibrated on the CARLA camera) both still need
  validation/recalibration against real track footage. Open item for the next outdoor session.
- Operational repeats: processes started in a `docker exec` foreground **die when the wifi drops**
  (mjpeg_server was killed twice mid-session) — tmux inside the container, always; the run command used
  omitted `--ipc=host` (worked anyway via `-v /dev:/dev`, but use the documented command); the tar path is
  case-sensitive (`/home/smart/Permanent`, not `permanent`); `docker load` over an existing image leaves
  the old one dangling — `docker image prune` occasionally.

Vehicle-day findings (2026-07-13, fourth on-vehicle session — log `output9.txt`, kept outside this
workspace):
- **"Container sees topics but `ros2 topic hz` says not published yet" — root cause was NOT the
  container/DDS.** The host's own shell couldn't `hz` `/imu/data` either. After the (overlayroot) reboot,
  all host sensor drivers (velodyne trio, `zed_wrapper`, `xsens_mti_node`, launched natively from
  `/home/smart/Projects/ros2_ws` on Foxy — there is **no separate sensor container**) were up and
  *advertising* (node list + topic list + QoS all normal, `/imu/data` RELIABLE with 1 publisher) but
  publishing **zero samples**, each busy-spinning at 84–143% CPU (`robot_state_publisher` at 83%,
  normally ~0% — the telltale). Fix: `pkill -9` the sensor processes and re-run the sensor launch;
  `/velodyne_points` came back at a clean 10 Hz. Likely trigger: sensor launch started too early after
  reboot, before devices/interfaces were ready (the known-failing `192.168.1.x`/`RTNETLINK busy` setup
  script is a prime suspect for Velodyne).
- **Debugging ladder for "no sensor data in container", in order**: (1) `ros2 topic hz` on the **host**
  first — if the host can't see it either, stop debugging the container entirely; (2)
  `ros2 topic info <topic> -v` for publisher count + QoS; (3) `ps aux | grep -Ei "zed|velodyne|xsens"` —
  drivers alive but at ~85%+ CPU with no output = the stuck-after-reboot state above; (4) only then
  DDS-level suspects (RMW, domain id, `--network host`/`--ipc=host`, stale `ros2 daemon` — `ros2 daemon
  stop` is a free first move on any weird CLI result).
- **`docker load` does not update an existing container** — after loading a new tar,
  `docker rm -f robotaksi_container` and `docker run` again, or it keeps running the old image's code
  (bit us this session).
- Operational repeats: the sensor launch was again running in an SSH foreground terminal (`pts/3`) —
  wifi drop kills it, taking all sensors down; host-side sensor bringup belongs in `tmux` too, same rule
  as container processes. VLP-16 at ~10 Hz is its design rate (600 RPM), not "slow"; a several-second
  `hz` startup delay is cold-daemon + big-graph discovery (ZED alone advertises ~60 topics), not a fault.

Vehicle-day findings (2026-07-13, fifth on-vehicle session — 11th mapping attempt, log `output11.txt`,
kept outside this workspace):
- **Mapping produced no map; root cause: `can_odom`'s odometry never moved.** `can_odom` (rev4)
  subscribed to `/beemobs/fbvehiclespeed` — a topic name taken from `pid_params.yaml` but **never
  verified to be published**; the live topic (echoed twice this session) is `/beemobs/FB_VehicleSpeed`.
  With no speed messages the stale-guard held `v=0` forever, `odom -> base_link` stayed frozen at the
  origin, `slam_toolbox` never accumulated `minimum_travel_distance` (0.5 m), added no nodes past the
  first scan, kept republishing `map -> odom` with a frozen stamp (the endless `TF_OLD_DATA ... frame
  odom` spam), and published no map ("No map received" in RViz). Note the failure signature: `tf2_echo
  odom velodyne` **resolved fine** but its translation equaled exactly the static `base_link->velodyne`
  offset `[0.177, ~0, 0.62]` — i.e. TF tree healthy, odometry pinned at zero. (An early "Invalid frame
  ID odom" line from tf2_echo is just its normal wait-for-buffer message, not evidence the frame is
  missing — the very next lines resolved it.) **Fixed 2026-07-13 (rev5)**: `speed_topic` default is now
  `/beemobs/FB_VehicleSpeed` and is exposed as a launch argument in both `pist_slam_real.launch.py` and
  `pist_localization_real.launch.py` for on-vehicle override.
- **All `Fbvehiclespeed` fields are `uint8`** (confirmed from the real msg file):
  `fb_reelvehiclespeed_ms` has 1 m/s resolution — useless at 5–10 km/h mapping speeds (jumps 0↔1↔2). Rev5
  therefore reads `fb_reelvehiclespeed_kmh` (1 km/h ≈ 0.28 m/s resolution) with `speed_scale=0.27778`;
  this also resolves the rev4-era inconsistency where the launch files still passed `0.27778` while the
  node read the m/s field (would have made odometry 3.6× slow). Finer future options if needed:
  `Fbmotordriver.vehiclerpm` (uint16, needs rpm→m/s calibration) or `plustripdistance` (uint16 trip
  counter, unit unverified). Verify on vehicle by driving a straight ~10 m and checking odom x.
  **Update: `speed_scale` default is now `0.31627`, not `0.27778`** (node + both `pist_*_real` launches
  agree). GPS/Kabsch check on the vehicle found dead-reckoning under-counting ~14% because the uint8
  `fb_reelvehiclespeed_kmh` truncates downward, so the km/h→m/s factor was scaled up: `0.27778 × 1.139 ≈
  0.31627`. Not a bug — an intentional truncation correction.
- `use_imu_yaw:=true` was in use and worked (yaw from XSENS gyro; small stationary bias drift ~0.05°/s
  observed via tf2_echo — expected, corrected by slam scan-matching once mapping actually runs).
- Steering feedback lock-to-lock raw values were measured (straight=2, full-left=-21, full-right=26) →
  `steer_feedback_gain`/`offset` are now calibrated defaults; see the `can_odom_node` bullet above.
- **The host sensor/CAN launch was running twice** (duplicate node names in `ros2 node list`:
  two `can_handler`s, two velodyne drivers, `launch_ros_3577` + `launch_ros_46516`) — two CAN writers on
  can0. Before any SLAM attempt, check `ros2 node list` for duplicate-name warnings and kill the extra
  launch. Also: `/imu/data` ran at ~50 Hz bursty this session (was 200 Hz smooth on 07-12) — watch it.
- RViz tip: slam_toolbox publishes `/map` transient-local; RViz's Map display defaults to Volatile
  durability and misses an already-latched map if started late — set Durability to Transient Local.

Vehicle-day findings (2026-07-13, sixth on-vehicle session — 12th mapping attempt, log `output12.txt`):
- **The rev5 deploy worked**: can_odom started with the new defaults (startup log shows
  `speed_topic=/beemobs/FB_VehicleSpeed ... steer_gain=-0.02322 ... (kalibre 2026-07-13)`), IMU gyro yaw
  went active, the `map` frame existed (RViz Global Status OK, Fixed Frame map), and **two posegraphs
  were serialized for the first time** (`pist_haritasi_2/3.posegraph`, persisted via the
  `/home/smart/Permanent/maps` volume).
- **New root cause found — `/scan` topic collision**: the host sensor launch's `velodyne_laserscan_node`
  also publishes `/scan` (single ring, variable 897/898 readings). slam_toolbox consumed *that* stream,
  registered its karto sensor expecting 898 readings, and then silently rejected nearly every scan
  ("LaserRangeScan contains 897 range readings, expected 898" spam) — so the height-windowed
  `pointcloud_to_laserscan` output never fed slam at all (its fixed-length 723-bin scans never appear in
  the karto log), and the RViz Map stayed width/height 0. The `/scan` QoS-incompatibility warnings (rviz
  and p2l) were symptoms of the same collision. **Fixed 2026-07-13 in the workspace**: both `pist_*_real`
  launches remap p2l output to **`/scan_bee1`** and both `slam_toolbox_pist*_real.yaml` configs set
  `scan_topic: /scan_bee1` (sim configs untouched). On the vehicle, verify `ros2 topic hz /scan_bee1`
  (~10 Hz) before starting a mapping run, and point any RViz LaserScan display at `/scan_bee1`.
- Operational: typing `exit` in the `docker run -it` shell **stops the container** (a later
  `docker exec` failed with "is not running") — restart with `docker start robotaksi_container`, or run
  the container detached and use `docker exec` for shells. Map files don't need the container at all:
  the volume means they live at `/home/smart/Permanent/maps` on the host. The tar-path case-sensitivity
  trap (`permanent` vs `Permanent`) bit again, and `/imu/data` is still ~50 Hz bursty (was 200 Hz on
  07-12) — still unexplained. can_odom's Ctrl+C shutdown traceback (`rcl_shutdown already called`) was
  cosmetic and is now guarded with `rclpy.ok()`.
- Still pending from session 5's checklist (not observed in this log): the driven ~10 m odometry check
  (`tf2_echo odom base_link` x advancing) and the left-turn sign check on the steering gain.

Vehicle-day findings (2026-07-13, seventh on-vehicle session — 13th attempt, log `output13.txt`):
- **The container was started with a wrong `docker run`**: `--ipc=host` missing and the maps volume
  mounted as lowercase `-v /home/smart/permanent/maps` — Docker silently auto-created that path (on the
  tmpfs overlay, wiped on reboot), so serialized maps would land in the wrong, non-persistent folder.
  Without `--ipc=host`, Fast DDS shared memory partially fails: `/velodyne_points` reached the container
  but `/imu/data` (fine at ~50 Hz on the host) never did — `can_odom` stayed on the tan(steer) fallback
  the whole session ("IMU verisi yok/bayat", never recovered). Always use the documented run command;
  prefer `docker run -d ... tail -f /dev/null` + `docker exec` shells so `exit` can't stop the container.
- The `/scan_bee1` "incompatible QoS (RELIABILITY)" warning was almost certainly RViz's LaserScan
  display still on its default Reliable before being switched to Best Effort (its subscription showed
  BEST_EFFORT later). slam_toolbox's own scan subscription is compatible with p2l (proven by the sim
  pist setup working with the same pair). Decisive check when the stack is up:
  `ros2 topic info /scan_bee1 -v` → 1 publisher (p2l, BEST_EFFORT) + subs slam_toolbox and rviz.
- Operational repeats: every `ros2 topic hz /scan_bee1` was Ctrl+C'd within ~1 s (before even the
  "not published yet" warning) — all inconclusive; wait 10-15 s. In one foreground attempt bringup was
  Ctrl+C'd *before* launching slam — they must run simultaneously (slam needs base_link->velodyne).
  The `docker exec -d` pattern (bringup + slam detached, logs to /root/*.log) survives wifi drops and
  is the way to run the stack when tmux isn't in the image.

Vehicle-day findings (2026-07-14, eighth on-vehicle session — 14th attempt, log `output14.txt`):
- **FIRST REAL MAP.** With the `/scan_bee1` fix + correct `--ipc=host` run command, mapping finally
  produced a genuine map: `pist_haritasi_4.posegraph` **47.9 MB** / `.data` **4.1 MB** (vs the empty
  ~8 KB / 1.3 KB skeletons of every prior attempt — those had zero scan nodes). RViz showed a real
  OccupancyGrid (Map Status OK, ~1535×1637 @ 0.05 m ≈ 77×82 m) with LaserScan on `/scan_bee1` Status OK.
  IMU was back to a healthy **200 Hz** this session (the `--ipc=host` shared-memory path fixed the
  container-side IMU starvation; can_odom got real gyro yaw). Serialized via
  `/slam_toolbox/serialize_map` to `/root/maps/pist_haritasi_4` (result=0).
- **"Map froze after ~5 min of good mapping" — almost certainly slam falling behind, NOT a sensor
  death.** The session's rosbag proves every raw sensor kept flowing for the full 8.9 min: `/scan`
  10.0 Hz, `/imu/data` 200 Hz, CAN 7–50 Hz — no dropout. So the map ceasing to grow points to
  slam_toolbox scan-matching falling behind as the graph bloated (the documented "queue is full" /
  large-map issue): new nodes stop being added, the map visually freezes though scans still arrive.
  Decisive check on the *slam* stdout: `queue is full` (slam behind → keep the lap single/short/
  constant-speed; 47 MB is already at the upper edge) vs `Velodyne poll() timeout` (sensor died — the
  bag does NOT support this). Not fully resolved yet; next run, watch the slam log live.
- **Record `/velodyne_points`, not `/scan`, in the mapping bag.** This session's bag captured `/scan`
  (host single-ring laserscan) plus `/imu`+CAN, but NOT `/velodyne_points` or `/scan_bee1` — so it
  can't be replayed through our p2l→`/scan_bee1` chain to re-map offline. With `/velodyne_points` in the
  bag we could re-run p2l+slam at the desk and tune mapping without the vehicle. Use:
  `ros2 bag record -o /root/maps/pist_$(date +%H%M) /velodyne_points /imu/data /tf_static
  /beemobs/FB_VehicleSpeed /beemobs/FeedbackSteeringAngle /beemobs/FB_MotorDriver`.
  **Do not record `/tf`** (revised 2026-07-17): the ZED wrapper may broadcast its own
  `odom -> base_link` (see the ZED `publish_tf` item under the 2026-07-17 session), which on replay
  would fight the `can_odom` odom the chain is supposed to regenerate — tf2 does not error on two
  broadcasters of one edge, last write just wins and odometry jumps. Raw CAN + IMU are in the bag, so
  TF is reproduced at the desk by replaying into bringup (static `base_link->velodyne`) + `can_odom`,
  exactly mirroring the sim `pist_*` chain. `/tf_static` is still worth recording (latched, a few KB,
  documents the offsets the vehicle actually ran) but must not be replayed alongside bringup, which
  publishes the same static frames.
- tmux is now baked into the deploy image (2026-07-13 Dockerfile change: `tmux nano less`).
- **`docker run` killed the HOST's own ROS topics too (2026-07-14)** — the decisive clue: every sensor
  `hz` was fine on the host *until* the container started, then **both** host and container went silent.
  Since `--network host` + `--ipc=host` means the only shared mutable resource is **`/dev/shm`**, and
  Fast DDS keeps its shared-memory segments there, the cause is an ownership/permission clash: the
  container runs as **root** while the host drivers run as **smart**, and Docker's default `umask 0022`
  makes root create the SHM segments `0644` — the host's `smart` processes then cannot write to them and
  their own publishing stalls. (It worked on 07-12/07-14 because `/dev/shm` happened to be clean; the
  root-owned segments accumulate.) **Fixed in the Dockerfile: `umask 0000`** so segments are created
  `0666` — verified in-image (`bash -c`/`-lc`/`-ic` all report 0000, and a file touched in `/dev/shm`
  comes out `-rw-rw-rw-`). Note **`.bashrc` alone is NOT enough** — it only covers interactive shells;
  `docker exec -d ... bash -c` is non-interactive, so the image sets all three: `/root/.bashrc`,
  `/etc/profile.d/00-umask.sh`, and `ENV BASH_ENV=/etc/umask_ros.sh`. Do **not** "solve" this by
  switching to Cyclone — Fast DDS is the deliberate, working choice that matches the vehicle host.
  Recovery if it happens again: `docker rm -f` the container, `pkill -9` the host sensor launch,
  `sudo rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_*`, restart host sensors. Verify after starting
  a container that `ls -la /dev/shm | grep fastrtps` shows `-rw-rw-rw-`, not `-rw-r--r--`.
- Still pending: verify `pist_haritasi_4` in localization mode
  (`pist_localization_real.launch.py map_file:=/root/maps/pist_haritasi_4`), and the driven ~10 m odom
  / left-turn steering-sign checks.

Vehicle-day findings (2026-07-17, ninth on-vehicle session):
- **Inside the container the maps volume is `/root/maps`; `/home/smart/Permanent/maps` is the HOST-side
  path only.** A mapping bag was recorded from a container shell with `ros2 bag record -o
  /home/smart/Permanent/maps/pist_$(date +%H%M)` — `ros2 bag` happily created that (nonexistent) path in
  the container's own writable layer and wrote there, so nothing ever appeared in the host's
  `Permanent/maps` and the recording looked like it had failed. Same family as the `permanent` vs
  `Permanent` case trap: a wrong path is silently *created*, never an error. **Any `-o` / `serialize_map`
  target typed inside the container must start with `/root/maps`.**
  - Recovering data stranded in a container's layer: `docker cp <container>:<path> <host path>` (works on
    a stopped container), or `docker exec ... mv <path> /root/maps/`. `docker run` does **not** help — it
    makes a *new* container that cannot see the old layer, and the habitual `docker rm -f && docker run`
    destroys the data. Do the copy before refreshing the container.
  - The layer is not durable anyway: host root is overlayroot, so if `/var/lib/docker` isn't on a
    persistent mount, a power cycle takes the container's writable layer with it. Only `/root/maps`
    (i.e. the volume) is safe.
- **UNVERIFIED, check before the next mapping/localization run: does the ZED wrapper broadcast
  `odom -> base_link`?** The zed-ros2-wrapper default is `pos_tracking.publish_tf: true` with
  `base_frame: base_link` / `odometry_frame: odom` (and `publish_map_tf` for `map -> odom`) — i.e. the
  exact edges `can_odom` and `slam_toolbox` own. Two broadcasters of one edge is **not** a tf2 error;
  last write wins, so localization would silently jump between the ZED's visual odom and our CAN
  dead-reckoning. This affects the **live race stack**, not just bag replay. Mapping succeeded on
  2026-07-14 with the host ZED up, which is weak evidence the ZED's TF is already off or prefixed
  (`zed_camera_center` etc.) — weak, not proof. Check on the vehicle:
  `ros2 run tf2_tools view_frames` (look at the broadcaster of the `odom -> base_link` edge),
  `ros2 topic info /tf -v | grep -i "node name"`, `ros2 param get /zed/zed_node pos_tracking.publish_tf`.
  If the ZED owns that edge, turn its `publish_tf`/`publish_map_tf` off in the host's ZED launch — our
  chain must be the only broadcaster of `map -> odom` (slam_toolbox) and `odom -> base_link` (can_odom).
  The ZED is a perception sensor for us (`lane_follower`/`tabela_tespit`), never a TF/odometry source.

Vehicle-day findings (2026-07-18, tenth on-vehicle session — live PID/throttle chain):
- **The real PID target topics are `std_msgs/Float64`, BOTH of them.** Confirmed from source
  (`smart_can_stuff/include/smart_can_stuff/pid_controller.hpp`: `setValueCallback` takes
  `Float64::SharedPtr`, single `PIDController` class used by both `steering_pid_node` and
  `speed_pid_node`). Our `neuravix_control_node_real.py` published `Float32` → DDS type mismatch, so the
  PID's `set_value` subscription silently never matched (no error; `ros2 topic echo` reports "contains
  more than one type"). **Fixed**: the real node now publishes both targets as `Float64` by default,
  with a `targets_float64` param (false → Float32) as an escape hatch. This closes the CLAUDE.md open
  question that had steering PID's type "unverified" — it's Float64 too, so the single param is enough.
- **TWO CAN name-traps, not one — both confirmed live via `ros2 node info`, both fixed with our-side
  relays (zero touch to the vehicle team's files):**
  - **Feedback (input):** `can2ros` publishes speed feedback on `/beemobs/FB_VehicleSpeed`, but
    `speed_pid_node` subscribes `/beemobs/fbvehiclespeed` (its `feedback_value_topic` param in
    `pid_params.yaml`). No match → PID never closes the loop. Bridged by
    **`bee1_description` node `speed_fb_relay`** (`FB_VehicleSpeed → fbvehiclespeed`, type
    `Fbvehiclespeed`).
  - **Throttle (output):** `speed_pid_node` publishes `/beemobs/rcthrtdata` (its `output_topic`), but
    `can_handler` (ros2can) **subscribes `/beemobs/RC_THRT_DATA`** (`ros2 node info /can_handler`:
    Subscribers list has `/beemobs/RC_THRT_DATA`, and `/beemobs/rcthrtdata` showed Publisher 1 /
    Subscription 0). ROS 2 topic names are case-sensitive → the two never meet, throttle never reaches
    CAN. Bridged by **`bee1_description` node `throttle_relay`** (`rcthrtdata → RC_THRT_DATA`, type
    `Rcthrtdata`). **This corrects an earlier wrong call** ("output side probably fine, matches at
    source") — the `.cpp` topic string was password-protected and had been assumed to match `rcthrtdata`;
    it doesn't. Both relays are needed together; `can_handler` then converts `RC_THRT_DATA` → `/to_can_bus`.
  - **⚠️ The two relays + a live `speed_target_value` = the throttle arm.** With `speed_fb_relay` up and
    a nonzero speed target flowing, the instant `throttle_relay` connects the PID output to `can_handler`
    the vehicle actually accelerates. Start `throttle_relay` LAST, area clear, driver on brake. Killing
    `throttle_relay` (Ctrl+C) drops the `RC_THRT_DATA` publisher and cuts throttle; `/safety/emergency_stop`
    remains the hard stop.
- **`AutonomousHeardBit` is NOT an enable we must send** — it's a `can2ros` *publisher* (veh→auto status;
  `ros2can.hpp`'s TX path has no heartbeat subscriber). The signal path (`rc_unittoOmux`) actuating
  physically already proved the ECU accepts our autonomous commands without us publishing any heartbeat.
- Both relays follow the `odom_relay`/`gps_relay` pattern (params `input_topic`/`output_topic`/
  `best_effort`, default reliable), installed in `bee1_description`'s CMakeLists. Run:
  `ros2 run bee1_description speed_fb_relay` / `ros2 run bee1_description throttle_relay`.

Control-log analysis (2026-07-20, bag `~/maps_son/kontrol_bag/debug_control5`, 17.9 min — lane_follower
from t=0, obstacle_lidar added at t=735 s, no `tabela_tespit`, emergency never fired):
- **`steer_auto_offset` was a ratchet and is now OFF by default.** The node restarted 5× during the run
  and each auto-capture took whatever the (not-centered) wheel read as "straight": offsets walked
  `-1 → -3 → -7 → -8 → -16`. After the last restart, FSM `steering_angle=45` (straight) published target
  **-16** — near the measured full-left lock (-21) — i.e. "drive straight" would circle. **Fixed
  2026-07-20**: `steer_target_offset` default `0.0 → 2.0` (the measured straight raw value),
  `steer_auto_offset` default `True → False`, and if auto is re-enabled a capture deviating more than
  `steer_auto_offset_max_dev` (5.0) from that reference is **rejected** with a warning instead of applied.
- **Steering targets could exceed the mechanical lock.** The `steer_delta_left/right` clamp bounds only
  the *deviation*; the offset is added afterwards, so a drifted offset pushed targets to **-34.75** and
  feedback to **-37/-38** (full-left is -21) — the steering motor grinding against its stop. **Fixed**:
  new params `steer_raw_min`/`steer_raw_max` (-21/26) clamp the **final** target.
- **Slalom could never terminate.** Two episodes of 18.4 s and 24.0 s in `OBSTACLE_AVOID` with the
  vehicle at 0 km/h and `front` stuck at 1–3 m: each finished weave re-armed a new weave in the opposite
  direction, sawing the wheel 70↔20 indefinitely. **Fixed in `decision_brain.py`**: `slalom_max_weaves`
  (3) + an `avoid_blocked` latch — after the cap the FSM drops to `OBSTACLE_STOP` and refuses to re-enter
  slalom until `front > slow_distance` actually clears. Normal, passable obstacles still slalom exactly
  as before (verified: 3 short weaves earlier in the same bag behaved correctly).
- **Obstacle sector data is noisy / partly bogus** (not yet fixed): `front` flips 99 ↔ 1.1 m within a
  second (this caused LANE_FOLLOW/AVOID flip-flop), and `left` sits at exactly 1.20 m for minutes — a
  fixed structure or the vehicle's own body inside the sector, which makes `_pick_avoid_direction` never
  choose left. Wants a k-of-n temporal filter in `obstacle_lidar_node.py` and a self-body/geometry check.
- **A second publisher exists on `/beemobs/AUTONOMOUS_BrakePedalControl`**: 9502 msgs `per=0` from our
  node (20 Hz) plus 60 msgs with `per=31…83` from someone else (ours only ever sends 0 or
  `brake_per_on=100`). Our 20 Hz stream overwrites that external brake command within 50 ms — worth
  resolving before relying on any non-autonomous brake path.

Lane-follower calibration (`lane_follower_node.py`, 2026-07-19/20):
- **`err_offset` (px) is the zero-point calibration** — the BEV `src_pts` plus the ZED's lateral mount
  offset mean the measured error is nonzero even with the car physically centered in the lane. Procedure:
  drive a straight stretch with the car visually centered, read **`AvgErr`** off the overlay (a 3 s
  rolling mean, drawn next to a **green reference center line** — yellow-on-green means zero error), then
  restart with `-p err_offset:=<current + AvgErr>`. **The parameter is read once at startup** (no
  `add_on_set_parameters_callback`), so `ros2 param set` does nothing — restart per attempt.
- `err = 0` is forced while `lane_lost`, so the offset can't drag the neutral 45 output off-center when
  there are no lanes to follow.
- **Single-lane frames used a wrong half-width (fixed 2026-07-21).** When only one lane fit exists the
  center is estimated as `fit ± half_lane`, which used the *theoretical* `0.30*img_w = 192 px` derived
  from `dst_pts`. On the real track the overlay's measured `LaneW` is ~**300 px** (half ≈ 150), so
  single-lane frames placed the lane center ~42 px to the wrong side — a systematic pull toward the
  missing line (bags 6/7: mean steering 47.7/48.9 while moving vs 43.9 in bag 5; the screencast shows
  `Error: -114px` on a right-line-only frame vs `-21px` with both). Now `_half_lane()` uses the measured
  `lane_w_px/2` (clamped to `0.15…0.40*img_w`) and falls back to the theoretical value only until the
  first measurement lands.
- **`lane_width_m` is display-only** — the PID is fed the raw pixel error; `lane_width_m` only converts it
  for the `Error: Npx (+X.XXm)` overlay text, using `lane_w_px` (measured whenever both lane fits exist,
  EMA-smoothed, held through single-fit frames). Default changed `3.5 → 3.0` on 2026-07-20: the real
  track's white-line spacing was measured at ~**2.96 m** (varies in places). Sim keeps CARLA's 3.5 m via
  `-p lane_width_m:=3.5`. Because the track width genuinely varies, **calibrate `err_offset` in pixels**,
  not against the metre readout.

Deploy hygiene (2026-07-20): `~/robotaksi_deploy` was found **5 files stale** (a whole day of lane work
plus `can_odom_node.py`, `ekf_odom_real.yaml` and both `pist_*_real` launches missing). `./export_deploy.sh`
is not optional — run it (or `--dry-run` first) before every `docker build`, and remember the image only
reaches the vehicle after `docker build` → `docker save` → `docker load` → `docker rm -f` + `docker run`
(loading over a running container keeps the old code). Image rebuilt 2026-07-20 with all of the above.

Code changes, 2026-07-21 (all built, deploy-synced and baked into `robotaksi_humble:latest`; the tar
`~/robotaksi_deploy/robotaksi_humble.tar` was regenerated after the last of them):

| file | change | why |
|---|---|---|
| `neuravix_control_node_real.py` | `steer_target_offset` default `0.0 → 2.0`; `steer_auto_offset` default `True → False`; new `steer_auto_offset_max_dev` (5.0) rejects an out-of-range auto capture | auto-capture ratcheted the "straight" value across restarts (`-1→-3→-7→-8→-16`) |
| `neuravix_control_node_real.py` | new `steer_raw_min` / `steer_raw_max` (-21/26) clamp the **final** target after the offset is added | targets reached -34.75, feedback -37/-38, motor grinding on the stop |
| `decision_brain.py` | `slalom_max_weaves` (3) + `avoid_blocked` latch; `_obstacle_stop_control` and `obstacle_event` both honour the latch, cleared when `front > slow_distance` | slalom re-armed forever (18.4 s / 24.0 s episodes at 0 km/h) |
| `lane_follower_node.py` | `lane_width_m` default `3.5 → 3.0` | real track's white-line spacing measured ≈2.96 m (display-only value) |
| `lane_follower_node.py` | new `_half_lane()` — single-lane center estimate uses measured `lane_w_px/2`, clamped `0.15…0.40*img_w`, theoretical 192 px only as fallback | 192 px vs the real ~300 px `LaneW` biased single-lane frames ~42 px |
| `obstacle_lidar_node.py` | full rewrite (teammate's version, reviewed + one fix) — see the dedicated section below | noisy/meaningless sector data in the 07-20 bags |

Verified before shipping: brain unit-scenarios (infinite-weave case now stops at 9 s → `OBSTACLE_STOP`,
clears when the road opens, normal 3-phase slalom unchanged), `_half_lane()` mapping table, live node
publishing `steering_target_value = 2.0` at rest, and `grep` inside the built image confirming all five
changes are in the installed files.

Teammate merge, 2026-07-21 16:00 (from `~/carla-ros2-ws.tar`, reviewed file-by-file and applied to the
workspace — **not yet rebuilt into the deploy image**, see below):

| file | change | why |
|---|---|---|
| `decision_brain.py` | obstacle threshold split in two: `slow_distance` (5.0) now only slows and **stays in lane**; new `avoid_distance` (3.0) + `avoid_confirm_time` (0.5 s) gate entry into slalom | in the `algi2/3/4` bags 7 of 9 slalom entries fired at front 4.45–4.99 m, i.e. right at the old single threshold — a 3 s open-loop manoeuvre for something still 5 m away |
| `decision_brain.py` | slalom phases are **distance-based** (`slalom_out_distance` 2.0 m, `slalom_weave_distance` 4.5 m); time survives only as a safety ceiling (`slalom_max_time` 12 s) and as the fallback when no motion source is fed (`_motion_ok` False ⇒ old time behaviour, so sim/odometry-less runs are unchanged) | measured on the vehicle: an 18.0 s slalom covered 3.12 m, and one 6.0 s weave covered 0.00 m — the timer completed phases the vehicle never drove |
| `decision_brain.py` | new `update_motion(speed_mps=/distance=)` feeds travelled distance; stall guard (`stall_timeout` 4 s / `stall_min_distance` 0.25 m) aborts to `OBSTACLE_STOP` | stop sawing the wheel when the manoeuvre plainly isn't happening |
| `decision_brain.py` | at each finished weave the direction is re-asked of `_pick_avoid_direction()` instead of blind `right if left else left`; both sides closed ⇒ `OBSTACLE_STOP` | the old alternation never consulted the lidar and could steer into a closed side |
| `decision_brain.py` | `get_decision()` gains `avoid_phase` + `lane_blend` (0.15 escape / 0.55 return) | lane data was valid 30–97 % of slalom time but `OBSTACLE_AVOID` published a hardcoded 70/25/20/65 and ignored it |
| both control nodes | consume `lane_blend` during avoidance (clamped 15..75) and call `update_motion` — real node from `/odometry/filtered` travel or CAN `Fbvehiclespeed.fb_reelvehiclespeed_kmh` × `speed_fb_scale` (0.31627, same calibration as `can_odom`), sim node from CARLA speed | keeps sim and vehicle on the same code path |
| `bee1_robotaxi.urdf.xacro`, `pointcloud_to_laserscan_real.yaml`, `obstacle_lidar_node.py` | LiDAR mount height 0.62 → **1.35 m** and the derived height windows | see the "(3) The 0.62 m mount height was WRONG" item above — verified independently against two bags before applying |

**Two hunks from that tar were deliberately rejected**: (a) `obstacle_lidar_node.py`'s `_on_params`
reverting to "reject every unknown parameter" (breaks `use_sim_time` — the fix documented below), and
(b) `tabela_tespit_node.py` pointing the model back at `best4.pt` (their copy predates `best5.pt`,
2026-07-21 14:26; the workspace now loads `best6.pt`, 2026-07-21 16:15). Also note `obstacle_lidar`'s `lidar_topic` default
is now `/velodyne_points`, so **CARLA runs must pass `-p lidar_topic:=/carla/ego_vehicle/lidar
-p lidar_height:=1.6`** — forgetting either fails safe (0,0,0 = stop) or trips the mount-height ERROR
rather than silently reporting a clear road.

Verified after the merge: scoped build of both packages, brain scenarios (4.5 m ⇒ slow only; 2.8 m
needs the 0.5 s hold before `OBSTACLE_AVOID`; distance-driven escape→return→lane; stall ⇒
`OBSTACLE_STOP`+`avoid_blocked`; `4,0,0,0` ⇒ stop with brake; both-sides-closed weave ⇒ stop, no blind
flip; `_motion_ok` False ⇒ time fallback still runs), real control node 6 s smoke test with
`auto_ignition:=false` (raw steer limits [-21,26] and offset 2.0 intact), and `obstacle_lidar` startup
showing `z=[-1.13,0.77] (lidar_height=1.35 → ground [0.22,2.12])` plus `ros2 param set use_sim_time`
succeeding and `corridor -1.0` being rejected. Phase transitions cost one 50 ms tick (the new phase's
steering applies on the next loop) — harmless, but it is why a single-tick test looks one step behind.

**Deploy image rebuilt 2026-07-21 17:34** (supersedes the 17:15 build, which lacked the BEV
recalibration below): image ID `d75c579a8679`, tar 4,220,516,352 bytes, SHA-256
`907b1ad2de61d08915d5c06935bacb86d01c312bfbbbb60708f508b0bf87b1a5`, new `src_pts` verified inside the
image. Earlier note kept for reference — **deploy image rebuilt 2026-07-21 17:15** with everything in this and the following sections:
`./export_deploy.sh` synced, `docker build` + `docker save` done. New image ID `24b47268bbaf`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` 4,220,513,792 bytes, SHA-256
`197fd8ac473eb929c4fd6af0dea7d96a4aa937872e70d153561f8f5bcb9bfd64`. Verified *inside* the built image:
`avoid_distance=3.0`, `avoid_abort_distance=1.0`, `slalom_max_time=3.0`, `stall_timeout=2.0`,
`weave_gap_time=1.5`, `curve_lane_dev=6.0`, `lidar_height=1.35`, URDF `lidar_z=1.350`, `_check_motion`
present. The previous `sonclaude` 10:32 image is preserved as the rollback copy at
`/home/neuravix/sonclaude/robotaksi_humble.tar` (SHA-256 `7db866053a…`) — do not overwrite that one.
**The vehicle still runs the old image until `docker load` + `docker rm -f` + `docker run` are done
there**; loading over a running container keeps the old code.

Slalom rhythm + curve suppression (`decision_brain.py`, 2026-07-21, operator-requested — priorities are
**slalom and cornering**, localization explicitly deprioritised so the map invalidation above is accepted):
- **No slalom in curves.** In a bend the track edge/barrier enters the *straight* ego corridor
  (`|y| < corridor`, up to 30 m) and reads as a real obstacle — at a ~15 m radius with the barrier 1.5 m
  off centreline it lands at ~4.9 m, right in the trigger band, so the car would start an open-loop weave
  mid-corner and leave the track. Bending the corridor would mean feeding steering into
  `obstacle_lidar_node`; instead the brain detects the curve from the lane angle it already receives:
  `_note_lane_angle()` keeps an EMA of `|lane_angle - 45|` and `_in_curve()` is true while it exceeds
  `curve_lane_dev` (8.0) plus `curve_hold_time` (1.0 s) of hysteresis. In a curve slalom **entry** is
  suppressed; the car still slows and still stops inside `stop_distance`, so a genuine obstacle is handled
  safely — only the swerve is withheld. **The EMA is frozen while in `OBSTACLE_AVOID`** — during a weave
  the wheel is deliberately hard over and the lane looks skewed, which would otherwise self-suppress
  every following weave.
- **Weave → lane-follow → weave rhythm.** Previously a finished weave immediately armed the next one and
  the car never settled into the lane. `_weave_finished()` now returns to `LANE_FOLLOW` for
  `weave_gap_time` (1.5 s) and lets `obstacle_event` re-arm afterwards if the obstacle is still there;
  direction is re-asked of the lidar at that point. Measured cycle at 4 km/h: 3.0 s weave (1.5 escape +
  1.5 return) → 1.5 s lane follow → repeat.
- **`slalom_max_time` 12.0 → 3.0 s, applied per phase** (`max_time*0.5` ends escape, `max_time` ends the
  weave). A single shared ceiling would end the weave the same tick the escape phase timed out, leaving
  the car displaced sideways without ever running the return phase. Distance remains the primary
  completion test; time is the ceiling.
- **`stall_timeout` 4.0 → 2.0 s** — it must stay *below* `slalom_max_time` or the weave always hits the
  3 s ceiling first and the stall guard becomes dead code. At 4 km/h, 2 s ≈ 2.2 m travelled, so the
  0.25 m `stall_min_distance` is a comfortable "not moving".
- **Zig-zag tie-break.** With both sides equally open `_pick_avoid_direction()` always returned "left",
  so a symmetric cone slalom weaved the same way every time. When the two clearances differ by at most
  `side_tie_margin` (0.5 m) it now picks the opposite of `_last_weave_direction`; a real asymmetry still
  wins, so this does **not** reintroduce the blind alternation removed earlier (that one steered into
  closed sides because it never consulted the lidar).
- `slalom_count` is deliberately **not** reset when a weave re-arms after the gap — resetting there would
  make `slalom_max_weaves` unreachable and disable the infinite-weave guard. It resets when the road
  actually opens (`front >= slow_distance`) and in `_end_avoidance`/`_abort_avoidance`.

`algi7/8/9` analysis (2026-07-21 session, bags recorded against the `sonclaude` 10:32 image, i.e.
**before** any of the changes above):
- **Analyse the ZIP copy (`~/algı.zip`), not the first `cp` into `~/maps_son/kontrol_bag`.** That first
  copy was truncated: `algi9` lost half its bytes and its `metadata.yaml`, `algi8` came out 170 s instead
  of **270.9 s**. A partial-scan recovery of the truncated `algi8` produced a **wrong conclusion** —
  it showed zero `RC_THRT_DATA` messages and `FB_VehicleSpeed` flat at 0, which read as "the throttle
  relay was down and the vehicle never moved". The intact bags say the opposite: RC_THRT_DATA present in
  all three (1112 / 717 / 1439 msgs, pedal 45–85) and the vehicle **did** drive (moving 21 % / 7 % / 30 %
  of the time, max 4 km/h, trip counter 0→4135 in each). Lesson: a truncated rosbag does not error, it
  silently answers a different question — check `duration` against `metadata.yaml` before drawing
  conclusions, and prefer an archive (zip/tar) over `cp` for moving bags off the vehicle.
  Corrupt-bag recovery is still worth knowing: open **without** `immutable=1` (that flag alone reports a
  readable file as "malformed"), probe for the rowid ceiling by doubling instead of `MAX(rowid)`, and read
  in rowid windows catching `DatabaseError` per window (`scratchpad/recover.py`).
- **The `_check_motion()` watchdog added to `neuravix_control_node_real.py` therefore rests on a
  misdiagnosis, but is kept**: it is cheap and the failure it describes (nonzero speed target published
  while fresh CAN speed feedback stays 0) is real and has bitten this project in other forms. It logs an
  ERROR naming `throttle_relay` after `motion_watchdog_sec` (5 s), and stays silent when speed feedback is
  absent (can't distinguish "not moving" from "no data"), when the target is 0, and when the car moves.
- **REAL BUG FOUND — the FSM kept weaving with an obstacle inside braking distance.** `obstacle_event`
  returns early while the state is `OBSTACLE_AVOID` (new distances land in the fields but no decision is
  taken) and `_obstacle_avoid_control` never tested any stop threshold — so once a weave started, nothing
  could brake it until the weave ended. In `algi9` that meant **8.6 s cumulative with `front` under
  2.2 m while slaloming**, across three episodes whose closest readings were 1.61 / 0.49 / **0.36 m**.
  Fixed: `_obstacle_avoid_control` now aborts to `OBSTACLE_STOP` via `_stop_for_close_obstacle()` when
  `front < avoid_abort_distance`.
  - **`avoid_abort_distance` (1.0 m) is deliberately much tighter than `stop_distance` (2.2 m).** Slalom
    by definition passes close to things; aborting at 2.2 m means the car can never round a cone it has
    approached — it stops in front of it and stays there (exactly `algi9` t=114.6: front 0.36 m, speed 0,
    stuck). At 1.0 m the 1.61 m pass continues and the 0.49/0.36 m ones stop.
  - `_stop_for_close_obstacle()` deliberately does **not** latch `avoid_blocked` (unlike
    `_abort_avoidance`): the slalom did not fail, the car just got close. Without the latch,
    `_obstacle_stop_control` can start a fresh weave after `obstacle_replan_wait` once a side is open,
    instead of waiting for the road to clear past 5 m.
- **The 5.0/3.0 threshold split is validated, and my earlier worry that 3.0 m would never fire was an
  artifact of the truncated bag.** In the intact `algi9`, `front` is under 3.0 m for 25.6 % of frames and
  the new trigger (front < 3.0 with an open side) would fire on **13.5 %** of frames — slalom still
  happens. All the old-code `OBSTACLE_AVOID` entries in `algi8` fired at front 4.59–5.09 m, the same
  "triggered at the old 5 m threshold" signature as `algi1..4`.
- **Obstacle noise filtering confirmed working**: `front` flipped 99↔obstacle once per ~170 s, versus the
  sub-second flapping that motivated the rewrite.
- **Curve detection was measuring the wrong thing** and is now fixed. The lane output's zero point drifts
  per run — `algi7` mean 48.2 (+3.2), `algi8` 43.9 (−1.1), `algi9` 46.8 (+1.8) — so a fixed-45 baseline
  spent most of the budget on bias and `|angle−45| > 8` fired on 0.00 % of frames: dead code.
  `_note_lane_angle()` now thresholds `curve_lane_dev` (6.0) on the gap between a fast EMA (0.30) and a
  slow per-run baseline EMA (0.01), which is immune to the drift. On the intact bags the new metric
  exceeds 6.0 on only 1.05 / 0.46 / 0.88 % of frames, so it will not smother legitimate slalom.
  **Still needs a bag with real corners to calibrate** — none of these three contains one.

Verified: persistent zero-point drift is not read as a curve while a sustained 12-unit swing is;
curve suppresses / straight road slaloms / genuine close obstacle in a curve still stops;
the weave-gap-weave cycle observed over a simulated 20 Hz run; escape 70 → return 25 steering per phase;
zig-zag alternates left→right on symmetric clearance but stays right when left is closed; stall fires at
2 s; `4,0,0,0` stops; time fallback still works when no motion source is fed; the 3-weave cap still
latches `avoid_blocked` across gaps. Note phase transitions cost one 50 ms tick (the new phase's steering
lands on the next loop) — harmless, but single-tick tests look one step behind.

`algi1..4` safety review (2026-07-21, based on `~/Downloads/OTURUM_RAPORU_2026-07-21.txt` and an
independent SQLite/CDR replay of all four bags):
- **The report's main diagnosis is confirmed.** Old lane outputs occupied only 37..57, while obstacle
  slalom commanded FSM angles 20..70 and therefore raw steering targets -16.75..20.75. Measured
  target→feedback lag was 0.35 / 0.80 / 0.75 / 0.70 s (`algi1..4`). Overlays contain false narrow
  pairs around 109..151 px and an `algi1` branch jump (`Error=-139`, `LaneW=386`); these are perception
  geometry faults, not a need for more steering authority.
- **The lane geometry/validity experiment was rolled back.** The active `sonclaude` source has none of
  the 250..520 px geometry gate, fit-jump checks, heading gain or `LaneValid` output introduced during
  the later review. ID-2 is again `2,<steer>` and the real wrapper has no lane-loss braking override.
- **Obstacle avoidance is the older direct flow.** There is no `obstacle_avoid_enabled` parameter,
  `OBSTACLE_APPROACH`, 5→2 m trigger layer or single-pass lock. `front < 5 m` plus an open side corridor
  immediately enters `OBSTACLE_AVOID`; each weave is 3 s (1.5 s out + 1.5 s recover). The earlier
  `slalom_max_weaves=3` / `avoid_blocked` infinite-oscillation guard remains present.
- **The later steering slew limiter was rolled back.** The absolute raw mechanical clamp (-21..26)
  remains, but `steer_slew_rate` and its temporary regression suite do not exist in this version.
- **Final deployment status (operator-requested restore):** `/home/neuravix/sonclaude/robotaksi_humble.tar`
  was copied atomically over `~/robotaksi_deploy/robotaksi_humble.tar` and loaded back as
  `robotaksi_humble:latest`. Workspace and deploy-staging copies of `decision_brain.py`,
  `lane_follower_node.py` and `neuravix_control_node_real.py` match the image source byte-for-byte.
  The restored tar is 4,132,538,880 bytes, SHA-256
  `7db866053a58470a7ff4a8a125b375482c767b05b6776c941a75ed0dd3d20711` (image created 10:32,
  tar timestamp 10:35). Scoped build and a 5 s real-node smoke test with ignition disabled pass.

`obstacle_lidar_node.py` rewrite (2026-07-21, teammate's version, reviewed and merged) — this changes
the **ID-4 contract**, so read this before touching the FSM's obstacle thresholds:
- **`left`/`right` changed meaning.** They used to be the *lateral* distance of the nearest point outside
  the corridor, which by construction could never be smaller than `corridor` — that is why the 07-20 bag
  showed `left` pinned at exactly 1.20 m for minutes and `_pick_avoid_direction` never chose left. Now
  all three values are **longitudinal clearance from the front bumper** in the corridor you would drive
  into: `front` (|y| < corridor), `left` (|y − side_offset| < corridor), `right` (|y + side_offset| <
  corridor). The brain's `safe_side_distance = 2.0` now reads as "≥2 m of room to swerve into", which is
  what it was always meant to be.
- **Consequence on a barriered track**: a continuous barrier fills the side corridor, so that side reports
  ~0 and the FSM will **not** slalom into it — it slows/stops instead (correct, but if slalom never
  triggers, check `side_offset`/`corridor` against the real track width first).
- **Still written for the old semantics**: `decision_brain`'s parking branches (`_park_search_control`
  `right > 3.5`, `_parking_control` `left/right > 4.0`) were authored when left/right were lateral gaps.
  They now mean "4 m of longitudinal room beside me", which is *not* the same test for finding a parking
  slot. Parking has never been exercised on the vehicle — revisit these thresholds before it is.
- **Noise filtering** (the 99 ↔ 1.1 m flapping): spatial — a sector needs ≥`min_points` (4) points and
  reports the k-th nearest, not the single nearest; temporal — the reported value is the
  `confirm_frames`-th smallest of the last `filter_window` frames (2-of-5), so one bad frame is dropped
  while *releasing* an obstacle needs a majority of clean frames (fails safe).
- **Fail-safe**: no cloud for `lidar_timeout` (0.5 s), an empty cloud, or an all-NaN cloud now publishes
  `0,0,0` (= stop), never stale `99`s. Silent driver death is the single most repeated failure on this
  vehicle, and the old node's "no data ⇒ 99 ⇒ road clear" was the worst possible response to it.
- Also new: geometry defaults derived from the URDF (corridor 0.70 from `body_width`, distances measured
  from the front bumper via `bumper_offset`, `side_x_min` at the rear bumper), height window derived from
  `lidar_height` (so the real vehicle needs no flag and **CARLA** passes `-p lidar_height:=1.6`), a
  near-field guard so an obstacle closer than `x_min` reports 0 instead of vanishing into 99, and a
  `set_parameters` callback so tuning at runtime actually works.
- **One fix applied to the submitted version** (and re-applied on 2026-07-21 when a teammate's copy
  reintroduced it — check this hunk on every merge): its parameter callback rejected every name it did not
  recognise, which would also reject infrastructure parameters (`use_sim_time`) and break
  `ros2 param set` / launch-time param passing for them. Unknown parameters are now passed through
  untouched; only known ones are validated. Verified with a 22-check harness (mixed-datatype Velodyne
  cloud, CARLA all-float32 regression, single-point and single-frame noise rejection, slow release,
  near-field guard, ground/ceiling rejection, barrier corridor, both fail-safe paths, runtime params).

Bag inventory (`~/maps_son/kontrol_bag`, 2026-07-20 session): `debug_control` / `2` / `3` have no
`/master` data; `debug_control_lane` / `lane2` are stationary lane-only runs; **`debug_control8` and
`debug_control9` are 0-byte — the recording never started** (foreground `docker exec` + wifi drop is the
likely cause). Always `ls -l` the bag directory ~15 s after starting a recording; a wrong or dead
recording is silent, never an error. Useful ones: `debug_control5` (17.9 min, control+obstacle),
`debug_control6` (3.7 min) and `debug_control7` (7.1 min, obstacle-heavy — 164 s + 40 s stuck in
`OBSTACLE_STOP`, the same noisy-sector root cause).

Disk temizligi + bag kurtarma (2026-08-19): `/home` **0 bayt** bosa dusmustu (bu yuzden o gun ~ altina
kopyalanan `bag_slalom.zip` ve `algı2.zip` yarim kaldi). En buyuk geri kazanim **docker**: build cache
42,6 GB (`docker builder prune -af`) + dangling imajlar 12 GB (`docker image prune -f`) -> toplam ~55 GB.
Docker kok dizini `/home/docker-data/docker`, yani docker `/home`'u yer, `/` bolumunu degil; `/` tarafinda
ise `/tmp/claude-1000` scratchpad'leri 4,5 GB tutuyordu. **`docker rmi` ile etiket kalkinca yer bosalmaz** —
katmanlar dangling kalir, `image prune` sart.
- **Yarim inen bag zip'i olu degil.** `algı2.zip`/`bag_slalom.zip` sadece **merkezi dizini** eksik
  (streaming zip); veri bloklari saglam. Kurtarma: yerel basliklardan (`PK\x03\x04`) uye adi + yontem
  (`method=8` -> deflate, 0 -> store) okunur, veri offset'inden EOF'a kadar `zlib.decompressobj(-15)` ile
  acilir. Boyle **`algi10`** tamamen kurtarildi (1,49 GB db3, 72.260 mesaj, 243,5 s, tum topic'ler okunur)
  ve artik `~/maps_son/kontrol_bag/algi10` altinda — baska hicbir kopyasi yoktu.
- **`kontrol_bag/algi9` artik saglam kopya** (723.886.080 bayt, 55.199 mesaj, `metadata.yaml` ile);
  onceki 347 MB'lik budanmis kopyanin uzerine `algı.zip`ten yazildi. Bu, CLAUDE.md'nin "ZIP kopyasini
  analiz et" uyarisini kapatir: zip'ler silindi, klasordeki kopyalar artik saglam olanlar.
- `~/asama0_48` (31 GB, ZED kayitlari) cope atilip bosaltilmis; ondan cikarilan **8162 kare** yalnizca bir
  `/tmp` scratchpad'inde duruyordu ve reboot'ta gidecekti -> `~/algi_asama_kareler/asama_full/` altina
  tasindi (cikarma betigi `cikar.py` ve ozet PNG'ler yaninda). Bozuk `bag_slalom.zip`ten kurtarilan
  parcalar `~/bag_slalom_kurtarma/` (db1/db2 `.db3.zstd` + `meta1.yaml`).
- Silinenler: acilmis dataset zip'leri (Tabela-Serit 5,2 G, full_model_dataset, 2x tabela dataset,
  `algı.zip`, `info_eda_pt.zip`), bozuk `algı2.zip`, eski imajlar `robotaksi:humble`/`ros:foxy`/
  `hello-world`. **Dokunulmayanlar** (operator karari): tum saha bag'leri ve CARLA kurulum tar.gz'leri
  (`Downloads/CARLA_0.9.16.tar.gz` 7,8 G + `AdditionalMaps_0.9.16.tar.gz` 14 G — acilmis halleri calisir
  durumda, gerekirse ilk silinecek yer bunlar).
- Root (`/`) tarafinda sudo isteyen kalanlar: `journalctl --vacuum-size=200M` (~700 MB),
  `apt clean` (151 MB), eski snap revizyonlari (`/var/lib/snapd` 7,8 GB).

Debug/diagnosis bag recipe (superset of the mapping recipe above — use this one for driving tests; run
it with `docker exec -d` or tmux, and the `-o` path must start with `/root/maps`):
`/velodyne_points /imu/data /scan_bee1 /tf_static` + all `/beemobs/*` (both `FB_*` feedback and our
commands, **including both `rcthrtdata` and `RC_THRT_DATA`** so the throttle relay's two ends are
visible) + `/master /neuravix/current_state /neuravix/decision_dump /safety/emergency_stop
/odometry/can_wheel` + **`/neuravix/lane_debug/compressed`** (cheap JPEG; without it "is lane detection
worse?" can only be answered from screen recordings, which is what happened on 07-20). Still **never
`/tf`**. `--compression-mode file --compression-format zstd -b 2000000000` keeps it manageable —
`/velodyne_points` alone is ~250 MB/min compressed, so drop it for long control-only sessions.

All three perception nodes subscribe to their sensor topic (camera/lidar) with `qos_profile_sensor_data`
(**best-effort**) — real drivers (Velodyne, ZED) typically publish best-effort, and a reliable
subscription silently never matches a best-effort publisher (no error, just no data). Best-effort
subscriptions still match CARLA's reliable publishers, so sim is unaffected. Check QoS at runtime with
`ros2 topic info <topic> --verbose`.

Headless debug video (real vehicle / X11'siz container): `lane_follower` and `tabela_tespit` publish
their annotated overlay as `sensor_msgs/CompressedImage` (JPEG) on `/neuravix/lane_debug/compressed` and
`/neuravix/tabela_debug/compressed` (`publish_debug_image` param, default true; tabela's is downscaled to
`display_width`x`display_height`). Their `cv2.imshow` windows (`show_window` / `show_display` params)
auto-disable when `DISPLAY` is unset instead of crashing. Watch wirelessly from a laptop with
`rqt_image_view` — requires the laptop on the vehicle wifi, matching `ROS_DOMAIN_ID`, and
`ROS_LOCALHOST_ONLY` **not** set in the container. Alternatively (added 2026-07-12, teammate
contribution) `ros2 run neuravix_ros2 mjpeg_server --ros-args -p topic:=/neuravix/lane_debug/compressed
-p port:=8081` serves the same JPEG stream over plain HTTP — the laptop then needs **no ROS at all**,
just a browser at `http://192.168.30.100:8081`, and the browser auto-reconnects after the frequent wifi
drops (unlike rqt). One server per topic/port; `raw:=true` lets it consume an uncompressed `Image` topic
(e.g. the ZED feed directly) at extra CPU cost. Subscriptions use best-effort sensor QoS so both our
reliable debug publishers and best-effort camera drivers match.

Sign/traffic-light class ids and Turkish names are defined at the top of `decision_brain.py`
(`SIGN_NAMES` dict). **The ID-3 `sign_class` field is a canonical id in that table, decoupled from
whichever YOLO model is loaded** (fixed 2026-08-18 — see the next section).

Sign-id mapping (`decision_brain.SIGN_NAME_TO_ID` / `canonical_sign_id()`, 2026-08-18):
- **The bug this fixes**: `tabela_tespit_node.py` used to publish YOLO's raw class *index* to `/master`,
  while `decision_brain`'s id constants come from the old `sonyaris.pt` (26 classes, English). The active
  model `best6.pt` (22 classes, Turkish — as do `best.pt`/`best3..6.pt`/`eda.pt`) has a completely
  different index order, so the contract was silently broken: model `PARK`(11) read as `DUR`(11) → the car
  stopped at parking signs; `SagdanGidiniz`(15) read as `KIRMIZI_ISIK`(15) → phantom red-light braking;
  the real `DUR`(1) read as `GIRILMEZ`(1) → **no stop at stop signs**. Only `YayaGecidi`(20) and
  `ParkEtmekYasak`(12) lined up by coincidence.
- **The fix**: the node maps the model's class **name** → canonical id via `canonical_sign_id()` before
  publishing. Name matching is normalization-based (Turkish chars folded, non-alphanumerics stripped), so
  `IleriMecburiYön`, `ileri_mecburi_yon` and `ahead` all resolve. Verified to map 100 % of the classes in
  `best6.pt`, `eda.pt`, `sonyaris.pt` and `best1.pt`.
- **Adding/retraining a model needs no code change** as long as its class names are already aliased;
  otherwise add the name to `_SIGN_ALIASES` in `decision_brain.py`. The node logs the full
  `model index → canonical id` table at startup and WARNs on any unmapped class. **An unmapped class is
  not published** (silence beats a fabricated id).
- Five ids were added for `best6` classes with no FSM behavior: `ADA_ETRAFINDA`(26),
  `ISIKLI_TABELA`(27), `SAGDAN_GIDINIZ`(28), `SOLDAN_GIDINIZ`(29), `SERIT_DUZENLEME`(30). They reach the
  brain, get logged, and produce no action — deliberately, rather than being force-fitted onto an
  existing constant.
- **Speed-limit signs are deliberately unmapped** — the 2026 dataset has none and the competition does not
  need them. `HIZ_20/30/20B` constants and their FSM branches stay for `sonyaris.pt` compatibility.
- **Traffic lights (`KIRMIZI/SARI/YESIL_ISIK`) do not exist in `best6.pt`** — its `IsikliTrafikLevhasi` is
  a junction *plate*, not the light, hence `ISIKLI_TABELA` with no behavior. The separate light model
  arrived 2026-08-18 (`models/yasin_green.pt`, see below) and mapped 2/2 with no code change; the same
  holds when it is later merged into one combined model.

`tabela_tespit_node.py` is now **multi-instance** (2026-08-18): `model_file` (default `best6.pt`),
`imgsz` (640), `topic_prefix` (`tabela`) and `distance_constant` (450.0) are ROS parameters, so the same
node runs signs and traffic lights side by side, both publishing canonical ID-3 to `/master`:

```bash
ros2 run neuravix_ros2 tabela_tespit                      # tabelalar, best6.pt
ros2 run neuravix_ros2 tabela_tespit --ros-args \
  -r __node:=isik_tespit -p model_file:=yasin_green.pt \
  -p imgsz:=960 -p topic_prefix:=isik                     # trafik isiklari
```

- **`topic_prefix` is mandatory for the second instance** — otherwise both write
  `/neuravix/tabela_debug/compressed` and `/tabela_tespit/processed_image`. With `isik` the debug stream
  is `/neuravix/isik_debug/compressed` (feed it to a second `mjpeg_server` on another port).
- **`models/yasin_green.pt`** (2026-08-18, from `~/yasin_green.pt.zip` — despite the name the file *is*
  the `.pt`; a torch checkpoint is itself a zip archive, nothing to extract): YOLO11s, 2 classes
  `green`/`red`, `imgsz=960`, 20 epochs, `/home/myozen/traffic_light_dataset`. **Pass `-p imgsz:=960`** —
  ultralytics' predict default is 640 regardless of training size, and a traffic light is a small object.
- **`distance_constant` almost certainly needs recalibrating for lights.** `distance = constant / bbox_h`,
  and the constant is `focal × real object height` — 450 was set for a ~0.9 m sign. If the model boxes only
  the lamp head rather than the full fixture, reported distance is inflated and `KIRMIZI_ISIK`'s `d < 12 m`
  branch may never fire (the failure is silent: lights get detected, the car never stops). Read the
  overlay's distance against a real light and set the parameter accordingly.
- Never hand-copy a `.pt` into `install/neuravix_ros2/share/neuravix_ros2/models/` — those are symlinks
  into `build/`. Drop the file in `src/neuravix_ros2/models/` and run the scoped build; `setup.py`'s
  `models/*.pt` glob picks it up with no code change.
- Cost note: two instances = two YOLO models inferring on every camera frame. On the vehicle (where CUDA
  works but headroom is thin) measure the frame rate of both debug streams before assuming it is free.

Red-light lock fixed (2026-08-18): `RED_LIGHT_STOP` used to be the FSM's only **locking** state — the
sole exit was detecting `YESIL_ISIK`, with no timeout, no distance bound and no alternative
(`STOP_SIGN` self-exits after 3 s, `CROSSWALK_STOP` after 5 s). Two real scenarios stopped the car
permanently: (1) a **false red** — a DUR sign is a red octagon and the standalone 2-class light model
called it `red` **10 times in 400 validation frames**; the sign stays in view, the state keeps
re-arming, the car never moves again; (2) a **genuine red** where the car creeps far enough forward that
the light leaves the camera frame, so the green is never seen. New `red_light_timeout` (40.0 s, ROS
parameter on both control nodes, 0 disables) releases to `LANE_FOLLOW`.
- **Measured from state entry (`_elapsed()`), deliberately NOT from `red_light_seen_time`.** Under a
  false detection the sign is continuously in view, so a "time since red last seen" timer would never
  expire and the valve would be dead code. `red_light_seen_time`/`green_light_seen_time` are still
  written and never read — they predate this fix.
- Release is **unconditional** (no "only if the road is clear" guard): a permanently-blocked front would
  reinstate the lock. A released car simply hits `OBSTACLE_STOP`, which is the safe path.
- On release, `KIRMIZI_ISIK` gets `red_light_release_cooldown` (15.0 s) — its normal cooldown is 1.0 s,
  so without this the same false detection would produce a 40 s-stop / 1 s-drive loop.
- Verified: stops at 39 s and releases at 41 s; a green at 5 s still exits immediately; **45 s of
  uninterrupted red still releases** (the false-detection case); no immediate re-lock, but re-locks
  after 16 s; `red_light_timeout:=0` restores the old infinite wait; `STOP_SIGN` unchanged.

`astar_planner.py` exists in two copies that must be kept in sync: `bee1_description/scripts/` (used by
`bee1_description`'s A* launch/node) and `neuravix_ros2/neuravix_ros2/` (imported by `decision_brain.py`
for obstacle replanning, used by both control nodes). They are currently identical; if you change the
planner logic, update both.

**A* unit-mismatch crash — FIXED 2026-07-13** (previously listed here as a "known pre-existing bug";
it finally fired on the real vehicle on 2026-07-12: `neuravix_control_real` crashed with `IndexError:
index 100 is out of bounds for axis 0 with size 60` in `Alkar_Function4.__init__`, so the real control
node could not start at all). Root cause: `decision_brain` keeps positions in **grid cells** (0..59,
nodes convert odometry meters via `GRID_SCALE=60/73`), but `AStarPlanner.plan_path()` treated its
arguments as world meters and divided by `resolution=0.5` again — `goal_position=(50,50)` became cell
`(100,100)`. The same double conversion would also have crashed `replan_if_needed` mid-drive whenever
`grid_x > 29`, and `decision_brain.py`'s `add_obstacle(..., safety_margin=2)` call was a latent
`TypeError` (the planner didn't accept that kwarg). Fix (all three): the brain's planner is now built
with `resolution=1.0` (cell == world unit, so all existing grid-cell callers pass through unchanged, one
cell ≈ 73/60 ≈ 1.22 real meters), `_nearest_free` bounds-checks and returns `None` for out-of-map cells
(empty path instead of IndexError — matters because ID-5 `/master` goals are unvalidated input), and
`add_obstacle` accepts `safety_margin` (extra cell radius stamped into the local costmap). Both
`astar_planner.py` copies updated in sync. Verified: standalone `Alkar_Function4()` constructs and plans,
replan at (55,55) with `safety_margin=2` works, out-of-map goal returns empty path, obstacle-avoid branch
runs end-to-end. Note `astar_planner.py`'s standalone `__main__` demo still uses meter semantics with its
own `resolution=0.5` instance — that usage remains valid; only the brain's instance changed.

YOLO weights live in `src/neuravix_ros2/models/*.pt` and are installed to
`share/neuravix_ros2/models` via `setup.py`'s `data_files` glob — a new weights file needs no code change
to be packaged, just a rebuild.


Lane pipeline validated against real track footage (2026-07-21, bag `~/maps_son/pist_18_3tem`, 36 GB,
9778 raw ZED `rgb/image_rect_color` frames over 326 s — the same bag `src_pts` was originally clicked on):
- **`best_yolo11.pt` is fine on real footage — the old "found nothing on real ZED images" worry was an
  indoor artifact.** Masks were produced on **100 %** of sampled frames (avg 4.1 masks/frame). The
  bottleneck is downstream geometry, not detection.
- **The BEV homography's top edge was wrong and is now corrected** (`312,367` → `338,409` at y=210).
  A correct IPM maps parallel lane lines to parallel vertical lines, i.e. BEV lane width must not depend
  on y; the old trapezoid narrowed the lane **12.8 %** from y=200 to y=355 (504 → 439 px) and left a
  systematic left/right slope difference of −0.488. Method: take the 83 frames the existing pipeline
  already accepted, inverse-warp their BEV fits back into image space (those lines are ground truth,
  independent of the homography), then grid-search the top edge for "width independent of y".
  **Validated on 153 held-out frames** (odd-indexed subset, never used in the search):

  | | old | new |
  |---|---|---|
  | width narrowing y=200→355 | −12.8 % | **−1.1 %** |
  | slope difference (0 = parallel) | −0.488 | **−0.114** |
  | LaneW at y=200/280/324/355 | 504/473/450/439 | **449/447/444/444** |
  | Error std (steering noise) | 32.8 px | **25.9 px** |
  | Error median | +34.8 px | +24.0 px |
  | frames with no fit | 28.1 % | 35.3 % ⚠️ |

- **The trade-off is real**: correcting the geometry costs ~7 points of fit rate (two-fit 43.1 % → 39.9 %)
  because the far field is stretched more, so fewer pixels land in each split window. Judged worth it —
  a 21 % reduction in steering-error scatter applies to *every* frame, while missing fits are bridged by
  `left_prev`/`right_prev` until `lane_lost_frames` (15). **If lane loss becomes a problem on the vehicle,
  widen the left/right split `offset = 70` in `cb()` — do not revert `src_pts`**, whose geometry is now
  measured rather than eyeballed.
- **Remaining lateral bias**: Error median is still +24 px after the fix. That is what `err_offset` exists
  for, but it must be calibrated the documented way (straight stretch, car visually centered, read
  `AvgErr` off the overlay) — a median over a whole bag cannot tell a miscalibrated zero from the car
  genuinely driving right of centre. Left unset.
- **Fit rejection reasons** (204-frame sample, for whoever tunes this next): left region OK 68.6 %,
  `<80 px` 20.6 %, slope-reject 8.8 %; right region OK 44.6 %, `<80 px` **34.8 %**, slope-reject 18.6 %.
  The right boundary (barrier) is markedly harder than the left (dashed line). The `abs(m) > 1.0` slope
  guard was rejecting asymmetrically because the old homography gave the two sides opposite mean slopes;
  with the corrected one this should even out — worth re-measuring before touching that threshold.
- **Unresolved conflict**: measured LaneW here is ~445 px (half ≈ 222, std 12) but the 2026-07-20 vehicle
  overlay read ~300 px (half ≈ 150). 1.5× apart, different sessions. The theoretical `half_lane_bev`
  fallback (192) was therefore left alone; it only applies until the first two-fit frame. Resolve by
  reading `LaneW` off the overlay on the vehicle.

Desk slalom simulator + slalom overhaul (2026-08-10, teammate's `slalom_sim.py` integrated):
- **`slalom_sim.py` (teammate contribution) integrated at `src/neuravix_ros2/slalom_sim.py`** — a
  CARLA-free, ROS-free desk test that drives `Alkar_Function4` through a bicycle vehicle model + synthetic
  lidar sectors (same geometry as `obstacle_lidar_node.py`) over 5 scenarios, writing `slalom_sim.png`.
  Run: `python3 src/neuravix_ros2/slalom_sim.py`. This is the fast iteration loop — fix logic here before
  CARLA. **Its synthetic lidar MUST mirror the node's geometry or it tests a fiction** (see next point).
- **obstacle_lidar geometry changed to the 3.0 m track lane** (the sim's `SIDE_OFF=3.0`/`SIDE_CORR=1.5`,
  teammate's "2026-08-03 pist ölçüsü"): `side_offset` 1.40 → **3.0** (neighbour-lane centre) and a new
  **`side_corridor` param = 1.5** (the side sector's half-width, previously reused `corridor`=0.70). So
  left/right ID-4 clearances now measure the full opposite lane you'd swerve into. Trap: this leaves a
  blind band `y∈(0.70,1.50)` between the front and side sectors — a 1.4 m box enters both so it's fine,
  but a thin object on the lane line can be missed. Node + sim geometry now agree.
- **Bug A — obstacle slowdown was defeated by `lane_detect_event`.** `obstacle_event` set `slow_speed`
  when front<slow_distance, but `lane_detect_event` (called every ~20 Hz ID-2) ran `_move_vehicle(
  default_speed)` right after and overrode it → the car approached obstacles at ~11 km/h instead of 6.
  This is real (not sim-only): both handlers set `self.target_speed` and the last writer won. Fixed with
  `_obstacle_speed_cap`: `obstacle_event` sets it from `front_distance` (10 Hz), `_move_vehicle` clamps to
  it, so lane events can no longer raise the speed past the cap. Cleared when front≥slow_distance.
- **Bug B — slalom never completed a lane change (car stopped 1.7 m short, min 0.58 m).** Two root causes,
  both found via `slalom_sim` traces:
  1. **Escape ended prematurely on `front > slow_distance`.** As the car angled during escape, the
     obstacle transiently left the *body-fixed* front corridor → front jumped to 99 → escape thought
     "road clear" at ~1.3 m lateral (target 3 m) and switched to return, which then steered back into the
     obstacle. Removed that early-exit.
  2. **Phases were arc-length (distance) based, which is radius-dependent.** `slalom_out_distance=5.3 m`
     of arc = 76° turn at R=4 m but **99° at R=3 m** (tighter steer) → the car nearly perpendiculared and
     the return couldn't recover (ended at y=1.2, "passed but didn't return"). **Rewritten to be
     heading (yaw) based**: escape steers hard until `|yaw−yaw_mark| ≥ slalom_escape_heading` (45°),
     return steers back until the nose realigns within `slalom_return_tol` (8°); lane-follow then
     recentres. Radius-independent, clean S. `update_motion()` gained a `yaw=` arg; **both control nodes
     now feed `self.odom_yaw`** (from the odom quaternion they already compute). Distance/time remain
     fallbacks when yaw isn't fed (degrades to the old, imperfect behaviour — so the real vehicle needs
     odometry orientation, which slam_toolbox/EKF provides).
- **Tuning that made the desk suite pass** (defaults now): `avoid_distance` 3.0 → **5.0** (the closed-loop
  yaw maneuver needs ~5 m to complete; the 07-21 5.0/3.0 split was for the *old open-loop* slalom and no
  longer applies — early/false triggers are still gated by `avoid_confirm_time` 0.5 s, curve suppression,
  and the 2/5-frame lidar filter), `avoid_abort_distance` 1.0 → **0.8** (algi9's 0.49/0.36 m close calls
  still abort, a 1.6 m pass still continues), `avoid_lane_blend_escape` 0.15 → **0.0** (full commit during
  escape), new `slalom_escape_steer`/`slalom_return_steer` params (70/65).
- **Result: 4/5 desk scenarios.** S1 (single box, full lane change, min 1.18 m) and S5 (alternating cones)
  pass cleanly; S3 (oncoming car in target lane) and S4 (road fully blocked) correctly stop without
  passing. **S2 fails** (two boxes 10 m apart, same lane): the car clears #1 but, having shifted into the
  opposite lane, only sees #2 once it recenters ~2 m away — too late to slalom, so it stops. This is a
  late-detection limitation of the body-fixed front corridor, not a logic bug; real slalom courses use
  offset cones (S5), which works. Open follow-up if same-lane close spacing matters: don't fully recentre
  between obstacles, or widen forward lookahead.
- **Not yet CARLA-verified and NOT rebuilt into the deploy image.** Next step is running the stack in
  CARLA (obstacle_lidar with `-p lidar_topic:=/carla/ego_vehicle/lidar -p lidar_height:=1.6`; note the
  3.0 m side geometry may need adjusting to CARLA's town lane width). All changes are workspace-only so
  far; `export_deploy.sh` + image rebuild deferred until CARLA confirms.

Slalom engine replaced with the teammate's `nursena` branch (2026-08-10 evening) — supersedes the
yaw-heading rewrite documented just above. Source: `github.com/teamneuravix/neuravix2026` branch
`nursena` (public). File-by-file: `slalom_sim.py` is byte-identical to what was integrated in the
afternoon (that WAS the full version); `obstacle_lidar_node.py` has identical geometry (`side_offset=3.0`,
`side_corridor=1.5`) but nursena's `_on_params` rejects unknown params (breaks `use_sim_time`) so **ours
was kept**; the sim control node's `use_planner` and the real node's `_check_motion` watchdog exist only
in ours so **both control nodes were kept**. The real change is `decision_brain.py`: nursena's is
objectively better on the desk suite (**5/5 vs our 4/5**, including the two-obstacle S2 our 2-phase engine
failed) because its slalom is **4-phase** (escape → **pass**, i.e. drive alongside the obstacle in the
adjacent lane → return → align) and integrates true lateral offset from yaw (`_lateral += sin(yaw−ref)·step`,
`slalom_lateral_target=3.0`) rather than steering to a heading target. It also already fixes Bug A (in
`lane_detect_event` directly, 2026-08-03) and already has the close-obstacle abort, two-stage thresholds,
infinite-weave guard and stall guard. **nursena's only gap was curve suppression** — grafted in from our
code (`_note_lane_angle`/`_in_curve`/`curve_lane_dev` etc.; suppresses slalom *entry* in a bend, car still
slows/stops). Deliberately dropped in favour of nursena's 4-phase: our 2-phase yaw-heading escape/return,
the weave-gap rhythm, the zig-zag tie-break. Active tuning is now nursena's: `slow_distance=6.0`,
`avoid_distance=4.5`, `avoid_confirm_time=0.3`, `safe_side_distance=10.0`, `stall_timeout=4.0`. Verified:
slalom_sim 5/5, curve suppression (drift≠curve, real curve suppresses, straight road slaloms), Bug A,
stall at 4 s, fail-safe 0,0,0, both control nodes start. Pre-merge brain backed up at
`scratchpad/backup_merge/decision_brain.MINE.py`. Still workspace-only; deploy image NOT rebuilt.

Slalom, CARLA'da uçtan uca çalışır hale getirildi (2026-08-17). Gün başında araç ilk engelde
bariyere giriyordu; gün sonunda 3 engelli sağ-sol-sağ dizide iki weave'i temiz tamamlayıp yoluna
devam ediyor (`SLALOM bitti (1. weave tamamlandi), bitis yanal ofset 0.30 m -> serit`, hiç
`OBSTACLE_STOP` yok). **3 engel için 2 weave doğru davranıştır** — karşı şeritteki engel kendi
şeridimizi kapatmadığı için manevra gerektirmez.

**ID-4 SÖZLEŞMESİ GENİŞLEDİ — yeni bir alan grubu var.** `obstacle_lidar_node` artık
`4,front,left,right` sonrasına **yanal klerans profili** ekliyor:

    4,front,left,right,P,y0,dy,c0,c1,...,c14

`P` bir işaretçidir ve **sayı değildir**; `y0=-3.50`, `dy=0.50`, ardından 15 kutu. Kutu `i`,
araç çerçevesinde `y0+i*dy` merkezli, yarı genişliği `corridor` (0.70) olan koridorda boylamsal
kleranstır. İlk üç alan aynen durur, eski tüketiciler bozulmaz. Fail-safe/bayat durumda profil
**yayınlanmaz** (beyin profilsiz kalınca eski davranışına düşer, yanlış veriye değil).
⚠️ **`/master` ayrıştıran her kod `P`'den öncesini sayısal, sonrasını ayrı okumalı.** Bu
eklendiğinde iki kontrol düğümü de mesajın tamamını `float()`'a çeviriyordu; her ID-4 mesajı
`ValueError` verip **tamamen düşüyordu** ve araç bir koşu boyunca hiç engel verisi almadı.

Profilin varlık sebebi: `front/left/right` araca SABİT sektörlerdir ve aracın şerit merkezinde
olduğunu varsayarlar. Weave ortasında araç kaymıştır; kendi şeridi artık `-_lateral` yanındadır,
sabit `side_offset`'te değil. Sağ bariyerli pistte sağ sektör hep 0 okuduğu için "kendi şeridime
dönebilir miyim" sorusu hiçbir zaman evet cevabı alamıyor, araç karşı şeritte 14 m oyalanıp son
anda tam kilitle kırıp bariyere giriyordu. Beyin artık `_klerans(yan)` ile doğrudan sorar.

Ölçülüp düzeltilen diğer yedi şey (hepsi CARLA log'undan, sırayla):

| bulgu | düzeltme |
|---|---|
| Dönüş fazında komutun %55'i şerit takipçisinden geliyor, o da "düz git" der: FSM 25 → araca 36 | `avoid_lane_blend_return` 0.55 → **0.15** (kaçış zaten 0.15) |
| Kaçış sapması 30 (FSM 75), dönüş sapması 20 (FSM 25) — asimetrik; dönüş 12 s / 8.6 m sürüp yanalın yarısını kapatamıyordu | dönüş artık kaçışın **aynası**: `45 ∓ (slalom_escape_steer-45)` |
| Geçiş fazı yanal hedefe varmıyor (15 m'de 1.1→1.4), araç yarı yolda kalınca sonraki engeli kendi koridorunda görüp geri dönüyor | `slalom_pass_lat_gain` 10 → **35** |
| Manevra tamamlanmadan gelen "önümde engel" sinyali yön değiştirtiyordu | `weave_done_frac` (0.85) — hedefin %85'ine varmadan yön değişmez |
| Açılıyken ön koridor yan bariyeri tarıyor (y=+0.5'te 20°→9.5 m, 44°→4.7 m okunur) | `front_trust_deg` (12°) — weave içi yeniden planlama sadece burun şerit yönüne yakınken |
| Kendi şeridine dönerken yan sektör o şeridi değil ötesindeki bariyeri ölçüyor | `home_return_lateral` (0.5) — geri dönüş yönünde yan klerans şartı aranmaz, sınır yine `lane_min/lane_max` |
| Weave bitiminde bir sonraki engel hep `slow_distance` (6.0) içinde olduğu için şerit takibine hiç dönülemiyor | weave çıkış eşiği `slow_distance` → **`avoid_distance`** |

**Gerçek araç varsayılanlarının hiçbiri değişmedi.** Bugün dört sabit ROS parametresi oldu ve
CARLA'ya özel değerler yalnızca arayüzün 8p butonundan geçiliyor:

| parametre | gerçek araç (varsayılan) | CARLA (8p) | neden farklı |
|---|---|---|---|
| `curve_lane_dev` | 6.0 | 25.0 | CARLA'nın şerit çıktısı 42 etrafında ±5.5 salınıyor ve viraj sanılıyordu (`VIRAJ -> slalom bastirildi`); Town04 road 25 düz (50 m'de 2.1°). Pistte gerçek viraj var, orada bastırma gerekli. |
| `side_min_clear` | 5.0 | 3.0 | Kaçış R=3.07 m'de 1.5 m yanalı 2.64 m'de bitiriyor; 5.0 istemek 2.4 m fazladan şart. Sol 4.1 m açıkken "IKI TARAF DA KAPALI" deyip duruyordu. Pistte karşı şeritte trafik olabilir, orada muhafazakâr kalsın. |
| `slalom_align_lateral` | 0.6 | 0.30 | 2.96 m şeritte 0.6 m yarı-şeridin %40'ı; araç weave'i 0.43 m kaymış bitiriyordu. |
| `carla_steer_scale` | — | 1.0 | Sadece sim düğümünde var. 3b butonu aracın `max_steer_angle`'ını 31.25°'ye çektiği için çarpana gerek kalmadı. |

**CARLA'nın aracı Bee1 değil, `arac_ayarla.py` ile eşitlenir.** Ölçüldü: FSM 75'te weave sonu
odometrisi ileri 1.0 m / yanal 1.51 m verdi → 113° dönüş, R=1.09 m, ~60° teker. Bee1'in mekanik
limiti 31.25° (R=3.07 m; doküman "duvardan duvara 4.100 mm / kaldırımdan kaldırıma 4.025 mm"
değerleri arka-aks yarıçapını 2.88–3.13 arasına koyuyor, model içinde). `carla_steer_scale` ile
çarpan denendi ama ilişki doğrusal değil (hıza bağlı direksiyon eğrisi + komut yumuşatma): 0.52
R'yi 1.09'dan 5.20'ye çıkardı, 3.07'ye değil. Doğru çözüm çarpan değil **aracın limitini
değiştirmek**; `~/Desktop/carla-slalom/arac_ayarla.py` bunu yapar (ego her spawn'da tekrar).

`slalom_sim.py` üç noktada gerçeği yansıtmıyordu ve 5/5 verirken CARLA kilitleniyordu — üçü de
düzeltildi: (1) duvar sadece sağdaydı ve **x=2'den** başlıyordu, yani araç hizasında duvar yoktu;
şimdi x=-5'ten başlıyor. (2) sektör geometrisi eski (3.0/1.5), şimdi 2.74/1.26. (3) `update_motion`'a
x/y verilmiyordu, beyin ölü-hesap yaw integraline düşüyordu — oysa iki kontrol düğümü de konum
besliyor. Yeni senaryolar: **P1** (3 engel sağ-sol-sağ 7 m, sağ bariyer), **P2** (5 m), **P3**
(karşı şerit kapalı → durmalı). Suite 7/8; kalan P2 geometrik sınır: weave biterken 2. engel tam
yanda kalıyor, 3. engele 3 m kalıyor ama manevra 3.6 m istiyor. İnsan sürücü o aralığı şeridine
dönmeden süzülerek geçer; mevcut strateji her engelden sonra dönüyor.

⚠️ **`PIST_PARAMS` (slalom_sim) ile 8p butonu aynı değerleri taşımalı** — ayrılırlarsa masa
simülatörü araçta çalışacak ayarı değil, varsayılanları test eder.

Yanal hedef, dönüşümlü dizide **tam şerit değişimi olamaz**: karşı şeritte de engel vardır.
2.96 m şerit + 1.21 m engelde araç merkezi ancak **1.14 .. 1.82 m** arasında olabilir (1. engeli
sıyır / 2. engele değme); `slalom_lateral_target=1.7` o aralığın üst ucuna yakın, geçiş payı
0.56 m. Tam şerit değişimi (2.96) 2. engelin tam içidir. Teorik S manevrası 5.25 m boyuna
sığıyor ama ölçülen weave 11.8 m sürüyor; weave 5-6 m'ye inerse tam şerit değişimi 7 m aralığa
sığar — açık iş.

CARLA pist kurulumu (`~/Desktop/carla-slalom`): `spawn_slalom_obstacles.py --pist` iki şeritli
koridoru bariyerle inşa eder. `--pist-serit` **TEK** şerit genişliğidir (2.96 = lane_follower'ın
`lane_w_px` ölçümü, bir şeridin iki çizgisi arası — ilk kurulumda iki şeridin toplamı sanılıp
1.48 m şerit çıkmıştı, 2 m'lik bariyer oraya sığmıyordu). **Sol duvar YOKTUR** (gerçek pistte de
yok); `--sol-duvar` sadece "iki tarafı da kapalı olsa" denemesi için. `--duvar-pay 0.60` duvarı
şerit kenarından dışarı alır — Şartname s.806 da bariyerlerin şeride taşmayacağını, şeridin
dışında herhangi bir noktada olabileceğini söylüyor. Engel `--bp static.prop.streetbarrier`
(1.21 x 0.39 m) ile doğrudan seçilir; `--engel-en` ölçüye en yakın prop'u bulur ama 1.30 hedefi
`warningaccident`'ı (bir kaza tabelası) seçiyordu.

Şartname bulguları (2026_Robotaksi-Şartnamesi.pdf, ilk kez okundu): **"Kullanılacak engellerin
boyutları, şekilleri ve düzenlemeleri belirli bir standarda sahip olmayacağından, araçların bu
çeşitlilik karşısında adapte olabilmesi beklenir"** (s.835) — yani engel düzeni tanımı gereği
belirsizdir, sabit bir `slalom_lateral_target`'a ayarlamak yarışmaya taşınmaz. **"Statik engeller
yalnızca bir şeridi kısmen veya tamamen kapatabilir"** — diğer şerit statik engelde her zaman
açıktır. **"sakınmayı sağlayacak alan mevcut değilse aracın o yol üzerinden geçmemesi gerekir"** —
`OBSTACLE_STOP` doğru davranış, başarısızlık değil. Test videosu dördünü birden istiyor: slalom,
şeritten çıkmadan viraj, şeritten çıkmadan 20 m, **ve engelde durma** (s.960).

Açık işler: (a) deploy imajı hâlâ 2026-07-21 18:21 build'i — bugünkü hiçbir düzeltme araçta yok;
(b) weave 11.8 m yerine 5-6 m'ye inmeli ki tam şerit değişimi sığsın; (c) `slalom_sim`'in P2
(5 m aralık) senaryosu; (d) weave sonrası şerit takibinin ortalayamaması (BEV/şerit tespiti işi,
slalomla ilgisi yok).

**Deploy imajı yeniden derlendi 2026-08-17 18:15** — bugünkü slalom çalışmasının tamamını içerir.
Image ID `62d71ae7b5c8`, tar `~/robotaksi_deploy/robotaksi_humble.tar` **4.257.087.488 bayt**,
SHA-256 `01f984f1bf5465e0b7615640b588f781e73e18e27233262359e2cae3fbd3f427`. İmajın *içinde*
doğrulandı (`/ros2_ws/install/.../neuravix_ros2/`, **`/ws` DEĞİL** — bu yol bir kez yanlış
denendi): `avoid_lane_blend_return=0.15`, `slalom_pass_lat_gain=35.0`, `slalom_escape_steer=75.0`,
`_profil`/`front_trust_deg`/`home_return_lateral`/`weave_done_frac` beyinde, `profile_y_max`
lidarda, altı yeni parametre gerçek kontrol düğümünde, ID-4'ün `P` ayrıştırması yerinde.

**ROLLBACK KOPYALARI T7 HARİCİ DİSKİNDE** (`/media/neuravix/T7/neuravix/`, exFAT, >4 GB dosya
alır): `robotaksi_humble_0721_1500.tar` (4.119.267.328 B, 21 Tem 15:41) ve
`robotaksi_humble.tar` (3.965.164.544 B, 18 Tem). Laptop'ta `/home/neuravix/sonclaude/` klasörü
SİLİNMİŞ ve `~/robotaksi_deploy/robotaksi_humble.tar` her `docker save` ile üzerine yazılıyor —
yani laptopta yedek kalmıyor, geri dönüş T7'den yapılır. **Her rebuild'den sonra yeni tar'ı
tarihli adla T7'ye kopyala**, `~/robotaksi_deploy` içindeki tek kopyaya güvenme.

Araç koşu talimatı ve bag komutu ayrı dosyada: **`ARAC_KOSU.md`** (workspace kökü). Aktüasyon
katmanında iki yol var, karıştırma: **(A)** aracın kendi PID'i + `speed_fb_relay`/`throttle_relay`,
**(B)** aracın PID'i kapalı + `steering_ctrl`/`throttle_ctrl` (2026-07-20'de yazıldı, 07-21'de
kullanıldı). B tercih ediliyor çünkü A'nın iki kusuru ölçüldü: direksiyon PID'i tek yönlü
(`min_output: 0` → negatif hatada `pwm=0` → motor kapanıp tekerlek serbest kalıyor, `debug_control`
bag'inde 1700 örnekte `pwm=0`), gaz PID'i anti-windup'sız (`ki=1.0` → dururken integral şişip pedal
255, 1.5 s'de 0→10 km/h). B'de röleler **çalıştırılmaz**; `throttle_ctrl` doğrudan `RC_THRT_DATA`'ya
yazar ve `FB_VehicleSpeed`'i doğrudan dinler. Bag'e `/beemobs/AUTONOMOUS_SteeringMot_Control`
eklenmeli (B'de direksiyonun CAN'e giden gerçek komutu odur) ve `/beemobs/rcthrtdata` gereksizdir
(o A yolunda vardı). Konteynerde `/root/neuravix_kayit` **bağlı olmayabilir** — mevcut `docker run`
yalnızca `maps`'i bağlıyor, o yüzden kayıtlar `/root/maps` altına alınmalı.

Şerit takibi arkadaşın sürümüyle değiştirildi (2026-08-19, kaynak `~/birlestirilcekws`) — **yalnızca
şerit boru hattı alındı, başka hiçbir dosyaya dokunulmadı.** O workspace 21 Temmuz civarı bir
kopyadan dallanmış; şerit takibinde ilerlemiş ama diğer beş düğümde donmuş. Alınmayanlar ve
alınmama sebepleri (hepsi geri gitme olurdu):

| dosya | onunki | neden alınmadı |
|---|---|---|
| `decision_brain.py` | 975 satır | bizimki 2064: nursena 4-fazlı slalom, viraj bastırma, yanal profil (`_profil`), `red_light_timeout`, `canonical_sign_id` — hiçbiri onda yok |
| iki kontrol düğümü | eski | ID-4'ün `P` işaretçisini ayrıştırmıyor, tüm mesajı `float()`'a veriyor → **bizim lidar düğümümüzle her ID-4 mesajı `ValueError` ile düşer** |
| `obstacle_lidar_node.py` | eski | `side_offset=1.40` (bizde 3.0), yanal klerans profili yok, `_on_params` bilinmeyen parametreyi reddediyor (`use_sim_time` kırılır) |
| `tabela_tespit_node.py` | eski | `best4.pt` + **YOLO'nun ham sınıf indeksini** yayınlıyor → 2026-08-18'de kapatılan "DUR tabelasında durmama" hatası geri gelir |
| `models/` klasörü | 6 model eksik | toptan senkronlanmadı; sadece `serit_v2.pt` kopyalandı |

Alınanlar: `lane_follower_node.py` (483 → 1334 satır), `models/serit_v2.pt`
(md5 `649d24df…`, yolo11s-seg, 2 sınıf `lane`/`barrier`, 391 el-etiketli pist karesi, 189 epoch —
149'da zirve, erken durdu; tutulan test bölünmesinde maske kalınlığı 0.241 m / el etiketi tavanı
0.238, fit RMS 16.3 px, çıkarım 5.1 ms/kare) ve iki masa testi `tools/serit_kapali_cevrim.py` +
`tools/serit_bag_cevrim.py`.

Şerit düğümünde neyin neden değiştiği (sayılar arkadaşın gerçek ZED kaydı `pist_18_3tem` ve
gerçek araç kaydı `asama0_48` üzerinde ölçtükleri):
- **Yeni model + sınıf süzgeci.** `_lane_cls` sadece `lane` maskelerini fitliyor; eskiden bariyer
  maskesi şerit sanılıp fitleniyordu. Model tek sınıflıysa süzgeç otomatik kapanır (eski
  ağırlıklarla uyumlu). ⚠️ **Sadece `.pt` dosyasını kopyalamak işe yaramaz** — süzgeç olmayan eski
  kod 2 sınıflı modelle eski modelden DAHA KÖTÜ çalışır. İkisi birlikte taşınmalı.
- **`MORPH_OPEN` 11x11 → 3x3.** İki-fit oranı %40.4 → %64.6, hiç fit yok %25.5 → %14.9. Ayrıca
  "homografi bozuk" sanılan %16.5'lik BEV genişlik sapmasının gerçek sebebi buymuş (%2.6'ya indi) —
  **morfoloji hatasını homografiye yazmayın.**
- **`np.std(xs) < 5` reddi kaldırıldı**, yerine satır açıklığı ölçütü. Eski kural tam da ideal
  durumu (düz, dikey şerit çizgisi) reddediyordu; düz yolda iki fit de düşüp yanal ofset hiç
  düzeltilmiyordu.
- **`fit_max_slope` 1.0 → 3.0.** Viraj kesitinde tek-fit kalan karelerin %81.5'inde eksik tarafın
  maskesi vardı, sadece bu kurala takılıyordu. 3.0 ≈ 5.6 m viraj yarıçapı; aracın tam kilitle
  alabileceği en dar viraj 3.4 m olduğundan her sürülebilir virajı kapsar.
- **Polinom derecesi 1 → 2** (veri yetersizse derece-1'e düşer). İleri bakış satırında isabet
  virajda 16.7 → 7.9 px; kapalı çevrimde virajda son yanal hata 0.53 → 0.20 m. **Adaptif seçim
  (`fit_deg2_kazanc=0.85`) denendi ve geri alındı** — statik metrikte iyi görünüyor ama döngüde
  neredeyse hep derece-1'i seçip viraj kazancını kaybediyor. Düz yolda oynama rahatsız ederse
  `-p fit_deg2_kazanc:=0.6`.
- **İleri bakış parametreli**: `y_eval` sabit `0.90*H` (≈2.2 m, aracın burnu) yerine
  `lookahead_frac=0.65` (≈4.8 m). Kök sebep buydu: fit burnun teğetini ölçüyordu, viraj ancak araç
  içine girdikten sonra hata üretiyordu. `fit_weight_pow` 4 → 1 (üs 4, fiti 1.7–2.5 m'ye kilitliyordu).
- **`_tek_fit_merkez()`**: iki fitten tek fite geçişte sabit yarım-şerit yerine *son ölçülen* ofset.
  Geçiş anındaki merkez sıçraması (%90 dilim) virajda 21 → 6 px. **EMA ile yumuşatılmışı denendi ve
  işe yaramadı** (60 → 66 px) — ortalama gecikiyor, önemli olan SON değer.
- **`heading_gain=30`** (şerit eğiminden ileri besleme) ve **`fit_confidence_px=800`** (az pikselli
  fitin direksiyona etkisini kısar).
- **PID `Kp` 0.08 → 0.03**, iki bağımsız yolla: gerçek araç kaydında sürücünün direksiyonunun ölçülen
  şerit hatasına regresyonu (şerit takibi bölgesinde 0.028–0.033) ve kapalı çevrim taraması (0.08 altı
  6 senaryonun 6'sında da aracı pistten çıkardı). Çelişki hız farkındanmış: kapalı çevrim testleri
  1.5–3.0 m/s'de koşuyordu, gerçek sürüş medyanı 0.83 m/s. Araçta salınım görülürse
  `-p steer_kp:=0.02` (yeniden derleme yok).
- **`Kd` 0.01'de kaldı. 0.40 kısa süre varsayılan yapıldı ve GERİ ALINDI** — yanal hatayı 0.33 m'ye
  indiriyor ama kare-kare direksiyon değişimini ort 2.68°/maks 60°'ye (≈900°/s) çıkarıyor; direksiyon
  motoru bunun onda birini yapamaz ve kontrolcü türev-baskın hale gelip gürültüyü takip ediyor
  (D/P 3.7×, direksiyon-hata korelasyonu 0.97 → 0.29). **Ders: bu boru hattında bir kontrol
  değişikliği tek metrikle onaylanmamalı — takip hatası + direksiyon yumuşaklığı BİRLİKTE.**
- **Yeni teşhis**: `/neuravix/bev_debug/compressed` (metre ızgaralı, ±yarım şerit referanslı
  kuşbakışı — homografi ilk kez gözle sınanabiliyor; `publish_bev_image:=false` ile kapanır) ve
  opsiyonel analitik IPM (`ipm_mode:=analytic`, kamera yüksekliği+eğiminden hesaplar). **Analitik mod
  varsayılan DEĞİL**: tahmini yükseklik/eğimle kurulunca elle tıklanmış `src_pts`'ten kötü çıkıyor
  (sabitlik 0.40–0.88 vs 1.026); gerçek ölçüm olmadan açmayın.

Bizim sürümümüzden **geri eklenen üç şey** (arkadaşın kopyasında yoktu, alınırken kaybedilecekti):
1. **`src_pts` ROS parametresi.** Onunkinde ZED trapezi koda sabit gömülüydü. `slalom_arayuz.py`'nin
   "6. Şerit Takip" butonu CARLA trapezini parametreyle geçiyor — sabit bırakılsa o buton **sessizce**
   ZED trapeziyle çalışırdı. Başlangıç log'una `BEV src_pts = ...` eklendi ki trapezin gerçekten
   ulaşıp ulaşmadığı görülebilsin.
2. **`yolo_conf` parametresi** (varsayılan 0.25).
3. **`camera_topic` varsayılanı** `/carla/ego_vehicle/rgb_overlay/image` → `/zed/...` (gerçek araç).
   CARLA zaten parametreyle geçiyor; varsayılanın araca bakması, parametre unutulduğunda düğümün
   sessizce hiçbir şey yayınlamamasını önler.

Doğrulandı: kapsamlı derleme; `serit_v2.pt` ile başlangıç (`serit sinif idx=0`); `best_yolo11.pt`
ile geriye uyum (tek sınıf → `idx=None`, süzgeç kapalı); CARLA parametre yolu (`src_pts` override
log'da doğru); masa kapalı çevrim `--karsilastir` — **ESKİ ayar şerit dışına taştı (ort 1.12 m,
maks 2.97 m), YENİ ayar şeritte kaldı (ort 0.61 m, maks 1.48 m)**. `/master` sözleşmesi değişmedi
(`2,<steer>`, 15..75), beyin tarafında düzeltme gerekmiyor.

⚠️ **Deploy imajı YENİDEN DERLENMEDİ.** Mevcut imaj `robotaksi_humble:latest`, ID
`f8769c87fa8d`, **2026-08-19 10:32** build'i, tar `~/robotaksi_deploy/robotaksi_humble.tar`
4.326.647.296 bayt (10:33), SHA-256 `c6cd5e6b0f12…`. **18 Ağustos tabela-id düzeltmesi bu imajın
İÇİNDE** — `export_deploy.sh --dry-run`'ın `decision_brain.py`/`tabela_tespit_node.py`'yi listelemesi
bayatlık değil, imajdan SONRA aynı gün yapılan işlerdir:
- `decision_brain.py` 18:50 — `slalom_return_max_deg` (45°): dönüş fazı, yanal/mesafe/süre ölçütleri
  karşılanmasa bile burun şerit yönüne 45° içine girince biter (açı tavanı).
- `tabela_tespit_node.py` 14:19 + `models/birlesik_v2.pt` 14:22 — varsayılan model `yasinfull.pt` →
  `birlesik_v2.pt`, ve trafik ışıkları için ayrı `light_distance_constant=150` (tabela sabiti 450
  ışıkta mesafeyi şişiriyordu).
- bu bölümün konusu olan şerit değişikliği + `serit_v2.pt`.
`neuravix_control_node_real.py` ve `obstacle_lidar_node.py` imajdakiyle birebir aynı.
Araca taşımadan önce: `./export_deploy.sh` → `docker build` → `docker save` → araçta `docker load` +
`docker rm -f` + `docker run`, ve yeni tar'ı tarihli adla T7'ye kopyala.

Direksiyon menzili düzeltildi — araç kilidin **%55'ini** kullanıyormuş (2026-08-19):
- **Bulgu.** `slalom_0819_1318` bag'inde kaçış fazında tekerlek geri beslemesi -19..-22'ye
  (yani `steer_raw_min=-21` clamp'ine) dayanıyor, ama araç o kilitte **R ≈ 5.4-6.0 m** çiziyor:
  yol 3.11 m / dönüş 29.9° → R = 5.97 m → teker 17.3°. Bağımsız ikinci ölçüm aynı sonucu veriyor
  (yanal 0.83 m + yaw 30.2° → R = 0.83/(1-cos30.2) = 6.1 m); yaw XSENS gyro'dan geldiği için
  direksiyon kalibrasyonundan **bağımsız**.
- **Spec ile birleştirince kök neden çıktı.** Ham birim ↔ teker açısı doğrusal:
  `ham sapma 21 → 17.3°` (ölçüldü) ⇒ `ham sapma 38 → 31.3° → R = 3.06 m`, ki bu dokümandaki
  tam kilidin (31.25°, R_arka 2.88–3.13 m) **birebir kendisi**. Yani gerçek mekanik kilit ham
  ~38'de; 2026-07-13'te kumandayla ölçülen -21/+26 kilide hiç varmamış (CLAUDE.md zaten
  "güvenilmez" diyordu).
- **Eski "-34.75 gönderildi, feedback -37/-38, motor stopta zorluyor" yorumu yanlıştı** — o -38
  motorun zorlanması değil, **kilidin kendisiydi**. O yanlış yorum yüzünden konan clamp aracın
  yarım kilitle dönmesine yol açtı: slalom manevrası iki kat geniş oldu, engel aralığına sığmadı,
  fazlar birbirine girdi. 08-19'daki "ikinci engelde toparlayamadı, durak alanına girdi"
  gözleminin doğrudan sebebi bu.
- **Uygulanan değişiklik** (`neuravix_control_node_real.py` varsayılanları):
  `steer_target_gain -0.75 → -1.20`, `steer_delta_left/right ∓22/23 → ∓36`,
  `steer_raw_min/max -21/26 → -34/38`. Kilidin 2 birim berisinde kesiyor → teker 29.7° → R = 3.26 m.
  Canlı doğrulandı: FSM 45 → hedef **2.0**, FSM 75 (tam sol) → **-34.0**, FSM 15 (tam sağ) → **+38.0**
  (simetrik ±36 sapma).
- `slalom_sim.py` `MAX_DELTA` = **29.7°** ve `~/Desktop/carla-slalom/arac_ayarla.py`
  `BEE1_MAX_STEER_DEG` = **29.7** (spec'in 31.25'i değil — CARLA aracın *ulaştığı* açıya oturtulmalı,
  ulaşamadığına değil).
- ⚠️ **Araçta ilk denemeyi düşük hızda, boş alanda, sürücü frende yapın**: aynı FSM açısı artık
  fiziksel olarak iki kat sert dönüyor. Salınım görülürse `-p steer_delta_left:=-30
  -p steer_delta_right:=30` ile kademeli açılabilir (yeniden derleme gerekmez).

Bunun ortaya çıkardığı iki yan bulgu (ikisi de düzeltildi, masa suite 7/8'e döndü):
- **Bug A'nın ikinci katı — hız yarışı hâlâ vardı.** 2026-08-03'te `lane_detect_event`'in koşulsuz
  `default_speed` yazması düzeltilmişti, ama düzeltme `slow_distance içindeysen slow_speed` diye
  **sabitlenmişti**. `obstacle_event` (10 Hz) daha düşük bir hız yazsa bile şerit olayı (20 Hz)
  50 ms içinde geri eziyordu. Artık iki çağıran da ortak `_engel_hiz_tavani()` kullanıyor.
- **Yeni `blocked_speed` (2.5 km/h).** Engel `avoid_distance` içindeyken açılacak taraf henüz yoksa
  (iki yan koridor kapalı / viraj bastırması / onay sürüyor) araç 6 km/h ile yaklaşıp manevra
  penceresini kendi kapatıyordu: masa sim P1'de taraf açılana kadar geçen 1 s'de 1.7 m yiyip 2.6 m'de
  kaçışa giriyor, kaçış için gereken ~2.5 m + emniyet payı kalmadığı için 0.7 m'de **kalıcı**
  `OBSTACLE_STOP`'a düşüyordu. Sürünme hızıyla taraf açıldığında elde 3.5+ m kalıyor.
- **`obstacle_lidar_node.py` `side_x_min` -2.51 → -1.86** (arka tampon → **arka aks**). Geometrik
  gerekçe: sola kırarken ani dönme merkezi arka aks hattındadır; dışarı en çok savrulan nokta sol ön
  köşedir, arka aksın **gerisindeki** noktalar dönüşün içine kaçar. Yani arka aksın gerisindeki bir
  cisme sola kırarak çarpmak mümkün değil — onu kaçış koridorunda "dolu" saymak gereksiz kısıttı.
  (Arka tamponun dışarı savrulması **geri viteste** olur, slalomda değil.) P1'de 2. engel geçildikten
  sonra 2.5 m boyunca sol koridoru sahte kapalı gösteren tam buydu.

- **`blocked_speed_kmh` iki kontrol düğümünde de ROS parametresi** ve `slow_speed`'i **aşamaz**
  (kod içinde `min()` ile kapılı). Gerekçe: CARLA 8p butonu `slow_speed_kmh:=2.0` geçiyor, beyin
  varsayılanı ise 2.5 — kapı olmasa "çıkış yok" durumu normal yavaşlamadan HIZLI olurdu. Sim
  varsayılanı 1.2, gerçek araç 2.5.
- `~/Desktop/carla-slalom/arac_ayarla.py` artık 29.7° veriyor; 8p yorumundaki "R 3.07 çıkmalı"
  beklentisi **R ≈ 3.26 m** oldu. 3b butonuna basmayı unutursan `[YANAL OLCUM]` yine ~1.1 gösterir.

Doğrulandı: masa suite **7/8** (P1 artık geçiyor; kalan P2 = 5 m aralık, bilinen geometrik sınır),
hem CARLA yan geometrisiyle (2.74/1.26) hem gerçek araç varsayılanlarıyla (3.0/1.0) aynı sonuç;
11 maddelik beyin regresyonu (Bug A, blocked_speed, viraj bastırma, kalıcı zero-drift'in viraj
sayılmaması, fail-safe 0,0,0, stop_distance kapısı, kırmızı ışık zaman aşımı) tamamı geçti; iki
düğüm de ayağa kalkıyor.

**Deploy imajı yeniden derlendi 2026-08-20 09:29** (09:03 build'in yerine — iki teşhis log'u eklendi).
Image ID `315421a85d07`, tar 4.400.084.992 bayt, SHA-256
`ad1101f505d487ce7952fabc1e8a220b5ca6cc9163f8695eb6eccb1f4bfb2040`.

**Konumsuz slalom artık sessiz değil (2026-08-20).** Masa testinde ölçüldü: `update_motion`'a konum
beslenmezse (yani `can_odom` çalışmıyorsa) 8 senaryonun **3'ü geriliyor** — S2 ve P1 geçiyorken
`OBSTACLE_STOP`'a düşüyor, P3'te araç **2.7 m şerit dışına** çıkıyor. Sebep: 4 fazlı slalomun yanal
ofseti konumdan ölçülüyor; konum yoksa zaman/mesafe yedeğine düşüyor. CLAUDE.md'nin eski
"odometri yoksa zarifçe FSM-only sürüşe düşer" ifadesi **slalom için geçerli değil**. Eklenen iki şey:
`neuravix_control_node_real.py`'nin her durum satırında `hareket=odom | ODOM YOK (CAN hizi) |
HAREKET VERISI YOK`, ve `OBSTACLE_AVOID`'a konumsuz girilirse bir kez WARN. Araç koşusu öncesi
`ros2 topic hz /odometry/can_wheel` **zorunlu ön kontrol**.

**Weave uzunluğu ölçüldü: 9.4–9.7 m** (29.7° kilit, yanal hedef 1.7). 17.08'de ölçülen 11.8 m'den
iyi ama hâlâ hedeflenen 5–6 m değil. Pratik sonuç: **engel aralığı ≥7 m olmalı**; 5 m aralıkta
(masa senaryosu P2) araç weave'i tamamlayamıyor ve güvenli şekilde duruyor (çarpışma yok, 1.12 m).

**⚠️ `steer_delta_left/right:=∓30` KULLANMAYIN.** İlk koşu için "kademeli emniyet" diye önerilmişti,
masa testi tam tersini gösterdi: 24.8°'de (∓30) **8 senaryonun 8'i** başarısız — tek engelli S1'de
bile araç yarı yolda kalıp `y=+0.87`'de şerit dışında duruyor. Yanal hedef/align ile ilgisi yok,
tek değişken direksiyon menzili. Sebep: kaçış fazı yanal hedefe varınca biter, R büyüdükçe aynı
yanal daha uzun yol ister ve manevra engel aralığına sığmaz — 08-19'da araçta görülen "ikinci engelde
toparlayamadı" davranışının ta kendisi. Emniyet direksiyonu kısarak değil **hızı düşürerek** alınır
(`-p slalom_speed_kmh:=6.0` geometriyi bozmaz).

Eski kayıt — imaj 2026-08-20 09:03 — 19 Ağustos şerit birleştirmesi + 19-20 Ağustos
direksiyon menzili / hız tavanı / `side_x_min` düzeltmelerinin tamamını içerir. Image ID
`dbe10531b493`, tar `~/robotaksi_deploy/robotaksi_humble.tar` **4.400.078.336 bayt**, SHA-256
`bf7f8dc8d9cb8e4c53ac65cdb2b2c186decf10170ed6e897fdfbd7293f95c0dd`. İmajın *içinde* doğrulandı
(`/ros2_ws/install/neuravix_ros2/lib/python3.10/site-packages/neuravix_ros2/`): gerçek düğümde
`steer_target_gain=-1.20`, `steer_delta_left/right=∓36`, `steer_raw_min/max=-34/38`,
`blocked_speed_kmh=2.5`; sim düğümünde `blocked_speed_kmh=1.2`; beyinde `blocked_speed=2.5` +
`_engel_hiz_tavani`; lidarda `side_x_min=-1.86`; `models/` içinde `serit_v2.pt` + `birlesik_v2.pt`.

⚠️ **Bir önceki imajın tar'ı laptopta `~/robotaksi_deploy/robotaksi_humble_0819_1033.tar` adıyla
duruyor** (4.326.647.296 bayt, 19 Ağu 10:33 — şerit birleştirmesi var, direksiyon düzeltmesi yok).
`docker save` sırasında T7 bağlı değildi; **T7'ye kopyalanınca laptoptaki bu yedek silinebilir.**
Araçta hâlâ eski imaj koşuyor: `docker load` + `docker rm -f robotaksi_container` + `docker run`
yapılmadan yeni kod araca ulaşmaz.

**DİREKSİYON HIZI ASIL DARBOĞAZ (2026-08-20).** Bugünkü ölçümler, slalomun neden araçta
tutmadığını kesinleştirdi ve sebebin beyin ayarları **olmadığını** gösterdi.

Ölçüm kaynakları: `~/lokal_0820_0722` (10:22:07 + 126 s, kontrol log'unun 10:23:44–10:24:13
penceresini kapsıyor) ve `~/slalom_0819_1318`. İkisi de workspace dışında, `~` altında.

- **Kalibrasyon doğrulandı, bağımsız sensörle.** `/imu/data` gyro-z + `/beemobs/FB_VehicleSpeed`
  ile bisiklet modelinden teker açısı (direksiyon kalibrasyonundan tamamen bağımsız):

  | ham sapma | teker açısı | R |
  |---|---|---|
  | 21 (**eski clamp**) | 19.9° | **5.13 m** |
  | 24 | 25.9° | 3.83 m |
  | 28 | 27.8° | 3.54 m |
  | **32** | **31.5°** | **3.03 m** |

  Doğrusal uyum `teker = 0.948 × ham_sapma`, yani **1 ham birim ≈ 1° teker açısı**. Spec'in
  31.25° / R 2.88–3.13 değeri ham sapma ~32'de tutuyor. 08-19 direksiyon menzili düzeltmesi
  (`steer_delta ∓36`, `ham_limit -34/+38`) **doğrulandı**. Not: tekerlek pratikte ham **±31**'de
  doyuyor, yani -34/+38 clamp'ine hiç ulaşılmıyor — zararsız.
- **Tekerlek YAVAŞ: medyan 10 birim/s** (görülen en yüksek 30.3). Kontrol log'undaki 9 saniyelik
  açıklanamayan yanal kayma tam olarak bu: t=10:23:52'de komut `+38`'e sıçradı, tekerlek `-27`'deydi;
  +1 s: -15, +2 s: **+2**, +4 s: +31. **İki saniye boyunca araç sağa kırdığını sanarken hâlâ sola
  dönüyordu.** Yanal ofset hedef 1.7 m iken 3.0'a çıktı; `v·T·sin(θ) = 0.55×3.2×0.67 = 1.18 m`
  hesabı ölçülen fazlayla birebir.
- **Menzili açmak bunu KÖTÜLEŞTİRDİ**: kilitten kilide 47 → **72 birim**, yani 4.7 s → 7.2 s.
  Bu, 08-19 düzeltmesinin bilinçli kabul edilmiş bedeli — menzili geri kısmak R'yi 5.1 m'ye
  döndürür ve masa testi onun 8/8 başarısız olduğunu söylüyor.
- **KÖK NEDEN `steering_ctrl`'ün `max_delta=68` clamp'i.** Yasa:
  `delta = min(max_delta, min_drive + kp*(|hata|-tol))`, `pwm = 127 ± delta`. Bag'den ölçülen:

  | hata | PWM sapması |
  |---|---|
  | 2 | +17 |
  | 13 | +49 |
  | 22 | **+67** |
  | 38 | **+67** (doymuş) |

  `delta` **|hata| ≈ 16'da** tavana vuruyor. Motorun yetkisi ±127; kontrolcü **%53'ünü**
  kullanıyor. Faz geçişinde hata 65'ti, PWM yine 195.
- **⛔ `max_delta` YÜKSELTMEK İŞE YARAMIYOR — ölçüldü, kapandı (2026-08-20).** T7'deki
  `joystick_46` bag'i bunu kesinleştirdi: joystick/RC yolu `AUTONOMOUS_SteeringMot_Control`'e
  **bang-bang** yazıyor (yalnızca 3 değer: 70, 200, 0), yani PWM sapması **73** — bizim
  `max_delta=68`'den DAHA BÜYÜK. Aynı yöntemle (>=20 birimlik kesintisiz geçişler) iki bag:

  | | joystick (sapma 73) | otonom (`max_delta=68`, sapma 68) |
  |---|---|---|
  | medyan geçiş hızı | **9.5** birim/s | **9.2** birim/s |
  | en iyi geçiş | 17.8 | 12.5 |

  Sapma 57 / 68 / 73 **aynı hızı** veriyor → doygunluk `max_delta`'da değil **motorda**.
  Tüm veride en iyi büyük geçiş: -38 → +20 (58 birim) 4.6 s = **12.6 birim/s**. Yani
  `-p max_delta:=90` / `:=110` denemenin bir anlamı yok; gerçek sınır ~10 birim/s sürdürülen,
  ~13-18 tepe. (Dosyanın kendi statik `semantik_1` ölçümü de aynı yöne işaret ediyordu:
  sapma 23 → 128, yani 5.5×, sadece 1.6× hız.) **Bu, daha önce bu dosyada "en değerli bulgu"
  diye yazılan `max_delta` önerisini GEÇERSİZ KILAR.**
- **Hız düşürmek de kurtarmıyor.** `slalom_speed` 4.0 / 2.5 / 1.5 × `slalom_escape_steer` 75/62 ×
  mesafeler: 16 kombinasyonun hepsi 3/8. Düşük hızda weave GEOMETRİK olarak tamamlanıyor
  (izde görüldü: engel y=+1.62 ile temiz geçildi) ama senaryo yine düşüyor.
- **Geriye kalan:** slalom stratejisinin kendisi 10 birim/s'lik bir aktüatöre göre yeniden
  düşünülmeli, ya da direksiyon sürüşü araç ekibiyle konuşulmalı
  (`autonomous_steeringmot_en` yalnızca 1 kullanılıyor; başka bir mod var mı bilinmiyor).

**Masa simülatörüne direksiyon aktüatörü eklendi (`slalom_sim.py`, 2026-08-20).** Önceden FSM açısı
ANINDA teker açısına çevriliyordu; suite 7/8 verirken araç sahada takılıyordu — simülatör gerçeği
değil bir kurguyu test ediyordu. Yeni model: `fsm_to_raw()` kontrol düğümünün ham eşlemesini birebir
kopyalar (gain -1.20, delta ∓36, limit -34/+38), tekerlek hedefe `STEER_SLEW` (varsayılan 10) birim/s
ile yaklaşır, `STEER_TOL` içinde motor kapalı, `DEG_PER_UNIT=0.98`. Doğrulama: gecikmesiz 7/8
(eski sonuç korunuyor), ölçülen gecikmeyle **3/8** — aracın hatasını birebir üretiyor.

| slew (birim/s) | suite |
|---|---|
| 10 (**şu an**, `max_delta=68`) | 3/8 |
| 13 (`max_delta=90` tahmini) | 3/8 |
| 20 | 3/8 |
| 30 (görülen en yüksek) | 4/8 |
| ∞ | 7/8 |

**Beyin tarafında hiçbir ayar kurtarmıyor** — 108+18+72 kombinasyon tarandı (`slow_distance`,
`avoid_distance`, `slalom_escape_steer`, kaçış çıkış eşiği, `slalom_speed`, lead), 10 birim/s'de
hepsi aynı sonucu verdi. Aritmetik: bir weave'de tekerlek düz→sol→sağ→düz ≈ **140 birim** = 14 s =
4 km/h'de **15 m**; engel aralığı 7 m. **Fiziksel olarak sığmıyor.** S1 izi: weave t=3.60'ta başlıyor
(hedef ham -28.6), t=5.90'da tekerlek daha -20.5, bu arada `front` 3.78 → 0.91 ve acil eşik kalıcı
`OBSTACLE_STOP` veriyor — araç kaçış açısına **hiç ulaşamadan** engele varıyor.

Bu yüzden `max_delta` ölçümü kritik: **"hızlandı mı" değil, kaç birim/s olduğu lazım.** Araç
kaldırılmış veya boş alanda yavaş sürerken (duran araçta lastik sürtünmesi ölçümü bozar):
`-30` → `+30` (60 birim) kaç saniyede gidiyor.

Bugün eklenen küçük şeyler (hepsi imajda):
- **`steering_ctrl` artık çalışırken ayarlanabiliyor** (`add_on_set_parameters_callback`).
  Öncesinde parametreler açılışta bir kez okunup instance değişkenine yazılıyordu, yani
  `ros2 param set /steering_ctrl max_delta 110` **sessizce hiçbir şey yapmıyordu** — "110'u
  denedim" diye kaydedilen bir koşu aslında 68 ile koşacaktı. (Aynı tuzak `lane_follower`'ın
  `err_offset`'inde de var.) `max_delta` 0..127 dışında reddedilir, `use_sim_time` gibi altyapı
  parametreleri dokunulmadan geçer, her değişiklik log'a yazılır. Tek koşuda 90 → 110 denemek
  artık mümkün, bag kesintiye uğramaz — **ama değişim anları bag'de görünmez, saatleri not edin.**
- **`steer_lead_time`** (varsayılan **0 = KAPALI**): `err_deg`'i yaw hızıyla ileri taşıyan lead
  kompanzasyonu. Denendi ve **her slew değerinde daha kötü** çıktı (gecikmesiz 7/8 → 5/8,
  slew=14'te 6/8 → 3/8): tekerlek hız sınırı bağlayıcı kısıtken "daha sert kır" demek komutu
  doyuma itmekten başka işe yaramıyor. Kod duruyor çünkü direksiyon hızlandıktan *sonra* kalan
  küçük gecikme için doğru araç odur. `_yaw_rate` (EMA 0.7/0.3) `update_motion`'da hesaplanır.
- **`slalom_escape_lat_frac`** (varsayılan 0.5, eskiden sabit): kaçış fazının çıkış eşiği.
- **Kontrol düğümünün başlangıç log'una şerit aralığı eklendi.** `lane_min`/`lane_max` görünmüyordu,
  yani "sol şeritte başlıyorum" parametresinin tuttuğu doğrulanamıyordu. Artık:
  `serit araligi -1..0 (baslangic 0, sola kacis YASAK, saga serbest)`.

**Şerit başlangıcı için ayrı parametre YOK ve gerekmiyor** — `lane_index` tanımı gereği hep 0
(= başladığın şerit), sınırlar ona **göreli** verilir:

| durum | parametre |
|---|---|
| 2 şeritli, sağ şeritte başla (varsayılan) | `lane_min:=0 lane_max:=1` |
| 2 şeritli, **sol** şeritte başla | `lane_min:=-1 lane_max:=0` |
| 3 şeritli, ortadan başla | `lane_min:=-1 lane_max:=1` |

Yanlış verilirse araç açık olan tarafa kaçmayı reddedip `IKI TARAF DA KAPALI: ... SERIT YOK` der.

**Deploy imajı yeniden derlendi 2026-08-20 13:59** (09:29 build'in yerine). Image ID `a9aa19d385c6`,
tar `~/robotaksi_deploy/robotaksi_humble.tar` **4.400.098.816 bayt**, SHA-256
`8add112d20d5ea486147f1c4c75b741755a45a59410e8cd8421bb1ce31b44ed0`. İmajın içinde doğrulandı:
`steering_ctrl`'de `_on_params`, kontrol düğümünde şerit aralığı log'u, beyinde `blocked_speed` /
`_engel_hiz_tavani` / `slalom_escape_lat_frac` / `steer_lead_time` / `_yaw_rate`.

Sıradaki araç koşusunun bag komutu (slalom + lokalizasyon birleşik, tek kayıt):
```
ros2 bag record -o /root/maps/slalom_$(date +%m%d_%H%M) \
  --compression-mode file --compression-format zstd -b 2000000000 \
  /master /neuravix/current_state /neuravix/decision_dump \
  /neuravix/lane_debug/compressed /neuravix/bev_debug/compressed \
  /velodyne_points /imu/data /scan_bee1 /tf_static \
  /odometry/can_wheel /safety/emergency_stop \
  /gnss /filter/positionlla /filter/velocity /filter/quaternion /imu/mag \
  /beemobs/FB_VehicleSpeed /beemobs/FeedbackSteeringAngle \
  /beemobs/FB_MotorDriver /beemobs/FB_OMUX_to_AUTONOMOUS \
  /beemobs/rc_unittoOmux /beemobs/AUTONOMOUS_BrakePedalControl \
  /beemobs/steering_target_value /beemobs/speed_target_value \
  /beemobs/AUTONOMOUS_SteeringMot_Control /beemobs/RC_THRT_DATA
```
Slew ölçümü için gereken üçlü (`steering_target_value` + `AUTONOMOUS_SteeringMot_Control` +
`FeedbackSteeringAngle`) bu listede. `steering_ctrl`'ü `-p tolerance:=2.0` ile başlatın: motor
hızlanınca ±1 birimlik bant dar kalıp salınıma girer.

`joystick_46` bag analizi (T7, 2026-08-20 10:09, 290.5 s, **30.6 GB — sıkıştırmasız kaydedilmiş**,
`--compression-mode` unutulmuş; aynı süre zstd ile ~1 GB olurdu):
- **Şerit boru hattı gerçek ZED üzerinde iyi çalışıyor.** 8154 ZED karesi → 7810 `/master` ID-2
  mesajı (**%96 kare işlendi**), overlay'de **FPS 26-27**. `serit_v2.pt` + yeni düğüm birlikte
  araçta ilk kez doğrulandı.
- Şerit açısı: ort **44.9**, std **2.8**, aralık 30..58 (mümkün olan 15..75'in çok içinde).
  Nötr 45 (= şerit kayıp) oranı **%12.5**. Yani karelerin %87.5'i gerçek bir kestirim üretmiş.
- **`LaneW` bedava bir geçerlilik sinyali ve KULLANILMIYOR.** Üç örnek kare:

  | kare | sahne | LaneW | Error | Steering |
  |---|---|---|---|---|
  | düz, çizgiler görünür | pist düzlüğü | **446 px** | +58 px (+0.39 m) | 43 |
  | otopark/padok, çizgiler görünür | insanlar var | **493 px** | +33 px (+0.20 m) | 42 |
  | **viraj, bariyer dolu, çizgi yok** | — | **129 px** | **-204 px (-4.75 m)** | 51 |

  446/493 px, `pist_18_3tem` analizindeki ~445 px ile birebir tutuyor — homografi doğru.
  Ama bariyerli virajda fit tamamen anlamsız bir şeye oturuyor (**1.04 m genişlik**, bir şerit
  olamaz) ve düğüm bunu **güvenle yayınlıyor**; `AvgErr -184` sürekli. Zararı `steer_kp=0.03`
  sayesinde sınırlı kalıyor (204 px → sadece +6 birim direksiyon), ama sürekli bir yanlılık
  üretiyor. `lane_w_px` zaten ölçülüyor; makul aralık dışındaysa (ör. <300 veya >550 px) fitin
  reddedilmesi tek satırlık bir kapı olurdu. ⚠️ Not: 2026-07-21'de bir şerit-geçerlilik deneyi
  (250..520 px geometri kapısı + fit-sıçrama + heading gain + `LaneValid`) **reddedilip geri
  alınmıştı**; buradaki öneri o paketin tamamı değil, yalnızca ölçülen `LaneW`'e bakan kapı.
- **`bev_debug` ilk kez araç verisinde işe yaradı.** Kuşbakışında bariyerlerin ışınsal şerit
  halinde ezildiği (yer düzlemi dışındaki her şeyin klasik IPM artefaktı) ve yolun sadece sol
  altta ince bir dilim kaldığı doğrudan görülüyor — bu görüntü olmadan "129 px neden" sorusu
  cevaplanamazdı.
- Bag'de `/beemobs/steering_target_value` YOK (kayıt listesinde değildi), o yüzden kontrolcü
  hatası hesaplanamadı; ama slew ölçümü için PWM + geri besleme yetti.

`_weave_finished()`'a burun-güveni kapısı eklendi (2026-08-20): weave bitiminde "engel devam
ediyor" kararı, burun şerit yönünden sapmışken **ön okumasına güvenmiyor** (`_front_guvenilir` /
`front_trust_deg`, weave İÇİ yeniden planlamada zaten vardı, bitişte eksikti). Masa siminde
ölçüldü: tek engelli S1'de engel çoktan geride kalmışken `front=5.1` okundu ve araç ortada engel
yokken ikinci bir weave açtı. Kapı gecikmesiz suite'i **7/8'de bırakıyor** (regresyon yok) ama
slew=10'daki 3/8'i de değiştirmiyor — doğru ama yeterli değil.

Şerit genişliği kapısı eklendi (`lane_follower_node.py`, 2026-08-20):
- **Ne yapar:** iki fit birden varken aralarındaki mesafe (= `LaneW`) `lane_w_min_px`..
  `lane_w_max_px` (**250..600**) dışındaysa çift-fit merkezi kullanılmaz.
- **Neden bu sınırlar:** ölçülen gerçek değerler dar bir bantta — `pist_18_3tem` analizinde
  445±12, `joystick_46`'da düz yolda 446 ve padokta 493. Bariyerli virajda okunan **129 px =
  1.04 m** ise fiziksel olarak imkânsız (araç bile 1.06 m eninde); o karede fit şerit çizgilerine
  değil bariyer/asfalt sınırına oturmuştu ve düğüm `Error -204 px (-4.75 m)` / `AvgErr -184`
  değerlerini güvenle yayınlıyordu. Amaç makul olanı elemek değil, imkânsız olanı elemek.
- **⚠️ REDDETMİYOR, TEK-FİTE DÜŞÜRÜYOR — bu kasıtlı.** Aynı dosyada 2026-08-19 tarihli bir not
  var: fit REDDETMEK kapalı çevrimi **kötüleştirmişti** (0.98 → 4.31 m), çünkü reddedilen kare
  bayat fitle köprüleniyor ve manevrada bayat bilgi gürültülü tazeden zararlı. Bu yüzden kapı
  fitleri atmaz; piksel sayısı yüksek olan **tek** fit tutulur ve merkez `_tek_fit_merkez()` ile
  son ölçülen yarım-şerit ofsetinden kurulur (taze bilgi + güvenilir geometri). Tek-fit yolu
  zaten karelerin %35-57'sinde kullanılan, denenmiş bir yol.
- **SINIRLAR VARSAYIM DEĞİL, ÖLÇÜM (T7'deki `joystick_46`, 204 kare boru hattından geçirildi).**
  144'ünde (%70.6) iki fit birden çıktı ve genişlik dağılımı **iki tepeli**, arada temiz bir
  boşluk var:

  ```
  50px:7  100px:10  150px:2  |  [150..250 arası HİÇ kare yok]  |  250:3 300:2 350:3 400:18 450:81 500:18
       19 kare — anlamsız fit                                          125 kare — gerçek şerit
  ```

  Medyan 462, %90 504, maks 548. Eşik o boşluğa kondu: **250..600**, gözlenen 19 anlamsız karenin
  tamamını eliyor ve gerçek kümeden hiçbir kareye dokunmuyor. (İlk denenen 300..550, 3 meşru kareyi
  de eliyordu — düzeltildi.) 250 px = 2.0 m, 2.96 m'lik bir şerit için hâlâ imkânsız derecede dar.
- **Doğrulandı, iki metrikle birden** (bu dosyadaki kural: takip hatası + direksiyon yumuşaklığı
  BİRLİKTE onaylanmalı). Sentetik kapalı çevrimde kapı **tamamen etkisiz** (kapısız referansla
  birebir aynı). Gerçek karelerde kapalı/açık aynı 204 kare üzerinde:

  | | kapalı | açık |
  |---|---|---|
  | ortalama direksiyon | 44.82 | 44.63 |
  | std | 2.84 | 2.83 |
  | kare-kare oynaklık | 1.64 | **1.60** |
  | ateşlenme | — | **25/204 = %12.3** |
  | tek karede en büyük düzeltme | — | **7 birim** |

  Yani ~%12 karede somut düzeltme yapıyor, yumuşaklığı bozmuyor (hafif iyileştiriyor).
  ⚠️ **Kanıtlanan şey "çıktı daha doğru" değil**, "çıktı geçerli bir öncüle dayanıyor": elenen
  karelerin fiti fiziksel olarak imkânsız bir genişlikten geliyordu. Yer gerçeği olmadan doğruluk
  iddiası kurulamaz. Kapatmak için `-p lane_w_gate:=false`.
- Düğüm her 50 ateşlemede bir WARN basıyor (`Serit genisligi NNNpx makul disi ... -> tek fite
  dusuldu (N. kez)`) — araçta oranı bu satırdan izleyin. %12'nin belirgin üstüne çıkarsa sınırlar
  gözden geçirilmeli.
- **⚠️ Şartname "şeritten çıkmadan viraj" istiyor.** Kapı bariyerli virajlarda sık ateşlenirse
  araç orada nötr 45'e yaklaşır, yani virajı şerit takibiyle dönemez. O durumda sorun kapıda
  değil algıda.

**İki masa aracının direksiyon sabitleri güncellendi ve bu beklenmedik bir kazanç ortaya çıkardı.**
`tools/serit_kapali_cevrim.py` ve `tools/serit_bag_cevrim.py` hâlâ `STEER_RAW_MIN/MAX = -21/26` ve
`FSM_TO_RAW_GAIN = -0.75` ile koşuyordu, yani **eski yarım-kilit aracı** modelliyorlardı.
Kontrol düğümüyle aynı değerlere çekilince (-34/+38, gain -1.20) sentetik kapalı çevrim:

| | ort hata | maks hata |
|---|---|---|
| eski sabitler | 0.60 m | 1.47 m |
| **yeni sabitler** | **0.20 m** | **0.43 m** |

Direksiyon menzili düzeltmesinin **şerit takibini de 3 kat iyileştirdiği**, ondan bağımsız bir
testte doğrulanmış oldu (maks ham komut 7.7, yani limitlere hiç dayanmıyor — kazanç gain'den
geliyor, aynı FSM açısı artık gerçekten dönüşe çevriliyor).
⚠️ Her iki masa aracı da direksiyon **SLEW** hızını (~10 birim/s) modellemiyor — sadece
`slalom_sim.py`'de var. Yani şerit sonuçları tekerleğin anında vardığını varsayar ve
özellikle keskin viraj girişlerinde **iyimserdir**.

**Deploy imajı yeniden derlendi 2026-08-20 14:50** (14:37 build'in yerine — kapı sınırları
ölçümle 250..600'e çekildi). Image ID `baaf1aa6e2c8`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.400.105.984 bayt**, SHA-256
`6ca613b5f3cb2a60f89f1510e9ef400a47de0f965f743f4d94daf1ba245e1a00`. İçinde doğrulandı:
`lane_w_min_px=250 / lane_w_max_px=600`.

`Bags_slaloms` — 5 kayıt, 2026-08-20 (birleşik tarifle alındı, hepsi eksiksiz):
`slalom_0820_0728` (44 s), `1212` (164 s), `1216` (98 s), `1220` (68 s), `1222` (43 s).
`/scan_bee1` hiçbirinde yok (p2l koşmuyordu, mapping yapılmadığı için sorun değil).

**SLALOM ARIZASI TAM OLARAK ÖLÇÜLDÜ (`slalom_0820_1212`).** `can_odom` yörüngesi weave başına
göre (t=114'te `OBSTACLE_AVOID`, front=3.7):

| t | ileri (m) | yanal (m) | yaw |
|---|---|---|---|
| 114 | 3.6 | 0.00 | 0° |
| 120 | 5.4 | +0.45 | +31° |
| **124** | 6.3 | +1.30 | **+52°** ← kaçış tepe açısı |
| 128 | 7.5 | +2.38 | +29° |
| **132** | 9.6 | **+2.85** ← yanal tepe (hedef **1.7**) | -4° |
| 136 | 11.8 | +1.94 | -39° |
| **140** | 13.1 | +0.06 | **-72°** ← şeride döndü ama burun 72° sağda |

Toplam 15.3 m yol. Araç yanal olarak şeride döndü ama **72° sağa bakar halde**, yani doğrudan
sağ bariyere doğru; orada durdu (`OBSTACLE_STOP`, front 0.5) ve operatör müdahale etti.
Son karenin overlay'i aracın bariyer duvarının burnunda olduğunu gösteriyor.

**Zincir, adım adım — hepsi direksiyon gecikmesinden türüyor:**
1. Kaçış fazı **yanal** ölçütle biter (`0.5 × weave_lat` = 0.85 m). Yanal, baş açısının GECİKMELİ
   göstergesidir: 0.85 m'ye varıldığında tekerlek zaten tam kilitte ve ters kilide gitmesi 3 s
   sürüyor — o sürede baş açısı **+52°**'ye çıkıyor (tasarım ~42°).
2. 52°'lik burunla geçiş fazı yanalı hızla yiyor: 1.30 → **2.85 m**, hedefin **%68 üstü**.
3. Dönüş fazı hem 2.85 m yanalı hem büyük açıyı toparlamak zorunda: **13 saniye** kesintisiz
   tam sağ kilit (hedef +38, tekerlek +32). R≈3 m'de bu ~130°'lik dönüş demek.
4. t=137'de FSM tekrar "sola" diyor ama **araç durmuştur** (hız 0) ve tekerlek +31'den 4 saniyede
   ancak 25'e geliyor = **1.5 birim/s**. Yani duran araçta direksiyon pratikte hareket etmiyor.

**YENİ VE ÖNEMLİ: slew hızı araç DURUNCA çöküyor.** Yuvarlanırken ölçülen ~10-17 birim/s,
0 km/h'de **~1.5 birim/s**. (Dosyanın kendi `semantik_1` statik ölçümü de 1.16 birim/s diyordu —
o değer "yanlış" değilmiş, DURAN araç için doğruymuş.) Sonuç: araç direksiyon kırıkken durursa
kendini düzeltemez. Bu, `OBSTACLE_STOP`'tan çıkışı da etkiler.

Bu kayıt, `slalom_sim.py`'ye eklenen direksiyon aktüatörü modelini **doğruluyor**: bag'de
t=114'te 22 birim/2 s = 11 birim/s, t=123'te 51 birim/3 s = 17 birim/s — modeldeki 10 birim/s
ile aynı mertebe, ve masa siminin ürettiği arıza deseni (kaçış aşımı → yanal aşım → toparlayamama)
sahada birebir gerçekleşmiş.

⚠️ **Bunun bir sonucu var: nursena'nın 4 fazlı (yanal ölçütlü) slalom motorunun, bizim
yaw-baş açısı ölçütlü 2 fazlı motorumuza tercih edilmesi (2026-08-10, masa suite 5/5 vs 4/5)
DİREKSİYON GECİKMESİ MODELLENMEYEN bir simülatörde karara bağlandı.** Yanal ölçüt gecikmeli,
baş açısı ölçütü değil — gecikmeli aktüatörde bu fark kritik olabilir. Karar yeniden
değerlendirilmeli; ancak `scratchpad/backup_merge/decision_brain.MINE.py` yedeği silinmiş,
eski motor `github.com/teamneuravix/neuravix2026` geçmişinden alınmalı.

**`/neuravix/decision_dump` teşhis için YETERSİZDİ, genişletildi (2026-08-20).** Sadece 5 alan
taşıyordu (steer, hız, fren, sinyal, limit) ve `avoid_phase` yoktu — 1212'de aracın 32 saniye
hangi fazda kaldığı bag'den **çıkarılamadı**. Artık 12 alan:
`[steer, hiz, fren, sinyal, limit, FAZ, _lateral, _weave_lat, lane_index, front, left, right]`,
faz kodu `0=yok 1=escape 2=pass 3=return 4=align`. Her iki kontrol düğümünde de.
(Not: `decision_dump` `Float32MultiArray`'dir, `String` değil — bag'den okurken bu karıştırıldı.)

**ŞERİT: `err_offset` DEĞİL, YANLIŞ ÇİZGİ ÇİFTİ.** Sahada okunan `-70 küsür` hata gerçek, ama
bir kalibrasyon sabiti değil:

| kayıt | saat | err ort |
|---|---|---|
| `joystick_46` | 10:09 | **≈ 0** (ort +0.7 px) |
| `slalom_0820_1220/1222` | 15:20 | **-63 px** (ort direksiyon 46.9) |

Kamera/trapez ofseti olsaydı ikisinde de aynı çıkardı. Overlay kareleri sebebi gösteriyor: geniş,
çok çizgili test alanında **sol fit en soldaki çizgiye, sağ fit bariyere** oturuyor — yani
bracket edilen "şerit" aracın gerçekte bulunduğu şerit değil. Ölçülen kareler: `Error -124px
LaneW 394px` ve `Error -78px LaneW 271px`.
- **Genişlik kapısı bu sınıfı YAKALAMIYOR**: 271 ve 394 px, kapının 250..600 bandının içinde.
  Kapı `joystick_46`'daki kaba hataları (50-150 px) eliyor, bunları elemiyor. Sınırları daraltmak
  gerçek kareleri de eleyeceği için doğru çözüm değil.
- **`-p err_offset:=-72` UYGULAMAYIN.** Bu kesitte semptomu bastırır, `joystick_46` gibi düzgün
  kesitlerde 72 px'lik ters hata üretir. Ölçüldü: off=-72 ile err ortalaması 0.7 → **+73.5 px**.
- **`-p heading_gain:=0` ayrı bir konu ve makul.** Ölçüldü: ofseti kaydırmıyor (katkı ort
  -0.9 px) ama saçılmayı azaltıyor (err std 104.7 → 88.9, %15). Tek karede 342 px'e kadar
  çıkabildiği için gürültü kaynağı.
- Asıl çözüm algı tarafında: modelin geniş çok-şeritli yüzeyde doğru çizgi çiftini seçmesi
  (ör. araca en yakın iki çizgi, ya da şerit-genişliği tutarlılığıyla eşleştirme).

`Bags_slaloms` tam envanter ve sorun listesi (2026-08-20, beş kaydın tamamı ölçüldü):

| bag | süre | ID-4 engel | FSM durumları | direksiyon hedefi | ne olduğu |
|---|---|---|---|---|---|
| `0728` | 44 s | 445 | sadece LANE_FOLLOW | sabit **-0.4** | **duran araçta tezgâh testi** (hız hep 0, tekerlek 0'da sabit; hata 0.4 < `tolerance` 1.0 olduğu için motor hiç çalışmadı — tutarlı) |
| `1212` | 164 s | 1630 | LANE→AVOID→**STOP** | -34..38 | **SLALOM**, %21.6 kaçınmada |
| `1216` | 98 s | 678 | LANE→AVOID→STOP | -34..38 | **SLALOM**, **%50.5 kaçınmada** |
| `1220` | 68 s | **0** | sadece LANE_FOLLOW | -3..6 | sadece şerit (`obstacle_lidar` koşmuyordu) |
| `1222` | 43 s | **0** | sadece LANE_FOLLOW | -3..2 | sadece şerit |

**S1 — Slalom manevrası her iki koşuda da AYNI şekilde aşıyor (tekrarlanabilir).**

| | 1212 | 1216 | tasarım |
|---|---|---|---|
| kaçış tepe baş açısı | **+52°** | **+46°** | ~42° |
| yanal tepe | **2.85 m** | **2.42 m** | 1.7 m |
| dönüş tepe açısı | **-72°** | **-59°** | ~0° |
| bitiş | bariyer burnunda, `OBSTACLE_STOP` | 18 s `OBSTACLE_AVOID`'da donuk | şeride dönmüş |

Sebep zinciri (ölçüldü): kaçış fazı **yanal** ölçütle biter (`0.5 × 1.7 = 0.85 m`); yanal, baş
açısının GECİKMELİ göstergesidir. 0.85 m'ye varıldığında tekerlek zaten tam kilitte ve ters kilide
gitmesi ~3 s sürdüğü için açı +46..52°'ye çıkar. Bu açıyla geçiş fazı yanalı hızla yer (2.4-2.9 m),
dönüş fazı hem yanalı hem açıyı toparlamak için 13 s tam kilit tutar ve burun -59..-72°'ye savrulur.
Araç yanal olarak şeride döner **ama bariyere bakar halde**.

**S2 — Direksiyon aktüatörü yavaş ve DURUNCA pratikte donuyor.**
- Yuvarlanırken 10-17 birim/s (bag'den: 22 birim/2 s ve 51 birim/3 s).
- **0 km/h'de 0.05 birim/s**: `1216`'da t=68-90 arası hedef -28, tekerlek +29 → +28, yani 22
  saniyede **1 birim**. Araç direksiyon kırıkken durursa kendini düzeltemez — kilitlenme.
- `1216`'da tekerlek hedefin **10 birimden fazla gerisinde kaldığı süre %70** (`1212`'de %12).
  Yani FSM hedefi, tekerleğin takip edebileceğinden hızlı değiştiriyor.
- `max_delta` değil motor sınırı (joystick bang-bang sapma 73 ile aynı hızı veriyor).

**S3 — Araç gaz komutuna rağmen ilerlemiyor.**
`1216` weave penceresinde: hız **hedefi hiç 0 olmadı (%0)**, gaz pedalı ortalama **70** (ölü bölge
47'nin çok üstünde), buna rağmen **gerçek hız %47 oranında 0**. `1212`'de hedef %11 sıfır, gerçek
%30 sıfır. Fren `per=0` (doğrulandı, fren değil).
Muhtemel sebep: tekerlek tam kilitteyken duran araçta lastik sürtünme momenti çok yüksek ve
mevcut pedal kalkışa yetmiyor. Bu S2 ile birlikte **kısır döngü** kuruyor: kırık tekerlek →
kalkamıyor → hareket olmadığı için tekerlek dönemiyor.

**S4 — Şerit hatası bir ofset DEĞİL; fit yanlış çizgi çiftine oturuyor.**
Beş kayıtta ima edilen hata: `0728` **-67**, `1220` -62, `1222` -63, `1212` -38, `1216` **+12** px.
**İşaret bile değişiyor** — sabit bir kalibrasyon ofseti böyle davranmaz.
Overlay kareleri sebebi gösteriyor: geniş çok-çizgili alanda sol fit en soldaki çizgiye, sağ fit
bariyere oturuyor; bracket edilen "şerit" aracın bulunduğu şerit değil. O karelerde
`LaneW` 271-394 px — **genişlik kapısının 250..600 bandının İÇİNDE**, yani kapı bu sınıfı
yakalamıyor (kapı `joystick_46`'daki 50-150 px'lik kaba hataları eliyor).
⇒ `-p err_offset:=-72` **verilmemeli**: `1220/1222`'yi düzeltir, `1216`'yı 84 px bozar.
`-p heading_gain:=0` ayrı ve makul (ofseti kaydırmaz, saçılmayı %15 azaltır).

**S5 — `1216`'da engel verisi 5 kat gürültülü.** 99↔engel sıçraması `1212`'de 0.04/s, `1216`'da
**0.21/s**. Aynı donanım, aynı gün. Bariyer geometrisine veya araç açısına bağlı olabilir;
`obstacle_lidar`'ın 2/5 kare zamansal süzgeci bunu tam bastıramıyor.

**S6 — `1216`'da stall guard çalışmadı.** Araç 18 saniye 0 km/h'de `OBSTACLE_AVOID`'da kaldı;
`stall_timeout` 4 s / `stall_min_distance` 0.25 m ile çoktan `OBSTACLE_STOP`'a düşmeliydi.
(`1212`'de düştü.) Neden ayrışmadığı henüz bilinmiyor — yeni genişletilmiş `decision_dump` ile
bir sonraki kayıtta faz + `_lateral` görülebileceği için cevaplanabilir olacak.

**Sorun OLMADIĞI doğrulananlar:** fren (`per` 0/100, doğru), fail-safe (1212'de 0 kez, 1216'da
1 kez), yanal klerans profili (ID-4'ün %100'ünde var), `lane_follower` kare hızı (FPS 24-33),
kayıt bütünlüğü (beş bag de tam).

Arkadaşın `return` fazı analizi — değerlendirme (2026-08-20):
**Teknik iddialarının hepsi doğru, koddan doğrulandı:**
- Dönüş direksiyonu gerçekten sabit ayna: `sap = slalom_escape_steer - 45;
  steering_angle = 45 - sap` → `escape_steer=75` ile FSM **15**, yani tam ters kilit. Kapalı
  çevrim merkezleme yok.
- `_return_hard` **ölü kod**: 1563 ve 1721'de yazılıyor ama direksiyon kararında hiç okunmuyor
  (yalnızca `get_decision`'da raporlanıyor). Yani "iki seviyeli dönüş" tasarımı kâğıt üstünde
  duruyor, çalışmıyor.
- `avoid_lane_blend_return = 0.15`, `slalom_return_max_deg = 45.0` — ikisi de dediği gibi.
- `align` fazı `45 - 1.5*err_deg - slalom_align_lat_gain*_lateral` ile 75'e doyabiliyor; bag'in
  sonundaki `steering_angle=70`, yeni bir kaçış değil, aşırı sağ dönüşü telafi eden doymuş sol
  komut. Doğru teşhis.

**Önemli bağlam: bu iki değeri 2026-08-17'de BEN değiştirdim** (blend 0.55→0.15, dönüş = ayna) ve
gerekçem bir CARLA ölçümüydü. Yani arkadaşın önerisi o değişikliği geri almak. Bu, arka arkaya
**üçüncü** karar oluyor ve üçü de **direksiyon gecikmesi modellenmeyen** bir simülatörde verildi:

| karar | tarih | dayanak | durumu |
|---|---|---|---|
| nursena 4-fazlı (yanal ölçüt) vs bizim yaw-açı motoru | 08-10 | masa sim 5/5 vs 4/5 | **şüpheli** |
| dönüş = kaçışın aynası, blend 0.55 → 0.15 | 08-17 | CARLA ölçümü | **şüpheli** |
| dönüş açı tavanı 20° reddi | 08-19 | masa sim bozuldu | **şüpheli** |

**`slalom_return_steer` parametre yapıldı** (None = ayna/eski davranış, sayı verilirse o FSM açısı;
`_return_hard` hâlâ aynayı zorlar) ki bu karar deneyle sınanabilsin.

⚠️ **AMA SINANAMADI, ve sebebi dürüstçe şu:** gecikmeli masa simülatöründe weave **kaçış fazını
hiç geçemiyor** (maks yaw 17-24°, maks yanal 0.26-0.46 m, faz hep `escape`). Araçta ise weave
dönüşe VARDI (yanal 2.85 m, yaw -72°). Fark, ön koridor geometrisinde: araçta engel araç açılınca
koridordan çıkıp `front=99` oluyor ve kaçış devam ediyor; simülatörün 1.4×1.4 m kutusu (gerçek
bariyer 1.21×0.39) koridorda kalıyor ve manevra erken kesiliyor. `avoid_emergency_front` 0.4'e
indirilerek denendi, değişmedi. **Sonuç: 8 ayarın 8'i de 3/8 veriyor ama bu "arkadaşın önerisi
işe yaramıyor" DEMEK DEĞİL — dönüş fazı hiç çalışmadığı için önerisi test edilmemiş oluyor.**
Sınamak için simülatörün engel derinliğinin gerçeğe (0.39 m) çekilmesi ve kaçış fazının
tamamlanabilmesi gerekiyor. Açık iş.

**SİMÜLATÖR GÜVENİLİR HALE GETİRİLDİ VE ÜÇ ŞÜPHELİ KARAR KAPANDI (2026-08-20).**

Kök sadakat hatası engel geometrisi değil, **hız ölçeklemesiydi**: `slalom_sim.py` FSM'in km/h
değerini araca DOĞRUDAN veriyordu. Gerçek düğüm (`_cmd_speed`) önce `× speed_target_scale` (0.25)
ölçekliyor, `max_speed_kmh` (5.0) ile kırpıyor ve `min_speed_kmh` (1.2) tabanını uyguluyor —
FSM'in 4.0 km/h'si araca **1.2 km/h** gidiyor. Simülatör 3-5 kat hızlı sürüyordu; direksiyon
gecikmesiyle birleşince tekerlek dönerken 2.9 m yiyip **kaçış fazında** acil eşiğe çarpıyordu,
oysa araç 0.9 m yiyip devam ediyor ve **dönüş fazında** aşıyor. Yani simülatör gerçeğin arızasını
değil BAŞKA bir arızayı üretiyordu ve dönüş fazı hiç test edilemiyordu.
`arac_hizi()` eklendi (kontrol düğümünün birebir aynısı), `run_scenario` süresi 60 → **120 s**
(araç artık gerçek gibi yavaş; 60 s bir senaryoyu bitirmeye yetmiyordu).

**Kabul ölçütü karşılandı** — simülatör aracın gerçek arıza imzasını üretiyor:

| | kaçış tepe yaw | yanal tepe (hedef 1.7) | dönüş tepe yaw | bitiş |
|---|---|---|---|---|
| araç `1212` | +52° | 2.85 | -72° | STOP, front 0.5 |
| araç `1216` | +46° | 2.42 | -59° | 18 s donuk |
| **simülatör (düzeltme öncesi)** | **+43°** | **2.51** | **-54°** | STOP, front 1.0 |

**Dört varsayılan değişti** (ölçümle, gecikmeli simülatörde):

| parametre | eski | yeni | gerekçe |
|---|---|---|---|
| `slalom_return_steer` | (yok, ayna=15) | **25.0** | sabit tam-ters-kilit burnu savuruyordu; arkadaşın saha teşhisi doğrulandı |
| `avoid_lane_blend_return` | 0.15 | **0.55** | 17.08'de CARLA ölçümüyle düşürülmüştü; o CARLA'da direksiyon anında varıyordu |
| `slalom_return_max_deg` | 45.0 | **25.0** | 19.08'de 20 denenip "sim bozuldu" diye reddedilmişti — o sim gecikmesizdi, karar geçersizdi |
| `slalom_escape_lat_frac` | 0.5 | **0.30** | yanal, baş açısının gecikmeli göstergesi; faz bittikten sonra da birikiyor |

Ölçülen etki (P1, gecikmeli sim):

| | maks yaw | maks yanal | P1 bitiş açısı | suite |
|---|---|---|---|---|
| mevcut | 54° | 2.51 | **-34°** (bariyere bakıyor) | 3/8 → 5/8 (hız düzeltmesinden sonra) |
| sadece arkadaşın önerisi | 54° | 2.52 | **-7°** | 5/8 |
| **hepsi birlikte** | **36°** | **1.82** (hedefe oturdu) | **-0°** | **6/8** |

CARLA benzeri gecikmesiz durumda **8/8 → 8/8**, yani regresyon yok. Kalan iki başarısız: `S2`
(10 m arayla iki engel) ve `P2` (5 m aralık, bilinen geometrik sınır).

**Ders (üç kez tekrarlandı, dördüncüye izin verilmemeli):** bu projede bir kontrol kararı,
simülatörün o kararın bağlı olduğu fiziği modellediği doğrulanmadan verilmemeli. Direksiyon slew'i
ve hız ölçeklemesi modellenmediği için 08-10, 08-17 ve 08-19'da verilen üç karar da yanlıştı.
`slalom_sim.py` artık: direksiyon slew'i + ölü bant, ham↔teker eşlemesi, hız ölçekleme/taban/tavan.
**Hâlâ modellenmiyor:** direksiyonun 0 km/h'de donması (ölçülen ~1.5 birim/s), aracın tam kilitte
kalkamaması. Bu ikisi araç ekibinin konusu (bkz. S2/S3 maddeleri).

⚠️ **DÜZELTME (2026-08-20 akşamı): "direksiyon durunca donuyor" ve "araç gaza rağmen
ilerlemiyor" bulguları GEÇERSİZ.** Operatör itiraz etti, kontrol edildi, haklıydı.

`FB_OMUX_to_AUTONOMOUS.fb_emergency` her iki slalom kaydında da **255** okuyor ve tam durma
anlarına denk geliyor:

| bag | acil pencere | araç durdu |
|---|---|---|
| `1212` | t=**139.7** .. 162.7 | t≈140 |
| `1216` | t=**67.7** .. 73.7 | t≈68 |

Bu acil bizim taraftan DEĞİL: `rc_unittoOmux.autonomous_emergency` hep 0, `/safety/emergency_stop`
bag'de kayıtlı bile değil. Yani fiziksel buton/kumanda — operatör aracı durdurdu.

Sonuçları:
- **"0 km/h'de tekerlek 22 saniyede 1 birim döndü" ölçümü kullanılamaz** — o pencerede acil
  aktifti, tahrik kesikti ve direksiyonun ECU tarafından kısıtlanıp kısıtlanmadığı bilinmiyor.
  Duran araçta direksiyon hızı hakkında bu bag'lerden bir şey söylenemez. (Dosyanın kendi
  `semantik_1` statik ölçümü — PWM 255'te 1.16 birim/s — bağımsızdır ama koşulları
  doğrulanmadı.)
- **"Hız hedefi hiç 0 değilken gerçek hız %47 sıfır" bulgusu da düşer** — o sürenin büyük kısmı
  acil penceresi ve sonrası.
- **1212'de araç bariyere sürüklenmedi**: acil t=139.7'de başlıyor, FSM `OBSTACLE_STOP`'a ancak
  t=145.3'te giriyor. Yani duruş operatör müdahalesiydi, kalıcı kilitlenme değil.

**Ayakta kalanlar** (acil penceresi DIŞINDA ölçüldü, etkilenmiyor):
- Yuvarlanırken slew **~10 birim/s** (medyan), tepe 17-30 — normal sürüşte onlarca büyük geçişten.
- `max_delta` yükseltmek işe yaramaz: joystick PWM sapma 73 ile aynı hızı veriyor (9.5 vs 9.2).
- Manevra aşımı: kaçış +52°, yanal 2.85 m (hedef 1.7), dönüş -72° — hepsi t=114-139 arası,
  acil öncesi.

**Ders:** araç bag'lerinde bir "araç hareket etmiyor / tepki vermiyor" gözlemi yorumlanmadan önce
`FB_OMUX_to_AUTONOMOUS.fb_emergency` MUTLAKA kontrol edilmeli. Bu alan bag'de vardı ve ilk
analizde bakılmadı; iki yanlış bulgu doğrudan bundan doğdu. Kayıt tarifinde
`/beemobs/FB_OMUX_to_AUTONOMOUS` zaten var — sorun kaydetmemek değil, okumamaktı.

Şerit düğümü arkadaşın 2026-08-21 sürümüyle değiştirildi (`~/carla-ros2-wss-mehmet.tar.gz`).
**Yalnızca `lane_follower_node.py` alındı** (1431 → 2114 satır); tar'daki `decision_brain.py`
(19 Ağu), iki kontrol düğümü (20 Ağu sabah) ve `obstacle_lidar_node.py` bizimkinden ESKİ, alınsa
20 Ağustos slalom düzeltmelerini geri götürürlerdi. Modeller birebir aynı.

Eklediği ve neden önemli olduğu: `serit_secim`/`_grupla`/`cift_sec` (doğru şerit çiftini seçme),
`bariyerde_mi`/`bariyer_ele_oran` (`serit_v2`'nin `barrier` sınıfıyla bariyer eleme),
`lane_w_tol`/`cift_gecerli` (bizim `lane_w_gate`'imizin yerini aldı), `heading_max_px=150`
(ölçülen 342 px'lik heading sıçramasını kırpar), `steer_mode` (pure-pursuit alternatifi).

**Algı kazancı ölçüldü** (`joystick_46`, T7, 204 gerçek ZED karesi, `err_offset` iki tarafta da 0):

| | eski | yeni |
|---|---|---|
| LaneW aralığı | **-57 .. 666 px** (negatif = fitler çaprazlanmış) | **262 .. 517 px** |
| LaneW std | 143 | **46** |
| fiziksel olarak imkânsız çift | **%19.6** | **%0.0** |

Bu, 08-20 bag analizindeki S4 maddesinin ("fit yanlış çizgi çiftine oturuyor, genişlik kapısı
271-394 px'i yakalamıyor") çözümüdür.

**`steer_mode` varsayılanı `pursuit` → `pid` yapıldı (2026-08-20/21 ölçümü).** Arkadaşın `pursuit`
tercihi masa kapalı çevriminden geliyordu; o test KUSURSUZ SENTETİK maskelerle çalışır ve bu
düğümün asıl kazancı olan çift-seçimini hiç sınamaz — **yanlış hakem**, `slalom_sim` dersinin
aynısı. Aynı kareler, aynı algı, tek değişen mod:

| | `joystick_46` (geniş çok-çizgili alan) | `pist_18_3tem` (326 s, VİRAJ içerir) |
|---|---|---|
| pursuit | std 7.59 / oynaklık 2.96 / 25..65 | std 4.62 / **3.11** / 30..62 |
| **pid** | **2.79 / 1.31 / 34..55** | **1.39 / 1.16 / 39..49** |

LaneW dağılımı iki modda AYNI, yani algı kazancı `pid`'de tamamen korunuyor; değişen sadece
çıkışın yumuşaklığı. "Pure-pursuit ileri bakışla çalıştığı için virajda avantajlıdır" beklentisi
**virajlı bagde de doğrulanmadı** — orada da en oynak mod pursuit. Denemek için
`-p steer_mode:=pursuit` (derleme gerekmez). `heading_gain` 75 → 30 ayrıca ~%10 daha yumuşak
ölçüyor (iki bagde tutarlı) ama etki küçük; arkadaşın 75 tercihi korundu.

⚠️ **`err_offset` varsayılanı -67 px ve bu ZED'in MONTAJ SAPMASIDIR** (gerekçe kodda: `joystick_46`
24-50 s penceresi, operatörün bilerek ortaladığı 194 kare, medyan -67.0, std 0.4). CARLA'nın
kamerası bambaşka — arayüzün 6 ve 6b butonlarına `-p err_offset:=0.0` eklendi. Aynı sınıf hata
`model_file`'da da vardı (buton geçmiyordu, `serit_v2` CARLA'da yolun kenarlarını maskeliyordu);
o da düzeltildi: `-p model_file:=best_yolo11.pt` + operatörün tıklayarak kalibre ettiği
`src_pts=[119,354, 611,357, 362,219, 298,220]`.

Arayüze eklenen butonlar: **6b** (aynı ayar, `serit_v2` ile kıyas), **6c/6d** (BEV ve şerit
overlay'ini tarayıcıda açar — düğümün log'u `http://<arac_ip>:8082` yazdığı için operatör
laptopta adresi bulamıyordu, buton artık `xdg-open localhost` yapıyor), **8p2** (8p'nin
`return_home_when_free:=false` sürümü — "geçtiği şeritte kal" tasarımı).

Tabela modeli **`birlesik_v2.pt` → `Yasin_Her_Sey.pt`** (başkası değiştirmiş, 2026-08-20 17:59).
Sınıf adları farklı (`DUR_TT-2`, `DURAK_B-22`, `ADA_ETRAFINDA_DONUNUZ_TT-37`, `Kirmizi_Isik`,
`Yesil_Isik`) ama **24/24 sınıf `canonical_sign_id()` ile doğru eşleşiyor** — normalizasyon ekli
sonekleri yutuyor. Kritik olanlar doğrulandı: `DUR_TT-2`→11, `Kirmizi_Isik`→15, `Yesil_Isik`→17,
`YayaGecidi`→20, `Park`→13, `DURAK_B-22`→14. Yani 18 Ağustos'ta kapatılan "DUR tabelasında
durmama" hatası geri gelmiyor.

Dört düğümün kapanışı tutarlı hale getirildi: `ExternalShutdownException` yakalanıyor ve
`rclpy.shutdown()` `rclpy.ok()` ile korunuyor. Öncesinde iki kontrol düğümü Ctrl+C/SIGTERM'de
`rcl_shutdown already called` traceback'i bırakıyordu — çalışmayı bozmuyor ama araç log'unun
sonunda gerçek bir hatayı gizleyebilir (`can_odom`'da aynısı 13.07'de düzeltilmişti).

**Deploy imajı yeniden derlendi 2026-08-21 12:52.** Image ID `01375efad972`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.435.475.456 bayt**, SHA-256
`28af3a0c25c9849d8d2b75c50dd9e44ab85fab03af7b061a624b0b165036b666`. İmajın içinde doğrulandı:
şerit düğümü 2136 satır + `steer_mode="pid"` + kapanış düzeltmesi, beyinde dört slalom
varsayılanı + `blocked_speed`, lidarda `side_x_min`, `steering_ctrl`'de `_on_params`,
`tabela_tespit`'te `Yasin_Her_Sey.pt`, `models/` içinde `serit_v2.pt` + `Yasin_Her_Sey.pt`.
Bir önceki tar `~/robotaksi_deploy/robotaksi_humble_0820_1736.tar` adıyla korundu.

`route_planner` (mission/rota katmanı) entegre edildi (2026-08-21, kaynak
`~/loc_planner_map.zip`). GEOJSON oku → GNSS'i map'e çevir → yol grafında dönüş-cezalı A* →
doğru anda `/master` ID-5 ile beynin hook'larını tetikle. Yazarı 233 yarışma kombinasyonunun
hepsini offline sürüş benzetimiyle test etmiş (233/233, 2622 komut, 0 rota uyarısı).

**Yeni ID-5 sözleşmesi** (eskisi grid A* hedefiydi, `5,<gx>,<gy>`):

| mesaj | anlam | beyin |
|---|---|---|
| `5,1,<±derece>` | dönüş (+sol / −sağ) | `PLANNER_TURN` (yeni state, 20) |
| `5,2,0` | yolcu al/bırak | `BUS_STOP` (zaten vardı) |
| `5,3,0` | park | `PARK_SEARCH` (zaten vardı) |
| `5,0,0` | iptal | `LANE_FOLLOW` |

⚠️ **Üç alan zorunlu.** `master_cb`, ID-5 için `len(data) < 3` olan mesajı atıyor; iki alanlı
`5,2` beyne hiç ulaşmaz. Planner dolgu sıfır gönderiyor, kontrol düğümüne dokunulmadı.

Beyne uygulanan beş dokunuş: `DriveState.PLANNER_TURN = 20`, `__init__`'e `_pturn_left` /
`_pturn_olcek`, `planner_event` yeniden yazıldı (eski grid-hedefi okuması `5,1,93.3`'ü
`(1, 93)` diye okurdu), `_is_blocking_state`'e `PLANNER_TURN`, dispatch + `_planner_turn_control`.
Grid A* (`self.planner`) engel yeniden planlamada **kullanılmaya devam ediyor** — sadece bu
giriş noktası değişti.

**Dönüş süresi açıyla ölçekleniyor** (`|derece|/90`, 0.35..1.60'a kırpılı): planner 40–131°
arası komut üretiyor, beynin sabit 5.5 s + 3 s tabela manevrası hepsini ~90° döndürürdü.
⚠️ Açık döngü, hıza duyarlı — tabela dönüşleriyle aynı sınırlama, sahada bir kavşakta
izlenip ince ayar gerekebilir.

**Yamanın yazıldığı beyin bizimki DEĞİLDİ.** Belgesi "workspace'teki beyin 975 satır, yaw hiç
yok" diyor; bizimki 2219 satır ve yaw'ı var. Yama yine de uyuyor çünkü yaw kullanmıyor —
bağımlılıklarının (`turn_speed`, `left/right_turn_angle`, `turn_recover_angle_*`, `_elapsed`,
`BUS_STOP`, `PARK_SEARCH`, `sign_cooldown`) tamamı bizde de var, tek tek doğrulandı.
`DriveState` en yükseği 13'tü, 20 boştu.

**Entegrasyonda değiştirilen tek şey veri yolu.** Node veri dosyalarını `__file__` yanında
arıyordu; `--symlink-install` ile kurulu modül src'ye sembolik bağ olduğu için orada bulunmaz.
Artık önce `share/neuravix_ros2/data/` bakılıyor (setup.py oraya kuruyor), bulunamazsa eski
davranışa düşüyor. Dosyalar `src/neuravix_ros2/data/`: `route_graph_refined.json` (7 KB),
`datum_yt.npz` (26 KB), `teknik_kontrol.geojson` (1.3 KB).

Çalıştırma:
```
ros2 run neuravix_ros2 route_planner --ros-args \
  -p geojson:=<yarış_günü.geojson> -p pose_topic:=/amcl_pose -p trigger_dist:=6.0
```

⚠️ **En kritik ön koşul: `pose_topic` MAP çerçeveli olmalı.** Graf map frame'inde;
`/odometry/filtered` odom-frame ve kayar, planner ilerlemeyi ölçemez. Şu an workspace'te
AMCL koşmuyor — planner'ı denemeden önce lokalizasyon zinciri ayağa kalkmalı.

Doğrulandı (2026-08-21): node kalkıyor ve `teknik_kontrol.geojson` için rota kuruyor
(`[1,0,4,50]`, tek dönüş `5,1,70` sol, doğrulama sapması 20° — eşik içinde); dört komut da
kontrol düğümü üzerinden uçtan uca çalışıyor (`PLANNER_TURN`/`BUS_STOP`/`PARK_SEARCH`/iptal),
"Planner mesaji eksik" uyarısı çıkmıyor; 28 maddelik beyin regresyonu (14'ü planner'a özel:
açı kırpma, bozuk giriş, faz zamanlaması, şerit ezmemesi, fail-safe'in yine durdurması) tam
geçiyor; slalom suite 6/8'de değişmedi; dört düğüm de traceback'siz kalkıyor.

Bilinmeyen/riskli kalanlar (yazarının kendi listesi + entegrasyon gözlemi):
- `pose_topic` map-frame olmadan planner çalışmaz — sahada ilk doğrulanacak şey.
- `5,3` (park) gerçek araçta hiç çalışmadı; `5,2` (durak) yalnız benzetimde.
- `trigger_dist=6.0` yarış hızında yeterli mi — her şey 0.66 m/s'de ölçüldü.
- `PLANNER_TURN` sırasında **engel olayı bloke değil** (tabela dönüşleriyle aynı): burun
  açılıyken ön koridor yol kenarını tarayabilir ve dönüş yarıda kesilebilir. Slalomdaki
  `front_trust_deg` koruması burada YOK. Bilinçli bırakıldı — gerçek engelde durabilmek
  daha önemli — ama sahada izlenmeli.

AMCL lokalizasyon yığını entegre edildi (2026-08-21, `~/loc_planner_map.zip` → `maps/lokalizasyon/`).
`route_planner` `pose_topic:=/amcl_pose` beklediği için bu, planner'ın **önkoşuluydu** — yığının
hiçbir dosyası workspace'te yoktu.

**`pist_localization_real.launch.py` (slam_toolbox localization) ARTIK KULLANILMIYOR.** 12.08'de
ölçülüp terk edilmiş: koşunun yalnızca **%15'inde kilitli**, medyan tarama-harita mesafesi
**3.01 m**, kilidi kaybedince geri dönemiyor. Yerine `pist_localization_amcl.launch.py`
(AMCL + GNSS gözetmeni): `pist_17tem_2` üzerinde medyan **1.19 m**, %90 **2.57 m**.

Kurulanlar (`bee1_description`): `launch/pist_localization_amcl.launch.py`,
`config/amcl_pist_real.yaml`, `scripts/{gnss_supervisor,tekerlek_odom_tf,yer_tanima,yer_tanima_db}.py`,
`maps/` (pist_final.pgm 11 MB + .yaml + datum_yt.npz + tunel.json + 3 dönüşüm scripti).
CMakeLists'e **yalnızca dört `install(PROGRAMS)` bloğu** eklendi, mevcut kurallar korundu.

**Entegrasyonda değiştirilen iki şey:**
1. **`nav2_amcl` bu sistemde ve deploy imajında YOKTU** — onsuz launch hiç kalkmaz.
   Dockerfile'a `nav2-amcl` + `nav2-map-server` + `nav2-lifecycle-manager` eklendi.
   ⚠️ Laptopta hâlâ kurulu değil (sudo gerekiyor): yerel deneme için
   `sudo apt install ros-humble-nav2-amcl`.
2. **`map_yaml` varsayılanı `/root/maps/pist_haritasi_img.yaml` → paketin içindeki
   `pist_final.yaml`.** Eski yol (a) bu workspace'te yok, (b) terk edilen slam_toolbox
   yığınına ait, (c) 20.08'de lidar montaj yüksekliği 0.62 → 1.35 düzeltilince zaten
   geçersizleşti. Harita artık imajla birlikte geliyor, volume'a bağımlı değil; daha yenisi
   için `map_yaml:=/root/maps/<yeni>.yaml`.

AMCL config bizim yığınla uyumlu: `scan_topic: /scan_bee1` (host `/scan` çakışması için
13.07'de yaptığımız remap), frame'ler `map/odom/base_link`, `recovery_alpha_slow/fast` açık.

**Yarış kurulumu** (bringup ÖNCE çalışıyor olmalı):
```
ros2 launch bee1_description pist_localization_amcl.launch.py \
  use_gnss:=true gnss_enabled:=true \
  initial_pose_x:=<gunun_start_x> initial_pose_y:=<gunun_start_y> \
  initial_pose_yaw:=<radyan> \
  use_yer_tanima:=false
```
İlk denemede `gnss_enabled:=false` — gözetmen ayrışmayı loglar ama karışmaz. `GNSS-AMCL ayrisma`
1-3 m ise datum doğru, 10 m üstüyse yanlış, öyle bırakma.

⚠️ **`datum_lat/lon` YARIŞ GÜNÜ DEĞİŞMEZ — bu dosya 21.08'de yanlış kaydetmişti.** Eski komut
`datum_lat:=<yarisma> datum_lon:=<yarisma>` diyordu; yazar 22.08'de teyit etti ki bu **yanlış**
(kendi `OKU.md`/`KURULUM.md`'sindeki yer tutucu da onun hatasıymış, `KURULUM.md`'nin gövde metni
doğruyu söylüyordu). Gözetmenin modeli **ötelemesiz** (`to_map` yalnızca `R.T @ v`), yani
`datum_lat/lon` **haritanın (0,0) noktasının enlem/boylamı** olmak zorunda:

    datum_lat:=40.79041010  datum_lon:=29.50912636  datum_yaw_deg:=-149.20   <- SABİT, haritaya bağlı

Üçü de artık launch varsayılanı, komut satırında **verilmemeli**. Yarışmanın geojson'undaki
`datum` satırı (40.789431 / 29.508361) **yalnızca** `maps/yarisma_donusum.py` içinde, geojson
koordinatlarını haritaya çevirirken kullanılır; gözetmene asla verilmez. İki çift arasında
**109 m kuzey + 64.5 m doğu** fark var — karıştırılırsa gözetmen AMCL'i 126 m öteye tohumlar.

**Yazarın 22.08 teyitleri ve bizde yapılan değişiklikler:**
- **`gnss_threshold` launch varsayılanı 18.0 → 3.0.** 18.0 13 Ağustos'tan kalmaydı (o gün
  haritanın kendisi ~11 m burulmuştu); 19.08'de datum yeniden çözülünce burulma medyanı 1.54 m'ye
  indi ve 3.0 üç bağımsız bag'de doğrulandı. Artık komut satırında vermeye gerek yok.
- **`initial_pose` artık launch argümanı** (`set_initial_pose`, `initial_pose_x/y/yaw`).
  `amcl_pist_real.yaml`'daki gömülü `(2.05, 0.76)` **başka harita+bag içindi**
  (`pist_C_19_3tem` + `pist_17tem_2`) — yazarın kendi başarılı koşuları da 16.5 m yanlış başlayıp
  gözetmenin düzeltmesiyle oturuyormuş. Her yarış gününün geojson'unun kendi `start`'ı olduğu için
  gömülü kalması tanımı gereği yanlış; günün değerini `maps/yarisma_donusum.py` üretir.
  Varsayılan = teknik kontrol start'ı: `(20.51, 3.89)` yaw `0.1749` rad (10.03°).
  ⚠️ Yarış günü hazırlık süresi **3 dakika** — RViz'de tıklamak yerine argümanla verin
  (`set_initial_pose:=false` + 2D Pose Estimate yedek yol).
- **Yarış hızı için iki yeni argüman: `gnss_sustain_s` (2.0) ve `gnss_min_interval_s` (5.0).**
  Gözetmenin tepki gecikmesi **`sustain_s`**'tir; log'daki 25 s bir kontrol aralığı DEĞİL, sadece
  `n_fix % 100` log satırıdır (karar her GNSS fix'inde, 4 Hz). 0.66 m/s'de `sustain 2.0` = 1.3 m
  yol, ama 15 km/h'de aynı 2 s = **8.4 m**. Yazarın yarış önerisi `sustain 1.0` / `min_interval 3.0`
  — **sahada A/B edin**, ölçüt tur boyunca tohum sayısı + ortalama ayrışma (tohum 15-20'yi
  geçiyorsa `sustain`'i geri açın). `gnss_threshold` ve `seed_std_xy` hıza bağlı değil, 3.0/2.0 kalsın.
- **`pointcloud_to_laserscan_real.yaml` bizde zaten doğru** — yazar kendi kopyasıyla karşılaştırdı,
  birebir aynı. `laser_max_range: 40.0` da haritayı üreten `slam_toolbox_pist_real.yaml`'ın
  `max_laser_range: 40.0` değeriyle eşleşiyor. İkisi de şüpheli listesinden çıktı.
- **`ekf_odom_real.yaml`** `use_ekf:=false` iken hiç okunmuyor (node koşullu), sorun değil.

⚠️ **`base_link → velodyne` SADECE `bee1_bringup`'tan gelir.** Yazar bag'in `/tf_static`'ini açıp
baktı: içinde **yalnızca `zed_*` frame'leri** var, `base_link`/`velodyne`/`odom` YOK. p2l'nin
`target_frame`'i `velodyne` ve bulutun `frame_id`'si de `velodyne` olduğu için **p2l hiç TF
olmadan da `/scan_bee1` üretir** — yani *"scan üretildi ve AMCL tüketti"* gözlemi TF ağacının
sağlam olduğunu **göstermez**. Kontrol: `ros2 run tf2_ros tf2_echo base_link velodyne`.
(Bag'de `/tf` topic'i hiç yok, yani çakışma da imkânsızmış.)

**Yazarının üç kararı, aynen korundu:**
- **Yer tanıma yarışta KAPALI** (`use_yer_tanima:=false`): çapraz-oturum hatası medyan 6.83 m,
  en kötüsü 46.7 m. Dosya pakette duruyor, tünelde GNSS keserse tek alternatif.
- **`gnss_threshold` 3.0** (4.5'ten): araç kalkarken poz ~3.8 m kayıyor, 4.5 bunu düzeltmiyordu.
- **Gözetmen ŞART**: gözetmensiz AMCL bu pistte kilitlenmiyor — doğru başlangıç pozuna rağmen
  iki bağımsız koşuda 27.3 ve 29.3 m medyana dağıldı.

⚠️ **Bu yığın gerçek araçta BİR KEZ BİLE çalışmadı.** 20 Ağustos otonom kayıtlarının hiçbirinde
`/amcl_pose` yok — araç yalnız şerit takibiyle sürüyordu. Planner o topic olmadan hiç komut
üretmez. Araçtaki ilk iş bu yığını ayağa kaldırmak (`maps/KAYIT_LISTESI.md` madde 0).

**Yazarın ölçüm script'leri kuruldu** (`src/bee1_description/maps/lokalizasyon/`):
`run_lokal3.sh` (bringup + lokalizasyon + pose_logger + bag, tek komut), `pose_logger.py`
(`map→base_link` TF'ini CSV'ye yazar), `puanla_lokal.py` (CSV'yi GNSS'e karşı puanlar).
`puanla_lokal.py` datum'u `<script>/../datum_yt.npz`'de arar, o yüzden bu klasörde durmalılar.
Kullanım:
```
WS=~/Desktop/carla-ros2-ws BAG_DIR=~ OUT=/tmp/loc ./run_lokal3.sh TAG lokal_0820_0722 3.0 0
BAG_DIR=~/lokal_0820_0722 OUT=/tmp/loc python3 puanla_lokal.py TAG:lokal_0820_0722
```
⚠️ Script'te bizde **bir düzeltme** var: artık-süreç kontrolü yazarın sürümünde
`[ -n "$LEFT" ] && { ...; exit 1; }` idi ve `set -e` altında **`LEFT` boşken de** (yani temiz
sistemde) script'i sessizce, hiç log üretmeden öldürüyordu. `if/fi`'ye çevrildi.
⚠️ Script'in üç kritik detayı, elle koşarken de uyulmalı: **bringup önden ve `use_sim_time:=true`**,
**`/tf_static` bag'den oynatılmaz** (topic filtresi), **`--clock 100`**. Ayrıca t=20 s'de
`map_server` deactivate/activate yapıyor — yazarın 0.21 m üreten koşularının hepsinde bu vardı,
nedenselliği kanıtlanmış değil ama `izle_rviz.sh`'te yok.

**Kayıt tarifine üç ekleme** (yazarın önerisi): `/filter/quaternion` + `/filter/positionlla`
(Xsens'in kendi füzyon çıktısı — dönme açısını sahada bunlarla doğrulamış, bağımsız referans ve
bedava) ve **`/scan_bee1`** (AMCL'in gerçekten ne gördüğünü çevrimdışı inceleyebilmek için).
En iyisi topic filtresi hiç koymadan hepsini kaydetmek.

Doğrulandı (2026-08-21): `bee1_description` derleniyor, dört yeni çalıştırılabilir kuruluyor,
launch `--show-args` ile çözümleniyor, harita paketin share'inde, `gnss_supervisor` datum'u
okuyup kalkıyor, `tekerlek_odom_tf` odometri gelmeyince doğru şekilde ERROR basıyor,
`map_server` haritayı lifecycle node olarak açıyor. Beyin regresyonu 28/28, slalom suite 6/8,
altı düğüm de traceback'siz.

**AMCL yığını laptopta offline denendi (2026-08-21) — boru hattı çalışıyor, LOKALİZASYON
YAKINSAMIYOR.** `lokal_0820_0722` bag'i `--clock` ile oynatılıp `pist_localization_amcl.launch.py`
koşuldu (`nav2_amcl` laptopa kuruldu).

**Çalışan kısım (entegrasyon doğrulandı):**
- Altı düğüm de kalkıyor; `map_server` ve `amcl` lifecycle **active [3]**
- Harita yükleniyor: **3401 x 3265 @ 0.05 m/pix**
- `pointcloud_to_laserscan` `/scan_bee1` üretiyor, AMCL tüketiyor (`createLaserObject`)
- AMCL `/amcl_pose` yayınlıyor (126 s'de 7121 mesaj)
- GNSS gözetmeni ayrışmayı ölçüyor ve tohumluyor; **25 tohumlamanın 25'i de kabul edildi**
  (`Setting pose`, TF reddi 0)
- Tohumlanan koordinatlar haritada **boş alanda** (kontrol edildi), yani GNSS->map dönüşümü
  ve datum doğru

**Çalışmayan kısım:** AMCL yakınsamıyor. Gözetmen 126 saniyede **24 kez** yeniden tohumluyor,
ayrışma **23-84 m** bandında kalıyor, AMCL poz kestirimi x in [-197, +250], y in [-269, +237]
aralığında uçuşuyor (araç gerçekte ~14 m gitti). Yazarının aynı bag'de ölçtüğü değer
**medyan 0.21 m / %90 2.54 m**.

**Elenen sebepler** (hepsi denendi, sonuç değişmedi):
- Oynatma hızı: 4x ve 1x aynı sonucu verdi
- Tarama yükseklik penceresi: yeni (-1.13/0.77) ve eski (-0.4/1.5) aynı
- `/tf_static` çakışması: bag'den hariç tutuldu, değişmedi (CLAUDE.md'nin kendi kuralı)
- `can_odom` girdisi: düğüm çalışıyor, IMU/hız/direksiyon akıyor, gyro yaw aktif
- Harita/datum: tohum noktaları boş alanda, harita doğru boyutta yükleniyor

**Denenmeyenler / açık şüpheliler:**
- `use_wheel_odom:=true` (bag'de `/odometry/can_wheel` var; `can_odom` yolu %25 eksik ölçüyor)
- AMCL config'indeki `initial_pose` başka bir konum için ve `always_reset_initial_pose: false`
- Replay ortamına özgü bir şey (yazar kendi makinesinde tam workspace'le ölçtü)

**ÇÖZÜLDÜ 2026-08-22 — ama HANGİ değişikliğin çözdüğü İZOLE EDİLMEDİ, aşağıyı oku.**

⚠️ **Önce bir düzeltme.** Bu bölüm ilk yazıldığında "kök neden `can_odom`'daki sınırsız `dt`"
deniyordu; **bu iddia ölçümle çürütüldü** (aynı gün, aşağıdaki A/B). Yakınsayan koşu yazarın
`run_lokal3.sh`'i ile alındı ve o koşu bir anda **beş** şeyi birden değiştirdi: (1) `bee1_bringup`
önden ve `use_sim_time:=true` (yani `base_link→velodyne` TF'i ilk kez var), (2) `--clock 100`,
(3) topic filtreli oynatma (`/tf_static` bag'den gelmiyor), (4) t=20 s'de `map_server`
deactivate/activate, (5) `max_dt` koruması. **Hangisinin çözdüğü bilinmiyor**; en güçlü aday (1),
çünkü o TF olmadan AMCL taramayı `base_link`'e taşıyamaz. Yığın bütün olarak çalışıyor, yani
akşamki koşuyu bloke etmiyor — ama tek değişkenli doğrulama açık iş olarak duruyor.

**`max_dt` koruması yine de doğru ve duruyor** (yazarın hipotezi): sınırsız `dt` gerçek bir açıktı.
`_integrate` her tikte `dt = now - _last_time` hesaplıyordu ve **üst sınırı yoktu**.
`use_sim_time:=true` iken `/clock` gelmeden `get_clock().now()` sıfır döner; bag başlayıp saat
bag zamanına sıçrayınca ilk `dt` dev olur. Ölçüldü: **`dt = 1.787.210.527 saniye`**. Hız tarafını
`speed_ok` kazara koruyordu (`v=0` → `x += 0`) ama **yaw korumasızdı** —
`yaw = yaw + yaw_rate*dt` rastgele bir değere gidiyor ve AMCL'e dev bir dönme deltası olarak
ulaşıyordu. Hangi tarafın patlayacağı `/clock` ile ilk hız/IMU mesajının sırasına bağlı bir yarış
durumu; bu yüzden yazarın makinesinde çıkmayıp bizde çıkmıştı.
**Düzeltme**: `max_dt` parametresi (0.5 s) — aşan tik entegre edilmeden atlanır (`_last_time`
yine güncellenir), bir kez WARN basar. Ölçülen etki, aynı bag (`lokal_0820_0722`), aynı komut:

| | önce | sonra |
|---|---|---|
| yeniden tohumlama | **24** (126 s'de, yani mümkün olan her fırsatta) | **0** |
| GNSS-AMCL ayrışma | 23-84 m | **2.7-2.8 m** |
| AMCL pozu | x∈[-197,+250] y∈[-269,+237] | harita içinde, izliyor |

⚠️ Bu düzeltme **gerçek araçta da geçerli**: orada `/clock` yok ama sistem saati düzeltmesi,
düğümün geç başlaması ya da uzun bir donma aynı sınırsız `dt`'yi üretir.

**AMA sıçrama tek başına zararsız çıktı — çünkü iki bayatlık koruması zaten devrede.**
`slalom_0820_1212` bag'i `can_odom`'dan iki kez geçirildi (tek değişken `max_dt`; `0.5` vs
`1e9` = eski davranış):

| | koruma AÇIK | koruma KAPALI (eski) |
|---|---|---|
| "Saat sicramasi" | 1 kez (açılışta) | — (yok) |
| ilk 100 tikte maks \|yaw\| | 0.00002 rad | **0.00002 rad** |
| bitiş pozu (16 m sürüş) | x 16.045 / y -0.341 / yaw -1.315 | x 16.046 / y -0.251 / yaw -1.310 |

Sebep: `dt > 0.5 s` olduğunda **hız mesajı da `speed_timeout` (0.5 s), IMU da `imu_timeout`
(0.3 s) sınırını aşmış oluyor** → eski kod da `v=0` ve `yaw_rate=0` ile hiçbir şey entegre
etmiyordu. Yazarın tarif ettiği yarış durumu (dev `dt` + TAZE veri) bu koşularda oluşmadı.
Yani koruma **sigorta**, kanıtlanmış bir arızanın tamiri değil.

**Yazarın sayıları artık bizde de üretiliyor.** Aynı bag, yazarın başlangıç pozuyla
(`IPX=2.05 IPY=0.76 IPYAW=0`) koşulduğunda log satırları onun referansıyla **birebir** çıkıyor
(`TOHUMLAMA #1: 16.5 m ayrisma 2.0 s surdu -> (18.5, 2.1)`, ardından `anlik 0.3 m`), puanlama:

    kosu       n     medyan   %90    maks    DURURKEN  HAREKETTE  tohum
    YAZAR    1048    0.29 m   1.80   3.94      0.27      1.12       2      <- yazarin: 0.21 / 2.54
    YENI     1048    2.74 m   2.80   2.96      2.75      1.66       0

⚠️ **YENI satırı yeni bir tuzağı gösteriyor: eşiğin ALTINDA kalan sabit bir yanlılık asla
düzeltilmiyor.** O koşuda başlangıç pozu teknik kontrol start'ıydı (20.51, 3.89) ama bag'de araç
oraya **2.7 m** uzakta duruyordu (`KAYIT_LISTESI.md` madde 3 bunu zaten söylüyor: "araç start'a
2-2.7 m mesafedeydi"). AMCL oraya kilitlendi, ayrışma `gnss_threshold` 3.0'ın hemen altında kaldı,
gözetmen hiç tohumlamadı ve **medyan 2.74 m sabit hata** koşu boyunca sürdü — dağılma yok
(maks 2.96), yani bu bir kaçış değil, kabul edilmiş bir kayma.
**Sonuç, sezgiye aykırı: 2-3 m yanlış bir başlangıç pozu, 16 m yanlış olandan DAHA KÖTÜ.**
16 m tohumlamayı tetikler ve 0.29 m'ye oturur; 2.7 m tetiklemez ve öyle kalır.
Sahada karşılığı: yığın kalkınca log'daki `GNSS-AMCL ayrisma` satırına bak — **1-3 m'de sabit
duruyorsa poz yanlıdır**, `gnss_threshold:=1.0` ile bir kez tohumlatıp sonra normal değere dönmek
(ya da aracı gerçekten start'a park etmek) gerekir. "1-3 m ise datum doğru" kuralı datum için
geçerli, poz doğruluğu için değil.

Şerit düğümü 2026-08-21 15:57 sürümüyle güncellendi (`~/carla-ros2-wss-bal.zip`). Yine
**yalnızca `lane_follower_node.py`** alındı (2136 → 2251 satır): o pakette `decision_brain.py`
2148 satır (bizimki 2295 — route_planner yaması ve 20.08 slalom düzeltmeleri onda YOK) ve
kontrol düğümlerinde kapanış düzeltmesi yok.

Eklediği: `guven_zayif_s` (0.30), `guven_kayip_s` (1.00), `cift_ikisi_de_taze` (True) —
şerit güvenini yaşlandırıp durumunu bildiriyor.

⚠️ **ID-2 SÖZLEŞMESİ GENİŞLEDİ, VE BU BİR TUZAKTI:**

    "2,<steer>"  ->  "2,<steer>,<guven>,<yas_s>,<durum>"

`durum` bir **METİN**: `TAZE` | `TAHMIN` | `ZAYIF` | `KAYIP`. Yazarı "eski ayrıştırıcılar
`data[1]`'i okumaya devam eder, bozulmaz" demiş — bu **beyin** için doğru
(`lane_detect_event` yalnız `data[1]` okuyor) ama **kontrol düğümü için DEĞİL**:
`master_cb` bütün alanları `[float(x) for x in ...]` ile çeviriyordu, `float("TAZE")`
`ValueError` verir ve **her şerit mesajı tamamen düşerdi** — araç hiç şerit verisi almazdı.
Bu, 17.08'de ID-4'e `P` işaretçisi eklenince yaşananın birebir aynısı (o zaman araç tüm
sürüş boyunca engel verisi almamış ve bariyere girmişti).

**Düzeltildi (her iki kontrol düğümünde):** ayrıştırma artık alan alan — çevrilebilen sayıya,
çevrilemeyen ham metne kalıyor. Hem konumsal okumalar (`data[0]`, `data[1]`) hem ileride
eklenecek metin alanları birlikte çalışıyor. Doğrulandı: `2,52,0.85,0.05,TAZE`,
`2,45,0.0,3.20,KAYIP`, `2,38,0.4,0.5,ZAYIF` ve eski `2,60` — dördü de geçiyor,
**parse hatası 0**.

`steer_mode` yine `pursuit` geliyordu, tekrar `pid` yapıldı (gerekçe ve iki bagdeki ölçüm
bir önceki bölümde). Kapanış düzeltmesi (`ExternalShutdownException` + `rclpy.ok()`) yeniden
uygulandı — arkadaşın kopyasında yok, her merge'de tekrar gerekiyor.

Doğrulandı: derleniyor, düğüm iki ayarda da traceback'siz kalkıyor, beyin regresyonu 28/28,
slalom suite 6/8 (değişmedi). ⚠️ **En yeni sürümün gerçek ZED karelerindeki ölçümü YAPILAMADI**
(T7 çıkarılmıştı); bir önceki sürümün ölçümü geçerli ve bu sürüm onun üstüne yalnızca güven
takibi ekliyor.

**SLALOM İÇİN NE GEREKLİ — kontrol edildi (2026-08-21).** Üç slalom düğümünün
(`lane_follower`, `obstacle_lidar`, `neuravix_control_real`) **hiçbiri TF kullanmıyor**
(`TransformListener`/`lookup_transform` sayısı üçünde de 0). Yani **`bee1_bringup` ve
lokalizasyon çalıştırmadan slalom denenebilir** — TF ağacı yalnızca AMCL/slam ve
`route_planner` için gerekli.

⚠️ **Tek istisna `can_odom`.** Kontrol düğümü `odom_topic`'ten (varsayılan
`/odometry/filtered`, araç komutunda `/odometry/can_wheel`) **topic** olarak konum okuyor,
TF'ten değil. Konum beslenmezse 4 fazlı slalomun yanal ofseti zaman/mesafe yedeğine düşer ve
masa testinde 8 senaryonun 3'ü geriliyor (bkz. "Konumsuz slalom" bölümü). Yani slalom için
gereken en küçük küme: `lane_follower` + `obstacle_lidar` + `neuravix_control_real` +
**odometri kaynağı**.

⚠️ `can_odom` da `/odometry/can_wheel`'e yayınlıyor (`odom_topic` parametresi, aynı
varsayılan). `maps/lokalizasyon/KURULUM.md`'ye göre **araçta hazır bir tekerlek odometrisi
zaten bu topic'te yayınlıyor**. İkisi birden koşarsa tek topic'te iki yayıncı olur.
Araçta önce şunu kontrol et:

    ros2 topic info /odometry/can_wheel -v

Yayıncı **varsa** `can_odom` çalıştırma (aracınki daha iyi: %6-9 eksik, `can_odom` %25).
Yayıncı **yoksa** `ros2 run bee1_description can_odom` ile başlat.
Koşu öncesi zorunlu ön kontrol zaten kayıtlı: `ros2 topic hz /odometry/can_wheel`.

**Deploy imajı yeniden derlendi 2026-08-21 17:49.** Image ID `87b47d4854ee`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.489.662.464 bayt**, SHA-256
`fa7b321a0ccfa7d3ff796fd919384c8cdfa86165989239551998bf4f3e6dc243`. Bu imaj bugünkü üç işi
birden taşıyor: yeni şerit düğümü (15:57 sürümü), `route_planner` mission katmanı, AMCL
lokalizasyon yığını.

İmajın *içinde* doğrulandı: `nav2_amcl`/`nav2_map_server`/`nav2_lifecycle_manager` kurulu;
şerit düğümü 2260 satır + `steer_mode="pid"` + üç güven parametresi; kontrol düğümünde
metin-toleranslı `/master` ayrıştırması; `route_planner` çalıştırılabilir + `share/data/`
üç dosya; `gnss_supervisor` + `tekerlek_odom_tf` kurulu; `share/maps/pist_final.pgm` var;
beyinde `slalom_return_steer=25` / `slalom_escape_lat_frac=0.30`.

⚠️ `/home`'da 33 GB kaldı ve `~/robotaksi_deploy` altında **dört tar** birikti (0819_1033,
0820_1736, 0821_1252 ve güncel) = ~17.6 GB. T7'ye kopyalandıkça eskileri silin.

`slalom_0821` bag analizi (3 slalom + 1 şerit takip, 2026-08-21) — **weave'lerin neden
54-57 s sürdüğü bulundu ve sebebi ayar değil, tek bir bayrak.**

**Önce doğrulananlar:** yeni şerit düğümü araçta çalıştı — ID-2 dört bag'de de **5 alanlı**
(`2,<steer>,<guven>,<yas>,<durum>`) ve **ayrıştırma hatası 0**, yani 21.08'de iki kontrol
düğümüne yapılan `float()` düzeltmesi gerekliydi ve tuttu. Algı kalitesi slalom koşularında
iyi: `TAZE` %70/%88/%81, güven ort 0.73/0.92/0.88. 08-20'ye göre engel verisi de belirgin
daha temiz: fail-safe **0**, 99↔engel sıçraması **0.02-0.07/s** (08-20'de 0.21/s), weave yaw
aralığı **-37..+43** (08-20'de +52/-72).

**⚠️ `1526` (şerit takip denemesi) dört bag'in en kötüsü**: `KAYIP` **%50**, güven ort 0.47.
Direksiyon std'si 0.8 ile çok yumuşak ama bunun sebebi bilgi değil bilgisizlik — karelerin
yarısında nötr 45 basılıyor. Şerit takibi ayrıca incelenmeli; slalom bag'lerindeki %70-88
oranı burada tutmuyor.

**KÖK NEDEN — `_return_hard` tam kilit dönüşü.** Üç bag temiz bir kontrollü karşılaştırma
verdi (aynı gün, aynı pist, aynı kod; tek değişken bu bayrak):

| bag | dönüş modu | dönüş FSM | **align süresi** | align'da yanal | weave |
|---|---|---|---|---|---|
| 1508 | **sert** | 19 | **30 s** | +0.54 → **-1.09** | **57 s** |
| 1515 | **sert** | 19 | **27 s** | +0.34 → **-1.54** | **54 s** |
| 1520 w1 | yumuşak | 36 | **6 s** | +0.55 → +0.05 | 36 s |
| 1520 w2 | yumuşak | 36 | **6 s** | +1.71 → +0.88 | 24 s |

`pass` fazında ön koridora engel girince (`front < avoid_distance`) `_return_hard = True`
oluyor ve dönüş **tam kilitte** yapılıyor. Dönüş fazı `slalom_return_max_deg` (25°) açı
tavanıyla biter — **ama tekerlek hâlâ +31'de, yani tam sağ kilitte**. 10 birim/s slew ile
geri gelmesi ~6 s sürer ve o sürede araç dönmeye devam eder: yaw -25 → -34, yanal +1.5'ten
geçip **-1.1 / -1.5'e**, yani kendi şeridinin ÖBÜR tarafına. `align` kalan mesafeyi 2 km/h'de
25 saniye sürünerek kapatır. Yumuşak dönüşte aynı fazlar 6 saniyede bitiyor.
Bu, kaçış fazının aşmasıyla **aynı sınıf** hata: faz çıkış ölçütü kasada sağlanıyor ama
aktüatör hız sınırlı olduğu için fiziksel dönüş devam ediyor.

**İKİNCİ, BAĞIMSIZ BULGU — yanal aşım hıza bağlı.** Direksiyon slew'i sabit olduğu için:

| weave | hız | yanal tepe (hedef 1.70) |
|---|---|---|
| 1508 / 1515 / 1520 w1 | 1-2 km/h | 1.93 - 2.00 (**+15%**) |
| **1520 w2** | **3 km/h** | **3.15** (**+85%**) |

Yani `slalom_speed_kmh` düşürmek manevra geometrisini bozmaz, **düzeltir** — 20.08'de
"emniyet direksiyonu kısarak değil hızı düşürerek alınır" diye yazılan kural burada
niceliksel olarak doğrulandı.

**Acil pencereleri (kural uygulandı):** `1515` t=87-106 ve `1520` t=95-102 `fb_emergency`
aktif — o iki bag'in sonundaki `OBSTACLE_STOP`'lar **operatör müdahalesi**, kod arızası
değil. **`1508`'de acil YOK**, tek tam yorumlanabilir kayıt odur: 57 s'lik weave'den sonra
t=138'de gerçek bir `OBSTACLE_STOP` (front 1.5, araç şeridinin 0.44 m solunda).

**`slalom_return_hard` parametre yapıldı, VARSAYILAN DEĞİŞTİRİLMEDİ (True = eski davranış).**
Gerekçe: masa simülatörü bu arızayı **hiç üretmiyor** — ölçüldü, sim'in align fazı sekiz
senaryonun hepsinde tek yönlü (+1.39 → +0.21) ve karşı tarafa hiç geçmiyor; sert/yumuşak
dönüş arasındaki suite farkı da yok (P2 min 1.39→1.43). Projenin üç kez tekrarlanmış dersi
gereği (bkz. 08-10 / 08-17 / 08-19 kararları) bu kararı sim veremez, **araçta A/B edilmeli**:

    ros2 run neuravix_ros2 neuravix_control_real --ros-args -p slalom_return_hard:=false

Doğrulandı: kapsamlı derleme, masa suite 8 senaryo değişmedi (regresyon yok), düğüm
`slalom_return_hard:=false` ile traceback'siz kalkıyor, yumuşak modda sapma 30 → 20 birim.

**Simülatörün hâlâ modellemediği şey:** `align` fazına tam kilitten girildiğinde oluşan
karşı-tarafa geçiş. Sim'i bu bağlamda güvenilir kılmak için önce bu imzayı üretmesi
sağlanmalı (araçta ölçülen: align girişinde tekerlek +31, çıkışta yanal -1.1).

`1526` şerit takip bag'i — **"fit atıyor ama direksiyona gitmiyor" ölçüldü: zincir sağlam,
iptal şerit düğümünün İÇİNDE** (2026-08-21):
- **Zincir kopuk değil.** ID-2 → beynin FSM açısı korelasyonu **+0.751**, FSM →
  `steering_target_value` **−1.000** (birebir doğrusal eşleme). Şerit ne ürettiyse direksiyona
  eksiksiz gitti. Ama çıktının kendisi ölü: ID-2 std **0.87**, direksiyon hedefi aralığı
  **−4.0..+4.4 ham** (mevcut ±36'nın %12'si), tekerlek −5..+4, direksiyon motoru pwm=0 **%71**.
- **MEKANIZMA — `Yön` terimi `Yanal` terimini iptal ediyor.** Overlay'den 12 kare okundu:
  `Error` tüm koşu boyunca **−57/−58 px'e çivili** kalırken `Yanal` +1 → +8 → +69 → **+92 px**
  gidiyor; `Yön` her seferinde ters işaretle büyüyüp (−59 → −65 → −109 → **−150**, doyuma
  vurmuş) hatayı sıfırlıyor. Yanal hata 90 kat arttı, çıktı kıpırdamadı.
- **KÖK NEDEN — sağ "şerit" fiti BARİYER.** BEV karesi belirleyici: doğru bir IPM'de şerit
  çizgisi dikeydir; kırmızı sağ fit ~45° eğimle bariyer tabanına oturmuş. `Yanal` ve `Yön`
  **aynı yanlış fitten** türediği için biri diğerini götürüyor. Yani "fit atıyor" doğru
  (`TAZE`, güven 1.00) — ürettiği iki terim birbirini yiyor.
- İki ayar bunu mümkün kılıyor, ikisi de arkadaşın 15:57 sürümünden: **`heading_gain=75`**
  (dosyanın kendi yorumu 30 diyor, bayat) ve **`fit_max_slope=5.0`** (yorumu 3.0 diyor, bayat).
  Gözlenen Yön −65 → eğim 0.87; Yön −150 → eğim ≥2.0. Sürülebilir en dar viraj 3.0'a karşılık
  gelir (5.6 m yarıçap), yani 5.0 hiçbir gerçek virajın gerektirmediği kadar gevşek.
- **Genişlik kapısı bu sınıfı yakalayamaz** (yine): LaneW 329-399 px = 2.6-3.2 m, 250..600
  bandının tam ortası. 08-20'de S4 diye kaydedilen "yanlış çizgi çifti" sınıfının aynısı.
- **Varsayılanlar DEĞİŞTİRİLMEDİ**: bu bag'de kamera topic'i kayıtlı olmadığı için boru hattı
  yeniden koşturulup ölçülemiyor; arkadaşın seçtiği iki değeri ölçemeden ezmek doğru değil.
  Sıradaki koşuda çalıştırma anında denenecek (⚠️ `lane_follower`'da parametre geri çağrımı
  YOK, `ros2 param set` sessizce hiçbir şey yapmaz — `err_offset`'teki tuzağın aynısı):

      ros2 run neuravix_ros2 lane_follower --ros-args \
        -p heading_gain:=0.0 -p fit_max_slope:=3.0

  Overlay'de bakılacak şey: `Error` artık `Yanal` ile birlikte hareket ediyor mu.
- **Asıl çözüm algı tarafında**: bariyerin asfaltla birleştiği çizgi model tarafından `lane`
  etiketlenmiş. Düğümün `bariyer_ele_oran=0.25` süzgeci ancak model oraya `barrier` maskesi
  koyarsa çalışır; koymamış. `serit_v2.pt`'nin eğitim setine bariyer tabanı örneği eklenmeli —
  parametreyle çözülmez.
- Yan bulgular: **`1526`'nın %77'sinde araç DURUYORDU** ve `KAYIP` %50'sinin büyük kısmı meşru
  (t=46 BEV karesi aracın bariyere baktığını, ortada yol olmadığını gösteriyor) — algı arızası
  değil, sahne. Overlay'deki **`FPS: 8` yanıltıcı**: gerçek yayın hızı 20.8 Hz (slalom
  bag'lerinde 14-17 Hz); yine de 08-20'deki 26-27 Hz'e göre ~%40 düşüş var, yeni düğümün ek
  işi (çift seçimi, bariyer eleme, güven takibi) muhtemel sebep.

**Deploy imajı yeniden derlendi 2026-08-21 19:19** (17:49 build'in yerine). Image ID
`0ead8620455b`, tar `~/robotaksi_deploy/robotaksi_humble.tar` **4.489.669.120 bayt**, SHA-256
`863166773af707dc2642a2681a2301454035c9e675eaf5b93ab1063f57642425`. İçerdiği üç yenilik,
imajın *içinde* doğrulandı: beyinde+iki kontrol düğümünde `slalom_return_hard` (varsayılan
True = eski davranış), şerit düğümünde `cift_paralel` paralellik kapısı +
`cift_paralel_tol=0.25` (düğüm 2322 satır). Bir önceki tar
`~/robotaksi_deploy/robotaksi_humble_0821_1752.tar` adıyla korundu.

⚠️ **`cift_paralel` kapısı TEST EDİLMEDEN imaja girdi** (operatör kararı, hız gerekçesiyle).
Sözdizimi kontrolü ve kapsamlı derleme yapıldı; kapının geometrik davranışı (bariyer fitini
reddedip gerçek çifti/virajı geçirdiği) **ölçülmedi**. Araçta şerit takibi kötüleşirse
yeniden derlemeye gerek yok: `-p cift_paralel_tol:=0.0` ile kapanır. Gerçek karelerde
ateşlenme oranı ölçümü de bekliyor (T7'deki `joystick_46` gerekiyor, disk bağlı değildi).

⚠️ **ROS 2 tanımlanmamış parametre override'ını HATA VERMEDEN YOK SAYAR.** 19:19 öncesi imajla
`-p slalom_return_hard:=false` çalıştırılsaydı araç sorunsuz kalkar, koşu "sert dönüş
kapatıldı" diye kaydedilir, ama eski davranış koşardı. Yeni bir parametreyi araçta denemeden
önce imajda var mı diye bak:
`docker run --rm robotaksi_humble:latest grep -c <param> /ros2_ws/install/neuravix_ros2/lib/python3.10/site-packages/neuravix_ros2/<dosya>.py`

⚠️ `/home`'da **27 GB** kaldı ve `~/robotaksi_deploy` altında **beş tar** birikti (~22 GB).
T7'ye kopyalandıkça eskileri silin.

**Gerçek kontrol düğümünün dört varsayılanı araç-doğrusu yapıldı (2026-08-21 akşamı).** Tetikleyen
olay: operatör düğümü **hiçbir `-p` vermeden** çalıştırdı ve araç hiçbir dönüşü düzgün
tamamlayamadı. Sebep tercih değil, varsayılanın araçta yanlış olmasıydı:

| parametre | eski | **yeni** | neden tercih değil |
|---|---|---|---|
| `odom_topic` | `/odometry/filtered` | **`/odometry/can_wheel`** | araçta o topic'i **kimse yayınlamıyor** (EKF planından kalma). Konum gelmeyince 4 fazlı slalomun yanal ofseti zaman/mesafe yedeğine düşüyor — masa testinde 8 senaryonun 3'ü bozuluyor, P3'te araç 2.7 m şerit dışına çıkıyor |
| `slalom_lateral_target` | 3.0 | **1.7** | 3.0 = tam şerit değişimi = dönümlü dizide 2. engelin tam içi. Ölçülmüş pencere 1.14..1.82 m |
| `speed_target_scale` | 0.15 | **0.25** | `slalom_speed_kmh` ile **ÇARPIM** halinde çalışıyor ve bu gözden kaçıyor |
| `slalom_speed_kmh` | 4.0 | **8.0** | eski çift `4.0×0.15=0.60` → tabana takılıp **1.2 km/h**; yeni çift `8.0×0.25=2.0 km/h`. 1.2 km/h'de 9-10 m'lik weave 30 s sürüyor |

**Bilerek varsayılan YAPILMAYAN ikisi** (bunlar gerçek A/B seçimleri, ölçmeden çevrilmemeli):
- **`return_home_when_free`** `False` kalıyor — strateji seçimi; operatör *"parametre olarak
  kalsın, ikisini de deneyeceğim"* demişti. `false` = geçtiği şeritte kal (bilinçli tasarım).
- **`slalom_align_lateral`** `0.6` kalıyor — `slalom_return_hard=True` ile **kötü etkileşiyor**:
  `slalom_0821`'de sert dönüş yüzünden align zaten 27-30 s sürüyordu ve −0.44/−0.86 m'de
  bitiyordu, 0.3 eşiği hep zaman aşımına düşerdi. Bu ikisi **birlikte** değişmeli; önce sert
  dönüş A/B'si.

⚠️ **Sim düğümü (`neuravix_control_node.py`) DEĞİŞMEDİ** — CARLA kendi değerlerini arayüzün 8p
butonundan geçiriyor (`slalom_lateral_target=3.0`, `slalom_speed_kmh=2.0`; `odom_topic` ve
`speed_target_scale` o düğümde zaten yok).

⚠️ **Bu değişiklikten sonra 19:19 imajı BAYAT** — dört varsayılan imajın içinde eski.
Doğrulandı: kapsamlı derleme, gerçek düğüm traceback'siz kalkıyor, açılış log'u
`odom_topic='/odometry/can_wheel' ... speed_scale=0.25` yazıyor.

⚠️ **ROS 2 tanımlanmamış parametre override'ını hata vermeden yok sayar** — bu yüzden "koşuda
`-p` verdim" demek onun etkili olduğu anlamına gelmiyor. Yeni bir parametreyi araçta denemeden
önce imajda var mı diye bak, ve koşu log'unun ilk satırındaki açılış özetiyle doğrula.

**İmaj yeniden derlendi 2026-08-22 09:54 — TAR OLUŞTURULMADI** (operatör kararı). Image ID
`d225cee655a3`; dört yeni varsayılan imajın içinde doğrulandı (`odom_topic=/odometry/can_wheel`,
`speed_target_scale=0.25`, `slalom_speed_kmh=8.0`, `slalom_lateral_target=1.7`), üç A/B bayrağı
bilerek eski (`slalom_align_lateral=0.6`, `slalom_return_hard=True`, `return_home_when_free=False`),
sim düğümü bozulmadı. ⚠️ `~/robotaksi_deploy/robotaksi_humble.tar` hâlâ **0ead8620455b (21 Ağu
19:19)** imajını taşıyor — yeni imaj yalnızca laptopta, araca gitmesi için `docker save` gerekiyor.

**Kayıt tarifine `/rosout` eklendi (2026-08-22).** `slalom_0821` bag'lerinde tesadüfen vardı ve
analizde belirleyici oldu; artık tarifte açıkça yazılı. Metin olduğu için maliyeti ihmal
edilebilir (`/velodyne_points` ~250 MB/dk, `/rosout` birkaç yüz KB) ve bag'den şunları okunur
kılıyor: kontrol düğümünün **açılış özeti** (`odom_topic=`, `speed_scale=`, `steer gain=`,
`serit araligi=` — yani "bu koşu hangi ayarla yapıldı" sorusu bag'in içinden cevaplanır),
`hareket=odom | ODOM YOK (CAN hizi) | HAREKET VERISI YOK` satırı, `SLALOM konum verisi OLMADAN
basladi` uyarısı, şerit düğümünün `Fit cifti PARALEL DEGIL` / `Serit genisligi ... tek fite
dusuldu` sayaçları, `obstacle_lidar`'ın açılıştaki yükseklik penceresi doğrulaması ve hangi
düğümlerin gerçekten koştuğu.

**Araç koşusu düğüm listesi ve sırası (2026-08-22, doğrulandı):** (0) `ros2 topic info
/odometry/can_wheel -v` + `ros2 topic hz /velodyne_points`; (1) `can_odom` **yalnızca**
`/odometry/can_wheel`'de yayıncı yoksa (aracınki %6-9 eksik, `can_odom` %25 — aracınki tercih
edilir, ikisi birden koşarsa tek topic'te iki yayıncı olur); (2) `lane_follower -p
camera_topic:=/zed/zed_node/rgb/image_rect_color -p show_window:=false` (camera_topic zaten
varsayılan); (3) `obstacle_lidar -p side_offset:=3.0 -p side_corridor:=1.26` — **`side_offset`
2.74 DEĞİL 3.0**: 2.74 CARLA'nın değeri, gerçek pist şeridi 2.96 m ölçüldü ve `side_offset`
komşu şeridin merkezidir; `side_corridor` 1.26 (varsayılan 1.0) kör bandı 1.30 → 1.04 m'ye
daraltır; `lidar_height` bayrağı gereksiz, 1.35 zaten varsayılan; (4) `neuravix_control_real`
(yeni imajla yalnızca üç A/B bayrağı); (5) `steering_ctrl -p tolerance:=2.0` — **`max_delta`
bayrağı VERİLMEMELİ**, 90'a çıkarmak ölçülmüş çıkmaz sokaktır (joystick sapma 73 ile aynı hız,
9.5 vs 9.2 birim/s; doygunluk motorda) ve koşuyu önceki kayıtlarla kıyaslanamaz kılar;
(6) `throttle_ctrl` **EN SON**, alan boş ve sürücü frende — gazı devreye alan adım budur.
Yol B kullanıldığı için `speed_fb_relay`/`throttle_relay` **çalıştırılmaz**. Hepsi `tmux` veya
`docker exec -d` içinde.

Şerit yön-terimi arızası ölçüldü ve düzeltildi (2026-08-22, **dört gerçek veri seti**:
T7'deki `joystick_46/47/48` ham ZED kareleri + `slalom_0821_1526`'nın overlay kareleri).
Ölçüm aracı `scratchpad/serit_olc.py` — gerçek `LaneFollowerNode`'u rclpy parametre
override'larıyla kurup bag karelerini `cb()`'ye veriyor, iç terimleri (`_lat_err`,
`_head_err`, `_paralel_red`) okuyor. `1526`'nın **ham kamerası hiçbir yerde yok**, o yüzden
`lane_debug` JPEG'leri kullanıldı (üstüne ince çizgi/yazı çizilmiş orijinal kare) — **yaklaşık**,
ama arızanın gerçekleştiği tek sahne o.

- **DÜN VERDİĞİM İKİ ÖNERİDEN BİRİ YANLIŞTI.** `-p fit_max_slope:=3.0` ölçüldü ve **zararlı**:
  `joystick_46`'da TAZE %91 → **%83**, `1526`'da hata std 84 → **174 px**. Önerilmiyor,
  `fit_max_slope=5.0` kalıyor.
- **"Yön terimi Yanal'ı iptal ediyor" bulgusu genel DEĞİL, `1526` sahnesine özgü.** İyi
  kayıtlarda iki terim **toplanıyor** (örn. `lat −54, head −59 → err −113`) ve kor(lat,err)
  0.984. Yani terim normalde tasarlandığı işi yapıyor.
- **Gerçek arıza şu: yön terimi hatanın İŞARETİNİ çevirebiliyor** — araç ölçülen sapmanın
  tersine kırılıyor. Ateşlenme oranı: joystick_46 %4, _47 %9, _48 %2, **1526 %35**
  (tipik kare: yanal +10 px, yön −43 px → hata −33 px).
- **Çözüm `heading_no_flip` (yeni parametre, varsayılan True)**: yön terimi hatayı sıfıra
  kadar küçültebilir ama ötesine geçemez. Yanal 0 iken tam öngörü serbest (viraj başında en
  çok ihtiyaç duyulan an), yanal büyüdükçe öngörü onu yalnızca yumuşatır.

  | | işaret ters çevirme | öngörü korunumu | TAZE | oynaklık |
  |---|---|---|---|---|
  | mevcut | 8 / 17 / 3 / **69** kare | %100 | — | referans |
  | **`heading_no_flip`** | **0 / 0 / 0 / 0** | **%95 / %90 / %98 / %74** | değişmedi | +%3-6 |
  | `heading_gain:=0` | 0 | **%0** | değişmedi | −%16-39 |

  `heading_gain:=0` de arızayı bitiriyor ve daha yumuşak, **ama öngörüyü tamamen atıyor** ve
  yumuşaklık kazancının doğruluk kazancı olduğunu gösterecek yer gerçeği yok. Hedefe yönelik
  olan tercih edildi. Kaba geri dönüş hâlâ mümkün: `-p heading_no_flip:=false -p heading_gain:=0.0`.
- **Paralellik kapısı (`cift_paralel`) doğrulandı ama bu arızayı ÇÖZMÜYOR.** Sentetik geometri
  testi geçiyor (dikey çift, aynı eğimli viraj ve %3.8 eğim farkı KABUL; bariyer eğim 0.87 →
  %27.7 RED, eğim 2.0 → %64.3 RED, eğim 0.5 → %16.1 kabul). Ama **794 gerçek karede 0 kez
  ateşledi**: `1526`'nın fit çifti *paralel ama eğik*ti (iki fit de aynı açıda), kapı ise
  **ıraksayan** çifti yakalar — o sınıfı tasarımı gereği göremez. Zararsız, varsayılan 0.25'te
  kalıyor, ama "1526'yı çözer" diye sayılmamalı.
- ⚠️ **`lane_w_min_px` 250 → 300'e geri gitmiş** (arkadaşın 15:57 sürümü). 20 Ağustos'taki 250
  ölçümü **eski çift-seçim boru hattına** aitti; yeni sürümde `cift_sec`/`lane_w_tol` var, o
  yüzden ölçümü doğrudan taşımak doğru değil. Düzeltmeden önce ham çift genişlikleri yeniden
  ölçülmeli. Şimdilik 300'de bırakıldı.
- **Asıl kök neden hâlâ modelde**: `serit_v2.pt` bariyerin asfaltla birleştiği çizgiyi `lane`
  diye etiketliyor. `bariyer_ele_oran=0.25` süzgeci ancak model oraya `barrier` maskesi
  koyarsa çalışır. Yukarıdakiler semptomu sınırlıyor; sebebi eğitim seti çözer.

`joystick_47` yanlış anlaşılması — **bayrak değil SAHNE** (2026-08-22). Bag 21 Ağustos 19:39'da,
yani `heading_gain:=0` önerisinden sonra kaydedildi ve overlay'de **`Yon: +0`** yazıyor, yani
gerçekten o bayrakla koşulmuş. Overlay'de `Error` −3 → +32 → +87 → **+317 → +352 px (+2.60 m)**
büyüyor ve bu ilk bakışta bayrağın zararı gibi görünüyor. **Değil:**
- `t=38 s` karesi aracın **açık padok/apron alanında** olduğunu gösteriyor — ortada şerit yok;
  `cizgi:4` maske bulmus ama mavi "sol serit" fiti yerdeki ince direge, sari merkez saga
  savrulmus.
- Aynı kareler her ayarla replay edildiğinde **hata dağılımı aynı**: `mevcut` (heading 75)
  max |err| 386 / 41 kare >250; `yon0` max 418 / **33** kare >250; `egim3` 454 / 42. Yani
  bayrak o hatayı üretmedi, hatta büyük-hata karesi sayısını biraz azalttı.
- ⚠️ **Güven değeri kalite ölçüsü DEĞİL**: düğüm bu bag'de %96 `TAZE` ve güven ort **0.98**
  diyor — padokta direk fitlerken de kendinden emin. `durum`/`guven` alanlarını "fit doğru"
  diye okumayın; yalnızca "fit taze" demek.
- Ders: bir ayarın zararlı olduğuna karar vermeden önce **aynı kareleri diğer ayarla da**
  koştur (`tools/serit_olc.py`). Sahne kaynaklı hata, ayar kaynaklı sanılabiliyor.

**Şerit düğümü için tampon (rollback) komutu** — bu oturumda eklenen iki değişikliği birden
kapatır ve arkadaşın 15:57 sürümünün birebir davranışına döner, yeniden derleme gerekmez:

    ros2 run neuravix_ros2 lane_follower --ros-args \
      -p camera_topic:=/zed/zed_node/rgb/image_rect_color -p show_window:=false \
      -p heading_no_flip:=false -p cift_paralel_tol:=0.0

**Deploy imajı yeniden derlendi 2026-08-22 11:49 ve tar alındı.** Image ID `7fe692ac1991`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.489.713.152 bayt**, SHA-256
`caa6c26adf1fdb390595b765f9bb35823b999db4e1da847c651cdcea2d2c42e6`. Bir önceki
`robotaksi_humble_0821_1919.tar` adıyla korundu. İmajın *içinde* doğrulandı — şerit düğümü:
`heading_no_flip=True` (yeni), `cift_paralel_tol=0.25`, `heading_gain=75.0`, `fit_max_slope=5.0`
(geri çekilen 3.0 önerisi UYGULANMADI); gerçek kontrol düğümü: `odom_topic=/odometry/can_wheel`,
`speed_target_scale=0.25`, `slalom_speed_kmh=8.0`, `slalom_lateral_target=1.7`,
`slalom_return_hard=True`.

⚠️ `/home`'da **19 GB** kaldı, `~/robotaksi_deploy` altında **altı tar** (~26 GB). T7'ye
kopyalandıkça eskileri silin.

## TEKNİK KONTROL (2026-08-22)

Şartlar `Finalist_Bilgilendirme.pdf` §1'den (dosya `~/loc_planner_map.zip` içinde, workspace'te
yoktu): araç başlangıçtan hareket edip **hedef bölgesine ulaşmalı**; **engel algılayıp sakınma
manevrası yapmalı** (birden fazla engel olabilir); **sakınma dışında şerit ihlali yapmamalı**;
**hedef noktasından sonra yolu kapatan bir engel var** ve "hedefe ulaşamayan VEYA hedefi geçip bu
engele çarparak duran" araç başarısız; **bariyere çarpan** araç başarısız.

`teknik_kontrol.geojson`: `start` (95.15, 48.88) h=229.17° → harita **(20.51, 3.89)** yaw 10.03°,
`hedef` (57.24, 20.82) h=139.17° → harita **(64.02, 22.09)**. Planner rotası `[1, 0, 4, 50]`,
iki olay: node 4'te **70° sol dönüş**, node 50'de **hedef**.

**KAPATILAN BOŞLUK — hedefte durma kodda HİÇ YOKTU.** `route_planner_node.py`'nin goal dalı
`else: # goal (hedef) — barier durdurur, komut yok` diyordu, yani durma tamamen lidara
bırakılmıştı: tek nokta arıza, üstelik engel `avoid_distance` (4.5 m) içine girdiğinde beyin onu
sıradan bir engel sanıp **etrafından dolaşmaya** kalkardı — bu doğrudan başarısızlık (hedefi geçmek
+ şerit ihlali). Artık iki kademeli:

    5,4,1   hedefe trigger_dist (6 m) kala  -> slalom girişi YASAK + hız tavanı (hedef_speed 3 km/h)
    5,4,0   hedefe hedef_dur_m (2 m) kala   -> DriveState.MISSION_END: SÜRÜNEREK yaklaş, engelde dur

**`5,4,0` neden hemen durdurmuyor (karar 2026-08-22):** komut konumdan tetikleniyor ve konum
hatası 1-3 m. "2 m kala kesin dur" deseydik hata ters yöne düştüğünde araç hedefe **varmadan**
durabilirdi — şartnamede "hedef noktasına ulaşamayan" da başarısızlık. `MISSION_END` bu yüzden
sürünme yapıyor: hız `hedef_speed` (3 km/h), direksiyon nötr, slalom yasak, ve **asıl durușu
LİDAR veriyor** (`front < stop_distance` ya da fail-safe `front=0`). Lidar hiç görmezse
`hedef_creep_m` (4.0 m) sonunda yine duruyor. Odometri yoksa sürünme ölçülemez → güvenli taraf,
hemen durur.
⚠️ `MISSION_END` `obstacle_event`'in erken-dönüş listesinde **olmak zorunda**: olmasaydı sürünme
sırasında engel görülünce state `OBSTACLE_STOP`'a geçer, `MISSION_END`'den ÇIKILIR ve yol
"açılınca" araç kapalı yola devam ederdi.

- **`MISSION_END` terminaldir**: şerit, engel (yol açılsa bile), tabela/yeşil ışık, planner
  dönüş/durak/park/iptal komutlarının hiçbiri aracı tekrar hareket ettiremez. Tek çıkış düğümün
  yeniden başlatılması. Gerekçe: hedeften sonrası kapalı yol.
- **Hedef olayı ATLANMAZ** (diğer olaylardaki `gecis_payi` atlama mantığı goal için devre dışı) ve
  araç hedefi geçmişse (`_yay > S[ri]`) mesafeye bakılmaksızın DUR gönderilir.
- Hız tavanı `_engel_hiz_tavani()` üzerinden uygulanır — Bug A'nın aynısına düşmemek için
  (şerit olayı 20 Hz, engel 10 Hz; ayrı yazılsa 50 ms'de ezilirdi).
- Yaklaşma kademesinde araç **yine yavaşlar ve `stop_distance` içinde durur**; bastırılan yalnızca
  savurma manevrası (virajdaki `_in_curve()` bastırmasıyla aynı mantık).

Doğrulandı: 18 maddelik hedef testi (yaklaşmada slalom yapmıyor / aynı engel yaklaşma yokken
slalom yapıyor = regresyon yok / hedefte dur / MISSION_END'den şerit-engel-tabela-planner ile
çıkış yok / yaklaşmada yakın engel yine durduruyor / fail-safe `0,0,0` yine durduruyor);
planner uçtan uca sürüş benzetimi tek örnekle **`5,1,70` (38.8 m) → `5,4,1` (48.5 m) →
`5,4,0` (52.2 m)**; slalom masa suite'i **7/8** (değişmedi, `_hedef_yaklasma` kapalıyken kod yolu
birebir aynı).

**Hedef yaklaşmasında lidar durması BOZULMUYOR** (ölçüldü, `5,4,1` açıkken):

| front | durum | hız | fren |
|---|---|---|---|
| 99 / 7.0 / 5.5 m | LANE_FOLLOW | 3.0 km/h (hedef tavanı) | 0 |
| 4.0 / 3.0 / 2.5 m | LANE_FOLLOW (slalom YOK) | 2.5 km/h | 0 |
| **2.0 / 1.0 / 0.5 / 0.0 m** | **OBSTACLE_STOP** | **0.0** | **1** |

Yani bastırılan tek şey savurma manevrası; yavaşlama ve `stop_distance` (2.2 m) freni aynen
duruyor, 20 Hz'lik şerit olayı hız tavanını ezemiyor. Kıyas: aynı 4.0 m engel yaklaşma
KAPALIYKEN `OBSTACLE_AVOID`'a giriyor (regresyon yok). Planner hiç komut göndermezse (lokalizasyon
yok) ve iki yan koridor da kapalıysa yine 2.0 m'de duruyor — eski davranış korunuyor.

**⚠️ Operatör kaçış yolu — lokalizasyon ayağa kalkmazsa el ile tetiklenebilir:**

    ros2 topic pub --once /master std_msgs/String "data: '5,4,1'"   # slalom yasak + yavasla
    ros2 topic pub --once /master std_msgs/String "data: '5,4,0'"   # DUR (gorev sonu)

**Teknik kontrole hazırlık durumu:**

| şart | durum |
|---|---|
| engel algılayıp sakınma | ✅ masa 7/8; araçta 08-21'de iki weave tamamlandı |
| engele/bariyere çarpmama | ✅ `avoid_abort_distance` + `stop_distance` + fail-safe `0,0,0` |
| **sakınma dışında şerit ihlali yok** | ⚠️ **EN BÜYÜK RİSK**, aşağıya bak |
| hedefe ulaşma (dönüş komutu) | ⚠️ `/amcl_pose` gerekiyor, araçta hiç çalışmadı |
| **hedefte durma** | ✅ bugün eklendi (kodda yoktu) |

**VİRAJDAKİ ENGELLER — ikinci kritik açık, aynı gün kapatıldı.** Teknik kontrolde virajın içine
iki engel konuyor: araç düz gidemez, sola dönmesi gerekiyor ve dönüşü planner komutluyor
(`5,1,70` @ node 4). Ölçüldü — **komutlu dönüş engel yüzünden kesiliyor ve komut kalıcı olarak
kayboluyordu**:

| dönüş sırasında front | eski davranış |
|---|---|
| 5 m | dönüş sürüyor |
| **4 / 3 m** | dönüş kesildi → **OBSTACLE_AVOID (slalom)** |
| **2 / 1 m** | dönüş kesildi → **OBSTACLE_STOP** |

Kesilince planner olayı zaten tükettiği için (`ev_i += 1`) komut bir daha gelmiyordu; araç yol
açılınca `LANE_FOLLOW`'a dönüp **kavşağı düz geçiyordu**. CLAUDE.md bu boşluğu 21.08'de
"PLANNER_TURN sırasında engel olayı bloke değil ... `front_trust_deg` koruması burada YOK,
bilinçli bırakıldı ama sahada izlenmeli" diye kaydetmişti — teknik kontrol senaryosu tam olarak
onu tetikliyor.

**Düzeltme: komutlu dönüş artık bir MANEVRA olarak ele alınıyor, weave ile aynı kurallarla.**
- **Slalom yok**: dönüşün kendisi zaten kaçınma manevrası.
- **Durma eşiği sıkı**: `stop_distance` (2.2 m) yerine `avoid_emergency_front` (1.0 m) — gerekçe
  weave'deki ile aynı: burun kasıtlı olarak şerit yönünden çıkmıştır, gövdeye sabit ön koridor
  dönüş boyunca yol kenarını ve köşe engellerini tarar.
- **Kesilirse kaybolmuyor**: kalan süre `_pturn_kalan`'da saklanıyor, `_obstacle_stop_control`
  yol açıldığında `LANE_FOLLOW` yerine **dönüşü kaldığı yerden tamamlıyor** (sinyal ve ölçek
  korunur).

Doğrulandı (15/15): 5.0/4.0/3.0/2.0/1.5 m engelde dönüş sürüyor; 0.7 m'de duruyor ve kalan süre
saklanıyor; yol açılınca `PLANNER_TURN`'e geri dönüp sola kırıyor; `0,0,0` fail-safe dönüşte de
durduruyor; engelsiz dönüş normal bitiyor ve bayrak temizleniyor. Hedef sürünmesi 12/12,
hedef davranışı 17/17, slalom masa suite **7/8 (değişmedi)**.

**KONUM KAYNAĞI: TEKNİK KONTROLDE YALNIZ GNSS** (operatör kararı 2026-08-22, "şu an riske
giremeyiz"). Yeni düğüm `bee1_description/scripts/gnss_pose_node.py` (çalıştırılabilir adı
`gnss_pose`): `/gnss` → map dönüşümü + Xsens `/filter/quaternion`'dan yön, çıktı
`/gnss_pose` (`PoseWithCovarianceStamped`, frame `map`).

    ros2 run bee1_description gnss_pose
    ros2 run neuravix_ros2 route_planner --ros-args -p pose_topic:=/gnss_pose \
      -p geojson:=<gunun.geojson> -p trigger_dist:=6.0

Gerekçe: AMCL bu pistte **tek başına kullanılamıyor** (medyan 27-29 m) — doğruluğu zaten GNSS
gözetmeninden geliyor, ve ölçülen 0.29-1.19 m sayıları **GNSS'e karşı** ölçüldü, yani "AMCL
GNSS'i takip ediyor" diyorlar. Yığın gerçek araçta hiç çalışmadı. Teknik kontrol rotası ~54 m,
tünel yok, iki olay var (6 m / 2 m eşikleri) — GNSS bunu taşır ve AMCL'in sahada denenmemiş
yakınsama/aliasing riskini ortadan kaldırır.
⚠️ **AMCL yığını YERİNDE DURUYOR ve değişmedi**; `gnss_pose` ayrı bir topic'e yayın yapıyor,
ikisi aynı anda koşabilir (AMCL'i izlemek için). Yarış günleri kararı sonra verilecek.

Doğrulandı (`lokal_0820_0722`, gerçek araç GNSS'i):
- **Konum**: düğümün ürettiği `(18.46, 2.09)`, aynı bag'de GNSS gözetmeninin AMCL'e attığı
  tohumla (`18.5, 2.1`) birebir aynı — dönüşüm bağımsız olarak doğrulandı.
- **Yön**: `yaw = filter_yaw − datum_yaw` formülü GNSS gidiş yönüne karşı **medyan +0.3°,
  std 0.4°** (30 hareketli örnek). Yazarın saha ölçümüyle (−2.2° / +0.1°) tutarlı. Üç alternatif
  formül denendi ve elendi (ofsetsiz +149.5°, ters işaret +18.4°, pusula/NED −10.0°).
- Başlangıçta okunan `+9.1°`, geojson'dan türetilen start yaw'ı `10.03°` ile ~0.9° uyuşuyor.
- `route_planner` `pose_topic:=/gnss_pose` ile hatasız kalkıyor ve rotayı kuruyor.
- Yön henüz yoksa (filtre gelmiyor + araç duruyor) düğüm **poz yayınlamaz** ve sebebini loglar —
  yanlış yönle dönüş komutu ürettirmemek için bilinçli.

**Kalan iki iş, önem sırasıyla:**
1. **Araçta `gnss_pose` + `route_planner` bir kez koşsun.** Kontrol: `ros2 topic hz /gnss_pose`
   (~4 Hz) ve planner log'unda `ROTA (... node)` satırı. Yedek yol: el ile tetikleme (yukarıda).
2. **`slalom_return_hard:=false` A/B'si** (isteğe bağlı — operatör şerit ihlalini teknik
   kontrol için kritik görmüyor). 08-21 ölçümü: `True` iken align 27-30 s
   sürüyor ve araç weave'i şeridinin **öbür tarafında** (−1.1 / −1.5 m) bitiriyor — bu tam olarak
   "sakınma dışında şerit ihlali" demek. `false` ölçülen iki weave'de align'ı **6 s**'ye indirmiş
   ve yanalı +0.05 / +0.88'de bırakmıştı. Varsayılan hâlâ `True` (masa simülatörü bu arızayı
   üretmediği için karar sim'e bırakılmadı).
3. ~~Şerit ayar denemesi~~ — **bu madde ZATEN KAPANDI**, yukarıdaki "Şerit yön-terimi arızası"
   bölümüne bak: `fit_max_slope:=3.0` ölçülüp **zararlı** çıktı (TAZE %91→%83), çözüm
   `heading_no_flip` oldu ve **varsayılan True**, yani ek bayrak gerekmiyor. Teknik kontrolde
   şerit için yapılacak bir şey yok; kalan kök neden (`serit_v2.pt`'nin bariyer tabanını `lane`
   etiketlemesi) eğitim seti işi, koşu ayarı değil.

**Deploy imajı yeniden derlendi 2026-08-22 14:37.** Image ID `10ea17e7fd02`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.542.557.184 bayt**, SHA-256
`45470c170a726b7125d4d5546588f6c855243a0ba781253266306ac26ea815c0`. Bir önceki tar
`robotaksi_humble_0822_1150.tar` adıyla korundu. İmajın *içinde* doğrulandı: beyinde
`MISSION_END` + `_mission_end_control` + `hedef_creep_m` + komutlu dönüş manevra kapısı +
`_pturn_kalan`; planner'da `hedef_dur_m` + `_send(4, 1)`; `bee1_description` içinde **`gnss_pose`**
ve `can_odom` (`max_dt` ile); AMCL launch'ında `gnss_threshold` 3.0 + `initial_pose_x`;
`models/` içinde `serit_v2.pt` + `zurnazurna.pt`.

⚠️ **Tabela modeli varsayılanı bu imajda `zurnazurna.pt`** (bir takım arkadaşı 22.08 14:25'te
değiştirmiş, `Yasin_Her_Sey.pt` yerine). İmaja koymadan önce sınıf eşlemesi denetlendi:
**24/24 sınıf `canonical_sign_id()` ile doğru eşleşiyor** (`DUR_TT-2`→11, `Kirmizi_Isik`→15,
`Yesil_Isik`→17, `YayaGecidi`→20 dahil), yani 18 Ağustos'ta kapatılan "DUR tabelasında durmama"
hatası geri gelmiyor.

⚠️ **Araçta hâlâ eski imaj koşuyor**: `docker load` + `docker rm -f robotaksi_container` +
`docker run` yapılmadan yeni kod araca ulaşmaz (`docker load` çalışan konteyneri güncellemez).

⚠️ `/home`'da **15 GB** kaldı ve `~/robotaksi_deploy` altında **yedi tar** (~31 GB) birikti.
T7 bağlı değil; bağlanınca eskileri oraya taşıyın.

## `slalom_0822` bag'leri — İLK BAŞARILI PLANNER KOŞUSU (2026-08-22)

Araçta planner + `gnss_pose` ilk kez koştu ve **zincirin tamamı çalıştı**.
`slalom_0822_1157` (169 s, sağlam) `/master`'da sırayla:

    t=115.6s   5,1,70.0     <- kavşakta 70° sol dönüş
    t=130.1s   5,4,1        <- hedef yaklaşması
    t=135.4s   5,4,0        <- hedefte dur

Durum akışı: `LANE_FOLLOW` → 3 kez `OBSTACLE_AVOID` (slalomlar) → `PLANNER_TURN`
(114.9-122.2) → `LANE_FOLLOW` → `MISSION_END` (134.7). Yani slalom, kavşak dönüşü
ve hedefte durma **araçta uçtan uca çalıştı**.

**AÇIK DÖNGÜ DÖNÜŞ KOMUT EDİLEN AÇIYI TESLİM ETMİYOR — ölçüldü ve düzeltildi.**
Odometri yaw'ı dönüş penceresinde:

| t | durum | yaw | Δyaw | steer |
|---|---|---|---|---|
| 115.0 | PLANNER_TURN başladı | +0.4° | — | 73 (tam sol) |
| 117.0 | | +9.8° | +9.4 | 73 |
| 120.0 | toparlama fazı | +37.6° | +37.2 | 50 |
| **122.2** | **LANE_FOLLOW (süre doldu)** | **+46.6°** | **+46.2** | 45 |
| 134.0 | hâlâ dönüyor | +65.4° | +65.0 | 45 |
| 138.0 | MISSION_END, sürünme | +70.4° | +70.0 | 45 |

Yani 7.3 s'lik faz süresi **tamamen doldu** (kesilme yok) ama araç yalnızca
**+46°** döndü; kalan 24 dereceyi şerit takibi 16 saniyede toparladı. Operatörün
"tam sola girip şeride oturtamadı" gözlemi tam olarak bu.
Kök neden ölçüldü: faz 1'in ilk ~2 saniyesinde tekerlek hâlâ tam kilide gidiyor
(yaw hızı 2.3 → 7.1 → 9.6 °/s diye tırmanıyor), yani sabit süre gerçek dönüşün
yarısını kaçırıyor. **Direksiyon hızı (10 birim/s) burada da bağlayıcı kısıt.**

**Düzeltme: `PLANNER_TURN` artık kapalı çevrim.** Fazları YAW bitiriyor, süre
yalnızca tavan (`pturn_max_scale` 2.5×):
- faz 1 (tam kilit) → tahmini dönüş hedefe `pturn_recover_deg` (20°) kalana kadar
- faz 2 (toparlama) → tahmin hedefe `pturn_tol_deg` (2°) kalana kadar
- `tahmin = dönülen + yaw_hızı × pturn_lead_s` — tekerlek merkeze dönerken araç
  dönmeye devam ettiği için ham açıyla bitirmek her dönüşü aşırdı.
- **Yaw beslenmiyorsa eski süre tabanlı yol aynen korunuyor** (regresyon yok).

Ayar masa taramasıyla seçildi; simülatör önce **araç verisine kalibre edildi**
(sahte saatle eski kod 7.3 s / +48° veriyor — bag'deki 7.3 s / +46° ile birebir):

| lead / tol | +40° | +70° | +90° | +110° |
|---|---|---|---|---|
| 1.5 / 5.0 (ilk) | −9.1 | −9.3 | −9.3 | −9.1 |
| **0.8 / 2.0 (seçilen)** | **−3.0** | **−3.1** | **−3.1** | **−3.2** |
| 0.6 / 0.0 (en iyi) | −0.2 | −0.3 | −0.1 | −0.1 |

⚠️ **En iyi satır BİLEREK seçilmedi.** Sönüm modeli tek bag'den kestirildi ve sola
dönüşte **aşmak karşı şeride girmek** demek; **eksik** kalmayı şerit takibi zaten
toparlıyor. Hata her açıda düz (−3°), yani sistematik ve öngörülebilir.

Doğrulandı: 35 maddelik regresyon (hedef yaklaşması + lidar durma tablosu, sürünme,
dönüş-engel etkileşimi ve kesilen dönüşün devamı, kapalı çevrim dönüş 6 açıda),
slalom masa suite **7/8 değişmedi**, düğüm traceback'siz.

⚠️ **`slalom_0822_1203` KULLANILAMAZ — dosyanın yalnızca %29'u var.** `.db3.zstd`
122 MB, bag1'in mesaj/bayt oranına göre beklenen ~423 MB; `zstd -l` "Error while
reading block header" diyor, sqlite şemayı okuyamıyor. Kurtarılan 313 MB koşunun
**başı** (20 kez `OBSTACLE_AVOID` var, `PLANNER_TURN`/`MISSION_END` YOK) — yani
sorulan kavşak bölümü eksik %71'de. **Araçtaki orijinali yeniden kopyalayın**
(`rsync -avP --append-verify`, `scp` koptuğunda baştan başlar).

⚠️ **İKİ BAG'DE DE `/gnss`, `/gnss_pose`, `/filter/*` KAYITLI DEĞİL** — kayıt eski
topic listesiyle alınmış. Bu yüzden "GPS kaydı mı" sorusu bu bag'lerden
**cevaplanamaz**: konum verisi hiç kaydedilmemiş. `TEKNIK_KONTROL_KOSU.md`'deki
kayıt komutu bu dört topic'i içeriyor; bir sonraki koşuda o komut kullanılmalı.
Kayıtlı olsaydı cevaplanabilecek soru: dönüş komutunun ateşlendiği andaki
`/gnss_pose` ile rota düğümü 4'ün (62.4, 12.7) arasındaki mesafe.

Şerit düğümü Taha'nın 2026-08-22 11:07 sürümüyle güncellendi
(`~/carla-ros2-wss-taha-serit-22082026.zip`). Yine **yalnızca `lane_follower_node.py`** alındı
(2344 → 2472 satır, birleştirme sonrası). Alınmayanlar ve sebepleri — hepsi bugünkü işi geri
götürürdü:

| dosya | onunki | neden alınmadı |
|---|---|---|
| `decision_brain.py` | 2239 satır (bizde 2660) | `MISSION_END` 0, `PLANNER_TURN` 0, `hedef_creep_m` 0, `slalom_return_hard` 0 — teknik kontrol hedef-durması, route_planner ve sert-dönüş A/B'si yok |
| `neuravix_control_node_real.py` | 871 (bizde 988) | `slalom_return_hard` 0, `odometry/can_wheel` 0 — bugünkü dört varsayılan yok |
| `neuravix_control_node.py` | 603 (bizde 674) | eski |
| `obstacle_lidar_node.py` | 515 (bizde 522) | eski |
| `tabela_tespit_node.py` | 740 | `zurnazurna.pt` yok (eski model varsayılanı) |
| `models/serit_v2.pt` | — | **birebir aynı** (md5 `649d24df…`), değişmemiş |

⚠️ **`carla-ros2-wss-newlane.zip` (aynı gün 14:36) BOZUK — kullanmayın.** 1,04 GB indi ama
`neuravix_ros2` metni dosyanın **hiçbir yerinde geçmiyor** (0 kez; dosya adları zip'te
sıkıştırılmadan durduğu için bu arama kesindir). Son yerel başlık 71,8 MB'ta ve kalan ~970 MB tek
başına `.vscode/browse.vc.db` (VSCode IntelliSense veritabanı, açılmış hâli 950 MB). Aktarım
yolunda **~1,043 GB'lık bir kesme** var: `bal.zip` 1.043.193.672, `newlane.zip` 1.043.547.229,
`taha-serit` 1.043.576.263 — üçü de aynı tavana dayanmış. `bal` ve `taha` sürümlerinde şerit
dosyası kesme noktasından önce yazıldığı için kurtuldu, `newlane`'de `.vscode` payı yiyip
`src/neuravix_ros2` hiç sıraya gelmedi. **Arşiv gönderilirken `.vscode/`, `build/`, `install/`,
`log/` ve `bee1_map.pcd` dışarıda bırakılmalı** — o zaman paket birkaç MB olur.

Taha'nın eklediği: **beş yeni parametre** (`taraf_kural` varsayılan `"sureklilik"`,
`taraf_bant_px=40`, `taraf_hist_px=0`, `taraf_hist_s=0.5`, `guven_taban=0.4`) — belirsiz bantta
(`|x−ref| < taraf_bant_px`) sol/sağ atamasını sürekliliğe bırakan bir kural, yani 08-20'de S4
diye kaydedilen "yanlış çizgi çifti" sınıfına yönelik.

**Merge'de yeniden uygulanan dördü** (her merge'de tekrar gerekiyor):
`steer_mode` `"pursuit"` → **`"pid"`**, `heading_no_flip`, `cift_paralel` + `cift_paralel_tol`,
ve kapanış düzeltmesi (`ExternalShutdownException`). `src_pts` / `yolo_conf` / `camera_topic`
bu sefer korunmuştu (bizim sürümü temel almış).

Ölçüldü (dört veri seti, `tools/serit_olc.py`) — **regresyon yok, ölçülebilir kazanç da yok**:

| bag | TAZE | steer std | oynaklık | işaret TERS |
|---|---|---|---|---|
| joystick_46 | %91 → %91 | 4.95 → 4.93 | 1.54 → 1.62 | 8 → **0** |
| joystick_47 | %97 → %97 | 3.26 → 3.24 | 1.09 → 1.15 | 17 → **0** |
| joystick_48 | %87 → %87 | 4.32 → 4.58 | 0.57 → 0.58 | 3 → **0** |
| 1526 | %94 → %94 | 2.38 → 2.26 | 1.00 → 1.02 | 69 → **0** |

Birleştirme öncesi sürümle aynı karelerde A/B: `joystick_46` ve `1526`'da sonuçlar **birebir
aynı** (LaneW 468/427, std 15.1/2.2 — hepsi eşit). Yani yeni taraf mantığı bu veri setlerinde
**tetiklenmiyor**; ölü kod DEĞİL (`taraf_kural:=eksen` steer std'yi 2.26 → 2.32 değiştiriyor),
sadece belirsiz bant bu sahnelerde nadiren isabet ediyor. Paralellik kapısı da yine 0 kez
ateşledi. Doğrulandı: kapsamlı derleme, düğüm hem varsayılanla hem tampon komutla traceback'siz
kalkıyor, `serit sinif idx=0` ve `src_pts` ZED trapezi log'da doğru.

⚠️ **Deploy imajı bu merge'den sonra YENİDEN BAYAT** — 11:49 build'i (`7fe692ac1991`) eski şerit
düğümünü taşıyor.

Taha'nın diğer üç değişikliği değerlendirildi (2026-08-22) — **ikisi alındı, biri reddedildi.**

**✅ ALINDI — direksiyon sıfır noktası 2.0 → 3.4 (`steer_target_offset` + `can_odom`'un
`steer_feedback_offset`'i).** Semptom: "araç sürekli hafif sola kayıyor". Eski 2.0,
2026-07-13'te araç **DURURKEN** kilitten kilide okunan sensör orta noktasıydı; aracı düz götüren
değer o değil (teker açıklığı + sensör montajı) ve duran araçta ölçülemez. Yeni değer
**SÜRÜŞTEN**, şerit boru hattından bağımsız: `κ = yaw_rate/hız` (IMU + hız) ile
`FeedbackSteeringAngle` regresyonu, κ'nın sıfırlandığı geri besleme değeri gerçek düzdür.
**Bağımsız olarak yeniden ölçüldü ve Taha'nın sayılarıyla 0.02-0.03 içinde tutuyor:**

| kayıt | bizim ölçüm | Taha |
|---|---|---|
| `slalom_0821_1508` | **+3.54** (r −0.97) | +3.52 |
| `slalom_0821_1515` | **+3.48** (r −0.97) | +3.47 |
| `slalom_0821_1520` | **+3.53** (r −0.98) | +3.54 |

Etkisi: "düz git" komutunda tekerlek gerçek düzün 1.4 birim **soluna** konuyordu → R ≈ 59 m sola
kavis → 20 m yolda ~3.4 m yanal kayma. Yol deveri elendi (çok yönlü harita turlarında değer
yönle değişmiyor) ve ölçüm artefaktı elendi (iki farklı hız kaynağı +3.36 vs +3.37).
⚠️ **DEĞER SABİT DEĞİL**: 18–19 Temmuz arasında ~5 birim kaymış (−2.05 → +2.93). Araç servise
girer / direksiyon sökülür / sensör sıfırlanırsa **yeniden ölçülmeli**. Ölçüm tarifi: `/imu/data`
yaw hızı + herhangi bir hız kaynağı + `/beemobs/FeedbackSteeringAngle`; κ=yaw/hız ile feedback'in
doğrusal regresyonu; hareket eşiği v>0.5 m/s, r>0.9 beklenir. **Duran araçta kilitten kilide
okuma bu değeri VERMEZ** — 2.0 hatası tam oradan geldi.
⚠️ Yan etki: offset 3.4 + `steer_delta ±36` + `ham_limit [−34,38]` ⇒ sol 36, sağ 34.6 birim
(sağda 1.4 birim kırpma). Küçük asimetri; gerekirse `steer_raw_max` 39.4 yapılabilir ama mekanik
limit önce doğrulanmalı.

**✅ ALINDI — viraj tespiti artık EĞRİLİKTEN, şerit açısından değil.** `_note_lane_angle` yolu
**yedek** olarak duruyor (`_curve_kaynak` = `"yaw"` | `"serit"` | `"-"` hangisinin gördüğünü
söyler). Yeni birincil yol `update_motion(yaw=...)` içinde: κ = |yaw_rate|/hız.
`curve_kappa=0.04` ⇔ **R = 25 m**; `curve_min_speed=0.4` m/s altında hesaplanmaz (dururken yaw
gürültüdür); `curve_min_time=0.0` (süreklilik şartı kapalı). `OBSTACLE_AVOID` sırasında
**bilerek bakılmaz ve sayaç sıfırlanır** — slalomda araç zaten kasten dönüyor; sayaç
sıfırlanmazsa weave'den önce başlamış damga manevra bitince anında "viraj" ilan edip sonraki
weave'i bastırıyor. ⚠️ **Bizim `_yaw_rate` DERECE/s tutuyor** (Taha'nınki rad/s) — port ederken
`math.radians()` eklendi.
Doğrulandı: düz yol ve R=67/33 m kavisler viraj sayılmıyor; R=18/11 m viraj sayılıyor (kaynak
`yaw`); slalom içinde ve v<0.4 m/s'de bastırılıyor. **Masa suite'inde beklenmedik kazanç:**
`P2` (5 m aralık, bilinen geometrik sınır) artık **geçiyor** (min 0.86 m) ve `P3`'te şerit dışına
taşma **1.78 → 1.39 m** düştü — eski şerit-açısı EMA'sı bazı durumları yanlış bastırıyormuş.

**❌ ALINMADI — `steering_ctrl -p min_drive:=30.0`.** Bu öneri **Taha'nın kendi CLAUDE.md'sindeki
ölçümle çelişiyor**: `semantik_1` bag'inde PWM 150 (sapma +23) tekerleği **+1.50 birim/s**
döndürüyor, yani `min_drive=22` tekerleği kıpırdatıyor; "ölü bölge yüzünden hareket etmiyor"
hipotezi **ölçümle reddedilmiş ve min_drive değiştirilmemiş** (dosyasının kendi ifadesi). Asıl
olgu takip gecikmesi: aktüatör 1.5–4.4 birim/s, hedef ise 0.10–0.15 s'de bir değişiyor. Bu, bizim
`max_delta` ölçümümüzle de tutarlı (joystick sapma 73 ile aynı hız → doygunluk motorda).
**Koşuda `-p min_drive:=30.0` vermeyin** — etkisi ölçülmemiş ve koşuyu önceki kayıtlarla
kıyaslanamaz kılar.

**Deploy imajı yeniden derlendi 2026-08-22 16:53 ve tar alındı.** Image ID `254eb5e66ce7`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.542.577.664 bayt**, SHA-256
`7d8563cdf91a12ecebca27da7359e8ae7574aae028a36c3e06fc6c431bb1d246`. Bir önceki
`robotaksi_humble_0822_1149.tar` adıyla korundu. İmajın *içinde* doğrulandı:
`steer_target_offset=3.4`, `can_odom`'da `steer_feedback_offset=3.4`, beyinde eğrilik viraj
tespiti (`curve_kappa`/`curve_min_speed`/`_curve_kaynak`), şerit düğümü **2472 satır** (Taha
11:07 + `heading_no_flip=True`, `cift_paralel_tol=0.25`, `steer_mode="pid"`, kapanış düzeltmesi)
ve Taha'nın yeni `taraf_kural="sureklilik"` / `guven_taban=0.4` parametreleri.

🔴 **`/home` KRİTİK: 7,8 GB kaldı** (%97 dolu), `~/robotaksi_deploy` altında **yedi tar ~31 GB**.
Bir sonraki `docker build` yer yetmediği için başarısız olabilir. T7'ye kopyalanan eski tar'lar
hemen silinmeli.

## `tk_0822` bag'leri — teknik kontrol denemesi ölçüldü (2026-08-22)

Beş bag geldi. **İçeriklerinden çıkarılan kimlikleri** (operatörün hatırladığı sıra tutmuyor,
aşağıdakiler ölçüm):

| bag | süre | ne | GNSS izi |
|---|---|---|---|
| `tk_0822_1418` | 315 s | **otonom teknik kontrol #1** | start (16.7,1.0) → hedefe **0.15 m** → durdu (64.29, 24.49) |
| `tk_0822_1424` | 173 s | **otonom teknik kontrol #2** | hedefe **1.69 m** → durdu (66.49, 25.89) |
| `tk_0822_1429` | 25 s | hareketsiz kayıt, start bölgesi (15.9, 3.4). **`metadata.yaml` YOK** | — |
| `tk_0822_1434` | 45 s | manuel; (61,9)'dan node4'ün 3.2 m yanından geçip **(78.8, 14.2)**'ye | kavşakta **sola DÖNMEDİ**, sağa/düz gitti |
| `tk_0822_1436` | 136 s | tam tur: (78.65,18.52) → (−2.52,15.33) park alanı | — |

⚠️ Operatör "3. bag manuel sola dönüş testi, doğru noktada durdu" demişti; **ölçüm bunu
doğrulamıyor** — `1434` kavşakta sola dönmüyor ve hedefe en yakın 12.1 m'den geçiyor. Yani
elimizde "doğru sol dönüş" referansı YOK.

**PLANNER VE GNSS KUSURSUZ ÇALIŞTI — sorun onlarda değil.** Komutlar tasarlanan mesafede ateşledi:

| komut | 1418 | 1424 | tasarım |
|---|---|---|---|
| `5,1,70` (node 4'e) | 5.97 m | 5.96 m | `trigger_dist` 6.0 |
| `5,4,1` (hedefe) | 5.99 m | 5.86 m | `trigger_dist` 6.0 |
| `5,4,0` (hedefe) | 1.99 m | 1.96 m | `hedef_dur_m` 2.0 |

Ve `1418`'de araç hedefin **0.15 m** yanından geçti — yani GNSS→map dönüşümü, datum ve rota
sahada doğrulandı. Kayma yok.

**"Daha yukarıda durdu"nun sebebi: sürünme bütçesi.** `5,4,0` sonrası `MISSION_END` lidar
bariyeri görene kadar sürünüyor; o koşularda duracak bir bariyer olmadığı için bütçe sonuna
kadar sürdü:

| | gerçek kat edilen | durduğu yer | hedefi aşma |
|---|---|---|---|
| 1418 | 4.39 m | (64.29, 24.49) | **2.42 m** |
| 1424 | 5.24 m | (66.49, 25.89) | **4.53 m** |

Bütçe 4.0 m'ydi ama gerçek yol 4.39 / 5.24 m çıktı — odometri kat edilen yolu **%10-31 eksik**
ölçüyor (`can_odom`'un bilinen kusuru).

**Düzeltme — durma kararı konumu bilen tarafa verildi.** Yeni alt komut:

    5,4,2   hedefe EN YAKIN noktadan geçildi -> HEMEN DUR (sürünme yok)

Planner `5,4,0`'dan sonra olayı tüketmiyor; hedefe olan mesafenin en küçüğünü izliyor ve mesafe
`hedef_gecis_pay_m` (0.5) kadar artmaya başlayınca `5,4,2` gönderiyor.

`1418`'in **gerçek GNSS izi** planner'a geri beslenerek ölçüldü:

| | `5,4,2` ateşleme mesafesi |
|---|---|
| hızlandırılmış replay | 1.46 m |
| **gerçek 4 Hz kadans** | **0.81 m** |
| (sahada gerçekte durduğu) | 2.42 m |

⚠️ Hızlandırılmış replay sayısı **şişkin**: planner'ın döngüsü metre başına daha az konum
örneği görüyor, yani "uzaklaşmaya başladı" tespiti gecikiyor. Bu sınıf ölçümde replay mutlaka
gerçek kadansta koşturulmalı. `hedef_creep_m` de 4.0 → **3.0** çekildi (yalnızca yedek tavan artık).

⚠️ **`MISSION_END` terminal kapısı `5,4,2`'yi de engelliyordu** — kapı artık `cmd != 4` diyor:
hedef alt komutları yalnızca durdurur ya da kısıtlar, asla hareket ettirmez. Bu yakalanmasaydı
`5,4,2` sessizce yok sayılacak ve sürünme aynen devam edecekti.

**Şerit tarafı:** `1418` hedefin 0.15 m yanından geçti, `1424` ise 1.69 m sağından (y=21..23
bandında x 65.5..65.9, hedef x=64.02). Yani iki koşu arasındaki fark GNSS değil **şeritteki
yanal konum**. Dönüş sonrası yön ise doğru oturuyor: `1424`'te dönüş bitiminde +66°, sonunda
+79.8° — gereken ~80.2°.

**Dönüş açısı düzeltmesi bu koşularda ZATEN ETKİNDİ** (ilk yazımda "imajda yoktu" demiştim,
yanlıştı). Bag adları saha saatini yansıtmıyor: mesaj epoch'ları koşuların **17:18–17:39**
arasında olduğunu, imajın ise **16:53**'te derlendiğini gösteriyor. Kanıt davranışta da var —
`PLANNER_TURN` süresi `1418`'de **8.6 s**, `1424`'te **9.9 s**; açık döngü sabit 7.3 s olurdu.
Yani kapalı çevrim dönüş sahada çalıştı ve `1424`'te bitiş yönü +79.8° (gereken ~80.2°) çıktı.

⚠️ **Deploy imajı bu oturumun dışında yeniden derlenmiş**: `254eb5e66ce7`, 2026-08-22 16:53,
tar `~/robotaksi_deploy/robotaksi_humble.tar` 4.542.577.664 bayt (16:54). Eski tarların çoğu da
silinmiş (kalan: `robotaksi_humble_0821_1919.tar`). İmaj ile şu anki kaynak arasındaki fark:

| | imaj (16:53) | kaynak | |
|---|---|---|---|
| `pturn_lead_s` / kapalı çevrim dönüş | var | var | aynı |
| `_pturn_kalan` (kesilen dönüş) | var | var | aynı |
| `hedef_creep_m` | **4.0** | **3.0** | farklı |
| `5,4,2` (`arg == 2`) | **yok** | var | farklı |
| `hedef_gecis_pay_m` (planner) | **yok** | var | farklı |

**LİDAR NEDEN DURDURMADI — ölçüldü.** `MISSION_END` süresince ID-4 `front`:

| bag | front (sürünme boyunca) | yan koridorlar |
|---|---|---|
| `1418` | 16.7 → 11.3 → **99** | `right` 1.31 → **0.00** (sağda bariyer) |
| `1424` | **99.00** (tamamen açık) | `left` **0.00** (solda bariyer) |

Yani yolu kapatan bir engel ego koridoruna hiç girmedi; bariyerler aracın **yanındaydı**.
`stop_distance` (2.2 m) altına inen hiçbir okuma yok, bu yüzden araç sürünme bütçesini sonuna
kadar kullandı. Operatörün "bariyerlerin sağından geçti" sezgisi doğru.
**Bu, `5,4,2`'nin gerekçesini kanıtlıyor**: duruşu lidara bırakmak, engelin koridorda olmadığı
her durumda aracı hedefin ötesine taşıyor.

## Komutlu dönüşün ÇIKIŞ hatası — asıl ölçü bu (2026-08-22 akşamı)

`tk_0822` koşuları, dönüş sonrası yanal kaymanın **tamamen** dönüş çıkışındaki yön hatasının
geometrisi olduğunu gösterdi. Şerit kontrolcüsünün katkısı bu mesafelerde ihmal edilebilir:

| | çıkış yön hatası | gidilen yol | tahmin yanal | **ölçülen yanal** | sonuç |
|---|---|---|---|---|---|
| `1418` | −7.5° | 5.0 m | 0.31 m | **0.28 m** | 0.45 → 0.17 m, toparladı |
| `1424` | **−14.7°** | 8.2 m | 1.14 m | **1.05 m** | −0.54 → −1.64 m, toparlayamadı |

Yani araç şeritten kaymıyor — **çapraz duruyor ve çapraz gittiği için kayıyor.**

**Şerit düğümü suçlu DEĞİL, ve kör de değil.** `1424` t=127 overlay'i: `Error: −124px (−1.02m)`,
`path: TAZE` — 1 m saptığını biliyor. Ama çıktısı `Steering: 47`, yani nötrden 2 birim, çünkü
`steer_kp=0.03` bilerek düşük (0.08 kapalı çevrimde aracı pistten çıkarmıştı). Ayrıca hata
teriminin çoğu **yön**den geliyor ve doyuyor (`1418`: `Yon +150` = `heading_max_px` tavanı,
`Yanal +26`), yani kontrolcü aracı şeride **paralel** yapıyor ama merkeze çekmiyor.

**`PLANNER_TURN`'ün şeridi baskılaması da suçlu değil**: iki koşuda da aynıydı, `1418`
toparladı, `1424` toparlamadı.

**`1424` neden iki kat kötü: dönüşe SLALOMUN İÇİNDEN girdi.**
`1418`: `LANE_FOLLOW@74s` → 17 s şerit takibi → `PLANNER_TURN@91s`.
`1424`: `OBSTACLE_AVOID@89s` → **doğrudan** → `PLANNER_TURN@110s`.
Öngörü terimi `_yaw_rate` EMA'sını kullanıyor ve EMA durumlar arasında taşınıyor; weave'den
çıkarken yaw hızı yüksek okunuyor, "nasılsa daha çok döneceğim" denip faz erken bitiyor.

**Uygulanan düzeltme: `pturn_lead_s` 0.8 → 0.4, `pturn_tol_deg` 2.0 → 0.0.**
Önceki değerler **oturan** açıya göre seçilmişti; oysa çaprazlığı belirleyen **çıkış** anındaki
hata (şerit takibi o anda devralıyor). Masa taraması, çıkış hatası / oturan hata:

| lead / tol | çıkış | oturan |
|---|---|---|
| 0.8 / 2.0 (eski) | −5.5° | −3.1° |
| **0.4 / 0.0 (yeni)** | **−1.7°** | **+0.8°** |
| 0.0 / 0.0 | +0.1° | +2.5° |

Hata açıdan bağımsız (40°..110° arasında −1.6..−1.8). lead→0 gidildikçe çıkış düzeliyor ama
oturan hata aşmaya (+) kayıyor; 0.4/0.0 ikisini de küçük tutuyor ve çıkıştaki artık hâlâ
"eksik" tarafta.

⚠️ **Model mutlak değeri EKSİK tahmin ediyor**: aynı ayarda model −5.5° derken araçta −7.5° ve
−14.7° ölçüldü. Yön güvenilir, sayı **sahada doğrulanmalı**. Bir sonraki koşuda bakılacak tek
ölçü: `PLANNER_TURN` bittiği andaki yön hatası. **<5°** olursa 8 m'de yanal kayma 0.7 m'nin
altında kalır ve `1424`'teki 1.05 m tekrar etmez.

Bir sonraki adım olarak "dönüşten sonra ayrı hizalama fazı" (B) **bilerek ertelendi** — A'nın
saha sonucu görülmeden yeni faz eklemek, bu dosyanın üç kez kaydettiği hatanın aynısı olur.

**Deploy imajı yeniden derlendi 2026-08-22 19:28.** Image ID `2ef1bd329ca3`, tar
`~/robotaksi_deploy/robotaksi_humble.tar` **4.542.582.272 bayt**, SHA-256
`86b7bab22b1c9464fa351405b162c594486f5bd0ef6d139c4b90c74a2c7b9ef6`. Bir önceki
(16:53 build'i, başka oturumda derlenmişti) `robotaksi_humble_0822_1653.tar` adıyla korundu.
İmajın *içinde* doğrulandı: `pturn_lead_s=0.4`, `pturn_tol_deg=0.0`, `hedef_creep_m=3.0`,
beyinde `arg == 2` (`5,4,2`), planner'da `hedef_gecis_pay`, `bee1_description` içinde `gnss_pose`.

Doğrulama: 35 maddelik regresyon 35/35, `5,4,2` testi 8/8, dönüş açı taraması 6 açıda |hata|<1°,
yaw yokken yedek yol korunuyor (7.3 s), slalom masa suite 7/8 (değişmedi).
