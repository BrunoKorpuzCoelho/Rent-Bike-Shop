from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, send_file, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime, timedelta
import zipfile
from io import BytesIO
import io
import os
import base64

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///teste.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

# BASE DE DADOS
class Alugador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    nif = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    morada = db.Column(db.String)
    telefone = db.Column(db.String)
    valor_pagar = db.Column(db.Float)
    _data_pagamento = db.Column('data_pagamento', db.String)
    veiculo_alugado = db.Column(db.String)
    recebido = db.Column(db.Integer, default=0)
    cartao_identificacao = db.Column(db.LargeBinary)
    cartao_identificacao_verso = db.Column(db.LargeBinary)  
    carta_conducao = db.Column(db.LargeBinary)
    carta_conducao_verso = db.Column(db.LargeBinary)

    def __init__(self, nome, nif, email, morada, veiculo_alugado, telefone, valor_pagar, data_pagamento, recebido=0, cartao_identificacao=None, cartao_identificacao_verso=None, carta_conducao=None, carta_conducao_verso=None):
        self.nome = nome.title()
        self.nif = nif
        self.email = email
        self.morada = morada
        self.telefone = telefone
        self.valor_pagar = valor_pagar
        self.data_pagamento = data_pagamento 
        self.veiculo_alugado = veiculo_alugado.upper()
        self.recebido = recebido
        self.cartao_identificacao = cartao_identificacao
        self.cartao_identificacao_verso = cartao_identificacao_verso
        self.carta_conducao = carta_conducao
        self.carta_conducao_verso = carta_conducao_verso

    @property
    def data_pagamento(self):
        return self._data_pagamento

    @data_pagamento.setter
    def data_pagamento(self, value):
        if value:
            self._data_pagamento = datetime.strptime(value, '%Y-%m-%d').strftime('%Y/%m/%d')
        else:
            self._data_pagamento = None

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_alugador = db.Column(db.Integer, db.ForeignKey('alugador.id'), nullable=False)
    contrato = db.Column(db.LargeBinary, nullable=False)
    data = db.Column(db.String)

    alugador = db.relationship('Alugador', backref=db.backref('contratos', lazy=True))

class Sinistro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_alugador = db.Column(db.Integer, db.ForeignKey('alugador.id'), nullable=False)
    _data_inicio = db.Column('data_inicio', db.String)
    _data_fim = db.Column('data_fim', db.String, nullable=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    estado = db.Column(db.String, default = "Aberto")

    alugador = db.relationship('Alugador', backref=db.backref('sinistros', lazy=True))
    veiculo = db.relationship('Veiculo', backref=db.backref('veiculos', lazy=True))
    

    def __init__(self, id_alugador, data_inicio, id_veiculo, data_fim=None, estado="Aberto"):
        self.id_alugador = id_alugador
        self.data_inicio = data_inicio  
        self.data_fim = data_fim  
        self.id_veiculo = id_veiculo
        self.estado = estado

    @property
    def data_inicio(self):
        return self._data_inicio

    @data_inicio.setter
    def data_inicio(self, value):
        if value:
            self._data_inicio = datetime.strptime(value, '%Y-%m-%d').strftime('%Y/%m/%d')
        else:
            self._data_inicio = None

    @property
    def data_fim(self):
        return self._data_fim

    @data_fim.setter
    def data_fim(self, value):
        if value:
            self._data_fim = datetime.strptime(value, '%Y-%m-%d').strftime('%Y/%m/%d')
        else:
            self._data_fim = None

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String)
    modelo = db.Column(db.String)
    matricula = db.Column(db.String)
    ano = db.Column(db.String)
    km = db.Column(db.String)
    documento_veiculo = db.Column(db.LargeBinary)

    def __init__(self, marca, modelo, ano, km, documento_veiculo, matricula):
        self.marca = marca.capitalize()
        self.modelo = modelo.capitalize()
        self.ano = ano
        self.km = km
        self.documento_veiculo = documento_veiculo
        self.matricula = matricula

class FotosVeiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    foto_1 = db.Column(db.LargeBinary)
    foto_2 = db.Column(db.LargeBinary)
    foto_3 = db.Column(db.LargeBinary)
    foto_4 = db.Column(db.LargeBinary)
    foto_5 = db.Column(db.LargeBinary)
    foto_6 = db.Column(db.LargeBinary)
    foto_7 = db.Column(db.LargeBinary)
    foto_8 = db.Column(db.LargeBinary)
    foto_9 = db.Column(db.LargeBinary)
    foto_10 = db.Column(db.LargeBinary)

    veiculo = db.relationship('Veiculo', backref=db.backref('FotosVeiculos', lazy=True))

    def __init__(self, id_veiculo, foto_1=None, foto_2=None, foto_3=None, foto_4=None, foto_5=None, foto_6=None, foto_7=None, foto_8=None, foto_9=None, foto_10=None):
        self.id_veiculo = id_veiculo
        self.foto_1 = foto_1
        self.foto_2 = foto_2
        self.foto_3 = foto_3
        self.foto_4 = foto_4
        self.foto_5 = foto_5
        self.foto_6 = foto_6
        self.foto_7 = foto_7
        self.foto_8 = foto_8
        self.foto_9 = foto_9
        self.foto_10 = foto_10

class LucroVeiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    valor_compra = db.Column(db.Float)
    valor_venda = db.Column(db.Float)
    valor_total_aluguer = db.Column(db.Float)
    valor_total_manutencao = db.Column(db.Float)
    valor_lucro = db.Column(db.Float)

    veiculo = db.relationship('Veiculo', backref=db.backref('LucroVeiculos', lazy=True))

    def __init__(self, id_veiculo, valor_compra, valor_venda, valor_total_aluguer, valor_total_manutencao, valor_lucro):
        self.id_veiculo = id_veiculo
        self.valor_compra = valor_compra
        self.valor_venda = valor_venda
        self.valor_total_aluguer = valor_total_aluguer
        self.valor_total_manutencao = valor_total_manutencao
        self.valor_lucro = valor_total_manutencao - valor_compra + valor_venda + valor_total_aluguer

class Manutencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    descricao = db.Column(db.String)
    valor_manutencao = db.Column(db.Integer)
    km = db.Column(db.String)
    data = db.Column(db.String)

    veiculo = db.relationship('Veiculo', backref=db.backref('Manutencoes', lazy=True))

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_binary):
    if image_binary:
        encoded_image = base64.b64encode(image_binary).decode("utf-8")
        return f"data:image/png;base64,{encoded_image}"
    else:
        return None

@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s).decode('utf-8')

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/Home", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/Clientes", methods=["GET"])
def clientes():
    return render_template("clientes.html")

@app.route("/Criar-Novo-Cliente", methods=["GET", "POST"])
def criar_novo_cliente():
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            nif = request.form["nif"]
            telefone = request.form["telefone"]
            email = request.form["email"]
            morada = request.form["morada"]
            valor_pagar = float(request.form["valor_pagar"])
            data_pagamento = request.form["data_pagamento"] if request.form["data_pagamento"] else None
            veiculo_alugado = request.form["veiculo_alugado"]
            contrato = request.files["contrato"].read() if "contrato" in request.files else None
            cartao_identificacao = request.files['cartao_identificacao'].read() if 'cartao_identificacao' in request.files else None
            cartao_identificacao_verso = request.files['cartao_identificacao_verso'].read() if 'cartao_identificacao_verso' in request.files else None
            carta_conducao = request.files['carta_conducao'].read() if 'carta_conducao' in request.files else None
            carta_conducao_verso = request.files['carta_conducao_verso'].read() if 'carta_conducao_verso' in request.files else None
            novo_cliente = Alugador(
                nome=nome.title(),
                nif=nif,
                email=email,
                morada=morada,
                telefone=telefone,
                valor_pagar=valor_pagar,
                data_pagamento=data_pagamento,
                veiculo_alugado=veiculo_alugado.upper(),
                cartao_identificacao=cartao_identificacao,
                cartao_identificacao_verso=cartao_identificacao_verso,
                carta_conducao=carta_conducao,
                carta_conducao_verso=carta_conducao_verso
            )
            db.session.add(novo_cliente)
            db.session.commit()
            print("Cliente criado com sucesso.")
            if contrato:
                novo_contrato = Contrato(id_alugador=novo_cliente.id, contrato=contrato, data=datetime.now().strftime('%Y-%m-%d'))
                db.session.add(novo_contrato)
                db.session.commit()
                print("Registo em 'Contrato' criado com sucesso.")
            veiculo = Veiculo.query.filter_by(matricula=veiculo_alugado).first()
            if veiculo:
                id_veiculo = veiculo.id
                novo_sinistro = Sinistro(
                    id_alugador=novo_cliente.id,
                    data_inicio=datetime.now().strftime('%Y-%m-%d'),
                    id_veiculo=id_veiculo,
                    estado = "Aberto"
                )
                db.session.add(novo_sinistro)
                db.session.commit()
                print("Registo em 'Sinistro' criado com sucesso.")
            else:
                print("Veículo não encontrado.")
            return redirect(url_for("clientes"))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar cliente: {e}")
            return render_template("criar_novo_cliente.html", error=str(e))
    return render_template("criar_novo_cliente.html")

