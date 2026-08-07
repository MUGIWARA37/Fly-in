import tkinter as tk
import math
from typing import List
from src.model.graph import Graph
from collections import defaultdict


def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2


class Visualizer:
    def __init__(self, graph: Graph, turns: List[str]):
        self.graph = graph
        self.turns = turns
        self.current_turn = -1

        self.root = tk.Tk()
        self.root.title("FLY-IN: NEON PROTOCOL")

        # Maximize window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        try:
            self.root.attributes('-zoomed', True)
        except tk.TclError:
            self.root.state('zoomed')

        # Elegant "Midnight Slate & Emerald" Palette
        self.bg_color = "#0B1120"        # Very dark elegant blue (slate-950)
        self.sidebar_bg = "#0F172A"      # Slate-900
        self.text_color = "#F8FAFC"      # Clean white (slate-50)
        self.text_muted = "#94A3B8"      # Muted gray (slate-400)
        self.accent_color = "#3B82F6"    # Electric Blue

        self.conn_color = "#334155"      # Subtle line color
        self.zone_normal = "#3B82F6"     # Blue nodes
        self.zone_blocked = "#64748B"    # Gray blocked
        self.zone_restricted = "#EC4899"  # Hot Pink restricted
        self.drone_color = "#10B981"     # Brilliant Emerald Green for drones

        # Fonts
        self.font_title = ("Helvetica", 20, "bold")
        self.font_turn = ("Helvetica", 36, "bold")
        self.font_small = ("Helvetica", 9)

        # Layout
        self.sidebar = tk.Frame(self.root, width=350, bg=self.sidebar_bg)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_frame = tk.Frame(self.root, bg=self.bg_color)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=self.bg_color,
            highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Sidebar UI
        tk.Label(
            self.sidebar,
            text="NEON ROUTING LOGIC",
            font=self.font_title,
            bg=self.sidebar_bg,
            fg=self.text_color).pack(
            pady=(
                40,
                20))

        self.lbl_turn = tk.Label(
            self.sidebar,
            text="TURN 00",
            font=self.font_turn,
            bg=self.sidebar_bg,
            fg=self.text_color)
        self.lbl_turn.pack(pady=20)

        def create_button(text, command, primary=False):
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=(
                    "Helvetica",
                    12,
                    "bold"),
                command=command,
                relief=tk.FLAT,
                bg=self.text_color if primary else "#303C4B",
                fg=self.bg_color if primary else self.text_color,
                activebackground=self.accent_color,
                activeforeground=self.bg_color,
                cursor="hand2",
                pady=12)
            btn.pack(fill=tk.X, padx=30, pady=10)
            return btn

        self.btn_auto = create_button(
            "▶ INITIATE SEQUENCE",
            self.toggle_auto_play,
            primary=True)
        self.btn_next = create_button("-> STEP FORWARD", self.next_turn)
        self.btn_retry = create_button("↺ REBOOT SYSTEM", self.retry)

        # Map configuration
        self.min_x = min(z.x for z in graph.zones.values())
        max_x = max(z.x for z in graph.zones.values())
        self.min_y = min(z.y for z in graph.zones.values())
        max_y = max(z.y for z in graph.zones.values())
        self.graph_w = max_x - self.min_x
        self.graph_h = max_y - self.min_y

        # State
        self.drone_positions = {}
        self.drone_angles = {}
        self.target_positions = {}
        self.drone_shapes = defaultdict(list)
        self.is_auto_playing = False

        self.root.update()
        self.retry()
        self.canvas.bind("<Configure>", lambda e: self.draw_graph())

    def get_coords(self, x: float, y: float):
        canvas_w = self.canvas.winfo_width() or (self.root.winfo_screenwidth() - 350)
        canvas_h = self.canvas.winfo_height() or self.root.winfo_screenheight()

        scale = min(canvas_w / (self.graph_w + 2), canvas_h / (self.graph_h + 2)
                    ) if (self.graph_w > 0 or self.graph_h > 0) else 50
        scale *= 0.85
        offset_x = (canvas_w - (self.graph_w * scale)) / 2
        offset_y = (canvas_h - (self.graph_h * scale)) / 2

        return offset_x + (x - self.min_x) * \
            scale, offset_y + (y - self.min_y) * scale

    def draw_graph(self):
        self.canvas.delete("graph")

        # Background subtle stars/dots for cyberpunk feel
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        for x in range(0, w, 60):
            for y in range(0, h, 60):
                self.canvas.create_oval(
                    x, y, x + 1, y + 1, fill="#1F2833", outline="", tags="graph")

        # Connections
        for conn in self.graph.connections:
            x1, y1 = self.get_coords(conn.zone_a.x, conn.zone_a.y)
            x2, y2 = self.get_coords(conn.zone_b.x, conn.zone_b.y)
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self.conn_color,
                width=6,
                tags="graph",
                capstyle=tk.ROUND,
                smooth=True)
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#303C4B",
                width=2,
                tags="graph",
                capstyle=tk.ROUND,
                smooth=True)

        # Zones
        for name, zone in self.graph.zones.items():
            x, y = self.get_coords(zone.x, zone.y)

            if zone.zone_type == "blocked":
                color = self.zone_blocked
            elif zone.zone_type == "restricted":
                color = self.zone_restricted
            else:
                color = self.zone_normal

            try:
                # Glowing outer ring
                self.canvas.create_oval(
                    x - 24,
                    y - 24,
                    x + 24,
                    y + 24,
                    outline=color,
                    width=2,
                    tags="graph")
                # Solid inner core
                self.canvas.create_oval(
                    x - 10,
                    y - 10,
                    x + 10,
                    y + 10,
                    fill=color,
                    outline="",
                    tags="graph")
            except tk.TclError:
                self.canvas.create_oval(
                    x - 24,
                    y - 24,
                    x + 24,
                    y + 24,
                    outline=self.text_color,
                    width=2,
                    tags="graph")

            self.canvas.create_text(
                x,
                y - 35,
                text=name.upper(),
                fill=self.text_muted,
                font=self.font_small,
                tags="graph")

    def draw_drone(self, d_id, cx, cy, angle):
        shapes = []
        size = 18

        # Dart shape logic
        px1 = cx + math.cos(angle) * size
        py1 = cy + math.sin(angle) * size

        px2 = cx + math.cos(angle + 2.5) * size
        py2 = cy + math.sin(angle + 2.5) * size

        px3 = cx + math.cos(angle + math.pi) * (size * 0.4)
        py3 = cy + math.sin(angle + math.pi) * (size * 0.4)

        px4 = cx + math.cos(angle - 2.5) * size
        py4 = cy + math.sin(angle - 2.5) * size

        # Draw dart body
        shapes.append(
            self.canvas.create_polygon(
                px1,
                py1,
                px2,
                py2,
                px3,
                py3,
                px4,
                py4,
                fill=self.drone_color,
                outline=self.bg_color,
                width=1))
        # Draw ID text
        shapes.append(
            self.canvas.create_text(
                cx,
                cy - 20,
                text=d_id,
                fill=self.text_color,
                font=(
                    "Helvetica",
                    8,
                    "bold")))

        self.drone_shapes[d_id] = shapes

    def draw_drones(self):
        for shapes in self.drone_shapes.values():
            for shape in shapes:
                self.canvas.delete(shape)
        self.drone_shapes.clear()

        pos_counts = defaultdict(list)
        for d_id, (x, y) in self.drone_positions.items():
            pos_counts[(round(x, 2), round(y, 2))].append(d_id)

        for (x, y), drones in pos_counts.items():
            base_cx, base_cy = self.get_coords(x, y)
            for i, d_id in enumerate(drones):
                offset_x = (i % 3) * 15 - 15 if len(drones) > 1 else 0
                offset_y = (i // 3) * 15 - 15 if len(drones) > 1 else 0
                angle = self.drone_angles.get(
                    d_id, -math.pi / 2)  # Default pointing up
                self.draw_drone(
                    d_id,
                    base_cx +
                    offset_x,
                    base_cy +
                    offset_y,
                    angle)

    def retry(self):
        self.is_auto_playing = False
        self.current_turn = -1
        self.lbl_turn.config(text="TURN 00")
        self.btn_auto.config(
            text="▶ INITIATE SEQUENCE",
            bg=self.text_color,
            fg=self.bg_color)
        self.btn_next.config(state=tk.NORMAL)

        start_zone = self.graph.get_zone(self.graph.start_hub)
        for i in range(1, self.graph.nb_drones + 1):
            self.drone_positions[f"D{i}"] = (start_zone.x, start_zone.y)
            self.target_positions[f"D{i}"] = (start_zone.x, start_zone.y)
            self.drone_angles[f"D{i}"] = -math.pi / 2  # Pointing UP

        self.draw_drones()
        self.draw_graph()

    def animate_step(self, frame, total_frames, start_positions):
        for d_id in self.drone_positions:
            start_x, start_y = start_positions[d_id]
            target_x, target_y = self.target_positions[d_id]

            progress = frame / total_frames
            eased_progress = ease_in_out_cubic(progress)

            curr_x = start_x + (target_x - start_x) * eased_progress
            curr_y = start_y + (target_y - start_y) * eased_progress
            self.drone_positions[d_id] = (curr_x, curr_y)

        self.draw_drones()

        if frame < total_frames:
            self.root.after(
                30,
                lambda: self.animate_step(
                    frame + 1,
                    total_frames,
                    start_positions))
        else:
            self.btn_next.config(state=tk.NORMAL)
            if self.is_auto_playing:
                # 10ms for smooth continuous transit
                self.root.after(10, self.next_turn)

    def next_turn(self):
        if self.current_turn + 1 >= len(self.turns):
            self.lbl_turn.config(text="DONE")
            self.is_auto_playing = False
            self.btn_auto.config(
                text="▶ INITIATE SEQUENCE",
                bg=self.text_color,
                fg=self.bg_color)
            return

        self.btn_next.config(state=tk.DISABLED)
        self.current_turn += 1
        self.lbl_turn.config(text=f"TURN {self.current_turn + 1:02d}")

        turn_str = self.turns[self.current_turn]
        movements = turn_str.split()
        start_positions = dict(self.drone_positions)

        for move in movements:
            parts = move.split("-")
            d_id = parts[0]
            if len(parts) == 2:
                zone = self.graph.get_zone(parts[1])
                self.target_positions[d_id] = (zone.x, zone.y)
            elif len(parts) == 3:
                # Target is instantly the destination!
                # This bypasses the midpoint entirely so they never look stuck
                # in the connection!
                z2 = self.graph.get_zone(parts[2])
                self.target_positions[d_id] = (z2.x, z2.y)

            # Update rotation angle based on movement direction
            sx, sy = start_positions[d_id]
            tx, ty = self.target_positions[d_id]
            if sx != tx or sy != ty:
                self.drone_angles[d_id] = math.atan2(ty - sy, tx - sx)

        # By bypassing the midpoint completely and animating straight to the destination over the duration,
        # we ensure they NEVER wait in the connection!
        self.animate_step(1, 20, start_positions)

    def toggle_auto_play(self):
        self.is_auto_playing = not self.is_auto_playing
        if self.is_auto_playing:
            self.btn_auto.config(
                text="⏸ HALT SEQUENCE",
                bg="#FF007A",
                fg="#FFFFFF")
            self.next_turn()
        else:
            self.btn_auto.config(
                text="▶ INITIATE SEQUENCE",
                bg=self.text_color,
                fg=self.bg_color)

    def start(self):
        self.root.mainloop()
