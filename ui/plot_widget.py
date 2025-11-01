from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
import plotly.graph_objects as go
import io
from PIL import Image


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Метка для отображения изображения графика
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

    def update_plot(self, measurements: list):
        """Обновляет график на основе списка измерений"""
        if not measurements:
            self.show_empty_plot("Нет данных для отображения")
            return

        # Создаём график Plotly
        fig = go.Figure()

        # Временные метки (удаляем 'Z' для корректного отображения)
        timestamps = [item["date"].replace("Z", "") for item in measurements]

        # Добавляем линии для параметров
        for param in ["temperature", "pressure", "humidity", "pm25", "pm10"]:
            values = [item.get(param) for item in measurements]
            if any(v is not None for v in values):
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=param.upper()
                ))

        # Настройка макета
        fig.update_layout(
            title="Динамика показателей",
            xaxis_title="Время",
            yaxis_title="Значения",
            hovermode="x unified",
            template="plotly_white"
        )

        # Экспортируем график в PNG
        img_bytes = fig.to_image(format="png", width=800, height=400)
        img = Image.open(io.BytesIO(img_bytes))
        pixmap = QPixmap.fromImage(img.toqimage())

        # Отображаем в QLabel
        self.label.setPixmap(pixmap)

    def show_empty_plot(self, message: str):
        """Отображает текстовое сообщение"""
        self.label.setText(message)
        self.label.setStyleSheet("font-size: 14px; color: gray;")
