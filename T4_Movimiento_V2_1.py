import sys
import cv2
import numpy as np
import serial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QGridLayout, 
                             QWidget, QPushButton, QVBoxLayout, QToolButton)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, pyqtSlot, QObject
from PyQt6.QtGui import QPixmap, QImage, QIcon
from pynput import keyboard

PUERTO_SERIAL = 'COM3'
BAUD_RATE = 9600
POSICION_NEUTRA = 128
VALOR_MAXIMO = 255
VALOR_MINIMO = 0
PASO_MOVIMIENTO = 20

class ControladorArduino:
    """Maneja la lógica de la comunicación serial para el movimiento."""
    def __init__(self):
        self.ver_duty = POSICION_NEUTRA
        self.hor_duty = POSICION_NEUTRA
        self.teclas_presionadas = set()
        self.arduino = None

    def conectar(self, puerto, baudrate):
        try:
            self.arduino = serial.Serial(puerto, baudrate, timeout=1)
            print(f"Arduino conectado en {puerto}")
            return True
        except serial.SerialException as e:
            print(f"Error: No se pudo abrir el puerto {puerto}. Detalles: {e}")
            return False

    def enviar_datos(self):
        if self.arduino and self.arduino.is_open:
            try:
                ver_enviar = max(VALOR_MINIMO, min(VALOR_MAXIMO, int(self.ver_duty)))
                hor_enviar = max(VALOR_MINIMO, min(VALOR_MAXIMO, int(self.hor_duty)))
                self.arduino.write(bytes([ver_enviar, hor_enviar]))
                print(f"Enviando -> Vertical: {ver_enviar}, Horizontal: {hor_enviar}", end='\r')
            except serial.SerialException as e:
                print(f"Error al escribir al puerto serial: {e}")

    def actualizar_movimiento(self):
        mov_vertical = 0
        mov_horizontal = 0
        if 'w' in self.teclas_presionadas: mov_vertical += 1
        if 's' in self.teclas_presionadas: mov_vertical -= 1
        if 'a' in self.teclas_presionadas: mov_horizontal -= 1
        if 'd' in self.teclas_presionadas: mov_horizontal += 1
        self.ver_duty = POSICION_NEUTRA + mov_vertical * PASO_MOVIMIENTO * 8
        self.hor_duty = POSICION_NEUTRA + mov_horizontal * PASO_MOVIMIENTO * 8
        self.enviar_datos()

    def procesar_tecla(self, tecla, presionada):
        if tecla in 'wasd':
            if presionada:
                self.teclas_presionadas.add(tecla)
            else:
                self.teclas_presionadas.discard(tecla)
            self.actualizar_movimiento()

    def cerrar_conexion(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.write(bytes([POSICION_NEUTRA, POSICION_NEUTRA]))
            self.arduino.close()
            print("\nConexión con Arduino cerrada.")

class ArduinoWorker(QObject):
    """Worker que vive en un hilo y maneja el controlador del Arduino."""
    def __init__(self):
        super().__init__()
        self.controlador = ControladorArduino()

    @pyqtSlot()
    def conectar_arduino(self):
        self.controlador.conectar(PUERTO_SERIAL, BAUD_RATE)

    @pyqtSlot(str, bool)
    def procesar_evento_tecla(self, tecla, presionada):
        self.controlador.procesar_tecla(tecla, presionada)

    @pyqtSlot()
    def cerrar_conexion(self):
        self.controlador.cerrar_conexion()
