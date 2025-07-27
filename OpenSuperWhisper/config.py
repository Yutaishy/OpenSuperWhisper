from PySide6.QtCore import QSettings

ORG_NAME = "OpenSuperWhisperProject"
APP_NAME = "OpenSuperWhisperApp"
settings = QSettings(ORG_NAME, APP_NAME)

KEY_ASR_MODEL = "models/asr_model"
KEY_CHAT_MODEL = "models/chat_model"
KEY_POST_FORMAT = "pipeline/enable_post_format"
KEY_PROMPT_TEXT = "formatting/prompt_text"
KEY_STYLE_GUIDE_PATH = "formatting/styleguide_path"
KEY_WINDOW_GEOMETRY = "ui/window_geometry"
KEY_API_KEY = "api/openai_key"
KEY_PROMPT_PRESETS = "formatting/prompt_presets"
KEY_CURRENT_PRESET = "formatting/current_preset"

def save_setting(key: str, value):
    settings.setValue(key, value)

def load_setting(key: str, default=None):
    return settings.value(key, default)
