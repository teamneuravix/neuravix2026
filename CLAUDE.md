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
  package needed. `ROS_DOMAIN_ID` must also match on both sides. Vehicle wifi: SSID `robotaxi_1`/`robotaxi_2`,
  password `robotaxi`, fixed IP `192.168.30.100`/`192.168.10.100`, SSH/SFTP user `smart`.
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
| 3 (`ID_SIGN`) | `tabela_tespit_node.py` | `id, sign_class, distance, cx, cy, w, h` (bbox center + size in pixels; `distance` is a rough bbox-height estimate with an uncalibrated constant. Sign/light class ids in `decision_brain.py`, e.g. `DUR`, `KIRMIZI_ISIK`, `SOLA_DON`. **Event-based**: published only per confirmed detection — no sign in view ⇒ no ID-3 traffic, unlike lane (every frame) and obstacle (10 Hz)) |
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
2026-07-21 14:26, which is what the workspace uses). Also note `obstacle_lidar`'s `lidar_topic` default
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
(`SIGN_NAMES` dict) — cross-reference this when changing detector output classes, since the class-id
contract between `tabela_tespit_node.py`'s YOLO model and the FSM is implicit (positional int, not a
shared enum/message).

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
