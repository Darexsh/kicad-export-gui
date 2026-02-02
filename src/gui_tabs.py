import wx

from ui_constants import (
    BACKGROUND_OPTIONS,
    PRESET_OPTIONS,
    QUALITY_OPTIONS,
    RESOLUTION_OPTIONS,
    SIDE_OPTIONS,
)


class TabsBuilder:
    def __init__(self, frame):
        self.frame = frame

    def build_pcb_tab(self):
        f = self.frame
        pcb_sizer = wx.BoxSizer(wx.VERTICAL)
        content = wx.BoxSizer(wx.HORIZONTAL)
        control_width = 320

        left = wx.Panel(f.pcb_tab)
        left.SetBackgroundColour(f.card_bg)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        f.log_card_pcb = wx.Panel(left)
        f.log_card_pcb.SetBackgroundColour(f.card_bg)
        log_card_sizer = wx.BoxSizer(wx.VERTICAL)

        left_header = wx.StaticText(f.log_card_pcb, label="Log")
        left_header.SetForegroundColour(f.text_primary)
        left_header.SetFont(f.font_label_bold)
        log_card_sizer.Add(left_header, 0, wx.BOTTOM, 10)

        f.log_container_pcb = wx.Panel(f.log_card_pcb)
        f.log_container_pcb.SetBackgroundColour(f.card_bg)
        log_container_sizer = wx.BoxSizer(wx.VERTICAL)
        f.log_text_pcb = wx.TextCtrl(
            f.log_container_pcb,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_RICH2,
        )
        f.log_text_pcb.SetBackgroundColour(f.card_bg)
        f.log_text_pcb.SetForegroundColour(f.text_primary)
        f.log_text_pcb.SetFont(f.font_sub)
        log_container_sizer.Add(f.log_text_pcb, 1, wx.EXPAND)
        f.log_container_pcb.SetSizer(log_container_sizer)
        log_card_sizer.Add(f.log_container_pcb, 1, wx.EXPAND)
        f.log_card_pcb.SetSizer(log_card_sizer)
        left_sizer.Add(f.log_card_pcb, 1, wx.EXPAND)

        left.SetSizer(left_sizer)

        right = wx.Panel(f.pcb_tab)
        right.SetBackgroundColour(f.card_bg)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        right_header = wx.StaticText(right, label="Render Settings")
        right_header.SetForegroundColour(f.text_primary)
        right_header.SetFont(f.font_label_bold)
        right_sizer.Add(right_header, 0, wx.BOTTOM, 10)

        right_scroller = wx.ScrolledWindow(right, style=wx.VSCROLL | wx.BORDER_NONE)
        right_scroller.SetBackgroundColour(f.card_bg)
        right_scroller.SetScrollRate(0, 12)
        right_scroller_sizer = wx.BoxSizer(wx.VERTICAL)

        resolution_label = wx.StaticText(right_scroller, label="Select resolution")
        resolution_label.SetForegroundColour(f.text_secondary)
        resolution_label.SetFont(f.font_label)
        right_scroller_sizer.Add(resolution_label, 0, wx.BOTTOM, 4)
        f.resolution_combo = wx.ComboBox(
            right_scroller, choices=RESOLUTION_OPTIONS, style=wx.CB_READONLY
        )
        f.resolution_combo.SetSelection(1)
        f.resolution_combo.SetMinSize((control_width, -1))
        f.resolution_combo.SetMaxSize((control_width, -1))
        right_scroller_sizer.Add(f.resolution_combo, 0, wx.EXPAND | wx.BOTTOM, 8)

        or_label = wx.StaticText(right_scroller, label="Or")
        or_label.SetForegroundColour(f.text_secondary)
        or_label.SetFont(f.font_label)
        right_scroller_sizer.Add(or_label, 0, wx.BOTTOM, 4)

        size_label = wx.StaticText(right_scroller, label="Size (px)")
        size_label.SetForegroundColour(f.text_secondary)
        size_label.SetFont(f.font_label)
        right_scroller_sizer.Add(size_label, 0, wx.BOTTOM, 4)

        size_row = wx.BoxSizer(wx.HORIZONTAL)
        f.width_input = wx.TextCtrl(right_scroller, value="1920")
        f.width_input.SetBackgroundColour(f.card_bg)
        f.width_input.SetForegroundColour(f.text_primary)
        f.width_input.SetMinSize((150, -1))
        f.width_input.SetMaxSize((150, -1))
        size_row.Add(f.width_input, 1, wx.RIGHT, 6)
        x_label = wx.StaticText(right_scroller, label="x")
        x_label.SetForegroundColour(f.text_secondary)
        x_label.SetFont(f.font_label)
        size_row.Add(x_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        f.height_input = wx.TextCtrl(right_scroller, value="1080")
        f.height_input.SetBackgroundColour(f.card_bg)
        f.height_input.SetForegroundColour(f.text_primary)
        f.height_input.SetMinSize((150, -1))
        f.height_input.SetMaxSize((150, -1))
        size_row.Add(f.height_input, 1)
        right_scroller_sizer.Add(size_row, 0, wx.EXPAND | wx.BOTTOM, 12)

        side_label = wx.StaticText(right_scroller, label="Side")
        side_label.SetForegroundColour(f.text_secondary)
        side_label.SetFont(f.font_label)
        right_scroller_sizer.Add(side_label, 0, wx.BOTTOM, 4)
        f.side_combo = wx.ComboBox(right_scroller, choices=SIDE_OPTIONS, style=wx.CB_READONLY)
        f.side_combo.SetStringSelection("top + bottom")
        f.side_combo.SetMinSize((control_width, -1))
        f.side_combo.SetMaxSize((control_width, -1))
        right_scroller_sizer.Add(f.side_combo, 0, wx.EXPAND | wx.BOTTOM, 10)

        background_label = wx.StaticText(right_scroller, label="Background")
        background_label.SetForegroundColour(f.text_secondary)
        background_label.SetFont(f.font_label)
        right_scroller_sizer.Add(background_label, 0, wx.BOTTOM, 4)
        f.background_combo = wx.ComboBox(
            right_scroller, choices=BACKGROUND_OPTIONS, style=wx.CB_READONLY
        )
        f.background_combo.SetStringSelection("transparent")
        f.background_combo.SetMinSize((control_width, -1))
        f.background_combo.SetMaxSize((control_width, -1))
        right_scroller_sizer.Add(f.background_combo, 0, wx.EXPAND | wx.BOTTOM, 10)

        quality_label = wx.StaticText(right_scroller, label="Quality")
        quality_label.SetForegroundColour(f.text_secondary)
        quality_label.SetFont(f.font_label)
        right_scroller_sizer.Add(quality_label, 0, wx.BOTTOM, 4)
        f.quality_combo = wx.ComboBox(right_scroller, choices=QUALITY_OPTIONS, style=wx.CB_READONLY)
        f.quality_combo.SetStringSelection("high")
        f.quality_combo.SetMinSize((control_width, -1))
        f.quality_combo.SetMaxSize((control_width, -1))
        right_scroller_sizer.Add(f.quality_combo, 0, wx.EXPAND | wx.BOTTOM, 10)

        f.advanced_container = wx.Panel(right_scroller)
        f.advanced_container.SetBackgroundColour(f.card_bg)
        advanced_sizer = wx.BoxSizer(wx.VERTICAL)

        advanced_label = wx.StaticText(f.advanced_container, label="Advanced")
        advanced_label.SetForegroundColour(f.text_secondary)
        advanced_label.SetFont(f.font_label)
        advanced_sizer.Add(advanced_label, 0, wx.BOTTOM, 6)

        f.floor_check = wx.CheckBox(f.advanced_container, label="Floor (shadows/post)")
        f.floor_check.SetForegroundColour(f.text_secondary)
        advanced_sizer.Add(f.floor_check, 0, wx.BOTTOM, 4)

        f.perspective_check = wx.CheckBox(f.advanced_container, label="Perspective")
        f.perspective_check.SetForegroundColour(f.text_secondary)
        advanced_sizer.Add(f.perspective_check, 0, wx.BOTTOM, 10)

        preset_label = wx.StaticText(f.advanced_container, label="Preset")
        preset_label.SetForegroundColour(f.text_secondary)
        preset_label.SetFont(f.font_label)
        advanced_sizer.Add(preset_label, 0, wx.BOTTOM, 4)
        f.preset_combo = wx.ComboBox(
            f.advanced_container, choices=PRESET_OPTIONS, style=wx.CB_READONLY
        )
        f.preset_combo.SetSelection(0)
        f.preset_combo.SetMinSize((control_width, -1))
        f.preset_combo.SetMaxSize((control_width, -1))
        advanced_sizer.Add(f.preset_combo, 0, wx.EXPAND | wx.BOTTOM, 10)

        f.zoom_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Zoom",
            "Example: 1",
            width=control_width,
        )
        f.pan_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Pan (X,Y,Z)",
            "Example: 3,0,0",
            width=control_width,
        )
        f.pivot_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Pivot (X,Y,Z)",
            "Example: -10,2,0",
            width=control_width,
        )
        f.rotate_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Rotate (X,Y,Z)",
            "Example: -45,0,45",
            width=control_width,
        )
        f.light_top_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Light top (Single number or R,G,B)",
            "Example: 0.8 or 0.8,0.8,0.8",
            width=control_width,
        )
        f.light_bottom_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Light bottom (Single number or R,G,B)",
            "Example: 0.3 or 0.3,0.3,0.3",
            width=control_width,
        )
        f.light_side_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Light side (Single number or R,G,B)",
            "Example: 0.5 or 0.5,0.5,0.5",
            width=control_width,
        )
        f.light_camera_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Light camera (Single number or R,G,B)",
            "Example: 0.2 or 0.2,0.2,0.2",
            width=control_width,
        )
        f.light_side_elevation_input = self._add_labeled_entry(
            f.advanced_container,
            advanced_sizer,
            "Light side elevation",
            "Example: 45",
            width=control_width,
        )

        f.advanced_container.SetSizer(advanced_sizer)
        f.advanced_container.Hide()

        right_scroller_sizer.Add(f.advanced_container, 0, wx.EXPAND | wx.TOP, 10)
        right_scroller.SetSizer(right_scroller_sizer)

        right_sizer.Add(right_scroller, 1, wx.EXPAND)
        right.SetSizer(right_sizer)

        f.pcb_left_panel = left
        f.pcb_right_panel = right
        f.pcb_content_sizer = content
        f.pcb_left_item = content.Add(left, 3, wx.EXPAND | wx.ALL, 10)
        f.pcb_right_item = content.Add(right, 2, wx.EXPAND | wx.ALL, 10)

        pcb_sizer.Add(content, 1, wx.EXPAND)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        f.progress_pcb = wx.Gauge(f.pcb_tab, range=100, size=(480, 18))
        f.progress_pcb.SetBackgroundColour(f.card_bg)
        f.progress_pcb.SetForegroundColour(f.progress_green)
        f.status_label_pcb = wx.StaticText(f.pcb_tab, label="Ready.")
        f.status_label_pcb.SetForegroundColour(f.text_muted)
        f.status_label_pcb.SetFont(f.font_status)
        actions.Add(f.progress_pcb, 0, wx.RIGHT, 10)
        actions.Add(f.status_label_pcb, 0, wx.ALIGN_CENTER_VERTICAL)
        actions.AddStretchSpacer()

        f.advanced_toggle = wx.CheckBox(f.pcb_tab, label="Advanced")
        f.advanced_toggle.SetForegroundColour(f.text_muted)
        actions.Add(f.advanced_toggle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        f.render_button = wx.Button(f.pcb_tab, label="Render Image")
        f.render_button.SetFont(f.font_button)
        f.render_button.SetMinSize((160, -1))
        f.render_button.SetMaxSize((160, -1))
        actions.Add(f.render_button, 0)

        pcb_sizer.Add(actions, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        f.pcb_tab.SetSizer(pcb_sizer)

    def build_schematic_tab(self):
        f = self.frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        card = wx.Panel(f.schematic_tab)
        card.SetBackgroundColour(f.card_bg)
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(card, label="Schematic Export")
        label.SetForegroundColour(f.text_primary)
        label.SetFont(f.font_label_bold)
        subtitle = wx.StaticText(card, label="Export the project schematic to a PDF.")
        subtitle.SetForegroundColour(f.text_secondary)
        subtitle.SetFont(f.font_label)
        card_sizer.Add(label, 0, wx.BOTTOM, 6)
        card_sizer.Add(subtitle, 0, wx.BOTTOM, 12)

        sch_label = wx.StaticText(card, label="Schematic file will be derived from the project.")
        sch_label.SetForegroundColour(f.text_secondary)
        sch_label.SetFont(f.font_label)
        card_sizer.Add(sch_label, 0, wx.BOTTOM, 12)

        card.SetSizer(card_sizer)
        sizer.Add(card, 0, wx.EXPAND | wx.ALL, 16)

        f.log_card_sch = wx.Panel(f.schematic_tab)
        f.log_card_sch.SetBackgroundColour(f.card_bg)
        log_card_sizer = wx.BoxSizer(wx.VERTICAL)

        log_header = wx.StaticText(f.log_card_sch, label="Log")
        log_header.SetForegroundColour(f.text_primary)
        log_header.SetFont(f.font_label_bold)
        log_card_sizer.Add(log_header, 0, wx.BOTTOM, 10)

        f.log_container_sch = wx.Panel(f.log_card_sch)
        f.log_container_sch.SetBackgroundColour(f.card_bg)
        log_container_sizer = wx.BoxSizer(wx.VERTICAL)
        f.log_text_sch = wx.TextCtrl(
            f.log_container_sch,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_RICH2,
        )
        f.log_text_sch.SetBackgroundColour(f.card_bg)
        f.log_text_sch.SetForegroundColour(f.text_primary)
        f.log_text_sch.SetFont(f.font_sub)
        log_container_sizer.Add(f.log_text_sch, 1, wx.EXPAND)
        f.log_container_sch.SetSizer(log_container_sizer)
        log_card_sizer.Add(f.log_container_sch, 1, wx.EXPAND)
        f.log_card_sch.SetSizer(log_card_sizer)
        sizer.Add(f.log_card_sch, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        f.log_spacer_sch = sizer.AddStretchSpacer(1)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        f.progress_sch = wx.Gauge(f.schematic_tab, range=100, size=(480, 18))
        f.progress_sch.SetBackgroundColour(f.card_bg)
        f.progress_sch.SetForegroundColour(f.progress_green)
        f.status_label_sch = wx.StaticText(f.schematic_tab, label="Ready.")
        f.status_label_sch.SetForegroundColour(f.text_muted)
        f.status_label_sch.SetFont(f.font_status)
        actions.Add(f.progress_sch, 0, wx.RIGHT, 10)
        actions.Add(f.status_label_sch, 0, wx.ALIGN_CENTER_VERTICAL)
        actions.AddStretchSpacer()
        f.export_schematic_button = wx.Button(f.schematic_tab, label="Export Schematic PDF")
        f.export_schematic_button.SetFont(f.font_button)
        f.export_schematic_button.SetMinSize((180, -1))
        f.export_schematic_button.SetMaxSize((180, -1))
        actions.Add(f.export_schematic_button, 0)
        sizer.Add(actions, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        f.schematic_tab.SetSizer(sizer)

    def build_layout_tab(self):
        f = self.frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        card = wx.Panel(f.layout_tab)
        card.SetBackgroundColour(f.card_bg)
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(card, label="Layout Export")
        label.SetForegroundColour(f.text_primary)
        label.SetFont(f.font_label_bold)
        subtitle = wx.StaticText(card, label="Export PCB layer PDFs and combine into one document.")
        subtitle.SetForegroundColour(f.text_secondary)
        subtitle.SetFont(f.font_label)
        card_sizer.Add(label, 0, wx.BOTTOM, 6)
        card_sizer.Add(subtitle, 0, wx.BOTTOM, 12)

        layers_label = wx.StaticText(card, label="Layers (auto-detected from project)")
        layers_label.SetForegroundColour(f.text_secondary)
        layers_label.SetFont(f.font_label)
        card_sizer.Add(layers_label, 0, wx.BOTTOM, 6)

        f.layers_value = wx.StaticText(card, label="None")
        f.layers_value.SetForegroundColour(f.text_muted)
        f.layers_value.SetFont(f.font_sub)
        card_sizer.Add(f.layers_value, 0, wx.BOTTOM, 8)

        f.change_layers_button = wx.Button(card, label="Change layers")
        f.change_layers_button.SetFont(f.font_sub)
        f.change_layers_button.SetMinSize((140, -1))
        f.change_layers_button.SetMaxSize((140, -1))
        card_sizer.Add(f.change_layers_button, 0, wx.BOTTOM, 12)

        card.SetSizer(card_sizer)
        sizer.Add(card, 0, wx.EXPAND | wx.ALL, 16)

        f.log_card_layout = wx.Panel(f.layout_tab)
        f.log_card_layout.SetBackgroundColour(f.card_bg)
        log_card_sizer = wx.BoxSizer(wx.VERTICAL)

        log_header = wx.StaticText(f.log_card_layout, label="Log")
        log_header.SetForegroundColour(f.text_primary)
        log_header.SetFont(f.font_label_bold)
        log_card_sizer.Add(log_header, 0, wx.BOTTOM, 10)

        f.log_container_layout = wx.Panel(f.log_card_layout)
        f.log_container_layout.SetBackgroundColour(f.card_bg)
        log_container_sizer = wx.BoxSizer(wx.VERTICAL)
        f.log_text_layout = wx.TextCtrl(
            f.log_container_layout,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_RICH2,
        )
        f.log_text_layout.SetBackgroundColour(f.card_bg)
        f.log_text_layout.SetForegroundColour(f.text_primary)
        f.log_text_layout.SetFont(f.font_sub)
        log_container_sizer.Add(f.log_text_layout, 1, wx.EXPAND)
        f.log_container_layout.SetSizer(log_container_sizer)
        log_card_sizer.Add(f.log_container_layout, 1, wx.EXPAND)
        f.log_card_layout.SetSizer(log_card_sizer)
        sizer.Add(f.log_card_layout, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        f.log_spacer_layout = sizer.AddStretchSpacer(1)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        f.progress_layout = wx.Gauge(f.layout_tab, range=100, size=(480, 18))
        f.progress_layout.SetBackgroundColour(f.card_bg)
        f.progress_layout.SetForegroundColour(f.progress_green)
        f.status_label_layout = wx.StaticText(f.layout_tab, label="Ready.")
        f.status_label_layout.SetForegroundColour(f.text_muted)
        f.status_label_layout.SetFont(f.font_status)
        actions.Add(f.progress_layout, 0, wx.RIGHT, 10)
        actions.Add(f.status_label_layout, 0, wx.ALIGN_CENTER_VERTICAL)
        actions.AddStretchSpacer()
        f.export_layout_button = wx.Button(f.layout_tab, label="Export Layout PDFs")
        f.export_layout_button.SetFont(f.font_button)
        f.export_layout_button.SetMinSize((180, -1))
        f.export_layout_button.SetMaxSize((180, -1))
        actions.Add(f.export_layout_button, 0)
        sizer.Add(actions, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        f.layout_tab.SetSizer(sizer)

    def _add_labeled_entry(self, parent, sizer, label, hint, width=None):
        f = self.frame
        label_text = wx.StaticText(parent, label=label)
        label_text.SetForegroundColour(f.text_secondary)
        label_text.SetFont(f.font_label)
        sizer.Add(label_text, 0, wx.BOTTOM, 4)
        entry = wx.TextCtrl(parent)
        entry.SetBackgroundColour(f.card_bg)
        entry.SetForegroundColour(f.text_primary)
        if width:
            entry.SetMinSize((width, -1))
            entry.SetMaxSize((width, -1))
        sizer.Add(entry, 0, wx.EXPAND | wx.BOTTOM, 4)
        hint_text = wx.StaticText(parent, label=hint)
        hint_text.SetForegroundColour(f.text_muted)
        hint_text.SetFont(f.font_banner_sub)
        sizer.Add(hint_text, 0, wx.BOTTOM, 10)
        return entry
