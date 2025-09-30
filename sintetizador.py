class SintetizadorVoz:
    """
    Clase corregida para manejar el motor de pyttsx3.
    Ahora inicializa el motor en cada llamada a 'hablar' para evitar
    problemas de reutilización.
    """
    def __init__(self) -> None:
        # El motor ya no se inicializa aquí.
        pass

    def hablar(self, texto: str, velocidad: int = 90) -> None:
        # 1. Se crea una instancia nueva y limpia del motor CADA VEZ.
        motor = pyttsx3.init()
        motor.setProperty('volume', 1.0)
        motor.setProperty('rate', velocidad)
        motor.say(texto)
        motor.runAndWait()
        # El motor se destruye automáticamente al salir de la función.

    def cambiar_voz(self, id_voz: int) -> None:
        # Esta función también necesita su propia instancia para funcionar.
        motor = pyttsx3.init()
        voces = motor.getProperty('voices')
        if 0 <= id_voz < len(voces):
            motor.setProperty('voice', voces[id_voz].id)
            # (Nota: este cambio de voz solo se aplicaría si hablaras
            # inmediatamente después dentro de esta misma función,
            # ya que la instancia es local.)
        else:
            raise ValueError("El índice de voz está fuera de rango.")

class VozWorker(QObject):
    """
    'Trabajador' que se moverá a un QThread para manejar la síntesis de voz
    sin bloquear la interfaz gráfica.
    """
    def __init__(self):
        super().__init__()
        self.sintetizador = SintetizadorVoz()
        print("VozWorker inicializado.")

    @pyqtSlot(str)
    def procesar_hablar(self, texto: str):
        """
        Este slot recibe el texto desde el hilo principal y ejecuta
        la función bloqueante hablar() de forma segura.
        """
        try:
            print(f"Recibido para hablar: '{texto}'")
            self.sintetizador.hablar(texto)
        except Exception as e:
            print(f"Error en el hilo de voz: {e}")
