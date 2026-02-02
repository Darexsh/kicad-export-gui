KICAD_CMD_DEFAULT = r"C:\Program Files\KiCad\9.0\bin\kicad-cmd.bat"

APP_BG = "#f4f6f9"
CARD_BG = "#ffffff"
CARD_BORDER = "#d9e1ea"
TEXT_PRIMARY = "#1b2430"
TEXT_SECONDARY = "#2f3a48"
TEXT_MUTED = "#5b6b7c"
TEXT_DISABLED = "#94a3b8"
ACCENT = "#2563eb"
ACCENT_DARK = "#1d4ed8"
BUTTON_BG = ACCENT
BUTTON_TEXT = "#ffffff"
BUTTON_HOVER = ACCENT_DARK
TAB_HOVER_BG = "#e6eefc"
PROGRESS_GREEN = "#22c55e"
PROGRESS_GREEN_DARK = "#16a34a"
PROGRESS_BORDER = CARD_BORDER
LISTBOX_SELECT = "#e2e8f0"

RESOLUTION_OPTIONS = [
    "720p (1280x720)",
    "1080p (1920x1080)",
    "2k (2560x1440)",
    "4k (3840x2160)",
]
RESOLUTION_MAP = {
    "720p (1280x720)": (1280, 720),
    "1080p (1920x1080)": (1920, 1080),
    "2k (2560x1440)": (2560, 1440),
    "4k (3840x2160)": (3840, 2160),
}

SIDE_OPTIONS = ["top", "bottom", "left", "right", "front", "back", "top + bottom"]
BACKGROUND_OPTIONS = ["default", "transparent", "opaque"]
QUALITY_OPTIONS = ["basic", "high", "user"]
PRESET_OPTIONS = ["", "follow_pcb_editor", "follow_plot_settings", "legacy_preset_flag"]
