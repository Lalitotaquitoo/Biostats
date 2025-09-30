import sys
import cv2
import numpy as np

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QGridLayout, 
                             QWidget, QPushButton, QVBoxLayout, QToolButton, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QIcon

# --------------------------------------------------------------------------- #
# Importación de Módulos Locales
# Se asume que estos archivos existen y contienen las clases correspondientes
# como se utilizan en main_funciona.py
# --------------------------------------------------------------------------- #
from objects_detection import YoloThread
from T4_Movimiento_V2_1 import ArduinoWorker
from sintetizador import VozWorker
from leerclicks import ClickWorker

# --------------------------------------------------------------------------- #
# VENTANA: CONFIGURACIÓN
# --------------------------------------------------------------------------- #
class Configure_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        layout = QGridLayout()
        layout.setSpacing(0)
        self.setLayout(layout)

                # --- Header ---
        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.label = QLabel("       Configuración del Movimiento")
        self.label.setProperty("class", "h1_label")
        layout.addWidget(self.label, 0, 1)

        # --- Asistente ---
        self.speed_label = QLabel("Asistente :")
        self.speed_label.setProperty("class", "h2_label")
        layout.addWidget(self.speed_label, 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        speed_buttons_layout = QHBoxLayout()
        speed_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.speed_button1 = QPushButton("Echo Dot")
        self.speed_button1.setProperty("class", "config_button")
        speed_buttons_layout.addWidget(self.speed_button1)

        self.speed_button2 = QPushButton("Alexa")
        self.speed_button2.setProperty("class", "config_button")
        speed_buttons_layout.addWidget(self.speed_button2)

        layout.addLayout(speed_buttons_layout, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Modo Oscuro ---
        self.dark_model_label = QLabel("Modo Oscuro:")
        self.dark_model_label.setProperty("class", "h2_label")
        layout.addWidget(self.dark_model_label, 3, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        dark_buttons_layout = QHBoxLayout()
        dark_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dark_model_on_button = QPushButton(QIcon('assets/config_window/sun.png'), "")
        self.dark_model_on_button.setIconSize(QSize(120, 120))
        self.dark_model_on_button.setFixedSize(200, 150)
        self.dark_model_on_button.setProperty("class", "config_button")
        dark_buttons_layout.addWidget(self.dark_model_on_button)

        self.dark_model_off_button = QPushButton(QIcon('assets/config_window/moon.png'), "")
        self.dark_model_off_button.setIconSize(QSize(120, 120))
        self.dark_model_off_button.setFixedSize(200, 150)
        self.dark_model_off_button.setProperty("class", "config_button")
        dark_buttons_layout.addWidget(self.dark_model_off_button)

        layout.addLayout(dark_buttons_layout, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Detección de Objetos ---
        self.Obj_detection_label = QLabel("Detección de Objetos:")
        self.Obj_detection_label.setProperty("class", "h2_label")
        layout.addWidget(self.Obj_detection_label, 5, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        obj_buttons_layout = QHBoxLayout()
        obj_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Obj_detection_on_button = QPushButton(QIcon('assets/config_window/obj_detec.png'), "")
        self.Obj_detection_on_button.setIconSize(QSize(120, 120))
        self.Obj_detection_on_button.setFixedSize(200, 150)
        self.Obj_detection_on_button.setProperty("class", "config_button")
        obj_buttons_layout.addWidget(self.Obj_detection_on_button)

        self.Obj_detection_off_button = QPushButton(QIcon('assets/config_window/obj_detection_off.png'), "")
        self.Obj_detection_off_button.setIconSize(QSize(120, 120))
        self.Obj_detection_off_button.setFixedSize(200, 150)
        self.Obj_detection_off_button.setProperty("class", "config_button")
        obj_buttons_layout.addWidget(self.Obj_detection_off_button)

        layout.addLayout(obj_buttons_layout, 6, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)


# --------------------------------------------------------------------------- #
# VENTANAS DE DOMÓTICA (CON FUNCIONALIDAD DE VOZ INTEGRADA)
# --------------------------------------------------------------------------- #
class Light_window(QWidget):
    hablar_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luz")
        
        # --- Hilo para síntesis de voz ---
        self.voz_thread = QThread()
        self.voz_worker = VozWorker()
        self.voz_worker.moveToThread(self.voz_thread)
        self.hablar_signal.connect(self.voz_worker.procesar_hablar)
        self.voz_thread.start()

        # --- Layout ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Control de la Luz")
        self.label.setProperty("class", "h1_label")
        layout.addWidget(self.label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)  

        self.on_button = QPushButton("Encender")
        self.on_button.setFixedSize(400, 250)
        self.on_button.setProperty("class", "ligth_button")
        self.on_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, enciende el foco"))
        layout.addWidget(self.on_button, 1, 0)

        self.off_button = QPushButton("Apagar")
        self.off_button.setFixedSize(400, 250)
        self.off_button.setProperty("class", "ligth_button")
        self.off_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, apaga el foco"))
        layout.addWidget(self.off_button, 1, 1)

        self.intensity_label = QLabel("Intensidad")
        self.intensity_label.setProperty("class", "h2_label")
        layout.addWidget(self.intensity_label, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.low_button = QPushButton("Baja")
        self.low_button.setProperty("class", "ligth_button")
        self.low_button.setFixedSize(400, 250)
        self.low_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, pon foco en intensidad baja"))
        layout.addWidget(self.low_button, 3, 0)

        self.medium_button = QPushButton("Media")
        self.medium_button.setFixedSize(400, 250)
        self.medium_button.setProperty("class", "ligth_button")
        self.medium_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, pon foco en intensidad media"))
        layout.addWidget(self.medium_button, 3, 1)

        self.high_button = QPushButton("Alta")
        self.high_button.setFixedSize(400, 250)
        self.high_button.setProperty("class", "ligth_button")
        self.high_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, pon foco en intensidad alta"))
        layout.addWidget(self.high_button, 3, 2)

        main_layout.addLayout(layout)

    def closeEvent(self, event):
        self.voz_thread.quit()
        self.voz_thread.wait()
        super().closeEvent(event)

class YT_window(QWidget):
    hablar_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube")

        # --- Hilo para síntesis de voz ---
        self.voz_thread = QThread()
        self.voz_worker = VozWorker()
        self.voz_worker.moveToThread(self.voz_thread)
        self.hablar_signal.connect(self.voz_worker.procesar_hablar)
        self.voz_thread.start()

        # --- Layout ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("YouTube")
        self.label.setProperty("class", "h1_label")
        layout.addWidget(self.label, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        
        buttons_info = {
            (1, 0): ("Canal 1", "Alexa, reproduce luisito comunica en youtube"),
            (1, 1): ("Canal 2", "Alexa, reproduce Roobeertoo emetezeta en youtube"),
            (1, 2): ("Canal 3", "Alexa, reproduce vegeta setesientossetentaysiete en youtube"),
            (1, 3): ("Canal 4", "Alexa, reproduce lord seivitforparts en youtube"),
            (2, 0): ("Canal 5", "Alexa, reproduce eseefedeequis chou"),
            (2, 1): ("Canal 6", "Alexa, reproduce diegoveloper en youtube"),
            (2, 2): ("Canal 7", "Alexa, reproduce topespidyermani en youtube"),
            (2, 3): ("Canal 8", "Alexa, reproduce el pingüino de mario en youtube"),
            (3, 0): ("Canal 9", "Alexa, reproduce Victor Mendiiivil en youtube"),
            (3, 1): ("Canal 10", "Alexa, reproduce deyen dalt en youtube"),
            (3, 2): ("Canal 11", "Alexa, reproduce luis erre conrriquez en youtube"),
            (3, 3): ("Canal 12", "Alexa, reproduce beisicali jomles en youtube"),
        }

        for pos, (text, command) in buttons_info.items():
            button = QPushButton(text)
            button.setFixedSize(250, 200)
            button.setProperty("class", "yt_button")
            button.clicked.connect(lambda _, cmd=command: self.hablar_signal.emit(cmd))
            layout.addWidget(button, pos[0], pos[1])

        main_layout.addLayout(layout)

    def closeEvent(self, event):
        self.voz_thread.quit()
        self.voz_thread.wait()
        super().closeEvent(event)

class Emergency_window(QWidget):
    hablar_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emergencia")

        # --- Hilo para síntesis de voz ---
        self.voz_thread = QThread()
        self.voz_worker = VozWorker()
        self.voz_worker.moveToThread(self.voz_thread)
        self.hablar_signal.connect(self.voz_worker.procesar_hablar)
        self.voz_thread.start()
        
        # --- Layout ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Emergencia")
        self.label.setProperty("class", "h1_label")
        layout.addWidget(self.label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.call_button1 = QPushButton("Llamar a Emergencias")
        self.call_button1.setFixedSize(400, 200)
        self.call_button1.setProperty("class", "emergency_button")
        self.call_button1.clicked.connect(lambda: self.hablar_signal.emit("Alexa, llama a emergencias"))
        layout.addWidget(self.call_button1, 1, 0)

        self.call_button2 = QPushButton("Llama a David")
        self.call_button2.setFixedSize(400, 200)
        self.call_button2.setProperty("class", "emergency_button")
        self.call_button2.clicked.connect(lambda: self.hablar_signal.emit("Alexa, llama a siete dosss dosss cuatroo seiss cuatrohh cerohh tress seisss nueveehh"))
        layout.addWidget(self.call_button2, 1, 1)

        self.call_button3 = QPushButton("Contactar Familiar")
        self.call_button3.setFixedSize(400, 200)
        self.call_button3.setProperty("class", "emergency_button")
        self.call_button3.clicked.connect(lambda: self.hablar_signal.emit("Alexa, llama a mi familiar"))
        layout.addWidget(self.call_button3, 1, 2)

        main_layout.addLayout(layout)
        
    def closeEvent(self, event):
        self.voz_thread.quit()
        self.voz_thread.wait()
        super().closeEvent(event)

class Weather_window(QWidget):
    hablar_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clima y hora")
        
        # --- Hilo para síntesis de voz ---
        self.voz_thread = QThread()
        self.voz_worker = VozWorker()
        self.voz_worker.moveToThread(self.voz_thread)
        self.hablar_signal.connect(self.voz_worker.procesar_hablar)
        self.voz_thread.start()

        # --- Layout ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.weather_label = QLabel("Clima")
        self.weather_label.setProperty("class", "h2_label")
        layout.addWidget(self.weather_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.china_button = QPushButton("China")
        self.china_button.setFixedSize(400, 250)
        self.china_button.setProperty("class", "config_button")
        self.china_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, como esta el clima en China"))
        layout.addWidget(self.china_button, 1, 0)

        self.canada_button = QPushButton("Canada")
        self.canada_button.setFixedSize(400, 250)
        self.canada_button.setProperty("class", "config_button")
        self.canada_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, como esta el clima en Canada"))
        layout.addWidget(self.canada_button, 1, 1)

        self.mexico_button = QPushButton("Mexico")
        self.mexico_button.setFixedSize(400, 250)
        self.mexico_button.setProperty("class", "config_button")
        self.mexico_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa como esta el clima en México"))
        layout.addWidget(self.mexico_button, 1, 2)

        self.time_label = QLabel("Hora")
        self.time_label.setProperty("class", "h2_label")
        layout.addWidget(self.time_label, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.china_time_button = QPushButton("China")
        self.china_time_button.setFixedSize(400, 250)
        self.china_time_button.setProperty("class", "config_button")
        self.china_time_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, Cuál es la hora en Beijing, China"))
        layout.addWidget(self.china_time_button, 3, 0)

        self.mexico_time_button = QPushButton("Mexico")
        self.mexico_time_button.setFixedSize(400, 250)
        self.mexico_time_button.setProperty("class", "config_button")
        self.mexico_time_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, Cuál es la hora en Ciudad de mexico, México"))
        layout.addWidget(self.mexico_time_button, 3, 1)

        self.canada_time_button = QPushButton("Canada")
        self.canada_time_button.setProperty("class", "config_button")
        self.canada_time_button.setFixedSize(400, 250)
        self.canada_time_button.clicked.connect(lambda: self.hablar_signal.emit("Alexa, Cuál es la hora en Toronto, Canada"))
        layout.addWidget(self.canada_time_button, 3, 2)

        main_layout.addLayout(layout)
        
    def closeEvent(self, event):
        self.voz_thread.quit()
        self.voz_thread.wait()
        super().closeEvent(event)

# --------------------------------------------------------------------------- #
# VENTANA: MOVIMIENTO (CON FUNCIONALIDAD DE YOLO Y ARDUINO)
# --------------------------------------------------------------------------- #
class Movement_window(QWidget):
    evento_tecla_signal = pyqtSignal(str, bool)
    cambiar_camara_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movimiento")
        self.setGeometry(100, 100, 800, 600)
        self.current_camera_index = 0
        self.config_window = None

        # --- Hilo de YOLO para la cámara ---
        self.yolo_thread = YoloThread(camera_index=self.current_camera_index)
        self.yolo_thread.frame_procesado.connect(self.actualizar_frame)
        self.yolo_thread.error_signal.connect(lambda msg: print(f"ERROR YOLO: {msg}"))
        self.cambiar_camara_signal.connect(self.yolo_thread.cambiar_camara)
        self.yolo_thread.start()

        # --- Hilo de Arduino para el control ---
        self.arduino_thread = QThread()
        self.arduino_worker = ArduinoWorker()
        self.arduino_worker.moveToThread(self.arduino_thread)
        self.evento_tecla_signal.connect(self.arduino_worker.procesar_evento_tecla)
        self.arduino_thread.started.connect(self.arduino_worker.conectar_arduino)
        self.arduino_thread.start()

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Header ---
        header_layout = QGridLayout()
        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setProperty("class", "header_button")
        self.back_button.setFixedSize(100, 80)
        self.back_button.clicked.connect(self.volver)
        header_layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.configure_button = QPushButton(QIcon('assets/header/config.png'), "")
        self.configure_button.setIconSize(QSize(60, 60))
        self.configure_button.setProperty("class", "header_button")
        self.configure_button.setFixedSize(100, 80)
        self.configure_button.clicked.connect(self.open_config)
        # Use a spacer item to push the config button to the right
        header_layout.setColumnStretch(1, 1)
        header_layout.addWidget(self.configure_button, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(header_layout)

        # --- Layout de Controles ---
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # --- Video Label ---
        self.video_label = QLabel()
        self.video_label.setFixedSize(600, 550)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #555;")
        layout.addWidget(self.video_label, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_info = {
            'w': ('assets/movement_arrow/up_arrow.png', (0, 1)),
            's': ('assets/movement_arrow/down_arrow.png', (2, 1)),
            'a': ('assets/movement_arrow/left_arrow.png', (1, 0)),
            'd': ('assets/movement_arrow/right_arrow.png', (1, 2)),
        }
        
        diagonal_buttons_info = {
            'wa': ('assets/movement_arrow/top_left_arrow.png', (0, 0)),
            'wd': ('assets/movement_arrow/top_right_arrow.png', (0, 2)),
            'sa': ('assets/movement_arrow/bottom_left_arrow.png', (2, 0)),
            'sd': ('assets/movement_arrow/bottom_right_arrow.png', (2, 2)),
        }

        # Botones de movimiento (rectos)
        for key, (icon_path, pos) in buttons_info.items():
            button = QPushButton(QIcon(icon_path), "")
            button.setIconSize(QSize(150, 150))
            button.setFixedSize(200, 150)
            button.setProperty("class", "movement_button")
            button.pressed.connect(lambda k=key: self.evento_tecla_signal.emit(k, True))
            button.released.connect(lambda k=key: self.evento_tecla_signal.emit(k, False))
            if key == 's': # Añadir cambio de cámara al botón de reversa
                 button.pressed.connect(self.cambiar_camara_auto)
            layout.addWidget(button, pos[0], pos[1], alignment=Qt.AlignmentFlag.AlignCenter)
            

        # Botones de movimiento (diagonales)
        for keys, (icon_path, pos) in diagonal_buttons_info.items():
            button = QPushButton(QIcon(icon_path), "")
            button.setIconSize(QSize(150, 150))
            button.setFixedSize(200, 150)
            button.setProperty("class", "movement_button")
            t1, t2 = keys[0], keys[1]
            button.pressed.connect(lambda t1=t1, t2=t2: self.presionar_dos_teclas(t1, t2))
            button.released.connect(lambda t1=t1, t2=t2: self.liberar_dos_teclas(t1, t2))
            if 's' in keys: # Añadir cambio de cámara a los botones de reversa
                 button.pressed.connect(self.cambiar_camara_auto)
            layout.addWidget(button, pos[0], pos[1], alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(layout)

    def presionar_dos_teclas(self, t1, t2):
        self.evento_tecla_signal.emit(t1, True)
        self.evento_tecla_signal.emit(t2, True)

    def liberar_dos_teclas(self, t1, t2):
        self.evento_tecla_signal.emit(t1, False)
        self.evento_tecla_signal.emit(t2, False)

    @pyqtSlot(np.ndarray)
    def actualizar_frame(self, cv_img):
        try:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = QPixmap.fromImage(convert_to_qt_format)
            self.video_label.setPixmap(
                p.scaled(self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            )
        except Exception as e:
            print(f"Error al actualizar frame: {e}")

    @pyqtSlot()
    def cambiar_camara_auto(self):
        self.current_camera_index = (self.current_camera_index + 1) % 2
        print(f"Solicitando cambio a cámara {self.current_camera_index}")
        self.cambiar_camara_signal.emit(self.current_camera_index)

    def volver(self):
        print("Cerrando ventana de movimiento...")
        self.yolo_thread.stop()
        self.arduino_worker.cerrar_conexion()
        self.arduino_thread.quit()
        self.yolo_thread.wait()
        self.arduino_thread.wait()
        self.close()
    
    def open_config(self):
        if self.config_window is None:
            self.config_window = Configure_window()
        self.config_window.show()

# --------------------------------------------------------------------------- #
# VENTANA: MENÚ DE DOMÓTICA
# --------------------------------------------------------------------------- #
class Domotica_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Domotica")
        self.light_window = None
        self.yt_window = None
        self.emergency_window = None
        self.weather_window = None
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        header_layout = QGridLayout()
        self.back_button = QPushButton(QIcon('assets/header/back.png'), "")
        self.back_button.setIconSize(QSize(60, 60))
        self.back_button.setFixedSize(100, 80)
        self.back_button.setProperty("class", "header_button")
        self.back_button.clicked.connect(self.close)
        header_layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(header_layout)

        domotica_layout = QGridLayout()
        domotica_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.light_button = QPushButton("Luz")
        self.light_button.setFixedSize(600, 400)
        self.light_button.setProperty("class", "domotica_button")
        self.light_button.clicked.connect(self.open_ligth)
        domotica_layout.addWidget(self.light_button, 0, 0)

        self.yt_button = QPushButton("YouTube")
        self.yt_button.setFixedSize(600, 400)
        self.yt_button.setProperty("class", "domotica_button")
        self.yt_button.clicked.connect(self.open_yt)
        domotica_layout.addWidget(self.yt_button, 0, 1)

        self.emergency_button = QPushButton("Emergencia")
        self.emergency_button.setFixedSize(600, 400)
        self.emergency_button.setProperty("class", "domotica_button")
        self.emergency_button.clicked.connect(self.open_emergency)
        domotica_layout.addWidget(self.emergency_button, 1, 0)

        self.weather_button = QPushButton("Clima")
        self.weather_button.setFixedSize(600, 400)
        self.weather_button.setProperty("class", "domotica_button")
        self.weather_button.clicked.connect(self.open_weather)
        domotica_layout.addWidget(self.weather_button, 1, 1)

        main_layout.addLayout(domotica_layout)
    
    def open_ligth(self):
        if self.light_window is None:
            self.light_window = Light_window()
        self.light_window.show()
    
    def open_yt(self):
        if self.yt_window is None:
            self.yt_window = YT_window()
        self.yt_window.show()
    
    def open_emergency(self):
        if self.emergency_window is None:
            self.emergency_window = Emergency_window()
        self.emergency_window.show()
    
    def open_weather(self):
        if self.weather_window is None:
            self.weather_window = Weather_window()
        self.weather_window.show()

# --------------------------------------------------------------------------- #
# VENTANA PRINCIPAL
# --------------------------------------------------------------------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sillodromo Lions")
        self.resize(1000, 600)
        self.setWindowIcon(QIcon('assets/Logo.jpeg'))
        
        # --- Hilo para detectar doble clic ---
        self.click_thread = QThread()
        self.click_worker = ClickWorker(tiempo_espera=2, tolerancia=20)
        self.click_worker.moveToThread(self.click_thread)
        self.click_thread.started.connect(self.click_worker.run)
        self.click_thread.start()

        # --- Layout de la ventana principal ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.domotica_button = QToolButton()
        self.domotica_button.setText("Domótica")
        self.domotica_button.setIcon(QIcon('assets/main/domotic.png'))
        self.domotica_button.setIconSize(QSize(300, 280))
        self.domotica_button.setProperty("class", "main_button")
        self.domotica_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.domotica_button.setFixedSize(550, 450)
        self.domotica_button.clicked.connect(self.open_domotica)
        layout.addWidget(self.domotica_button, 0, 0)

        self.movement_button = QToolButton()
        self.movement_button.setText("Movimiento")
        self.movement_button.setIcon(QIcon('assets/main/silla_main.svg'))
        self.movement_button.setIconSize(QSize(300, 280)) 
        self.movement_button.setProperty("class", "main_button")
        self.movement_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.movement_button.setFixedSize(550, 450)
        self.movement_button.clicked.connect(self.open_movimiento)
        layout.addWidget(self.movement_button, 0, 1)

        self.domotica_window = None
        self.movimiento_window = None
        
    def open_domotica(self):
        if self.domotica_window is None:
            self.domotica_window = Domotica_window()
        self.domotica_window.show()

    def open_movimiento(self):
        # Siempre crea una nueva instancia para reiniciar los hilos de Arduino y YOLO
        self.movimiento_window = Movement_window()
        self.movimiento_window.show()

    def closeEvent(self, event):
        print("Cerrando aplicación principal...")
        self.click_worker.stop()
        self.click_thread.quit()
        self.click_thread.wait()
        event.accept()

# --------------------------------------------------------------------------- #
# PUNTO DE ENTRADA DE LA APLICACIÓN
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    try:
        with open('styles.css', 'r') as file:
            app.setStyleSheet(file.read())
            print("Hoja de estilos 'styles.css' cargada correctamente.")
    except FileNotFoundError:
        print("Advertencia: No se encontró 'styles.css'. Se usarán los estilos por defecto.")

    window = MainWindow()
    window.show() 
    sys.exit(app.exec())