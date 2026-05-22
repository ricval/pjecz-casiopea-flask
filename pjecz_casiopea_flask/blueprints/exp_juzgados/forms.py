"""
Expedientes-Juzgados, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

from ...lib.safe_string import CLAVE_REGEXP


class ExpJuzgadoForm(FlaskForm):
    """Formulario Expediente-Juzgado"""

    clave = StringField("Clave (única de hasta 16 caracteres)", validators=[DataRequired(), Regexp(CLAVE_REGEXP)])
    descripcion_corta = StringField("Descripción corta", validators=[DataRequired(), Length(max=64)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
