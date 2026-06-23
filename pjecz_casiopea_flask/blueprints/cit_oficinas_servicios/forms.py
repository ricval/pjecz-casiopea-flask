"""
Cit Oficinas-Servicios, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from ..cit_servicios.models import CitServicio
from ..oficinas.models import Oficina


class CitOficinaServicioWithCitServicioForm(FlaskForm):
    """Formulario para nuevo Cit Oficina-Servicio con un CitServicio"""

    cit_servicio = StringField("Servicio")  # Read only
    oficina = SelectField("Oficina", coerce=str, validators=[DataRequired()])
    limite_personas = IntegerField("Límite de Personas", validators=[DataRequired(), NumberRange(min=1)])
    guardar = SubmitField("Guardar")

    def __init__(self):
        """Inicializar y cargar opciones para oficina"""
        super().__init__()
        self.oficina.choices = [
            (o.id, o.clave + " - " + o.descripcion_corta)
            for o in Oficina.query.filter_by(estatus="A").order_by(Oficina.clave).all()
        ]


class CitOficinaServicioWithOficinaForm(FlaskForm):
    """Formulario para nuevo Cit Oficina-Servicio con una Oficina"""

    cit_servicio = SelectField("Servicio", coerce=str, validators=[DataRequired()])
    oficina = StringField("Oficina")  # Read only
    limite_personas = IntegerField("Límite de Personas", validators=[DataRequired(), NumberRange(min=1)])
    guardar = SubmitField("Guardar")

    def __init__(self):
        """Inicializar y cargar opciones para cit_servicio"""
        super().__init__()
        self.cit_servicio.choices = [
            (s.id, s.clave + " - " + s.descripcion)
            for s in CitServicio.query.filter_by(estatus="A").order_by(CitServicio.clave).all()
        ]


class CitOficinaServicioEditForm(FlaskForm):
    """Formulario para editar Cit Oficina-Servicio"""

    cit_servicio = StringField("Servicio")  # Read only
    oficina = StringField("Oficina")  # Read only
    limite_personas = IntegerField("Límite de Personas", validators=[DataRequired(), NumberRange(min=1)])
    guardar = SubmitField("Guardar")
