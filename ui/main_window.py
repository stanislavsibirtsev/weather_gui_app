from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QGroupBox, QCheckBox, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from ui.plot_widget import PlotWidget
from services.api_client import WeatherAPI
from models.database import WeatherDB
from models.weather_model import WeatherData
import config
from datetime import datetime, timedelta


class MainWindow(QMainWindow):
    def __init__(self, save_to_db=True):
        super().__init__()
        self.save_to_db = save_to_db
        self.db = WeatherDB(config.DB_PATH)
        self.api = WeatherAPI(config.API_KEY)
        
        # Инициализация UI
        self.setup_ui()
        self.load_cities()
        
        # Сразу загружаем погоду для дефолтного города
        self.fetch_weather()

    def setup_ui(self):
        """Настройка основного интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной вертикальный макет
        main_layout = QVBoxLayout(central_widget)
        
        # 1. Секция выбора города
        city_group = QGroupBox("Выбор местоположения")
        city_layout = QHBoxLayout()
        
        self.city_combo = QComboBox()
        self.city_combo.setMinimumWidth(200)
        
        self.country_combo = QComboBox()
        self.country_combo.addItems(["RU", "US", "GB", "DE", "JP", "CN"])
        self.country_combo.setMaximumWidth(80)
        
        self.refresh_btn = QPushButton("Обновить погоду")
        self.refresh_btn.setStyleSheet("padding: 5px;")
        
        city_layout.addWidget(QLabel("Город:"))
        city_layout.addWidget(self.city_combo)
        city_layout.addWidget(QLabel("Страна:"))
        city_layout.addWidget(self.country_combo)
        city_layout.addWidget(self.refresh_btn)
        city_group.setLayout(city_layout)
        
        main_layout.addWidget(city_group)
        
        # 2. Секция погодных данных
        weather_group = QGroupBox("Актуальные данные")
        weather_layout = QGridLayout()
        
        # Список отображаемых параметров
        self.display_fields = [
            ("temp", "Температура (°C)"),
            ("feels_like", "Ощущается как (°C)"),
            ("pressure", "Давление (гПа)"),
            ("humidity", "Влажность (%)"),
            ("dew_point", "Точка росы (°C)"),
            ("uvi", "УФ-индекс"),
            ("clouds", "Облачность (%)"),
            ("visibility", "Видимость (м)"),
            ("wind_speed", "Скорость ветра (м/с)"),
            ("wind_deg", "Направление ветра (°)")
        ]
        
        self.data_labels = {}
        row = 0
        for field, label_text in self.display_fields:
            weather_layout.addWidget(QLabel(label_text), row, 0)
            value_label = QLabel("—")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.data_labels[field] = value_label
            weather_layout.addWidget(value_label, row, 1)
            row += 1
        
        weather_group.setLayout(weather_layout)
        main_layout.addWidget(weather_group)
        
        # 3. Секция графика
        plot_group = QGroupBox("Динамика показателей")
        plot_layout = QVBoxLayout()
        
        # Чекбоксы выбора параметров для графика
        checkbox_layout = QHBoxLayout()
        self.checkboxes = {}
        for field, _ in self.display_fields:
            cb = QCheckBox(field.replace("_", " ").capitalize())
            cb.setChecked(True)  # По умолчанию все включены
            cb.stateChanged.connect(self.on_plot_option_changed)
            checkbox_layout.addWidget(cb)
            self.checkboxes[field] = cb
        
        plot_layout.addLayout(checkbox_layout)
        
        # Виджет графика
        self.plot_widget = PlotWidget()
        plot_layout.addWidget(self.plot_widget)
        
        plot_group.setLayout(plot_layout)
        main_layout.addWidget(plot_group)
        
        # Подключение сигналов
        self.refresh_btn.clicked.connect(self.fetch_weather)
        self.city_combo.currentIndexChanged.connect(self.on_city_changed)

    def load_cities(self):
        """Загрузка списка городов в комбобокс"""
        cities = [
            ("Москва", "RU"),
            ("Санкт‑Петербург", "RU"),
            ("Новосибирск", "RU"),
            ("Екатеринбург", "RU"),
            ("Казань", "RU"),
            ("Нью‑Йорк", "US"),
            ("Лондон", "GB"),
            ("Берлин", "DE"),
            ("Токио", "JP"),
            ("Пекин", "CN")
        ]
        
        for city, country in cities:
            self.city_combo.addItem(city, (city, country))
        
        # Устанавливаем дефолтный город
        default_index = self.city_combo.findData((config.DEFAULT_CITY, config.DEFAULT_COUNTRY))
        if default_index != -1:
            self.city_combo.setCurrentIndex(default_index)

    def on_city_changed(self):
        """Обработчик смены города — автоматически обновляем погоду"""
        self.fetch_weather()

    def fetch_weather(self):
        """Получение погоды для выбранного города"""
        try:
            city, country = self.city_combo.currentData()
            weather = self.api.get_current_weather(city, country)
            
            # Отображаем данные
            self.display_weather(weather)
            
            # Сохраняем в БД, если разрешено
            if self.save_to_db:
                self.db.save_weather(city, country, weather)
            
            # Обновляем график
            self.update_plot(city, country)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось получить погоду:\n{str(e)}"
            )

    def display_weather(self, weather: WeatherData):
        """Отображение погодных данных в интерфейсе"""
        for field in self.data_labels:
            value = getattr(weather, field)
            if value is not None:
                if field == "temp" or field == "feels_like" or field == "dew_point":
                    self.data_labels[field].setText(f"{value:.1f}")
                elif field == "wind_speed":
                    self.data_labels[field].setText(f"{value:.2f}")
                else:
                    self.data_labels[field].setText(str(value))
            else:
                self.data_labels[field].setText("—")

    def update_plot(self, city: str, country: str):
        """Обновление графика с выбранными параметрами"""
        # Получаем данные за последние 24 часа
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        try:
            data = self.db.get_data_for_plot(city, country, start_time, end_time)
            
            if not data:
                self.plot_widget.clear()
                self.plot_widget.ax.text(
                    0.5, 0.5, "Нет данных для отображения",
                    transform=self.plot_widget.ax.transAxes,
                    ha='center', va='center'
                )
                self.plot_widget.canvas.draw()
                return

            self.plot_widget.clear()

            # Добавляем выбранные серии на график
            for field, checkbox in self.checkboxes.items():
                if checkbox.isChecked():
                    timestamps = [item["timestamp"] for item in data if item[
