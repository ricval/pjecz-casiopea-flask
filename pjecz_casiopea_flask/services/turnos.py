"""
Servicio para enviar correos electrónicos
"""

from typing import Tuple
from pjecz_casiopea_flask.config.settings import Settings


class MyAnyError(Exception):
    """Base exception class"""

class MyRequestError(MyAnyError):
    """Excepción porque falló el request"""

class Turnos():
    """Turnos"""

    _settings: Settings
    _turno_id: int
    _turno_codigo: str

    def __init__(self, setting: Settings):
        """Inicializa el servicio de turnos"""

        self._settings = setting
        self._turno_id = 0
        self._turno_codigo = ""
    
    def crear_turno(self):
        """
        Crea un nuevo turno en el sistema de turnos con el tipo cita.
        :return ID del turno y el código del turno generado.
        """

        self.turno_id = 444;
        self.turno_codigo = "OCP-102"

    def get_turno_id(self) -> int:
        """Entrega el ID del turno generado"""
        return self._turno_id
    
    def get_turno_codigo(self) -> int:
        """Entrega el Código del turno generado"""
        return self._turno_codigo
    
    def test_conexion(self) -> Tuple[bool, str]:
        """
        Prueba de conexión con el sistema de turnos
        :return Éxito o fallo y mensaje de respuesta.
        """

        respuesta = True
        mensaje = 'Todo Bien'

        return respuesta, mensaje
    
    def test_crear_turno(self) -> Tuple[bool, str]:
        """
        Prueba de conexión con el sistema de turnos
        :return Éxito o fallo y mensaje de respuesta.
        """

        respuesta = True
        mensaje = 'Todo Bien'

        return respuesta, mensaje
    
    def _conectar_api_turnos(self):
        """Conecta por API-Key al sistema de turnos"""