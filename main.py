import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from src.gui.custom_widgets import DUO_ToolKit

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'duo_toolkit.log'), mode='w'),
    ]
)

logging.debug("This is a test log message")

if __name__ == "__main__":
    try:
        logging.info("Starting application")
        app = QApplication(sys.argv)
        logging.info("Creating main window")
        window = DUO_ToolKit()
        logging.info("Showing main window")
        window.show()
        logging.info("Entering main event loop")
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        import traceback
        logging.error(traceback.format_exc())
        input("Press Enter to exit...")