@app.route("/Pesquisar-Cliente", methods=["GET", "POST"])
def pesquisar_cliente():
    if request.method == "POST":
        termo_pesquisa_nome = request.form.get("nome")
        termo_pesquisa_nif = request.form.get("nif")
        termo_pesquisa_telefone = request.form.get("telefone")
        query = Alugador.query
        if termo_pesquisa_nome:
            query = query.filter(Alugador.nome.ilike(f"%{termo_pesquisa_nome}%"))
        if termo_pesquisa_nif:
            query = query.filter(Alugador.nif.ilike(f"%{termo_pesquisa_nif}%"))
        if termo_pesquisa_telefone:
            query = query.filter(Alugador.telefone.ilike(f"%{termo_pesquisa_telefone}%"))
        resultados = query.all()
        for cliente in resultados:
            cliente.sinistro_aberto = Sinistro.query.filter_by(id_alugador=cliente.id, estado="Aberto").order_by(desc(Sinistro.id)).first()
        return render_template("pesquisar_cliente.html", resultados=resultados)
    else:
        return render_template("pesquisar_cliente.html")

@app.route("/Editar-Cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    cliente = Alugador.query.get_or_404(id)
    if request.method == "POST":
        data_atualizada = {}
        campos = ['nome', 'nif', 'telefone', 'email', 'morada', 'valor_pagar', 'data_pagamento', 'veiculo_alugado']
        for campo in campos:
            valor_novo = request.form.get(campo)
            valor_atual = getattr(cliente, campo)
            if valor_novo != valor_atual:
                data_atualizada[campo] = valor_novo
        if data_atualizada:
            for campo, valor in data_atualizada.items():
                setattr(cliente, campo, valor)
            db.session.commit()
            flash('Alterações salvas com sucesso!', 'success')
        else:
            flash('Nenhuma alteração detectada.', 'info')
        if 'contrato' in request.files:
            contrato_file = request.files['contrato']
            if contrato_file and allowed_file(contrato_file.filename):
                contrato_data = contrato_file.read()
                novo_contrato = Contrato(
                    id_alugador=cliente.id,
                    contrato=contrato_data,
                    data=datetime.now().strftime('%Y-%m-%d')
                )
                db.session.add(novo_contrato)
                db.session.commit()
                flash('Contrato adicionado com sucesso!', 'success')
        return redirect(url_for('editar_cliente', id=id))
    else:
        return render_template("editar_cliente.html", cliente=cliente)

@app.route('/download-documentos/<int:alugador_id>', methods=['GET'])
def download_documentos(alugador_id):
    alugador = Alugador.query.get_or_404(alugador_id)
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        if alugador.cartao_identificacao:
            zf.writestr('cartao_identificacao.jpg', alugador.cartao_identificacao)
        if alugador.cartao_identificacao_verso:
            zf.writestr('cartao_identificacao_verso.jpg', alugador.cartao_identificacao_verso)
        if alugador.carta_conducao:
            zf.writestr('carta_conducao.jpg', alugador.carta_conducao)
        if alugador.carta_conducao_verso:
            zf.writestr('carta_conducao_verso.jpg', alugador.carta_conducao_verso)
    
    memory_file.seek(0)
    
    return send_file(memory_file, download_name=f'documentos_alugador_{alugador_id}.zip', as_attachment=True)

@app.route("/Terminar-Contrato/<int:id>", methods = ["POST"])
def terminar_contratos(id):
    if request.method == "POST":
        sinistro = Sinistro.query.get_or_404(id)
        sinistro.data_fim = datetime.now().strftime('%Y-%m-%d')
        sinistro.estado = "Fechado"
        db.session.commit()
        return jsonify({'message': 'Terminado com sucesso.'}), 200

@app.route("/Criar-Sinistro/<int:id>", methods=["POST"])
def criar_sinistro(id):
    if request.method == "POST":
        alugador = Alugador.query.get_or_404(id)
        print(f"Alugador ID from URL: {id}")
        print(f"Alugador ID from Database: {alugador.id}")
        
        if alugador.veiculo_alugado:
            veiculo = Veiculo.query.filter_by(matricula=alugador.veiculo_alugado.upper()).first()
            print(f"Veículo alugado pelo Alugador (uppercase): {alugador.veiculo_alugado.upper()}")
            
            if veiculo:
                print(f"Veículo encontrado: ID {veiculo.id}, Matrícula {veiculo.matricula}")
                novo_sinistro = Sinistro(
                    id_alugador=alugador.id,
                    data_inicio=datetime.now().strftime('%Y-%m-%d'),
                    id_veiculo=veiculo.id,
                    estado="Aberto"
                )
                db.session.add(novo_sinistro)
                db.session.commit()
                print("Sinistro criado com sucesso.")
                return jsonify({'message': 'Criado com sucesso.'}), 200
            else:
                print("Veículo não encontrado.")
                return jsonify({'message': 'Veículo não encontrado.'}), 404
        else:
            print("Alugador não possui veículo alugado.")
            return jsonify({'message': 'Alugador não possui veículo alugado.'}), 400

@app.route("/Contratos/<int:id>", methods=["GET"])
def contratos(id):
    cliente = Alugador.query.get_or_404(id)
    contratos = Contrato.query.filter_by(id_alugador=id).order_by(desc(Contrato.data)).all()
    return render_template("contratos.html", cliente=cliente, contratos=contratos)

@app.route('/download-contrato/<int:contrato_id>', methods=['GET'])
def download_contrato(contrato_id):
    contrato = Contrato.query.get_or_404(contrato_id)
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode='w') as zip_file:
        zip_file.writestr(f'contrato_{contrato_id}.jpg', contrato.contrato)
    zip_data.seek(0)
    response = make_response(zip_data.getvalue())
    response.mimetype = 'application/zip'
    response.headers.set('Content-Disposition', 'attachment', filename=f'contrato_{contrato_id}.zip')
    return response

