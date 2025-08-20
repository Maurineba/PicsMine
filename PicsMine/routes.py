 
from flask import redirect, flash, render_template, session, url_for
from PicsMine import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from PicsMine.forms import FormCriarConta, FormLogin, FormFoto
from PicsMine.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("homepage"))


@app.route("/homepage", methods=["GET","POST"])  
def homepage(): 
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):    
            login_user(usuario)
            return redirect(url_for("feed", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login, body_class="login_fundo") 

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    formcriarconta = FormCriarConta()

    if formcriarconta.validate_on_submit():
        
        try:           
            senha = bcrypt.generate_password_hash(formcriarconta.criar_senha.data).decode('utf-8')
            usuario = Usuario(username=formcriarconta.username.data, email=formcriarconta.email.data, senha=senha)

            
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario, remember=True)  
            return redirect(url_for("routes.perfil", id_usuario=usuario.id))                              
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            database.session.rollback()
        
    return render_template("criarconta.html", form=formcriarconta, body_class="login_fundo")


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"]) 
def perfil(id_usuario):
    

    if int(id_usuario) == int(current_user.id):
        formfoto = FormFoto()
        if formfoto.validate_on_submit():
            arquivo_foto = formfoto.foto.data
            nome_arquivo = secure_filename(arquivo_foto.filename)

            
            pasta_destino = os.path.join(app.root_path, 'static', 'fotos_posts')
            os.makedirs(pasta_destino, exist_ok=True)

            
            caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
            print(" Salvando imagem em:", caminho_arquivo)

            
            arquivo_foto.save(caminho_arquivo)

            
            foto = Foto(image=nome_arquivo, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()

        return render_template("perfil.html", usuario=current_user, form=formfoto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.creation_date).all()
    return render_template("feed.html", fotos=fotos)


@app.route('/deletar_foto/<int:foto_id>', methods=['POST'])
@login_required
def deletar_foto(foto_id):
    
    foto = Foto.query.get_or_404(foto_id)
    
    
    if not current_user.is_authenticated or foto.id_usuario != current_user.id:
        flash('Você não pode deletar esta foto!', 'danger')
        return redirect(url_for('routes.perfil', id_usuario=current_user.id))
    
    try:        
        if foto.image != 'default.png':
            pasta_destino = os.path.join(app.root_path, 'static', 'fotos_posts')
            caminho_arquivo = os.path.join(pasta_destino, foto.image)
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

        database.session.delete(foto)
        database.session.commit()
        
        flash('Foto deletada com sucesso!', 'success')
    except Exception as e:
        database.session.rollback()
        flash('Erro ao deletar foto.', 'danger')
        app.logger.error(f'Erro ao deletar foto: {str(e)}')
    
    return redirect(url_for("routes.perfil", id_usuario=current_user.id))