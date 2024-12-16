import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QFileDialog, QComboBox, QLineEdit
)

class DataAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("6лаб")
        self.data = None


        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)


        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)


        self.button_layout = QHBoxLayout()


        self.load_button = QPushButton("Загрузить файл")
        self.load_button.clicked.connect(self.load_data)
        self.button_layout.addWidget(self.load_button)


        self.plot_button = QPushButton("Нарисовать график")
        self.plot_button.clicked.connect(self.plot_graph)
        self.button_layout.addWidget(self.plot_button)


        self.layout.addLayout(self.button_layout)


        self.stats_label = QLabel("Статистика будет здесь")
        self.layout.addWidget(self.stats_label)


        self.chart_selector = QComboBox()
        self.chart_selector.addItems(["Line Chart", "Histogram", "Pie Chart"])
        self.layout.addWidget(self.chart_selector)


        self.add_data_layout = QHBoxLayout()
        self.new_data_input = QLineEdit()
        self.add_data_button = QPushButton("Добавить данные(Date,Value1,Value2,Category)")
        self.add_data_button.clicked.connect(self.add_data)
        self.add_data_layout.addWidget(self.new_data_input)
        self.add_data_layout.addWidget(self.add_data_button)
        self.layout.addLayout(self.add_data_layout)

    def load_data(self):
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Load CSV File", "", "CSV Files (*.csv)", options=options)
            if not file_path:
                self.stats_label.setText("Ошибка")
                return

            self.data = pd.read_csv(file_path)

            expected_columns = {"Date", "Value1", "Value2", "Category"}
            missing_columns = expected_columns - set(self.data.columns)
            if missing_columns:
                self.stats_label.setText(f"Missing columns: {', '.join(missing_columns)}")
                self.data = None
                return


            stats = (
                f"Строки: {self.data.shape[0]}, Столбцы: {self.data.shape[1]}\n"
                f"Мин:\n{self.data.min(numeric_only=True)}\n"
                f"Maкс:\n{self.data.max(numeric_only=True)}\n"
                f"Среднее:\n{self.data.mean(numeric_only=True)}\n"
            )
            self.stats_label.setText(stats)

        except Exception as e:
            self.stats_label.setText(f"Ошибка чтеня: {str(e)}")
            self.data = None

    def plot_graph(self):
        chart_type = self.chart_selector.currentText()
        self.figure.clear()

        try:
            ax = self.figure.add_subplot(111)

            if chart_type == "Line Chart":
                if "Date" in self.data.columns and "Value1" in self.data.columns:

                    self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')
                    self.data.dropna(subset=["Date"], inplace=True)
                    ax.plot(self.data["Date"], self.data["Value1"])
                    ax.set_title("Линейный")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Value1")
                    self.figure.autofmt_xdate(rotation=45)
                else:
                    raise ValueError("Столбцы 'Date' и 'Value1' пропали!")

            elif chart_type == "Histogram":
                if "Date" in self.data.columns and "Value2" in self.data.columns:
                    self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')
                    self.data.dropna(subset=["Date"], inplace=True)
                    ax.bar(self.data["Date"], self.data["Value2"])
                    ax.set_title("Гистрограмма")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Value2")
                    self.figure.autofmt_xdate(rotation=45)  # Поворот меток на оси X
                else:
                    raise ValueError("Столбцы 'Date' и 'Value2' пропали!")

            elif chart_type == "Pie Chart":
                if "Category" in self.data.columns:
                    category_counts = self.data["Category"].value_counts()
                    ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
                    ax.set_title("Пирог")
                else:
                    raise ValueError("'Category' пропал")

            self.canvas.draw()  # Обновляем график
        except Exception as e:
            self.stats_label.setText(f"Ошибка: {str(e)}")

    def add_data(self):
        if self.data is None:
            self.stats_label.setText("Сначала загрузите файл")
            return

        new_data = self.new_data_input.text()
        if not new_data:
            self.stats_label.setText("Пусто")
            return

        try:
            new_values = new_data.split(',')
            if len(new_values) != len(self.data.columns):
                raise ValueError(
                    f"Ято то не так, ожидали {len(self.data.columns)} значений, но получили {len(new_values)}."
                )


            new_row = {col: val for col, val in zip(self.data.columns, new_values)}
            self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)

            # Обновляем статистику и график
            self.stats_label.setText("данные добавлены")
            self.plot_graph()
        except Exception as e:
            self.stats_label.setText(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAnalysisApp()
    window.show()
    sys.exit(app.exec_())