@app.route("/Sinistros/<int:id_alugador>", methods=["GET"])
def sinistros(id_alugador):
    alugador = Alugador.query.get(id_alugador)
    if not alugador:
        return render_template('404.html'), 404
    sinistros = Sinistro.query.filter_by(id_alugador=id_alugador).order_by(Sinistro.id.desc()).all()
    sinistros_list = []
    for sinistro in sinistros:
        sinistro_dict = {
            'id': sinistro.id,
            'data_inicio': sinistro.data_inicio,
            'data_fim': sinistro.data_fim,
            'id_veiculo': sinistro.id_veiculo,
            'estado': sinistro.estado
        }
        sinistros_list.append(sinistro_dict)
    return render_template('sinistros.html', alugador=alugador, sinistros_list=sinistros_list)

@app.route("/Pesquisar-Sinistros", methods=["GET", "POST"])
def pesquisar_sinistros():
    if request.method == "POST":
        matricula = request.form.get("matricula").upper()
        veiculo = Veiculo.query.filter_by(matricula=matricula).first()
        if veiculo:
            sinistros = Sinistro.query.filter_by(id_veiculo=veiculo.id).order_by(desc(Sinistro.id)).all()
            alugadores = {sinistro.id: Alugador.query.get(sinistro.id_alugador) for sinistro in sinistros}
            return render_template("pesquisar_sinistros.html", sinistros=sinistros, veiculo=veiculo, alugadores=alugadores)
        else:
            flash('Veículo não encontrado.', 'error')
            return render_template("pesquisar_sinistros.html", sinistros=None)
    else:
        return render_template("pesquisar_sinistros.html", sinistros=None)

