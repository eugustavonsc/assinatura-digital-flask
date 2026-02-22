from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, Response
import fitz  # PyMuPDF
import base64
import io
import os
import re
from dotenv import load_dotenv

# 1. Pega o endereço exato de onde este arquivo (flask_app.py) está rodando
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# 2. Força o sistema a procurar o cofre (.env) exatamente nesta mesma pasta
caminho_env = os.path.join(DIRETORIO_BASE, '.env')
load_dotenv(caminho_env)

app = Flask(__name__)

# Puxa a chave secreta
app.secret_key = os.getenv('CHAVE_SECRETA')

# Configura a pasta de uploads
PASTA_UPLOADS = os.path.join(DIRETORIO_BASE, 'uploads')
os.makedirs(PASTA_UPLOADS, exist_ok=True)

# ==========================================
# REGRAS DE SEGURANÇA E LOGIN
# ==========================================

# 3. Puxa as senhas e já usa o .strip() para limpar qualquer espaço invisível que tenha ficado no .env
USUARIO_ADM = os.getenv('MEU_USUARIO')
if USUARIO_ADM: USUARIO_ADM = USUARIO_ADM.strip()

SENHA_ADM = os.getenv('MINHA_SENHA')
if SENHA_ADM: SENHA_ADM = SENHA_ADM.strip()

def id_eh_valido(pedido_id):
    return bool(re.match("^[0-9]+$", str(pedido_id)))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == USUARIO_ADM and senha == SENHA_ADM:
            session['logado'] = True
            return redirect(url_for('tela_upload'))
        else:
            erro = "Usuário ou senha incorretos. Tente novamente."

    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect(url_for('login'))

# ==========================================
# ROTAS DO PAINEL (NOVIDADES AQUI)
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def tela_upload():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        arquivo = request.files.get('arquivo_pdf')
        pedido_id_bruto = request.form.get('pedido_id')
        pedido_id = pedido_id_bruto.strip() if pedido_id_bruto else ""

        if not pedido_id or not id_eh_valido(pedido_id):
            return "Erro de Segurança: O número do pedido deve conter apenas números.", 400

        if not arquivo or not arquivo.filename.endswith('.pdf'):
            return "Por favor, anexe um arquivo PDF válido.", 400

        caminho_arquivo = os.path.join(PASTA_UPLOADS, f"pedido_{pedido_id}.pdf")
        arquivo.save(caminho_arquivo)

        link_cliente = f"{request.host_url}assinar/{pedido_id}"

        return f"""
        <div style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px; padding: 20px;">
            <h2 style='color: #28a745; margin-bottom: 5px;'>✅ Upload Sucesso!</h2>
            <p style='color: #555;'>PDF do pedido <b>{pedido_id}</b> está pronto.</p>
            <p style='margin-bottom: 10px;'>Envie este link para o cliente assinar:</p>

            <input type='text' id='link_gerado' value='{link_cliente}' style='width: 100%; max-width: 350px; padding: 15px; text-align: center; border: 2px solid #ddd; border-radius: 6px; font-size: 16px; margin-bottom: 15px; background-color: #f9f9f9;' readonly>
            <br>

            <button onclick="copiarLink()" id="btnCopiar" style="background-color: #333; color: white; border: none; padding: 15px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; margin-bottom: 10px; width: 100%; max-width: 350px; font-weight: bold; transition: 0.3s;">📋 Copiar Link</button>
            <br>

            <button onclick="compartilharWhatsApp()" style="background-color: #25D366; color: white; border: none; padding: 15px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; margin-bottom: 30px; width: 100%; max-width: 350px; font-weight: bold;">💬 Enviar por WhatsApp</button>
            <br>

            <a href='/' style='padding: 15px 20px; background-color: #cc0000; color: white; text-decoration: none; border-radius: 6px; display: inline-block; width: 100%; max-width: 310px; font-weight: bold; box-sizing: border-box;'>Voltar ao Painel</a>

            <script>
                function copiarLink() {{
                    var linkInput = document.getElementById("link_gerado");
                    linkInput.select();
                    linkInput.setSelectionRange(0, 99999);

                    navigator.clipboard.writeText(linkInput.value).then(function() {{
                        var btn = document.getElementById("btnCopiar");
                        btn.innerHTML = "✅ Copiado com sucesso!";
                        btn.style.backgroundColor = "#28a745";

                        setTimeout(function() {{
                            btn.innerHTML = "📋 Copiar Link";
                            btn.style.backgroundColor = "#333";
                        }}, 3000);
                    }});
                }}

                function compartilharWhatsApp() {{
                    var link = document.getElementById("link_gerado").value;
                    var mensagem = encodeURIComponent("Olá! Parabéns pela conquista! 🏍️ Segue o link para assinar a confirmação do seu brinde (Capacete) da campanha Acessório 0KM da Cajueiro Motos: " + link);
                    window.open("https://api.whatsapp.com/send?text=" + mensagem, "_blank");
                }}
            </script>
        </div>
        """

    return render_template('upload.html')

