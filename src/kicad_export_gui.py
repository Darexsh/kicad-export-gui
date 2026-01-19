import os
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from render_command import build_cmd_exe_command, build_kicad_cli_command
from ui_constants import (
    APP_BG,
    BACKGROUND_OPTIONS,
    BUTTON_BG,
    BUTTON_HOVER,
    BUTTON_TEXT,
    CARD_BG,
    KICAD_CMD_DEFAULT,
    LISTBOX_SELECT,
    PRESET_OPTIONS,
    PROGRESS_BORDER,
    PROGRESS_GREEN,
    PROGRESS_GREEN_DARK,
    QUALITY_OPTIONS,
    RESOLUTION_MAP,
    RESOLUTION_OPTIONS,
    SIDE_OPTIONS,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from ui_helpers import bind_mousewheel


class KiCadExportGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KiCad Export Studio")
        self.geometry("860x600")
        self.resizable(False, False)

        self.board_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.resolution_var = tk.StringVar(value=RESOLUTION_OPTIONS[1])
        self.side_var = tk.StringVar(value="top + bottom")
        self.background_var = tk.StringVar(value="transparent")
        self.quality_var = tk.StringVar(value="high")
        self.preset_var = tk.StringVar(value="")
        self.floor_var = tk.BooleanVar(value=False)
        self.perspective_var = tk.BooleanVar(value=False)
        self.zoom_var = tk.StringVar()
        self.pan_var = tk.StringVar()
        self.pivot_var = tk.StringVar()
        self.rotate_var = tk.StringVar()
        self.light_top_var = tk.StringVar()
        self.light_bottom_var = tk.StringVar()
        self.light_side_var = tk.StringVar()
        self.light_camera_var = tk.StringVar()
        self.light_side_elevation_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")
        self.show_log_var = tk.BooleanVar(value=False)
        self.show_advanced_var = tk.BooleanVar(value=False)
        self.log_queue = queue.Queue()
        self.render_in_progress = False

        self._configure_style()
        self._build_ui()
        self._poll_log_queue()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        self.configure(bg=APP_BG)
        style.configure(
            "App.TFrame",
            background=APP_BG,
        )
        style.configure(
            "Card.TFrame",
            background=CARD_BG,
            relief="flat",
        )
        style.configure(
            "Header.TLabel",
            background=APP_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Sub.TLabel",
            background=APP_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardSub.TLabel",
            background=CARD_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Hint.TLabel",
            background=CARD_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Label.TLabel",
            background=CARD_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "HeaderCard.TLabel",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=APP_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TButton",
            background=BUTTON_BG,
            foreground=BUTTON_TEXT,
            padding=(10, 6),
        )
        style.configure(
            "TEntry",
            padding=6,
            fieldbackground=CARD_BG,
            foreground=TEXT_PRIMARY,
        )
        style.configure(
            "TCombobox",
            padding=4,
            fieldbackground=CARD_BG,
            foreground=TEXT_PRIMARY,
            arrowsize=14,
            arrowcolor=TEXT_SECONDARY,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", CARD_BG), ("!disabled", CARD_BG)],
            foreground=[("readonly", TEXT_PRIMARY), ("!disabled", TEXT_PRIMARY)],
            background=[("readonly", CARD_BG), ("!disabled", CARD_BG)],
            arrowcolor=[("active", TEXT_PRIMARY), ("!disabled", TEXT_SECONDARY)],
        )
        self.option_add("*TCombobox*Listbox.background", CARD_BG)
        self.option_add("*TCombobox*Listbox.foreground", TEXT_PRIMARY)
        self.option_add("*TCombobox*Listbox.selectBackground", LISTBOX_SELECT)
        self.option_add("*TCombobox*Listbox.selectForeground", TEXT_PRIMARY)
        self.option_add("*Listbox.background", CARD_BG)
        self.option_add("*Listbox.foreground", TEXT_PRIMARY)
        self.option_add("*Listbox.selectBackground", LISTBOX_SELECT)
        self.option_add("*Listbox.selectForeground", TEXT_PRIMARY)
        style.map(
            "TButton",
            background=[("active", BUTTON_HOVER)],
            foreground=[("active", BUTTON_TEXT), ("disabled", TEXT_DISABLED)],
        )
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=CARD_BG,
            background=PROGRESS_GREEN,
            bordercolor=PROGRESS_BORDER,
            lightcolor=PROGRESS_GREEN,
            darkcolor=PROGRESS_GREEN_DARK,
        )
        style.configure(
            "Small.TCheckbutton",
            background=APP_BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
            padding=(6, 2),
            focuscolor=APP_BG,
        )
        style.map(
            "Small.TCheckbutton",
            background=[("active", APP_BG)],
            foreground=[("active", TEXT_SECONDARY), ("disabled", TEXT_DISABLED)],
            focuscolor=[("focus", APP_BG)],
        )
        style.configure(
            "Card.TCheckbutton",
            background=CARD_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 9),
            padding=(6, 2),
            focuscolor=CARD_BG,
        )
        style.map(
            "Card.TCheckbutton",
            background=[("active", CARD_BG)],
            foreground=[("active", TEXT_PRIMARY), ("disabled", TEXT_DISABLED)],
            focuscolor=[("focus", CARD_BG)],
        )

    def _build_ui(self):
        root = ttk.Frame(self, padding=20, style="App.TFrame")
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root, style="App.TFrame")
        header.grid(row=0, column=0, sticky="we")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="KiCad Export Studio", style="Header.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        top_actions = ttk.Frame(header, style="App.TFrame")
        top_actions.grid(row=0, column=1, sticky="e")
        self.log_toggle = ttk.Checkbutton(
            top_actions,
            text="Show log",
            variable=self.show_log_var,
            command=self._toggle_log,
            style="Small.TCheckbutton",
        )
        self.log_toggle.pack(side="right")
        ttk.Label(
            root,
            text="Render PCB images with a clean, repeatable setup.",
            style="Sub.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        content = ttk.Frame(root, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")

        left = ttk.Frame(content, style="Card.TFrame", padding=16)
        right = ttk.Frame(content, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right.grid(row=0, column=1, sticky="nsew")

        right_canvas = tk.Canvas(
            right, background=CARD_BG, highlightthickness=0, bd=0
        )
        right_scroll = ttk.Scrollbar(
            right, orient="vertical", command=right_canvas.yview
        )
        right_canvas.configure(yscrollcommand=right_scroll.set)
        right_canvas.grid(row=0, column=0, sticky="nsew")
        right_scroll.grid(row=0, column=1, sticky="ns")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        right_inner = ttk.Frame(right_canvas, style="Card.TFrame", padding=16)
        right_window = right_canvas.create_window(
            (0, 0), window=right_inner, anchor="nw"
        )
        right_inner.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")),
        )
        right_canvas.bind(
            "<Configure>",
            lambda e: right_canvas.itemconfigure(right_window, width=e.width),
        )
        bind_mousewheel(self, right_canvas)

        ttk.Label(left, text="Board + Output", style="HeaderCard.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10)
        )

        ttk.Label(left, text="Board file (.kicad_pcb)", style="Label.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(left, textvariable=self.board_var, width=44).grid(
            row=2, column=0, sticky="we"
        )
        ttk.Button(left, text="Browse", command=self._browse_board).grid(
            row=2, column=1, sticky="e", padx=(8, 0)
        )

        ttk.Label(left, text="Output folder", style="Label.TLabel").grid(
            row=3, column=0, sticky="w", pady=(14, 6)
        )
        ttk.Entry(left, textvariable=self.output_var, width=44).grid(
            row=4, column=0, sticky="we"
        )
        ttk.Button(left, text="Browse", command=self._browse_output_folder).grid(
            row=4, column=1, sticky="e", padx=(8, 0)
        )

        self.log_label = ttk.Label(left, text="Log", style="Label.TLabel")
        self.log_text = scrolledtext.ScrolledText(
            left,
            height=8,
            wrap="word",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
        )
        self.log_label.grid(row=5, column=0, sticky="w", pady=(14, 6))
        self.log_text.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.log_text.configure(state="disabled")
        self.log_label.grid_remove()
        self.log_text.grid_remove()

        # KiCad command path is configured via KICAD_CMD_DEFAULT.

        ttk.Label(right_inner, text="Render Settings", style="HeaderCard.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        ttk.Label(right_inner, text="Select resolution", style="Label.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 4)
        )
        ttk.Combobox(
            right_inner,
            textvariable=self.resolution_var,
            values=RESOLUTION_OPTIONS,
            state="readonly",
        ).grid(row=2, column=0, sticky="we")
        self.resolution_var.trace_add("write", self._apply_resolution)
        ttk.Label(right_inner, text="Or", style="CardSub.TLabel").grid(
            row=3, column=0, sticky="w", pady=(6, 4)
        )
        ttk.Label(right_inner, text="Size (px)", style="Label.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        size_frame = ttk.Frame(right_inner, style="Card.TFrame")
        size_frame.grid(row=5, column=0, sticky="we", pady=(6, 10))
        size_frame.columnconfigure(0, weight=1)
        size_frame.columnconfigure(2, weight=1)
        ttk.Entry(size_frame, textvariable=self.width_var).grid(
            row=0, column=0, sticky="we"
        )
        ttk.Label(size_frame, text="x", style="Label.TLabel").grid(
            row=0, column=1, padx=6
        )
        ttk.Entry(size_frame, textvariable=self.height_var).grid(
            row=0, column=2, sticky="we"
        )

        ttk.Label(right_inner, text="Side", style="Label.TLabel").grid(
            row=6, column=0, sticky="w", pady=(12, 4)
        )
        ttk.Combobox(
            right_inner,
            textvariable=self.side_var,
            values=SIDE_OPTIONS,
            state="readonly",
        ).grid(row=7, column=0, sticky="we")

        ttk.Label(right_inner, text="Background", style="Label.TLabel").grid(
            row=8, column=0, sticky="w", pady=(10, 4)
        )
        ttk.Combobox(
            right_inner,
            textvariable=self.background_var,
            values=BACKGROUND_OPTIONS,
            state="readonly",
        ).grid(row=9, column=0, sticky="we")

        ttk.Label(right_inner, text="Quality", style="Label.TLabel").grid(
            row=10, column=0, sticky="w", pady=(10, 4)
        )
        ttk.Combobox(
            right_inner,
            textvariable=self.quality_var,
            values=QUALITY_OPTIONS,
            state="readonly",
        ).grid(row=11, column=0, sticky="we")

        self.advanced_container = ttk.Frame(right_inner, style="Card.TFrame")
        self.advanced_container.grid(row=12, column=0, sticky="nsew", pady=(14, 0))
        ttk.Label(self.advanced_container, text="Advanced", style="Label.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        ttk.Checkbutton(
            self.advanced_container,
            text="Floor (shadows/post)",
            variable=self.floor_var,
            style="Card.TCheckbutton",
        ).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(
            self.advanced_container,
            text="Perspective",
            variable=self.perspective_var,
            style="Card.TCheckbutton",
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Preset", style="Label.TLabel").grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Combobox(
            self.advanced_container,
            textvariable=self.preset_var,
            values=PRESET_OPTIONS,
            state="readonly",
        ).grid(row=4, column=0, sticky="we", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Zoom", style="Label.TLabel").grid(
            row=5, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.zoom_var).grid(
            row=6, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container, text="Example: 1", style="Hint.TLabel"
        ).grid(row=7, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Pan (X,Y,Z)", style="Label.TLabel").grid(
            row=8, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.pan_var).grid(
            row=9, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container, text="Example: 3,0,0", style="Hint.TLabel"
        ).grid(row=10, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Pivot (X,Y,Z)", style="Label.TLabel").grid(
            row=11, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.pivot_var).grid(
            row=12, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container, text="Example: -10,2,0", style="Hint.TLabel"
        ).grid(row=13, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Rotate (X,Y,Z)", style="Label.TLabel").grid(
            row=14, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.rotate_var).grid(
            row=15, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container, text="Example: -45,0,45", style="Hint.TLabel"
        ).grid(row=16, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Light top (Single number or R,G,B)", style="Label.TLabel").grid(
            row=17, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.light_top_var).grid(
            row=18, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container,
            text="Example: 0.8 or 0.8,0.8,0.8",
            style="Hint.TLabel",
        ).grid(row=19, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Light bottom (Single number or R,G,B)", style="Label.TLabel").grid(
            row=20, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.light_bottom_var).grid(
            row=21, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container,
            text="Example: 0.3 or 0.3,0.3,0.3",
            style="Hint.TLabel",
        ).grid(row=22, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Light side (Single number or R,G,B)", style="Label.TLabel").grid(
            row=23, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.light_side_var).grid(
            row=24, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container,
            text="Example: 0.5 or 0.5,0.5,0.5",
            style="Hint.TLabel",
        ).grid(row=25, column=0, sticky="w", pady=(0, 10))

        ttk.Label(self.advanced_container, text="Light camera (Single number or R,G,B)", style="Label.TLabel").grid(
            row=26, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(self.advanced_container, textvariable=self.light_camera_var).grid(
            row=27, column=0, sticky="we", pady=(0, 4)
        )
        ttk.Label(
            self.advanced_container,
            text="Example: 0.2 or 0.2,0.2,0.2",
            style="Hint.TLabel",
        ).grid(row=28, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            self.advanced_container, text="Light side elevation", style="Label.TLabel"
        ).grid(row=29, column=0, sticky="w", pady=(0, 6))
        ttk.Entry(
            self.advanced_container, textvariable=self.light_side_elevation_var
        ).grid(row=30, column=0, sticky="we", pady=(0, 4))
        ttk.Label(
            self.advanced_container, text="Example: 45", style="Hint.TLabel"
        ).grid(row=31, column=0, sticky="w", pady=(0, 2))

        self.advanced_container.columnconfigure(0, weight=1)
        self.advanced_container.grid_remove()

        # Log is shown in the Board + Output panel.

        actions = ttk.Frame(root, style="App.TFrame")
        actions.grid(row=3, column=0, sticky="we", pady=(18, 0))
        self.progress = ttk.Progressbar(
            actions, mode="determinate", length=480, style="Green.Horizontal.TProgressbar"
        )
        self.progress.pack(side="left", padx=(0, 10))
        ttk.Label(actions, textvariable=self.status_var, style="Status.TLabel").pack(
            side="left"
        )
        self.render_button = ttk.Button(
            actions,
            text="Render Image",
            style="Primary.TButton",
            command=self._run_render,
        )
        self.render_button.pack(side="right")
        self.advanced_toggle = ttk.Checkbutton(
            actions,
            text="Advanced",
            variable=self.show_advanced_var,
            command=self._toggle_advanced,
            style="Small.TCheckbutton",
        )
        self.advanced_toggle.pack(side="right", padx=(0, 10))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)
        content.columnconfigure(0, weight=3, uniform="content")
        content.columnconfigure(1, weight=2, uniform="content")
        content.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(6, weight=1)
        right_inner.columnconfigure(0, weight=1)
        right_inner.rowconfigure(12, weight=1)

    def _toggle_log(self):
        if self.show_log_var.get():
            self.log_label.grid()
            self.log_text.grid()
        else:
            self.log_label.grid_remove()
            self.log_text.grid_remove()

    def _toggle_advanced(self):
        if self.show_advanced_var.get():
            self.advanced_container.grid()
        else:
            self.advanced_container.grid_remove()

    def _browse_board(self):
        path = filedialog.askopenfilename(
            title="Select KiCad board file",
            filetypes=[("KiCad PCB", "*.kicad_pcb"), ("All files", "*")],
        )
        if path:
            self.board_var.set(path)

    def _browse_output_folder(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_var.set(path)

    def _apply_resolution(self, *_):
        value = self.resolution_var.get()
        if not value:
            return
        size = RESOLUTION_MAP.get(value)
        if size:
            self.width_var.set(str(size[0]))
            self.height_var.set(str(size[1]))

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _collect_render_options(self, board, width, height):
        return {
            "board": board,
            "output": "",
            "width": width,
            "height": height,
            "side": self.side_var.get(),
            "background": self.background_var.get(),
            "quality": self.quality_var.get(),
            "preset": self.preset_var.get().strip(),
            "floor": self.floor_var.get(),
            "perspective": self.perspective_var.get(),
            "zoom": self.zoom_var.get().strip(),
            "pan": self.pan_var.get().strip(),
            "pivot": self.pivot_var.get().strip(),
            "rotate": self.rotate_var.get().strip(),
            "light_top": self.light_top_var.get().strip(),
            "light_bottom": self.light_bottom_var.get().strip(),
            "light_side": self.light_side_var.get().strip(),
            "light_camera": self.light_camera_var.get().strip(),
            "light_side_elevation": self.light_side_elevation_var.get().strip(),
        }

    def _poll_log_queue(self):
        while True:
            try:
                event = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if event[0] == "line":
                self._append_log(event[1])
            elif event[0] == "progress":
                self.progress["value"] = min(event[1], self.progress["maximum"])
            elif event[0] == "done":
                self.render_in_progress = False
                self.render_button.configure(state="normal")
                if event[1]:
                    self.status_var.set("Render complete.")
                else:
                    self.status_var.set("Render failed.")
        self.after(120, self._poll_log_queue)

    def _run_render(self):
        if self.render_in_progress:
            return
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError:
            messagebox.showerror("KiCad Render", "Width and height must be integers.")
            return

        board = self.board_var.get().strip()
        output_dir = self.output_var.get().strip()
        kicad_cmd = KICAD_CMD_DEFAULT.strip()

        if not board:
            messagebox.showerror("KiCad Render", "Please choose a board file.")
            return
        if not output_dir:
            messagebox.showerror("KiCad Render", "Please choose an output folder.")
            return
        if not kicad_cmd:
            messagebox.showerror(
                "KiCad Render",
                "KiCad command not configured. Update KICAD_CMD_DEFAULT in the script.",
            )
            return

        os.makedirs(output_dir, exist_ok=True)
        options = self._collect_render_options(board, width, height)

        selected_side = options["side"]
        if selected_side == "top + bottom":
            kicad_cli_cmds = []
            for side in ("top", "bottom"):
                output_path = os.path.join(output_dir, f"{side}.png")
                kicad_cli_cmds.append(
                    build_kicad_cli_command({**options, "side": side, "output": output_path})
                )
            kicad_cli_cmd_list = kicad_cli_cmds
        else:
            output_path = os.path.join(output_dir, f"{selected_side}.png")
            kicad_cli_cmd_list = [
                build_kicad_cli_command(
                    {**options, "output": output_path, "side": selected_side}
                )
            ]

        full_cmds = [build_cmd_exe_command(kicad_cmd, cmd) for cmd in kicad_cli_cmd_list]
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.status_var.set("Rendering...")
        self.render_in_progress = True
        self.render_button.configure(state="disabled")
        self.progress["maximum"] = 100
        self.progress["value"] = 0
        thread = threading.Thread(target=self._run_render_worker, args=(full_cmds,))
        thread.daemon = True
        thread.start()

    def _run_render_worker(self, full_cmds):
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        success = True
        progress_re = re.compile(r"Rendering:\s*(\d+)\s*%")
        total_steps = max(len(full_cmds), 1)
        for index, cmd in enumerate(full_cmds):
            self.log_queue.put(("line", f"$ {cmd}\n"))
            try:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=creationflags,
                )
            except Exception as exc:
                self.log_queue.put(("line", f"Failed to launch: {exc}\n"))
                success = False
                break

            if proc.stdout:
                for line in proc.stdout:
                    self.log_queue.put(("line", line))
                    match = progress_re.search(line)
                    if match:
                        percent = min(int(match.group(1)), 100)
                        overall = ((index + (percent / 100)) / total_steps) * 100
                        self.log_queue.put(("progress", overall))
            return_code = proc.wait()
            if return_code != 0:
                self.log_queue.put(("line", f"Command failed with code {return_code}\n"))
                success = False
                break
            overall = ((index + 1) / total_steps) * 100
            self.log_queue.put(("progress", overall))

        self.log_queue.put(("done", success))

if __name__ == "__main__":
    app = KiCadExportGUI()
    app.mainloop()