@app.route("/Pagamentos", methods=["GET", "POST"])
def pagamentos_pendentes():
    if request.method == "GET":
        data_atual = datetime.now().strftime('%Y/%m/%d')
        clientes = Alugador.query.filter(Alugador._data_pagamento == data_atual).all()
        print(clientes)
        return render_template("pagamentos_pendentes.html", clientes=clientes)
    else:
        return render_template("pagamentos_pendentes.html")

@app.route("/validar-pagamento/<int:id>", methods=["POST"])
def validar_pagamento(id):
    data_pagamento = request.json.get('dataPagamento')
    alugador = Alugador.query.get(id)
    if alugador:
        data_pagamento_obj = datetime.strptime(data_pagamento, '%Y/%m/%d')
        nova_data_pagamento = data_pagamento_obj + timedelta(days=7)
        nova_data_pagamento_str = nova_data_pagamento.strftime('%Y/%m/%d')
        alugador._data_pagamento = nova_data_pagamento_str
        db.session.commit()
        veiculo = Veiculo.query.filter_by(matricula=alugador.veiculo_alugado).first()
        if veiculo:
            lucro_veiculo = LucroVeiculo.query.filter_by(id_veiculo=veiculo.id).first()
            if lucro_veiculo:
                lucro_veiculo.valor_total_aluguer += alugador.valor_pagar
                lucro_veiculo.valor_lucro = (lucro_veiculo.valor_total_aluguer - lucro_veiculo.valor_compra + lucro_veiculo.valor_venda - lucro_veiculo.valor_total_manutencao)
                
                db.session.commit()
            return jsonify({'message': 'Pagamento validado com sucesso', 'nova_data_pagamento': nova_data_pagamento_str})
        else:
            return jsonify({'message': 'Veículo não encontrado para o alugador'})
    else:
        return jsonify({'message': 'Alugador não encontrado'})

@app.route("/Veículos", methods=["GET"])
def veiculos():
    return render_template("veiculos.html")

@app.route("/Criar-Novo-Veiculo", methods=["GET", "POST"])
def criar_veiculo():
    if request.method == "POST":
        try:
            marca = request.form["marca"]
            modelo = request.form["modelo"]
            matricula = request.form["matricula"]
            ano = request.form["ano"]
            km = request.form["km"]
            valor_compra = int(request.form["valor_compra"])
            documento_veiculo = request.files["documento_veiculo"].read() if "documento_veiculo" in request.files else None
            foto_1 = request.files["foto_1"].read() if "foto_1" in request.files else None
            foto_2 = request.files["foto_2"].read() if "foto_3" in request.files else None
            foto_3 = request.files["foto_3"].read() if "foto_3" in request.files else None
            foto_4 = request.files["foto_4"].read() if "foto_4" in request.files else None
            foto_5 = request.files["foto_5"].read() if "foto_5" in request.files else None
            foto_6 = request.files["foto_6"].read() if "foto_6" in request.files else None
            foto_7 = request.files["foto_7"].read() if "foto_7" in request.files else None
            foto_8 = request.files["foto_8"].read() if "foto_8" in request.files else None
            foto_9 = request.files["foto_9"].read() if "foto_9" in request.files else None
            foto_10 = request.files["foto_10"].read() if "foto_10" in request.files else None
            novo_veiculo = Veiculo(
                marca = marca,
                modelo = modelo,
                matricula = matricula,
                ano = ano,
                km = km,
                documento_veiculo = documento_veiculo
            )
            db.session.add(novo_veiculo)
            db.session.commit()
            print("Veículo criado com sucesso.")
            if foto_1:
                nova_foto = FotosVeiculo(
                    id_veiculo = novo_veiculo.id,
                    foto_1 = foto_1,
                    foto_2 = foto_2,
                    foto_3 = foto_3,
                    foto_4 = foto_4,
                    foto_5 = foto_5,
                    foto_6 = foto_6,
                    foto_7 = foto_7,
                    foto_8 = foto_8,
                    foto_9 = foto_9,
                    foto_10 = foto_10
                )
                db.session.add(nova_foto)
                db.session.commit()
                print("Fotos do veículo criadas com sucesso.")
            novo_investimento = LucroVeiculo(
                id_veiculo = novo_veiculo.id,
                valor_compra = valor_compra,
                valor_venda = 0,
                valor_total_aluguer = 0,
                valor_total_manutencao = 0,
                valor_lucro = 0 - valor_compra
            )
            db.session.add(novo_investimento)
            db.session.commit()
            print("Investimento do veículo criado com sucesso.")
            return redirect(url_for("veiculos")) 
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar veiculo: {e}")
            flash("Erro ao criar veículo: " + str(e), "error")
            return redirect(url_for("veiculos"))  
    else:
        return render_template("criar_veiculo.html")