# NOVA ROTA: Lista de PDFs Assinados
@app.route('/downloads')
def lista_downloads():
    if not session.get('logado'):
        return redirect(url_for('login'))

    arquivos_assinados = []
    if os.path.exists(PASTA_UPLOADS):
        # Varre a pasta procurando os arquivos que começam com 'ASSINADO_'
        for nome_arquivo in os.listdir(PASTA_UPLOADS):
            if nome_arquivo.startswith('ASSINADO_') and nome_arquivo.endswith('.pdf'):
                # Extrai só o número para mostrar na tela
                pedido_id = nome_arquivo.replace('ASSINADO_pedido_', '').replace('.pdf', '')
                arquivos_assinados.append({
                    'nome_arquivo': nome_arquivo,
                    'pedido_id': pedido_id
                })

    # Ordena para os números menores/maiores (ordem alfabética)
    arquivos_assinados.sort(key=lambda x: x['pedido_id'])

    return render_template('lista.html', arquivos=arquivos_assinados)

# NOVA ROTA: Fazer o download do arquivo
@app.route('/baixar/<nome_arquivo>')
def baixar_arquivo(nome_arquivo):
    if not session.get('logado'):
        return redirect(url_for('login'))

    if not nome_arquivo.startswith('ASSINADO_') or not nome_arquivo.endswith('.pdf'):
        return "Arquivo inválido.", 400

    caminho_completo = os.path.join(PASTA_UPLOADS, nome_arquivo)
    if not os.path.exists(caminho_completo):
        return "Arquivo não encontrado.", 404

    # O as_attachment=True força o navegador a fazer o download em vez de tentar abrir
    return send_file(caminho_completo, as_attachment=True)

# NOVA ROTA: Apagar o arquivo
@app.route('/apagar/<nome_arquivo>', methods=['POST'])
def apagar_arquivo(nome_arquivo):
    if not session.get('logado'):
        return redirect(url_for('login'))

    # Validação de segurança dupla
    if not nome_arquivo.startswith('ASSINADO_') or not nome_arquivo.endswith('.pdf'):
        return "Arquivo inválido.", 400

    caminho_completo = os.path.join(PASTA_UPLOADS, nome_arquivo)

    # Se o arquivo existe, manda para o lixo e volta para a lista
    if os.path.exists(caminho_completo):
        os.remove(caminho_completo)

    return redirect(url_for('lista_downloads'))

# ==========================================
# ROTAS DO CLIENTE (ASSINATURA)
# ==========================================

@app.route('/assinar/<pedido_id>')
def assinar_pagina(pedido_id):
    if not id_eh_valido(pedido_id):
        return "Link inválido.", 400

    caminho_arquivo = os.path.join(PASTA_UPLOADS, f"pedido_{pedido_id}.pdf")

    if not os.path.exists(caminho_arquivo):
        return "<h3 style='font-family: Arial; color: red; text-align: center; margin-top: 50px;'>Este pedido não existe ou já foi assinado.</h3>", 404

    return render_template('assinar.html', pedido_id=pedido_id)

@app.route('/preview_pdf/<pedido_id>')
def preview_pdf(pedido_id):
    if not id_eh_valido(pedido_id):
        return "Link inválido.", 400

    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, f"pedido_{pedido_id}.pdf")
        with open(caminho_arquivo, "rb") as f:
            pdf_bytes = f.read()

        doc = fitz.open("pdf", pdf_bytes)
        pagina = doc[0]
        pix = pagina.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        doc.close()

        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/api/salvar_assinatura', methods=['POST'])
def salvar_assinatura():
    dados = request.json
    pedido_id = dados.get('pedido_id')
    imagem_base64 = dados.get('assinatura')

    if not id_eh_valido(pedido_id):
        return jsonify({"erro": "ID inválido."}), 400

    if not imagem_base64:
        return jsonify({"erro": "Assinatura não fornecida"}), 400

    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, f"pedido_{pedido_id}.pdf")

        formato, imgstr = imagem_base64.split(';base64,')
        img_bytes = base64.b64decode(imgstr)

        with open(caminho_arquivo, "rb") as f:
            pdf_bytes = f.read()

        doc = fitz.open("pdf", pdf_bytes)
        pagina = doc[0]

        areas_texto = pagina.search_for("VALORES GERAIS")

        if areas_texto:
            posicao_texto = areas_texto[0]
            retangulo_assinatura = fitz.Rect(50, posicao_texto.y0 - 60, 250, posicao_texto.y0)
        else:
            retangulo_assinatura = fitz.Rect(50, 600, 250, 660)

        pagina.insert_image(retangulo_assinatura, stream=img_bytes)

        nome_arquivo_saida = f"ASSINADO_pedido_{pedido_id}.pdf"
        caminho_saida = os.path.join(PASTA_UPLOADS, nome_arquivo_saida)
        doc.save(caminho_saida)
        doc.close()

        os.remove(caminho_arquivo)

        return jsonify({"mensagem": "PDF assinado com sucesso!", "arquivo": nome_arquivo_saida}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)