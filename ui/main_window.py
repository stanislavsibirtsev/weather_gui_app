from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QGridLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from services.api_client import WeatherAPI
from models.database import MySQLManager
from ui.plot_widget import PlotWidget
from utils.helpers import parse_datetime_to_iso
import config


class MainWindow(QMainWindow):
    def __init__(self, save_to_db=True):  # Принимаем параметр, но не используем в GUI-логике
        super().__init__()
        self.save_to_db = save_to_db  # Сохраняем флаг для дальнейшей обработки

        self.setWindowTitle(f"Погода — {config.MYSQL_DATABASE}")
        self.resize(1200, 800)

        # Инициализация сервисов
        self.api = WeatherAPI(config.API_KEY)
        self.db = MySQLManager()
        if self.save_to_db:
            self.db.connect()
            self.db.create_table()

        # Основной контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Секция управления
        control_group = QGroupBox("Управление")
        control_layout = QHBoxLayout()

        self.fetch_btn = QPushButton("Получить погоду")
        self.fetch_btn.setStyleSheet("""
            padding: 12px;
            font-weight: bold;
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
        """)
        self.fetch_btn.setToolTip("Запросить данные за последний час")

        control_layout.addWidget(self.fetch_btn)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # 2. Секция текущих показателей
        data_group = QGroupBox("Текущие показатели")
        data_layout = QGridLayout()

        self.fields = {
            "temperature": "Температура (°C)",
            "pressure": "Давление (гПа)",
            "humidity": "Влажность (%)",
            "pm25": "PM₂.₅ (мкг/м³)",
            "pm10": "PM₁₀ (мкг/м³)",
            "co": "CO (мг/м³)",
            "no2": "NO₂ (мг/м³)",
            "so2": "SO₂ (мг/м³)",
            "o3": "O₃ (мг/м³)",
            "h2s": "H₂S (мг/м³)",
            "aqi": "AQI"
        }

        self.labels = {}
        row = 0
        for key, label_text in self.fields.items():
            data_layout.addWidget(QLabel(label_text), row, 0)
            value_label = QLabel("—")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value_label.setStyleSheet("font-size: 16px; padding: 4px;")
            self.labels[key] = value_label
            data_layout.addWidget(value_label, row, 1)
            row += 1

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # 3. Секция управления графиком
        plot_controls_group = QGroupBox("Настройки графика")
        plot_controls_layout = QHBoxLayout()

        # Чекбоксы для выбора отображаемых параметров (можно расширить логику)
        for field, label in self.fields.items():
            cb = QCheckBox(label.split(" (")[0])
            cb.setChecked(True)
            plot_controls_layout.addWidget(cb)
        plot_controls_group.setLayout(plot_controls_layout)
        main_layout.addWidget(plot_controls_group)


        # 4. Секция графика
        plot_group = QGroupBox("Динамика показателей за последний час")
        plot_layout = QVBoxLayout()
        self.plot_widget = PlotWidget()
        plot_layout.addWidget(self.plot_widget)
        plot_group.setLayout(plot_layout)
        main_layout.addWidget(plot_group)


        # Подключение сигналов
        self.fetch_btn.clicked.connect(self.fetch_weather)

    def fetch_weather(self):
        """Получает погоду через API и сохраняет в БД (если save_to_db=True)"""
        try:
            # Шаг 1: Получаем последнюю станцию
            post = self.api.get_latest_post()
            post_id = post["id"]

            # Шаг 2: Получаем измерения
            measurements = self.api.get_measurements(post_id)


            if not measurements:
                QMessageBox.warning(self, "Нет данных", "Не получено данных за последний час.")
                return

            # Шаг 3: Сохраняем в БД, если разрешено
            if self.save_to_db:
                for item in measurements:
                    raw_date = item.get("date")
                    if not raw_date:
                        continue
                    dt_iso = parse_datetime_to_iso(raw_date)

                    data = {
                        "datetime": dt_iso,
                        "temperature": item.get("temperature"),
                        "pressure": item.get("pressure"),
                        "humidity": item.get("humidity"),
                        "pm25": item.get("pm2"),
                        "pm10": item.get("pm10"),
                        "co": item.get("co"),
                        "no2": item.get("no2"),
                        "so2": item.get("so2"),
                        "o3": item.get("o3"),
                        "h2s": item.get("h2s"),
                        "aqi": item.get("aqi", {}).get("instantAqi", {}).get("value10")
                    }
                    self.db.insert_measurement(data)

            # Шаг 4: Обновляем интерфейс и график
            latest = measurements[-1]
            self.update_ui(latest)
            self.plot_widget.update_plot(measurements)

            QMessageBox.information(self, "Успех", "Данные получены и сохранены в БД.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")

    def update_ui(self, data: dict):
        """Обновляет метки интерфейса на основе полученных данных"""
        for key, label in self.labels.items():
            value = data.get(key)
            if value is not None:
                if key in ["temperature", "pressure", "humidity", "aqi"]:
                    label.setText(f"{value:.1f}")
                else:
                    label.setText(f"{value:.3f}")
            else:
                label.setText("—")