@app.route("/Pesquisar-Veiculo", methods = ["GET", "POST"])
def pesquisar_veiculos():
    if request.method == "POST":
        termo_pesquisa_marca = request.form.get("marca")
        termo_pesquisa_matricula = request.form.get("matricula")
        query = Veiculo.query
        if termo_pesquisa_marca:
            query = query.filter(Veiculo.marca.ilike(f'%{termo_pesquisa_marca}%'))
        if termo_pesquisa_matricula:
            query = query.filter(Veiculo.matricula.ilike(f'%{termo_pesquisa_matricula}%'))
        resultados = query.all()
        return render_template("pesquisar_veiculos.html", resultados=resultados)
    else:
        return render_template("pesquisar_veiculos.html")

@app.route("/Editar-Veiculo/<int:id>", methods=["POST", "GET"])
def editar_veiculos(id):
    veiculo = Veiculo.query.get_or_404(id)
    if request.method == "POST":
        data_atualizada = {}
        campos = ["marca", "modelo", "matricula", "ano", "km"]
        for campo in campos:
            valor_novo = request.form.get(campo)
            valor_atual = getattr(veiculo, campo)
            if valor_novo != valor_atual:
                data_atualizada[campo] = valor_novo
        if data_atualizada:
            for campo, valor in data_atualizada.items():
                setattr(veiculo, campo, valor)
            db.session.commit()
            flash('Alterações salvas com sucesso!', 'success')
        else:
            flash("Nenhuma alteração detetada", "info")
        return redirect(url_for("editar_veiculos", id=id))
    else:
        return render_template("editar_veiculo.html", veiculo=veiculo)

@app.route("/Adicionar-Manutencao", methods = ["GET", "POST"])
def adicionar_manutencao():
    if request.method == "POST":
        termo_pesquisa_marca = request.form.get("marca")
        termo_pesquisa_matricula = request.form.get("matricula")
        query = Veiculo.query
        if termo_pesquisa_marca:
            query = query.filter(Veiculo.marca.ilike(f'%{termo_pesquisa_marca}%'))
        if termo_pesquisa_matricula:
            query = query.filter(Veiculo.matricula.ilike(f'%{termo_pesquisa_matricula}%'))
        resultados = query.all()
        return render_template("adicionar_manutencao.html", resultados=resultados)
    else:
        return render_template("adicionar_manutencao.html")

@app.route("/Adicionar-Serviços/<int:id>", methods=["GET", "POST"])
def adicionar_servicos(id):
    veiculo = Veiculo.query.get_or_404(id)
    lucro_veiculo = LucroVeiculo.query.filter_by(id_veiculo=id).first()
    if not lucro_veiculo:
        lucro_veiculo = LucroVeiculo(
            id_veiculo=id,
            valor_compra=0,
            valor_venda=0,
            valor_total_aluguer=0,
            valor_total_manutencao=0,
            valor_lucro=0
        )
        db.session.add(lucro_veiculo)
        db.session.commit()

    if request.method == "POST":
        try:
            descricao = request.form["descricao"]
            valor_manutencao = float(request.form["valor_manutencao"])
            km = request.form["km"]
            novo_servico = Manutencao(
                id_veiculo=veiculo.id,
                descricao=descricao,
                valor_manutencao=valor_manutencao,
                km=km,
                data=datetime.now().strftime('%Y/%m/%d')
            )
            db.session.add(novo_servico)
            db.session.commit()
            lucro_veiculo.valor_total_manutencao += valor_manutencao
            lucro_veiculo.valor_lucro = (lucro_veiculo.valor_total_aluguer - lucro_veiculo.valor_compra + lucro_veiculo.valor_venda - lucro_veiculo.valor_total_manutencao)
            db.session.commit()

            flash('Serviço salvo com sucesso!', 'success')
            return redirect(url_for("veiculos"))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar serviço: {e}")
            flash("Erro ao adicionar serviço: " + str(e), "error")
            return redirect(url_for("veiculos"))
    else:
        return render_template("adicionar_servico.html", veiculo=veiculo)

