import sys
import os
from PySide6.QtWidgets import QApplication
from .ui_mainwindow import MainWindow
from . import config

def main():
    app = QApplication(sys.argv)
    
    # Check for OpenAI API key - first from environment, then from stored settings
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        stored_key = config.load_setting(config.KEY_API_KEY, "")
        if stored_key:
            os.environ["OPENAI_API_KEY"] = stored_key
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(None, "API Key Required", 
                               "Please set your OpenAI API key using Settings → Set OpenAI API Key... menu.")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()