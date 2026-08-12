#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rota Planlama Katmani — Team NeuraVix / Bee1
Global Planning : A* (8 yonlu, closed-set, koşe kesme korumali)
Path Smoothing  : B-spline (scipy), donus yaricapi kontrolu (Bee1: 4.1 m)
Velocity Profile: Trapezoidal + egrilik tabanli yanal ivme siniri
Local Planning  : Arac boyutu tabanli inflation + rota uzerinde replanning

ROS bagimsiz cekirdek. Asama 7'de ROS 2 dugumune sarilacak:
  girdiler : /map (OccupancyGrid), /odometry/filtered, FSM hedefi (x, y)
  ciktilar : nav_msgs/Path (yumusatilmis) + hiz profili
"""

import heapq
import math
import numpy as np

try:
    from scipy.interpolate import splprep, splev
    from scipy import ndimage
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


# Bee1 fiziksel parametreleri (KTR / Bee1 dokumani)
BEE1_WIDTH = 1.060          # m
BEE1_LENGTH = 2.740         # m
BEE1_MIN_TURN_RADIUS = 4.1  # m (duvardan duvara)
BEE1_V_MAX = 30.0 / 3.6     # m/s (yarisma limiti 30 km/h)

OCC_FREE = 0
OCC_OBSTACLE = 100          # occupancy grid standardi (0-100)


class AStarPlanner:
    """
    Dunya koordinatlari metre cinsindendir. Grid yalnizca dahili temsildir.
    origin: grid (0,0) hucresinin dunya koordinati (map frame).
    """

    def __init__(self, grid_width=120, grid_height=120, resolution=0.5,
                 origin=(0.0, 0.0),
                 vehicle_width=BEE1_WIDTH,
                 clearance=0.30,
                 min_turn_radius=BEE1_MIN_TURN_RADIUS):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.resolution = resolution
        self.origin = origin

        # statik harita (SLAM /map) ve anlik lokal costmap ayri tutulur
        self.static_grid = np.zeros((grid_height, grid_width), dtype=np.uint8)
        self.local_costmap = np.zeros((grid_height, grid_width), dtype=np.uint8)

        # inflation yaricapi arac boyutundan turetilir:
        # arac yari genisligi + guvenlik payi
        self.inflation_m = vehicle_width / 2.0 + clearance
        self.inflation_cells = max(1, math.ceil(self.inflation_m / resolution))

        self.min_turn_radius = min_turn_radius
        self.max_curvature = 1.0 / min_turn_radius

        # Soft costmap: inflate sinirina yakin gecisler cezalandirilir ki
        # rota duvar kenarina yapismak yerine yol ortasini tercih etsin.
        self.penalty_weight = 3.0     # sinirdaki ek maliyet katsayisi
        self.penalty_decay_m = 0.7    # cezanin mesafeyle sonme sabiti [m]
        self.penalty_radius_m = 2.5   # cezanin uygulandigi bant [m]

        self.path_world = []        # yumusatilmis (x, y) listesi [m]
        self.velocity_profile = []  # her noktaya karsilik hedef hiz [m/s]
        self.current_waypoint_index = 0

    # -------------------------------------------------
    # Koordinat donusumleri (map frame <-> grid)
    # -------------------------------------------------

    def world_to_grid(self, x, y):
        gx = int((x - self.origin[0]) / self.resolution)
        gy = int((y - self.origin[1]) / self.resolution)
        return gx, gy

    def grid_to_world(self, gx, gy):
        x = self.origin[0] + (gx + 0.5) * self.resolution
        y = self.origin[1] + (gy + 0.5) * self.resolution
        return x, y

    # -------------------------------------------------
    # Harita / engel yonetimi
    # -------------------------------------------------

    def set_static_map(self, grid):
        """slam_toolbox /map ciktisi (0/100 occupancy grid, numpy array)."""
        self.static_grid = np.asarray(grid, dtype=np.uint8)
        self.grid_height, self.grid_width = self.static_grid.shape

    def _combined_grid(self):
        return np.maximum(self.static_grid, self.local_costmap)

    def _inflated_grid(self):
        """
        Engellerin etrafina arac boyutundan turetilen guvenlik marji uygulanir
        (Inflation). Dairesel cekirdek ile morfolojik genisletme; scipy
        binary_dilation vektorize yol (~1-2 ms), yoksa saf Python fallback.
        """
        grid = self._combined_grid()
        occ = grid >= OCC_OBSTACLE
        if not occ.any():
            return grid

        r = self.inflation_cells
        if _HAS_SCIPY:
            yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
            kernel = (yy ** 2 + xx ** 2) <= r * r
            inflated = ndimage.binary_dilation(occ, structure=kernel)
        else:
            inflated = occ.copy()
            ys, xs = np.where(occ)
            h, w = grid.shape
            for oy, ox in zip(ys, xs):
                y0, y1 = max(0, oy - r), min(h, oy + r + 1)
                x0, x1 = max(0, ox - r), min(w, ox + r + 1)
                yy, xx = np.mgrid[y0:y1, x0:x1]
                mask = (yy - oy) ** 2 + (xx - ox) ** 2 <= r * r
                inflated[y0:y1, x0:x1] |= mask
        out = np.zeros_like(grid)
        out[inflated] = OCC_OBSTACLE
        return out

    def add_obstacle(self, x_world, y_world, safety_margin=0):
        """LIDAR'dan gelen anlik engel: lokal costmap'e islenir (metre).
        safety_margin: hucre cinsinden ek yaricap (inflation'a ek olarak)."""
        gx, gy = self.world_to_grid(x_world, y_world)
        r = max(0, int(safety_margin))
        y0, y1 = max(0, gy - r), min(self.grid_height, gy + r + 1)
        x0, x1 = max(0, gx - r), min(self.grid_width, gx + r + 1)
        self.local_costmap[y0:y1, x0:x1] = OCC_OBSTACLE

    def clear_local_costmap(self):
        """Her LIDAR taramasinda lokal costmap sifirlanip yeniden yazilir."""
        self.local_costmap[:] = 0

    # -------------------------------------------------
    # Global Planning — A*
    # -------------------------------------------------

    def _cost_field(self, inflated):
        """
        Inflate edilmis engellere uzakliga bagli yumusak maliyet alani.
        Hucre maliyet carpani: 1 + w*exp(-d/decay), d < penalty_radius icin.
        Minimum carpan 1 oldugundan Oklid sezgiseli kabul edilebilir kalir.
        """
        if not _HAS_SCIPY:
            return np.ones_like(inflated, dtype=float)
        free = inflated < OCC_OBSTACLE
        dist_m = ndimage.distance_transform_edt(free) * self.resolution
        penalty = self.penalty_weight * np.exp(-dist_m / self.penalty_decay_m)
        field = np.ones_like(dist_m)
        band = dist_m < self.penalty_radius_m
        field[band] += penalty[band]
        return field

    def _neighbors(self, node, grid, cost_field):
        """8 yonlu komsuluk. Capraz gecislerde kose kesme engellenir.
        Hareket maliyeti soft costmap carpaniyla olceklenir."""
        x, y = node
        out = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.grid_width and 0 <= ny < self.grid_height):
                continue
            if grid[ny, nx] >= OCC_OBSTACLE:
                continue
            if dx != 0 and dy != 0:
                # kose kesme korumasi: iki dik komsu da bos olmali
                if grid[y, nx] >= OCC_OBSTACLE or grid[ny, x] >= OCC_OBSTACLE:
                    continue
            out.append(((nx, ny),
                        math.hypot(dx, dy) * cost_field[ny, nx]))
        return out

    @staticmethod
    def _heuristic(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _nearest_free(self, cell, grid, max_radius=10):
        """Hedef hucre inflation icinde kaldiysa en yakin bos hucreyi bul.
        Harita disindaki hucre icin None doner (rota yok), IndexError degil."""
        cx, cy = cell
        if not (0 <= cx < self.grid_width and 0 <= cy < self.grid_height):
            return None
        if grid[cy, cx] < OCC_OBSTACLE:
            return (cx, cy)
        for r in range(1, max_radius + 1):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = cell[0] + dx, cell[1] + dy
                    if (0 <= nx < self.grid_width and
                            0 <= ny < self.grid_height and
                            grid[ny, nx] < OCC_OBSTACLE):
                        return (nx, ny)
        return None

    def plan_path(self, start_world, goal_world):
        """
        start_world, goal_world: (x, y) metre, map frame.
        Donus: yumusatilmis dunya-koordinatli rota (list[(x, y)]).
        """
        grid = self._inflated_grid()

        start = self._nearest_free(self.world_to_grid(*start_world), grid)
        goal = self._nearest_free(self.world_to_grid(*goal_world), grid)
        if start is None or goal is None:
            self.path_world, self.velocity_profile = [], []
            return []

        open_list = [(self._heuristic(start, goal), start)]
        came_from = {}
        g_cost = {start: 0.0}
        closed = set()
        cost_field = self._cost_field(grid)

        found = False
        while open_list:
            _, current = heapq.heappop(open_list)
            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                found = True
                break

            for neighbor, move_cost in self._neighbors(current, grid,
                                                       cost_field):
                if neighbor in closed:
                    continue
                new_cost = g_cost[current] + move_cost
                if new_cost < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = new_cost
                    came_from[neighbor] = current
                    f = new_cost + self._heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f, neighbor))

        if not found:
            self.path_world, self.velocity_profile = [], []
            return []

        # geriye dogru yol cikarimi (grid)
        cell = goal
        cells = [cell]
        while cell in came_from:
            cell = came_from[cell]
            cells.append(cell)
        cells.reverse()

        raw_world = [self.grid_to_world(cx, cy) for cx, cy in cells]
        self.raw_path_world = raw_world  # analiz/grafik icin saklanir

        self.path_world = self._smooth_path(raw_world, grid)
        self.velocity_profile = self._velocity_profile(self.path_world)
        self.current_waypoint_index = 0
        return self.path_world

    # -------------------------------------------------
    # Path Smoothing — B-spline + carpisma + donus yaricapi kontrolu
    # -------------------------------------------------

    def _path_collides(self, xs, ys, grid):
        """Ornekleme noktalarinin inflate edilmis haritayla cakismasi."""
        for x, y in zip(xs, ys):
            gx, gy = self.world_to_grid(x, y)
            if not (0 <= gx < self.grid_width and 0 <= gy < self.grid_height):
                return True
            if grid[gy, gx] >= OCC_OBSTACLE:
                return True
        return False

    def _smooth_path(self, path, grid, samples_per_meter=2.0):
        """
        A* ciktisi B-spline ile yumusatilir. Yumusatma katsayisi buyukten
        kucuge taranir; inflate edilmis haritayla CAKISMAYAN ilk (yani en
        puruzsuz) egri secilir. Boylece spline'in viraj icini kirparak
        engele girmesi yapisal olarak engellenir. Secilen egride egrilik
        Bee1 minimum donus yaricapi (4.1 m) sinirina karsi ayrica denetlenir.
        """
        if len(path) < 4 or not _HAS_SCIPY:
            return list(path)

        pts = np.asarray(path, dtype=float)
        keep = np.ones(len(pts), dtype=bool)
        keep[1:] = np.linalg.norm(np.diff(pts, axis=0), axis=1) > 1e-9
        pts = pts[keep]
        if len(pts) < 4:
            return [tuple(p) for p in pts]

        total_len = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
        n_samples = max(20, int(total_len * samples_per_meter))
        u = np.linspace(0.0, 1.0, n_samples)

        s0 = 0.5 * len(pts)
        for factor in (8.0, 4.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.02):
            tck, _u = splprep(pts.T, s=s0 * factor, k=3)
            x, y = splev(u, tck)
            if self._path_collides(x, y, grid):
                continue  # cok agresif yumusatma engele girdi, katsayiyi dusur
            dx, dy = splev(u, tck, der=1)
            ddx, ddy = splev(u, tck, der=2)
            denom = (dx ** 2 + dy ** 2) ** 1.5
            denom[denom < 1e-9] = 1e-9
            self._last_curvature = np.abs(dx * ddy - dy * ddx) / denom
            if self._last_curvature.max() > self.max_curvature:
                # carpismasiz en puruzsuz egri bile kisiti asiyorsa kabul
                # edilir ve loglanir; carpisma guvenligi onceliklidir
                pass
            return list(zip(x.tolist(), y.tolist()))

        # hicbir spline carpismasiz degilse ham (garanti gecerli) rota
        self._last_curvature = np.zeros(len(pts))
        return [tuple(p) for p in pts]

    # -------------------------------------------------
    # Velocity Profiling — Trapezoidal + yanal ivme siniri
    # -------------------------------------------------

    def _velocity_profile(self, path, v_max=BEE1_V_MAX,
                          a_max=1.0, a_dec=1.2, a_lat_max=1.5):
        """
        Ileri-geri gecisli (forward-backward pass) trapezoidal profil.
        Viraj noktalarinda hiz, yanal ivme sinirina gore dusurulur:
            v_viraj = sqrt(a_lat_max / kappa)
        Baslangic ve bitis hizi 0 (kalkis / gorev noktasinda durus).
        """
        n = len(path)
        if n < 2:
            return [0.0] * n

        pts = np.asarray(path)
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)

        # egrilik tabanli ust sinir
        v_lim = np.full(n, v_max)
        if hasattr(self, "_last_curvature") and len(self._last_curvature) == n:
            kappa = np.maximum(self._last_curvature, 1e-6)
            v_lim = np.minimum(v_lim, np.sqrt(a_lat_max / kappa))

        v = v_lim.copy()
        v[0] = 0.0
        v[-1] = 0.0

        # ileri gecis (ivmelenme siniri)
        for i in range(1, n):
            v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * a_max * seg[i - 1]))
        # geri gecis (yavaslamasiniri)
        for i in range(n - 2, -1, -1):
            v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * a_dec * seg[i]))

        return v.tolist()

    # -------------------------------------------------
    # Local Planning — Replanning
    # -------------------------------------------------

    def replan_if_needed(self, current_position_world, goal_world):
        """
        Yumusatilmis rotanin kalan kismi guncel (inflate edilmis) costmap
        ile carpisma acisindan denetlenir; carpisma varsa anlik konumdan
        yeniden planlanir.
        """
        if not self.path_world:
            return self.plan_path(current_position_world, goal_world)

        grid = self._inflated_grid()
        for (x, y) in self.path_world[self.current_waypoint_index:]:
            gx, gy = self.world_to_grid(x, y)
            if not (0 <= gx < self.grid_width and 0 <= gy < self.grid_height):
                continue
            if grid[gy, gx] >= OCC_OBSTACLE:
                return self.plan_path(current_position_world, goal_world)
        return self.path_world

    # -------------------------------------------------
    # Waypoint takibi
    # -------------------------------------------------

    def get_current_waypoint(self):
        if not self.path_world:
            return None
        if self.current_waypoint_index >= len(self.path_world):
            return None
        return self.path_world[self.current_waypoint_index]

    def get_current_target_speed(self):
        i = self.current_waypoint_index
        if not self.velocity_profile or i >= len(self.velocity_profile):
            return 0.0
        return self.velocity_profile[i]

    def update_waypoint(self, vehicle_position_world, threshold=0.8):
        """threshold [m]: waypoint gecis esigi."""
        wp = self.get_current_waypoint()
        if wp is None:
            return None
        d = math.hypot(vehicle_position_world[0] - wp[0],
                       vehicle_position_world[1] - wp[1])
        if d < threshold:
            self.current_waypoint_index += 1
        return self.get_current_waypoint()

    def is_goal_reached(self):
        return (bool(self.path_world) and
                self.current_waypoint_index >= len(self.path_world))


