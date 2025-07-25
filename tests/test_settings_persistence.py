from PyQt6.QtCore import QSettings


def test_qsettings_persistence(tmp_path):
    ini_file = tmp_path / "settings.ini"
    settings = QSettings(str(ini_file), QSettings.Format.IniFormat)
    settings.setValue("foo", "bar")
    settings.sync()

    settings2 = QSettings(str(ini_file), QSettings.Format.IniFormat)
    assert settings2.value("foo") == "bar" 