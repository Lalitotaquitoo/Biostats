import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QGridLayout, 
                             QWidget, QPushButton, QVBoxLayout, QToolButton)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QIcon
from ultralytics import YOLO
model= YOLO('yolov8n.pt')
class YoloThread(QThread):
    """
    Hilo para procesar el video de la cámara con el modelo YOLOv8 sin
    bloquear la interfaz. Permite cambiar de cámara dinámicamente.
    """
    frame_procesado = pyqtSignal(np.ndarray)
    alerta_detectada = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.activo = True
        self.camera_index = camera_index
        self._camara_solicitada = -1
        try:
            self.model = YOLO('yolov8n.pt')
        except Exception as e:
            self.error_signal.emit(f"Error al cargar el modelo YOLO: {e}")
            self.model = None

    def run(self):
        if not self.model:
            self.stop()
            return
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error_signal.emit(f"Error: No se pudo abrir la cámara {self.camera_index}.")
            self.stop()
            return

        print(f"Cámara {self.camera_index} abierta correctamente.")
        objetos_a_detectar = ['person']
        clases_a_detectar_ids = [k for k, v in self.model.names.items() if v in objetos_a_detectar]

        while self.activo:
            if self._camara_solicitada != -1:
                print(f"Solicitud de cambio a cámara {self._camara_solicitada} detectada.")
                cap.release()
                cap = cv2.VideoCapture(self._camara_solicitada)
                if not cap.isOpened():
                    self.error_signal.emit(f"Error: No se pudo cambiar a la cámara {self._camara_solicitada}.")
                    self.stop()
                    break
                self.camera_index = self._camara_solicitada
                self._camara_solicitada = -1
                print(f"Cámara cambiada a índice {self.camera_index}.")

            if not cap.isOpened():
                time.sleep(0.1)
                continue

            success, frame = cap.read()
            if success:
                results = self.model(frame, classes=clases_a_detectar_ids, verbose=False)
                annotated_frame = results[0].plot()
                for r in results:
                    if r.boxes:
                        nombre_clase = self.model.names[int(r.boxes[0].cls[0])]
                        self.alerta_detectada.emit(f"¡ALERTA! Se detectó: {nombre_clase.upper()}")
                        break
                self.frame_procesado.emit(annotated_frame)
            else:
                time.sleep(0.01)
        cap.release()
        print("Captura de video finalizada.")

    @pyqtSlot(int)
    def cambiar_camara(self, index):
        if self.camera_index != index:
            self._camara_solicitada = index

    def stop(self):
        print("Deteniendo hilo de YOLO...")
        self.activo = False
        self.quit()
        self.wait(2000)