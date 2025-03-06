import tkinter as tk
from tkinter import ttk
import threading
import time
import os

# Función para la importación de módulos
def importar_modulos():
    global sys, queue, threading, serial, np, matplotlib
    global plt, animation, FigureCanvas, uic, QApplication, QMainWindow
    global QVBoxLayout, QWidget, QFileDialog, QMessageBox, QAction, QComboBox
    global QCheckBox, QPushButton, pyqtSignal, spectrogram, csv, datetime, QIcon

    import sys
    import queue
    import threading
    import serial
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from PyQt5 import uic
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QAction, QComboBox, QCheckBox, QPushButton)
    from PyQt5.QtCore import pyqtSignal
    from scipy.signal import spectrogram
    import csv
    from datetime import datetime
    from PyQt5.QtGui import QIcon

    print("Módulos importados")

    # Programar el cierre de la ventana después de la importación de las librerías
    root.after(1, root.destroy)

def mostrar_progreso():
    global root
    root = tk.Tk()
    root.title("Movement")
    root.geometry("300x100")
    root.iconbitmap('movement.ico')
    label = tk.Label(root, text="Cargando módulos, por favor espere...", padx=20, pady=20)
    label.pack()

    progress = ttk.Progressbar(root, orient="horizontal", length=250, mode="indeterminate")
    progress.pack(pady=10)
    progress.start()

    # Ejecuta la función de importación en un hilo separado al principal
    threading.Thread(target=importar_modulos, daemon=True).start()

    root.mainloop()

mostrar_progreso()




# Función para escanear puertos seriales disponibles
def scan_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]
    return port_list

# Función para obtener el tiempo actual con microsegundos únicos
last_microseconds = -1

def get_unique_microseconds():
    global last_microseconds
    while True:
        now = datetime.now()
        microseconds = now.microsecond
        if microseconds != last_microseconds:
            last_microseconds = microseconds
            return now.strftime('%H:%M:%S.') + f'{microseconds:06d}'

