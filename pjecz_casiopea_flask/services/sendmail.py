"""
Servicio para enviar correos electrónicos
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
import locale
import pytz

from jinja2 import Environment, FileSystemLoader

import sendgrid
from sendgrid.helpers.mail import Content, Email as EmailSendGrid, Mail
from pjecz_casiopea_flask.config.settings import Settings, get_settings


class MyAnyError(Exception):
    """Base exception class"""

class MyRequestError(MyAnyError):
    """Excepción porque falló el request"""


class PlantillaEmailBase(ABC):
    """Clase base abstracta para las plantillas de correo."""

    FORMATO_FECHA_Y_HORA = "%d de %B del %Y a las %I:%M %p"

    _enviroment: Environment
    _fecha_hora_envio_str: str

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Nombre del archivo de la plantilla Jinja2."""
        pass

    @property
    @abstractmethod
    def subject(self) -> str:
        """Asunto del correo electrónico."""
        pass
    
    @property
    @abstractmethod
    def _variables_contenido(self) -> dict[str, str | list]:
        """Variables para la plantilla."""
        pass

    def __init__(self):
        """Constructor de la clase."""

        # Configurar el locale a español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'es_ES')

        # Por defecto se establece al fecha de envío en el momento de creación de la plantilla
        self.set_fecha_envio(datetime.now())

        # Configurar el entorno de Jinja2 para cargar plantillas desde el directorio 'templates/email'
        # La ruta se construye de forma relativa a la ubicación de este archivo.
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self._enviroment = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def set_fecha_envio(self, fecha_envio:datetime) -> None:
        """Establece la fecha y hora de envío"""
        
        self._fecha_hora_envio_str = fecha_envio.strftime(self.FORMATO_FECHA_Y_HORA)

    @abstractmethod
    def get_contenido(self) -> dict:
        """Diccionario con las variables para renderizar la plantilla."""
        pass

    def get_contenido(self) -> Content:
        """Carga las variables en la plantilla y la regresa como contenido HTML"""

        # Cargar la plantilla específica
        template = self._enviroment.get_template(self.template_name)
        # Renderizar la plantilla con las variables proporcionadas
        return Content("text/html", template.render(**self._variables_contenido, fecha_hora_envio=self._fecha_hora_envio_str))


class PlantillaReporteCitasProximas(PlantillaEmailBase):
    """
    Define la plantilla para el envío de un reporte a un usuario listando las próximas citas
    para el siguiente día hábil, solo se incluyen citas en estado pendiente y filtradas por su oficina.
    """
    template_name = "reporte_oficina_citas_proximas.jinja2"
    subject = "Reporte de próximas citas del Sistema de Citas SAJI"
    _variables_contenido: dict[str, str | list] = {
        'fecha_reporte': '',
        'usuario_nombre': '',
        'oficina': '',
        'citas': [],
    }

    def __init__(self, fecha_reporte: str, usuario_nombre: str, oficina: str, citas: list):
        super().__init__()

        self._variables_contenido['fecha_reporte'] = fecha_reporte
        self._variables_contenido['usuario_nombre'] = usuario_nombre
        self._variables_contenido['oficina'] = oficina
        self._variables_contenido['citas'] = citas


class Email():
    """Email"""

    _settings: Settings
    _remitente_email: EmailSendGrid
    plantilla: PlantillaEmailBase
    to_email: str | list

    def __init__(self, to_email: str | list, plantilla: PlantillaEmailBase = None):
        """Inicializa el servicio de email, especifica el destinatario y si quieres una plantilla"""

        self._settings = get_settings()
        self._remitente_email = EmailSendGrid(self._settings.SENDGRID_FROM_EMAIL)
        
        self.plantilla = plantilla
        self.to_email = to_email    # Puede ser un string o una lista de strings

        # Configurar el locale a español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'es_ES')

    def set_plantilla(self, plantilla: PlantillaEmailBase) -> None:
        """Establece una nueva plantilla a utilizar"""
        self.plantilla = plantilla

    def enviar_email(self):
        """ Envío de email por SendGrid """

        # Establecer la fecha y hora de envío
        self.plantilla.set_fecha_envio(datetime.now(tz=pytz.timezone(self._settings.TZ)))

        # Enviar el e-mail
        send_grid = sendgrid.SendGridAPIClient(api_key=self._settings.SENDGRID_API_KEY)
        
        mail = Mail(
            from_email=self._remitente_email,
            to_emails=self.to_email,
            subject=self.plantilla.subject,
            html_content=self.plantilla.get_contenido(),
        )

        # Enviar mensaje de correo electrónico
        try:
            send_grid.send(mail)
        except Exception as error:
            raise MyRequestError(f"Error al enviar el mensaje por Sendgrid: {str(error)}") from error
