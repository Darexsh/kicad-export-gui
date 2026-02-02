import os
import queue
import re
import subprocess
import shutil
import threading

import wx

from render_command import build_cmd_exe_command, build_kicad_cli_command
from gui_tabs import TabsBuilder
from ui_constants import (
    APP_BG,
    BACKGROUND_OPTIONS,
    BUTTON_BG,
    BUTTON_HOVER,
    BUTTON_TEXT,
    CARD_BG,
    KICAD_CMD_DEFAULT,
    PRESET_OPTIONS,
    PROGRESS_GREEN,
    PROGRESS_GREEN_DARK,
    QUALITY_OPTIONS,
    RESOLUTION_MAP,
    RESOLUTION_OPTIONS,
    SIDE_OPTIONS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def _hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


class KiCadExportFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="KiCad Export Studio", size=(1000, 680))
        self.SetMinSize((1000, 680))
        self.SetMaxSize((1000, 680))

        self.log_queue = queue.Queue()
        self.render_in_progress = False
        self.current_action_label = "Render"
        self.layer_aliases = {
            "F.SilkS": "F.Silkscreen",
            "B.SilkS": "B.Silkscreen",
        }
        self.layer_aliases_reverse = {v: k for k, v in self.layer_aliases.items()}
        self.layer_order = [
            "F.Cu",
            "B.Cu",
            "F.Adhesive",
            "B.Adhesive",
            "F.Paste",
            "B.Paste",
            "F.Silkscreen",
            "B.Silkscreen",
            "F.Mask",
            "B.Mask",
            "User.Drawings",
            "User.Comments",
            "User.Eco1",
            "User.Eco2",
            "Edge.Cuts",
            "Margin",
            "F.Courtyard",
            "B.Courtyard",
            "F.Fab",
            "B.Fab",
            "User.1",
            "User.2",
            "User.3",
            "User.4",
            "User.5",
            "User.6",
            "User.7",
            "User.8",
            "User.9",
        ]
        self.extra_layers = [
            "F.Adhesive",
            "B.Adhesive",
            "F.Paste",
            "B.Paste",
            "F.Silkscreen",
            "B.Silkscreen",
            "F.Mask",
            "B.Mask",
            "User.Drawings",
            "User.Comments",
            "User.Eco1",
            "User.Eco2",
            "Edge.Cuts",
            "Margin",
            "F.Courtyard",
            "B.Courtyard",
            "F.Fab",
            "B.Fab",
            "User.1",
            "User.2",
            "User.3",
            "User.4",
            "User.5",
            "User.6",
            "User.7",
            "User.8",
            "User.9",
        ]
        self.detected_layers = []
        self.selected_layers = []

        self._init_colors()
        self._init_fonts()
        self._build_ui()
        self._bind_events()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._poll_log_queue, self.timer)
        self.timer.Start(120)

    def _load_icon(self, filename, size=16):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "icons", filename)
        if not os.path.isfile(path):
            return None
        image = wx.Image(path, wx.BITMAP_TYPE_PNG)
        if image.IsOk() and size:
            image = image.Scale(size, size, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image) if image.IsOk() else None

    def _init_colors(self):
        self.app_bg = wx.Colour(*_hex_to_rgb(APP_BG))
        self.card_bg = wx.Colour(*_hex_to_rgb(CARD_BG))
        self.text_primary = wx.Colour(*_hex_to_rgb(TEXT_PRIMARY))
        self.text_secondary = wx.Colour(*_hex_to_rgb(TEXT_SECONDARY))
        self.text_muted = wx.Colour(*_hex_to_rgb(TEXT_MUTED))
        self.button_bg = wx.Colour(*_hex_to_rgb(BUTTON_BG))
        self.button_hover = wx.Colour(*_hex_to_rgb(BUTTON_HOVER))
        self.button_text = wx.Colour(*_hex_to_rgb(BUTTON_TEXT))
        self.progress_green = wx.Colour(*_hex_to_rgb(PROGRESS_GREEN))
        self.progress_green_dark = wx.Colour(*_hex_to_rgb(PROGRESS_GREEN_DARK))

    def _init_fonts(self):
        self.font_header = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Bahnschrift")
        self.font_sub = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Bahnschrift")
        self.font_banner = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Bahnschrift")
        self.font_banner_sub = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Bahnschrift")
        self.font_label = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Bahnschrift")
        self.font_label_bold = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Bahnschrift")
        self.font_status = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Bahnschrift")
        self.font_button = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Bahnschrift")

    def _build_ui(self):
        self.SetBackgroundColour(self.app_bg)

        root = wx.Panel(self)
        root.SetBackgroundColour(self.app_bg)

        root_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(root, label="KiCad Export Studio")
        title.SetForegroundColour(self.text_primary)
        title.SetFont(self.font_header)
        header.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        self.show_log_checkbox = wx.CheckBox(root, label="Show log")
        self.show_log_checkbox.SetForegroundColour(self.text_muted)
        self.show_log_checkbox.SetValue(False)
        header.Add(self.show_log_checkbox, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)


        root_sizer.Add(header, 0, wx.EXPAND | wx.ALL, 6)

        banner = wx.Panel(root)
        banner.SetBackgroundColour(self.card_bg)
        banner_sizer = wx.BoxSizer(wx.HORIZONTAL)

        accent = wx.Panel(banner, size=(6, 36))
        accent.SetBackgroundColour(self.button_bg)
        banner_sizer.Add(accent, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)

        banner_text = wx.BoxSizer(wx.VERTICAL)
        banner_title = wx.StaticText(banner, label="Your KiCad export studio - consistent and fast.")
        banner_title.SetForegroundColour(self.text_primary)
        banner_title.SetFont(self.font_banner)
        banner_sub = wx.StaticText(banner, label="Use tabs to switch between image, schematic, and layout exports.")
        banner_sub.SetForegroundColour(self.text_muted)
        banner_sub.SetFont(self.font_banner_sub)
        banner_text.Add(banner_title, 0, wx.BOTTOM, 2)
        banner_text.Add(banner_sub, 0)

        banner_sizer.Add(banner_text, 1, wx.ALIGN_CENTER_VERTICAL)
        banner.SetSizer(banner_sizer)
        root_sizer.Add(banner, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        paths_card = wx.Panel(root)
        paths_card.SetBackgroundColour(self.card_bg)
        paths_sizer = wx.BoxSizer(wx.VERTICAL)

        paths_header = wx.StaticText(paths_card, label="Project Paths")
        paths_header.SetForegroundColour(self.text_primary)
        paths_header.SetFont(self.font_label_bold)
        paths_sizer.Add(paths_header, 0, wx.BOTTOM, 10)

        board_label = wx.StaticText(paths_card, label="Project file (.kicad_pro)")
        board_label.SetForegroundColour(self.text_secondary)
        board_label.SetFont(self.font_label)
        paths_sizer.Add(board_label, 0, wx.BOTTOM, 6)

        board_row = wx.BoxSizer(wx.HORIZONTAL)
        self.project_input = wx.TextCtrl(paths_card)
        self.project_input.SetBackgroundColour(self.card_bg)
        self.project_input.SetForegroundColour(self.text_primary)
        board_row.Add(self.project_input, 1, wx.RIGHT, 8)
        self.project_browse = wx.Button(paths_card, label="Browse")
        self.project_browse.SetFont(self.font_button)
        self.project_browse.SetMinSize((110, -1))
        self.project_browse.SetMaxSize((110, -1))
        board_row.Add(self.project_browse, 0)
        paths_sizer.Add(board_row, 0, wx.EXPAND | wx.BOTTOM, 12)

        output_label = wx.StaticText(paths_card, label="Output folder")
        output_label.SetForegroundColour(self.text_secondary)
        output_label.SetFont(self.font_label)
        paths_sizer.Add(output_label, 0, wx.BOTTOM, 6)

        output_row = wx.BoxSizer(wx.HORIZONTAL)
        self.output_input = wx.TextCtrl(paths_card)
        self.output_input.SetBackgroundColour(self.card_bg)
        self.output_input.SetForegroundColour(self.text_primary)
        output_row.Add(self.output_input, 1, wx.RIGHT, 8)
        self.output_browse = wx.Button(paths_card, label="Browse")
        self.output_browse.SetFont(self.font_button)
        self.output_browse.SetMinSize((110, -1))
        self.output_browse.SetMaxSize((110, -1))
        output_row.Add(self.output_browse, 0)
        paths_sizer.Add(output_row, 0, wx.EXPAND)

        paths_card.SetSizer(paths_sizer)
        root_sizer.Add(paths_card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        notebook = wx.Notebook(root)
        notebook.SetBackgroundColour(self.app_bg)
        self.pcb_tab = wx.Panel(notebook)
        self.pcb_tab.SetBackgroundColour(self.app_bg)
        self.schematic_tab = wx.Panel(notebook)
        self.schematic_tab.SetBackgroundColour(self.app_bg)
        self.layout_tab = wx.Panel(notebook)
        self.layout_tab.SetBackgroundColour(self.app_bg)
        notebook.AddPage(self.pcb_tab, "PCB Images Export")
        notebook.AddPage(self.schematic_tab, "Schematic Export")
        notebook.AddPage(self.layout_tab, "Layout Export")

        root_sizer.Add(notebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)

        self.tabs = TabsBuilder(self)
        self.tabs.build_pcb_tab()
        self.tabs.build_schematic_tab()
        self.tabs.build_layout_tab()

        footer = wx.BoxSizer(wx.HORIZONTAL)
        self.developer_label = wx.StaticText(
            root,
            label="Developed by: Darexsh by Daniel Sichler",
        )
        self.developer_label.SetForegroundColour(self.text_muted)
        self.developer_label.SetFont(self.font_status)
        footer.Add(self.developer_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.developer_github = wx.Button(root, label="GitHub")
        self.developer_github.SetFont(self.font_button)
        self.developer_github.SetMinSize((90, -1))
        self.developer_github.SetMaxSize((90, -1))
        github_icon = self._load_icon("github.png", size=16)
        if github_icon:
            self.developer_github.SetBitmap(github_icon)
        footer.Add(self.developer_github, 0, wx.ALIGN_CENTER_VERTICAL)
        self.coffee_button = wx.Button(root, label="Buy me a coffee")
        self.coffee_button.SetFont(self.font_button)
        self.coffee_button.SetMinSize((150, -1))
        self.coffee_button.SetMaxSize((150, -1))
        coffee_icon = self._load_icon("buy-me-coffee-icon.png", size=16)
        if coffee_icon:
            self.coffee_button.SetBitmap(coffee_icon)
        footer.Add(self.coffee_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        root_sizer.Add(footer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        root.SetSizer(root_sizer)
        self._toggle_log_all(False)


    def _bind_events(self):
        self.show_log_checkbox.Bind(wx.EVT_CHECKBOX, self._on_toggle_log)
        self.project_browse.Bind(wx.EVT_BUTTON, self._browse_project)
        self.output_browse.Bind(wx.EVT_BUTTON, self._browse_output_folder)
        self.resolution_combo.Bind(wx.EVT_COMBOBOX, self._apply_resolution)
        self.render_button.Bind(wx.EVT_BUTTON, self._run_render)
        self.advanced_toggle.Bind(wx.EVT_CHECKBOX, self._on_toggle_advanced)
        self.export_schematic_button.Bind(wx.EVT_BUTTON, self._export_schematic)
        self.export_layout_button.Bind(wx.EVT_BUTTON, self._export_layout)
        self.change_layers_button.Bind(wx.EVT_BUTTON, self._change_layers)
        self.developer_github.Bind(wx.EVT_BUTTON, self._open_github)
        self.coffee_button.Bind(wx.EVT_BUTTON, self._open_coffee)

    def _on_toggle_log(self, event):
        self._toggle_log_all(self.show_log_checkbox.GetValue())

    def _open_github(self, _event):
        wx.LaunchDefaultBrowser("https://github.com/Darexsh")

    def _open_coffee(self, _event):
        wx.LaunchDefaultBrowser("https://buymeacoffee.com/darexsh")


    def _on_toggle_advanced(self, event):
        self._toggle_advanced(self.advanced_toggle.GetValue())

    def _toggle_log_all(self, show):
        self.log_card_pcb.Show(show)
        if show:
            self.log_card_sch.Show(True)
            self.log_card_layout.Show(True)
            self.log_spacer_sch.Show(False)
            self.log_spacer_layout.Show(False)
        else:
            self.log_card_sch.Show(False)
            self.log_card_layout.Show(False)
            self.log_spacer_sch.Show(True)
            self.log_spacer_layout.Show(True)
        if show:
            self.pcb_left_panel.Show(True)
            self.pcb_left_item.SetProportion(3)
            self.pcb_right_item.SetProportion(2)
        else:
            self.pcb_left_panel.Show(False)
            self.pcb_left_item.SetProportion(0)
            self.pcb_right_item.SetProportion(1)
        self.pcb_tab.Layout()
        self.schematic_tab.Layout()
        self.layout_tab.Layout()

    def _toggle_advanced(self, show):
        self.advanced_container.Show(show)
        self.pcb_tab.Layout()

    def _browse_project(self, _event):
        with wx.FileDialog(
            self,
            "Select KiCad project file",
            wildcard="KiCad Project (*.kicad_pro)|*.kicad_pro|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.project_input.SetValue(dialog.GetPath())
                self._update_detected_layers()

    def _browse_output_folder(self, _event):
        with wx.DirDialog(self, "Select output folder", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.output_input.SetValue(dialog.GetPath())

    def _apply_resolution(self, _event):
        value = self.resolution_combo.GetValue()
        if not value:
            return
        size = RESOLUTION_MAP.get(value)
        if size:
            self.width_input.SetValue(str(size[0]))
            self.height_input.SetValue(str(size[1]))

    def _append_log(self, text):
        for log in (self.log_text_pcb, self.log_text_sch, self.log_text_layout):
            log.AppendText(text)
            log.ShowPosition(log.GetLastPosition())

    def _detect_layers_from_pcb(self, pcb_path):
        if not os.path.isfile(pcb_path):
            return []
        try:
            with open(pcb_path, "r", encoding="utf-8", errors="ignore") as handle:
                pcb_text = handle.read()
        except OSError:
            return []
        known_layers = [
            "F.Cu",
            "In1.Cu",
            "In2.Cu",
            "B.Cu",
            "F.SilkS",
            "B.SilkS",
            "F.Silkscreen",
            "B.Silkscreen",
            "F.Mask",
            "B.Mask",
            "Edge.Cuts",
        ]
        detected = [layer for layer in known_layers if layer in pcb_text]
        internal_found = sorted(
            set(re.findall(r"\bIn\d+\.Cu\b", pcb_text)),
            key=lambda x: int(re.findall(r"\d+", x)[0]),
        )
        for layer in internal_found:
            if layer not in detected:
                detected.append(layer)
        normalized = []
        for layer in detected:
            normalized.append(self.layer_aliases.get(layer, layer))
        return normalized

    def _update_detected_layers(self):
        _project, pcb_path, _sch = self._derive_paths_from_project()
        detected = self._detect_layers_from_pcb(pcb_path)
        self.detected_layers = detected
        seen = set()
        deduped = []
        for layer in detected:
            if layer not in seen:
                seen.add(layer)
                deduped.append(layer)
        self.selected_layers = deduped
        self.layers_value.SetLabel(", ".join(self.selected_layers) if self.selected_layers else "None")

    def _change_layers(self, _event):
        if not self.detected_layers:
            self._update_detected_layers()
        if not self.detected_layers:
            wx.MessageBox("No layers detected yet. Choose a project file first.", "Layout Export", wx.ICON_WARNING)
            return
        choices = []
        internal_layers = [layer for layer in self.detected_layers if re.match(r"^In\d+\.Cu$", layer)]
        internal_layers.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
        for layer in self.layer_order:
            if layer == "B.Cu" and internal_layers:
                for internal in internal_layers:
                    if internal not in choices:
                        choices.append(internal)
            if layer not in choices:
                choices.append(layer)
        for layer in self.detected_layers:
            if layer not in choices:
                choices.append(layer)
        preselect = [choices.index(layer) for layer in self.selected_layers if layer in choices]
        dialog = wx.MultiChoiceDialog(
            self,
            "Select layers to export",
            "Layout Layers",
            choices,
        )
        dialog.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        dialog_sizer = dialog.GetSizer()
        if dialog_sizer:
            dialog.Layout()
        def _select_all(_evt):
            dialog.SetSelections(list(range(len(choices))))
        def _clear_all(_evt):
            dialog.SetSelections([])
        def _show_context_menu(evt):
            menu = wx.Menu()
            select_id = wx.NewIdRef()
            clear_id = wx.NewIdRef()
            menu.Append(select_id, "Select all")
            menu.Append(clear_id, "Clear all")
            dialog.Bind(wx.EVT_MENU, _select_all, id=select_id)
            dialog.Bind(wx.EVT_MENU, _clear_all, id=clear_id)
            dialog.PopupMenu(menu)
            menu.Destroy()
        listbox = None
        for child in dialog.GetChildren():
            if isinstance(child, wx.ListBox):
                listbox = child
                break
        target = listbox or dialog
        target.Bind(wx.EVT_CONTEXT_MENU, _show_context_menu)
        if preselect:
            dialog.SetSelections(preselect)
        if dialog.ShowModal() == wx.ID_OK:
            selections = dialog.GetSelections()
            self.selected_layers = [choices[i] for i in selections]
            if self.selected_layers:
                self.layers_value.SetLabel(", ".join(self.selected_layers))
            else:
                self.layers_value.SetLabel("None")
        dialog.Destroy()

    def _derive_paths_from_project(self):
        project_path = self.project_input.GetValue().strip()
        if not project_path:
            return "", "", ""
        project_dir = os.path.dirname(project_path)
        project_name = os.path.splitext(os.path.basename(project_path))[0]
        pcb_path = os.path.join(project_dir, f"{project_name}.kicad_pcb")
        sch_path = os.path.join(project_dir, f"{project_name}.kicad_sch")
        return project_path, pcb_path, sch_path

    def _wrap_kicad_cmd(self, cmd):
        if os.name == "nt":
            kicad_cmd = KICAD_CMD_DEFAULT.strip()
            if not kicad_cmd:
                return cmd
            return build_cmd_exe_command(kicad_cmd, cmd)
        return cmd

    def _collect_render_options(self, board, width, height):
        return {
            "board": board,
            "output": "",
            "width": width,
            "height": height,
            "side": self.side_combo.GetValue(),
            "background": self.background_combo.GetValue(),
            "quality": self.quality_combo.GetValue(),
            "preset": self.preset_combo.GetValue().strip(),
            "floor": self.floor_check.GetValue(),
            "perspective": self.perspective_check.GetValue(),
            "zoom": self.zoom_input.GetValue().strip(),
            "pan": self.pan_input.GetValue().strip(),
            "pivot": self.pivot_input.GetValue().strip(),
            "rotate": self.rotate_input.GetValue().strip(),
            "light_top": self.light_top_input.GetValue().strip(),
            "light_bottom": self.light_bottom_input.GetValue().strip(),
            "light_side": self.light_side_input.GetValue().strip(),
            "light_camera": self.light_camera_input.GetValue().strip(),
            "light_side_elevation": self.light_side_elevation_input.GetValue().strip(),
        }

    def _start_command_run(self, full_cmds, status_text, action_label):
        for log in (self.log_text_pcb, self.log_text_sch, self.log_text_layout):
            log.SetValue("")
        for label in (self.status_label_pcb, self.status_label_sch, self.status_label_layout):
            label.SetLabel(status_text)
        self.current_action_label = action_label
        self.render_in_progress = True
        self.render_button.Enable(False)
        self.export_schematic_button.Enable(False)
        self.export_layout_button.Enable(False)
        self.progress_pcb.SetValue(0)
        self.progress_sch.SetValue(0)
        self.progress_layout.SetValue(0)

        thread = threading.Thread(target=self._run_command_worker, args=(full_cmds,))
        thread.daemon = True
        thread.start()

    def _poll_log_queue(self, _event):
        while True:
            try:
                event = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if event[0] == "line":
                self._append_log(event[1])
            elif event[0] == "progress":
                value = min(int(event[1]), 100)
                self.progress_pcb.SetValue(value)
                self.progress_sch.SetValue(value)
                self.progress_layout.SetValue(value)
            elif event[0] == "done":
                self.render_in_progress = False
                self.render_button.Enable(True)
                self.export_schematic_button.Enable(True)
                self.export_layout_button.Enable(True)
                if event[1]:
                    message = f"{self.current_action_label} complete."
                else:
                    message = f"{self.current_action_label} failed."
                self.status_label_pcb.SetLabel(message)
                self.status_label_sch.SetLabel(message)
                self.status_label_layout.SetLabel(message)
                wx.CallLater(5000, self._reset_progress_if_idle)

    def _reset_progress_if_idle(self):
        if self.render_in_progress:
            return
        self.progress_pcb.SetValue(0)
        self.progress_sch.SetValue(0)
        self.progress_layout.SetValue(0)

    def _run_render(self, _event):
        if self.render_in_progress:
            return
        try:
            width = int(self.width_input.GetValue())
            height = int(self.height_input.GetValue())
        except ValueError:
            wx.MessageBox("Width and height must be integers.", "KiCad Render", wx.ICON_ERROR)
            return

        project_path, board, _sch = self._derive_paths_from_project()
        output_dir = self.output_input.GetValue().strip()
        if not project_path:
            wx.MessageBox("Please choose a project file.", "KiCad Render", wx.ICON_ERROR)
            return
        if not output_dir:
            wx.MessageBox("Please choose an output folder.", "KiCad Render", wx.ICON_ERROR)
            return
        if not os.path.isfile(board):
            wx.MessageBox("Matching .kicad_pcb not found for this project.", "KiCad Render", wx.ICON_ERROR)
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

        full_cmds = [self._wrap_kicad_cmd(cmd) for cmd in kicad_cli_cmd_list]
        self._start_command_run(full_cmds, "Rendering...", "Render")

    def _export_schematic(self, _event):
        if self.render_in_progress:
            return
        project_path, _board, schematic = self._derive_paths_from_project()
        output_dir = self.output_input.GetValue().strip()
        if not project_path:
            wx.MessageBox("Please choose a project file.", "Schematic Export", wx.ICON_ERROR)
            return
        if not output_dir:
            wx.MessageBox("Please choose an output folder.", "Schematic Export", wx.ICON_ERROR)
            return
        if not os.path.isfile(schematic):
            wx.MessageBox("Matching .kicad_sch not found for this project.", "Schematic Export", wx.ICON_ERROR)
            return
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "Project_schematics.pdf")
        cmd = subprocess.list2cmdline(
            ["kicad-cli", "sch", "export", "pdf", "--output", output_path, schematic]
        )
        self._start_command_run([self._wrap_kicad_cmd(cmd)], "Exporting schematics...", "Schematic export")

    def _export_layout(self, _event):
        if self.render_in_progress:
            return
        project_path, board, _sch = self._derive_paths_from_project()
        output_dir = self.output_input.GetValue().strip()
        if not project_path:
            wx.MessageBox("Please choose a project file.", "Layout Export", wx.ICON_ERROR)
            return
        if not output_dir:
            wx.MessageBox("Please choose an output folder.", "Layout Export", wx.ICON_ERROR)
            return
        if not os.path.isfile(board):
            wx.MessageBox("Matching .kicad_pcb not found for this project.", "Layout Export", wx.ICON_ERROR)
            return
        if shutil.which("pdfunite") is None:
            wx.MessageBox("pdfunite not found. Install poppler-utils.", "Layout Export", wx.ICON_ERROR)
            return

        layers = [self.layer_aliases_reverse.get(layer, layer) for layer in self.selected_layers]
        deduped = []
        seen = set()
        for layer in layers:
            if layer not in seen:
                seen.add(layer)
                deduped.append(layer)
        layers = deduped
        if not layers:
            wx.MessageBox("Please select at least one layer.", "Layout Export", wx.ICON_ERROR)
            return
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = os.path.join(output_dir, "temp_layers")
        os.makedirs(temp_dir, exist_ok=True)
        output_pdf = os.path.join(output_dir, "Project_board_layers.pdf")

        def worker():
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            try:
                with open(board, "r", encoding="utf-8", errors="ignore") as handle:
                    pcb_text = handle.read()
                exports = []
                for layer in layers:
                    if layer not in pcb_text:
                        self.log_queue.put(("line", f"[WARN] Layer {layer} not found; skipping.\n"))
                        continue
                    out_file = os.path.join(temp_dir, f"board_{layer.replace('.', '_')}.pdf")
                    cmd = subprocess.list2cmdline(
                        [
                            "kicad-cli",
                            "pcb",
                            "export",
                            "pdf",
                            "--output",
                            out_file,
                            "--layers",
                            layer,
                            board,
                        ]
                    )
                    full_cmd = self._wrap_kicad_cmd(cmd)
                    self.log_queue.put(("line", f"$ {full_cmd}\n"))
                    proc = subprocess.Popen(
                        full_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=creationflags,
                    )
                    if proc.stdout:
                        for line in proc.stdout:
                            self.log_queue.put(("line", line))
                    if proc.wait() != 0:
                        self.log_queue.put(("line", "[ERR] Layer export failed.\n"))
                        self.log_queue.put(("done", False))
                        return
                    exports.append(out_file)
                    self.log_queue.put(("progress", (len(exports) / max(len(layers), 1)) * 80))

                if not exports:
                    self.log_queue.put(("line", "[ERR] No layers found to export.\n"))
                    self.log_queue.put(("done", False))
                    return

                combine_cmd = subprocess.list2cmdline(["pdfunite", *exports, output_pdf])
                self.log_queue.put(("line", f"$ {combine_cmd}\n"))
                proc = subprocess.Popen(
                    combine_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=creationflags,
                )
                if proc.stdout:
                    for line in proc.stdout:
                        self.log_queue.put(("line", line))
                if proc.wait() != 0:
                    self.log_queue.put(("line", "[ERR] PDF combine failed (pdfunite).\n"))
                    self.log_queue.put(("done", False))
                    return
                self.log_queue.put(("progress", 100))
                self.log_queue.put(("done", True))
            finally:
                try:
                    for file_name in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, file_name))
                    os.rmdir(temp_dir)
                except OSError:
                    pass

        for log in (self.log_text_pcb, self.log_text_sch, self.log_text_layout):
            log.SetValue("")
        for label in (self.status_label_pcb, self.status_label_sch, self.status_label_layout):
            label.SetLabel("Exporting layout PDFs...")
        self.current_action_label = "Layout export"
        self.render_in_progress = True
        self.render_button.Enable(False)
        self.export_schematic_button.Enable(False)
        self.export_layout_button.Enable(False)
        self.progress_pcb.SetValue(0)
        self.progress_sch.SetValue(0)
        self.progress_layout.SetValue(0)
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def _run_command_worker(self, full_cmds):
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


class KiCadExportApp(wx.App):
    def OnInit(self):
        frame = KiCadExportFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = KiCadExportApp()
    app.MainLoop()
