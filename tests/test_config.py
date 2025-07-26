import OpenSuperWhisper.config as config

def test_settings_save_and_load():
    config.save_setting("test/key1", "value1")
    val = config.load_setting("test/key1")
    assert val == "value1"

def test_settings_default_value():
    val = config.load_setting("nonexistent/key", "default_val")
    assert val == "default_val"