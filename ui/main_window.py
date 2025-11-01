from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QGridLayout, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
import logging
from services.weather_client import fetch_weather_data
from config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Загрузка данных стран/городов
        self.countries_data = self._load_countries_data()

        # Выпадающий список стран
        self.country_combo = QComboBox()
        self.country_combo.addItem("-- Не выбрано --")
        for code, data in self.countries_data.items():
            self.country_combo.addItem(f"{data['name']} ({code})", code)
        self.country_combo.currentTextChanged.connect(self._on_country_changed)

        # Выпадающий список городов
        self.city_combo = QComboBox()
        self.city_combo.addItem("-- Не выбрано --")
        self.city_combo.currentTextChanged.connect(self._on_city_selected)

        # Кнопка «Обновить»
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self._fetch_weather)
        self.refresh_btn.setEnabled(False)  # Пока город не выбран

        # Размещение элементов
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Страна:"))
        input_layout.addWidget(self.country_combo)
        input_layout.addWidget(QLabel("Город:"))
        input_layout.addWidget(self.city_combo)
        input_layout.addWidget(self.refresh_btn)
        layout.addLayout(input_layout)


        # Статусная строка
        self.status_label = QLabel("Выберите страну и город")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Группа с данными погоды
        weather_group = QGroupBox("Данные о погоде")
        weather_layout = QGridLayout()
        weather_group.setLayout(weather_layout)
        layout.addWidget(weather_group)

        # Словарь меток для данных
        self.labels = {}
        row = 0

        fields = [
            ("city_name", "Город"),
            ("country", "Страна"),
            ("lat", "Широта (град.)"),
            ("lon", "Долгота (град.)"),
            ("temp", "Температура (°C)"),
            ("feels_like", "Ощущается как (°C)"),
            ("temp_min", "Мин. температура (°C)"),
            ("temp_max", "Макс. температура (°C)"),
            ("pressure", "Давление (гПа)"),
            ("humidity", "Влажность (%)"),
            ("wind_speed", "Скорость ветра (м/с)"),
            ("clouds", "Облачность (%)"),
            ("weather_description", "Описание"),
            ("sunrise", "Восход"),
            ("sunset", "Закат"),
            ("dt", "Время измерения")
        ]

        for key, desc in fields:
            label_desc = QLabel(f"{desc}:")
            label_value = QLabel("--")
            self.labels[key] = label_value
            weather_layout.addWidget(label_desc, row, 0)
            weather_layout.addWidget(label_value, row, 1)
            row += 1

        # Растягиваем последнюю строку
        weather_layout.setRowStretch(row, 1)

    def _load_countries_data(self) -> dict:
        """Загружает данные стран и городов из JSON-файла"""
        try:
            with open("data/cities_countries.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Ошибка загрузки данных стран/городов: {e}")
            return {}

    def _on_country_changed(self, text: str):
        """Обновляет список городов при выборе страны и статус"""
        code = self.country_combo.currentData()
        if code and code in self.countries_data:
            cities = self.countries_data[code]["cities"]
            self.city_combo.clear()
            self.city_combo.addItem("-- Не выбрано --")
            self.city_combo.addItems(cities)
            # Страна выбрана, но город ещё нет
            self._show_status("Выберите город", "orange")
            self.refresh_btn.setEnabled(False)
        else:
            # Страна не выбрана
            self.city_combo.clear()
            self.city_combo.addItem("-- Не выбрано --")
            self._show_status("Выберите страну", "red")
            self.refresh_btn.setEnabled(False)

    def _on_city_selected(self, text: str):
        """Обрабатывает выбор города и управляет статусом/кнопкой"""
        if text == "-- Не выбрано --":
            # Город сброшен
            self.refresh_btn.setEnabled(False)
            self._clear_weather()
            # Проверяем, выбрана ли страна
            if self.country_combo.currentIndex() > 0:
                self._show_status("Выберите город", "orange")
            else:
                self._show_status("Выберите страну", "red")
        else:
            # Город выбран — запрашиваем погоду
            self.refresh_btn.setEnabled(True)
            self._fetch_weather()

    def _fetch_weather(self):
        """Запрос погоды по выбранному городу"""
        city = self.city_combo.currentText()
        if not city or city == "-- Не выбрано --":
            self._show_status("Выберите город", "orange")
            return

        self._show_status("Загрузка...", "orange")

        weather = fetch_weather_data(city)

        if weather:
            self._update_ui(weather)
            self._show_status("Данные обновлены", "green")
        else:
            self._show_status("Ошибка загрузки", "red")

    def _clear_weather(self):
        """Очищает все поля погоды"""
        for label in self.labels.values():
            label.setText("--")

    def _show_status(self, message: str, color: str):
        """Обновляет статусную строку с заданным цветом"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")

    def _update_ui(self, data: dict):
        """Обновление меток интерфейса"""
        for key, label in self.labels.items():
            value = data.get(key, "--")
            if isinstance(value, float):
                label.setText(f"{value:.1f}")
            else:
                label.setText(str(value))