# Ventana de Configuración usando main.ui
class ConfigWindow(QMainWindow):
    config_ready = pyqtSignal(dict)  # Señal para pasar la configuración

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        # Acceder a los widgets desde el archivo .ui
        self.combo_box = self.findChild(QComboBox, 'puertos')
        self.combo_box.addItems(scan_ports())
        self.check_box = self.findChild(QCheckBox, 'guardar_datos')
        self.boton = self.findChild(QPushButton, 'iniciar')

        self.boton.clicked.connect(self.obtener_informacion)

    def mostrar_advertencia(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText("El sismógrafo no está conectado, por favor conéctelo.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def obtener_informacion(self):
        informacion = {}
        # Comprobar el estado del CheckBox
        informacion['guardar_datos'] = self.check_box.isChecked()
        if self.combo_box.currentText() == "":
            self.mostrar_advertencia()
            self.combo_box.addItems(scan_ports())
            return
        else:
            informacion['puerto_serial'] = self.combo_box.currentText()

        # Si el checkbox está marcado, obtener la ruta del directorio seleccionado
        if informacion['guardar_datos']:
            directory = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta para guardar los datos")
            if directory:
                informacion['ruta_guardado'] = directory
            else:
                informacion['guardar_datos'] = False
                informacion['ruta_guardado'] = None
        else:
            informacion['ruta_guardado'] = None

        self.config_ready.emit(informacion)
        self.close()

# Ventana para mostrar la gráfica
class PlotWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("Movement")
        self.showMaximized()  # Aumentar el tamaño de la ventana
        self.setWindowIcon(QIcon('movement.ico'))
        self.running = True
        self.ser=None
        # Crear el widget de Matplotlib
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Aumentar el tamaño de la figura
        self.fig, self.axes = plt.subplots(3, 2, figsize=(16, 10.5))  # Ajusta el tamaño de la figura
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.canvas.setSizePolicy(1, 1)
        self.canvas.updateGeometry()

        # Crear menú
        menubar = self.menuBar()
        opciones_menu = menubar.addMenu('Opciones')
        self.actionRecalibrar = QAction('Recalibrar', self)
        opciones_menu.addAction(self.actionRecalibrar)
        self.actionRecalibrar.triggered.connect(self.recalibrate)

        # Inicialización de los datos
        self.fs = 450  # Frecuencia de muestreo (Hz)
        self.window_size = 1800  # Número de muestras a mostrar
        self.data_queue = queue.Queue()  # Cola para almacenar los datos recibidos

        self.data_x = np.zeros(self.window_size)
        self.data_y = np.zeros(self.window_size)
        self.data_z = np.zeros(self.window_size)
        self.time = np.arange(0, self.window_size) / self.fs  # Tiempo en segundos
        self.colors = ['r', 'g', 'b']  # Rojo para X, Verde para Y, Azul para Z

        self.lines = []
        self.ylabels = []  # Lista para almacenar las referencias a las etiquetas del eje Y
        for i, ax in enumerate(self.axes[:, 0]):
            line, = ax.plot(self.time, np.zeros(self.window_size), color=self.colors[i])
            self.lines.append(line)
            ax.grid(True)
            ax.margins(x=0.1, y=0.1)  # Margen interno del subplot
            ylabel = ax.text(1.02, 0.5, '', transform=ax.transAxes, va='center')
            self.ylabels.append(ylabel)

        self.im = []
        for i, ax in enumerate(self.axes[:, 1]):
            img = ax.imshow(np.zeros((256, self.window_size)), aspect='auto', origin='lower',
                            extent=[0, self.window_size/self.fs, 0, self.fs/2], cmap='viridis')
            self.im.append(img)
            self.fig.colorbar(img, ax=ax)
            ax.set_ylim(0, self.fs/2)  # Establecer límites iniciales de frecuencia
            ax.margins(x=0.1, y=0.1)  # Margen interno del subplot

        # Eliminar leyendas y etiquetas de ejes
        for ax in self.axes.flatten():
            ax.set_xticklabels([])  # Eliminar etiquetas del eje X
            ax.set_yticklabels([])  # Eliminar etiquetas del eje Y

        # Ajustar los márgenes
        plt.subplots_adjust(left=0.01, right=1.03, bottom=0.1, top=0.975, hspace=0.2, wspace=0.1)

        self.ani = animation.FuncAnimation(self.fig, self.update_data, blit=True, interval=1000/self.fs, cache_frame_data=False)

        self.config = config
        self.guardar_datos = config.get('guardar_datos', False)
        self.serial_port = config.get('puerto_serial', "")
        self.init_serial()

        if self.guardar_datos:
            self.csv_filename = self.get_csv_filename()
            self.csv_file = open(self.csv_filename, mode='a', newline='')
            self.csv_writer = csv.writer(self.csv_file, delimiter=';')
            self.csv_writer.writerow(['Time', 'X', 'Y', 'Z'])
            print(f"Abriendo archivo: {self.csv_filename}")

            self.start_csv_timer()

    def init_serial(self):
        self.baud_rate = 115200
        try:

            self.ser = serial.Serial(self.serial_port, self.baud_rate)
        except:
                try:
                    print("Intentando liberar el puerto")
                    ser = serial.Serial(self.serial_port)
                    ser.close()
                    print(f"Puerto {self.serial_port} cerrado")
                    self.ser = serial.Serial(self.serial_port, self.baud_rate)
                except:
                    print("No se ha conseguido liberar")
                    pass
        self.running = True  # Asegurar que la bandera esté activa

        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def get_csv_filename(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        return f'{self.config.get("ruta_guardado", ".")}/data_{timestamp}.csv'

    def start_csv_timer(self):
        self.csv_timer = threading.Timer(600, self.update_csv_file)  # Cambia el archivo cada 10 minutos
        self.csv_timer.start()

    def update_csv_file(self):
        # Cerrar el archivo actual si está abierto
        if hasattr(self, 'csv_file') and not self.csv_file.closed:
            self.csv_file.close()

        # Abrir un nuevo archivo
        self.csv_filename = self.get_csv_filename()
        self.csv_file = open(self.csv_filename, mode='a', newline='')
        self.csv_writer = csv.writer(self.csv_file, delimiter=';')
        self.csv_writer.writerow(['Time', 'X', 'Y', 'Z'])
        print(f"Abriendo nuevo archivo: {self.csv_filename}")

        # Reiniciar el temporizador
        self.start_csv_timer()


    def read_serial(self):
        while self.running and self.ser.is_open:
            try:
                line = self.ser.readline().strip().decode('utf-8')
                value_x, value_y, value_z = map(float, line.split(' '))
                self.data_queue.put((value_x, value_y, value_z))
            except Exception as e:
                print(f"Error al leer datos del puerto serial: {e}")

    def update_data(self, frame):
        while not self.data_queue.empty():
            try:
                value_x, value_y, value_z = self.data_queue.get_nowait()
            except queue.Empty:
                value_x, value_y, value_z = 0.0, 0.0, 0.0

            self.data_x = np.append(self.data_x[1:], value_x)
            self.data_y = np.append(self.data_y[1:], value_y)
            self.data_z = np.append(self.data_z[1:], value_z)
            self.time = np.append(self.time[1:], self.time[-1] + 1/self.fs)

            if self.guardar_datos:
                try:
                    if hasattr(self, 'csv_file') and not self.csv_file.closed:
                        self.csv_writer.writerow([get_unique_microseconds(), value_x, value_y, value_z])
                except ValueError as e:
                    print(f"Error al escribir en el archivo CSV: {e}")
                except Exception as e:
                    print(f"Error inesperado al escribir en el archivo CSV: {e}")

        # Código para actualizar gráficos
        for i, data in enumerate([self.data_x, self.data_y, self.data_z]):
            self.lines[i].set_xdata(self.time)
            self.lines[i].set_ydata(data)
            ymin = np.min(data)
            ymax = np.max(data)
            y_range = ymax - ymin
            ymin -= 0.05 * y_range
            ymax += 0.05 * y_range

            if y_range < 5000:
                ymin, ymax = -2500, 2500

            self.axes[i, 0].set_ylim(ymin, ymax)
            self.axes[i, 0].set_xlim(self.time[0], self.time[-1])

        for i, data in enumerate([self.data_x, self.data_y, self.data_z]):
            frequencies, times, Sxx = spectrogram(data, self.fs, nperseg=256, noverlap=128)
            Sxx[Sxx == 0] = 1e-10
            self.im[i].set_data(10 * np.log10(Sxx))
            self.im[i].set_extent([self.time[-self.window_size], self.time[-1], frequencies[0], frequencies[-1]])
            self.im[i].set_clim(np.percentile(10 * np.log10(Sxx), [5, 95]))

        return self.lines + self.im + self.ylabels

    def recalibrate(self):
        if self.ser.is_open:
            self.ser.write(b"recalibrar\n")
        print("Recalibrando...")

    def closeEvent(self, event):
        if self.guardar_datos:
            self.csv_timer.cancel()
            self.csv_file.close()

        self.running = False

        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print("Puerto serial cerrado correctamente")
            except Exception as e:
                print(f"Error al cerrar el puerto: {e}")

        if self.serial_thread.is_alive():
            print("*"*200)
            self.serial_thread.join(timeout=1) 

        event.accept()

def aplicar_estilo(app):
    with open("style.qss", "r") as estilo:
        app.setStyleSheet(estilo.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    aplicar_estilo(app)  # Aplicar el estilo
    config_window = ConfigWindow()
    config_window.config_ready.connect(lambda config: PlotWindow(config).show())
    config_window.show()
    sys.exit(app.exec_())