import sys
import cv2
import numpy as np
import pyautogui
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QGridLayout, 
                             QWidget, QPushButton, QVBoxLayout, QToolButton)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, pyqtSlot, QObject
from PyQt6.QtGui import QPixmap, QImage, QIcon

class ClickWorker(QObject):
    """
    Worker que monitorea la posición del puntero y hace clic si permanece
    en un área por un tiempo determinado. Se ejecuta en un hilo separado.
    """
    def __init__(self, tiempo_espera=2, tolerancia=20):
        super().__init__()
        self.tiempo_espera = tiempo_espera
        self.tolerancia = tolerancia
        self.running = True

    def run(self):
        """Contiene el bucle principal que se ejecutará en el hilo."""
        print(f"Monitoreo de clics iniciado con una tolerancia de +/- {self.tolerancia} píxeles.")
        try:
            posicion_ancla = pyautogui.position()
            tiempo_inicio_area = time.time()
            x1, x2 = posicion_ancla.x - self.tolerancia, posicion_ancla.x + self.tolerancia
            y1, y2 = posicion_ancla.y - self.tolerancia, posicion_ancla.y + self.tolerancia

            while self.running:
                posicion_actual = pyautogui.position()
                esta_en_area = (x1 <= posicion_actual.x <= x2 and
                                y1 <= posicion_actual.y <= y2)

                if esta_en_area:
                    if time.time() - tiempo_inicio_area >= self.tiempo_espera:
                        pyautogui.click()
                        print(f"\nClic realizado en {posicion_actual} por permanecer en el área.")
                        posicion_ancla = posicion_actual
                        tiempo_inicio_area = time.time()
                        x1, x2 = posicion_ancla.x - self.tolerancia, posicion_ancla.x + self.tolerancia
                        y1, y2 = posicion_ancla.y - self.tolerancia, posicion_ancla.y + self.tolerancia
                else:
                    print(f"Nueva área de anclaje centrada en {posicion_actual}", end='\r')
                    posicion_ancla = posicion_actual
                    tiempo_inicio_area = time.time()
                    x1, x2 = posicion_ancla.x - self.tolerancia, posicion_ancla.x + self.tolerancia
                    y1, y2 = posicion_ancla.y - self.tolerancia, posicion_ancla.y + self.tolerancia
                time.sleep(0.1)
        except Exception as e:
            print(f"Ocurrió un error en el hilo del monitor de clics: {e}")
        print("\nEl monitoreo de clics ha terminado.")

    def stop(self):
        """Detiene el bucle en el hilo."""
        self.running = False