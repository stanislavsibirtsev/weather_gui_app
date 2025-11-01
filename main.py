import sys
import argparse
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Не сохранять данные в БД (тестовый режим)"
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(save_to_db=not args.no_db)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