@app.route('/download/<int:veiculo_id>', methods=['GET'])
def download_documento_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        if veiculo.documento_veiculo:
            zf.writestr('documento_veiculo.jpg', veiculo.documento_veiculo)
    memory_file.seek(0)
    return send_file(memory_file, download_name=f'documentos_veiculo_{veiculo_id}.zip', as_attachment=True)

@app.route('/download-fotos/<int:veiculo_id>', methods=['GET'])
def download_fotos_veiculo(veiculo_id):
    veiculo_fotos = FotosVeiculo.query.filter_by(id_veiculo=veiculo_id).order_by(FotosVeiculo.id.desc()).first()
    if not veiculo_fotos:
        abort(404, description="Fotos do veículo não encontradas")
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for i in range(1, 11):
            foto_attr = getattr(veiculo_fotos, f'foto_{i}')
            if foto_attr:
                zf.writestr(f'foto_{i}.jpg', foto_attr)
    memory_file.seek(0)
    return send_file(memory_file, download_name=f'fotos_veiculo_{veiculo_id}.zip', as_attachment=True)

@app.route("/Manutenção/<int:id>", methods=["GET"])
def manutencao(id):
    veiculo = Veiculo.query.get_or_404(id)
    manutencoes = Manutencao.query.filter_by(id_veiculo=id).order_by(Manutencao.id.desc()).all()
    return render_template("manutencao.html", veiculo=veiculo, manutencoes=manutencoes)

@app.route("/Lucro", methods=["GET", "POST"])
def lucro():
    if request.method == "POST":
        termo_pesquisa_marca = request.form.get("marca")
        termo_pesquisa_matricula = request.form.get("matricula")
        query = Veiculo.query
        if termo_pesquisa_marca:
            query = query.filter(Veiculo.marca.ilike(f'%{termo_pesquisa_marca}%'))
        if termo_pesquisa_matricula:
            query = query.filter(Veiculo.matricula.ilike(f'%{termo_pesquisa_matricula}%'))
        resultados = query.all()
        return render_template("lucro.html", resultados=resultados)
    else:
        return render_template("lucro.html")

@app.route("/Financeiro/<int:id>", methods=["GET"])
def financeiro_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    lucro_veiculo = LucroVeiculo.query.filter_by(id_veiculo=id).first()
    return render_template("financeiro.html", veiculo=veiculo, lucro = lucro_veiculo)

@app.route("/Outros", methods=["GET"])
def outros():
    return render_template("outros.html")


@app.route("/Definições", methods=["GET"])
def definicoes():
    return render_template("definicoes.html")

@app.route("/Dados-Aplicação", methods=["GET"])
def dados_aplicacao():
    return render_template("dados_aplicacao.html")

@app.route("/Finanças", methods=["GET"])
def financas_totais():
    total_valor_compra = db.session.query(db.func.sum(LucroVeiculo.valor_compra)).scalar() or 0
    total_valor_venda = db.session.query(db.func.sum(LucroVeiculo.valor_venda)).scalar() or 0
    total_valor_total_aluguer = db.session.query(db.func.sum(LucroVeiculo.valor_total_aluguer)).scalar() or 0
    total_valor_total_manutencao = db.session.query(db.func.sum(LucroVeiculo.valor_total_manutencao)).scalar() or 0
    
    total_valor_lucro = total_valor_venda + total_valor_total_aluguer - total_valor_compra - total_valor_total_manutencao
    total_registros = db.session.query(db.func.count(LucroVeiculo.id)).scalar()

    return render_template(
        "financas_totais.html",
        total_valor_compra=total_valor_compra,
        total_valor_venda=total_valor_venda,
        total_valor_total_aluguer=total_valor_total_aluguer,
        total_valor_total_manutencao=total_valor_total_manutencao,
        total_valor_lucro=total_valor_lucro,
        total_registros=total_registros
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True, port=5000)
