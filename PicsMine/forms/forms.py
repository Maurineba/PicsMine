# criaçao dos formularios do site
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from PicsMine.models.models import Usuario   

class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_conf = SubmitField("Fazer Login")

class FormCriarConta(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    username = StringField("Nome", validators=[DataRequired()])
    criar_senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    conf_senha = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("criar_senha")])
    botao_conf = SubmitField("Criar conta")

    def validade_email(self, email):
        usuario = Usuario.query.filter.by(email=email.data).first()
        if usuario:
            return ValidationError("E-mail ja cadastrado faça login para continuar")
        
class FormFoto(FlaskForm):
    foto = FileField("Foto", validators=[DataRequired()])
    botao_conf = SubmitField("Enviar")
