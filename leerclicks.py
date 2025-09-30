import pyautogui
import time
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class ClickWorker(QObject):
    status_updated = pyqtSignal(str)
    

    def __init__(self, tiempo_espera=2, duracion_sostenido=3, tolerancia=20):
        super().__init__()
        self.tiempo_espera = tiempo_espera
        self.duracion_sostenido = duracion_sostenido
        self.tolerancia = tolerancia
        self._is_running = True

    @pyqtSlot()
    def run(self):
        """
        Bucle principal del worker que se ejecuta en el hilo.
        """
        self.status_updated.emit(f"Monitoreo de clics iniciado.")
       
        try:
            pos_anchor = pyautogui.position()
            time_anchor = time.time()
            x1 = pos_anchor.x - self.tolerancia
            x2 = pos_anchor.x + self.tolerancia
            y1 = pos_anchor.y - self.tolerancia
            y2 = pos_anchor.y + self.tolerancia

            while self._is_running:
                current_pos = pyautogui.position()
               
                is_in_area = (x1 <= current_pos.x <= x2 and y1 <= current_pos.y <= y2)

                if is_in_area:
                    if time.time() - time_anchor >= self.tiempo_espera:
                        self.status_updated.emit(f"Activando clic sostenido en {current_pos}...")
                       
                        pyautogui.mouseDown(button='left')
                       
                        # Bucle para la espera, permite una interrupción más rápida
                        start_hold_time = time.time()
                        while time.time() - start_hold_time < self.duracion_sostenido:
                            if not self._is_running:
                                break
                            time.sleep(0.1)
                           
                        pyautogui.mouseUp(button='left')
                       
                        if self._is_running:
                            self.status_updated.emit("Clic liberado. Reiniciando ancla.")
                       
                        # Reinicia el ancla para evitar repeticiones inmediatas
                        pos_anchor = pyautogui.position()
                        time_anchor = time.time()
                        x1, x2 = pos_anchor.x - self.tolerancia, pos_anchor.x + self.tolerancia
                        y1, y2 = pos_anchor.y - self.tolerancia, pos_anchor.y + self.tolerancia
                else:
                    # Si el cursor se mueve, reinicia el área
                    pos_anchor = current_pos
                    time_anchor = time.time()
                    x1, x2 = pos_anchor.x - self.tolerancia, pos_anchor.x + self.tolerancia
                    y1, y2 = pos_anchor.y - self.tolerancia, pos_anchor.y + self.tolerancia
               
                time.sleep(0.1)
               
        except Exception as e:
            self.status_updated.emit(f"Error en ClickWorker: {e}")
       
        self.status_updated.emit("Monitoreo de clics detenido.")

    def stop(self):
        """
        Método para detener el bucle del worker de forma segura.
        """
        self.status_updated.emit("Recibida señal para detener.")
        self._is_running = False