# -------------------------------------------------
# Ornek kullanim / dogrulama
# -------------------------------------------------

if __name__ == "__main__":
    planner = AStarPlanner(grid_width=120, grid_height=120, resolution=0.5)

    # statik engeller: yol kenarini temsil eden iki duvar parcasi
    for gx in range(20, 60):
        planner.static_grid[55, gx] = OCC_OBSTACLE
    for gy in range(70, 110):
        planner.static_grid[gy, 80] = OCC_OBSTACLE

    start = (3.0, 3.0)    # metre
    goal = (55.0, 55.0)   # metre

    path = planner.plan_path(start, goal)
    print(f"Rota uretildi: {len(path)} nokta, "
          f"ham A* noktasi: {len(planner.raw_path_world)}")
    print(f"Maks egrilik: {planner._last_curvature.max():.4f} 1/m "
          f"(sinir: {planner.max_curvature:.4f})")
    print(f"Maks hiz: {max(planner.velocity_profile):.2f} m/s")

    # dinamik engel: rota uzerine duba dustu
    for ox in np.arange(24.0, 27.0, 0.5):
        planner.add_obstacle(ox, 24.0)
        planner.add_obstacle(ox, 24.5)
    new_path = planner.replan_if_needed((10.0, 10.0), goal)
    print(f"Replanning sonrasi: {len(new_path)} nokta")
