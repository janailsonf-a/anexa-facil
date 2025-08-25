from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps
import io
import tempfile
import re

import fitz  # PyMuPDF

app = Flask(__name__)

# --------- MESMAS FUNÇÕES DE EXTRAÇÃO ----------
def extrair_nome_pagador(texto_completo):
    linhas = texto_completo.split('\n')
    for i, linha in enumerate(linhas):
        if re.search(r'pagador', linha, re.IGNORECASE):
            partes = re.split(r':\s*', linha)
            if len(partes) > 1 and partes[1].strip():
                return partes[1].strip()
            if i + 1 < len(linhas) and linhas[i+1].strip():
                return linhas[i+1].strip()
    return None

def extrair_data_vencimento(texto_completo):
    match = re.search(r'(\d{2})/(\d{2})/(\d{4})', texto_completo)
    if match:
        return match.group(2), match.group(3)
    return None
# ------------------------------------------------

@app.route('/api/process', methods=['POST'])
def process_files():
    try:
        # --- VALIDAÇÃO DE ENTRADA ---
        if 'boleto' not in request.files or 'comprovante' not in request.files:
            return jsonify(error="Ambos os arquivos (boleto e comprovante) são obrigatórios."), 400

        boleto_file = request.files['boleto']
        comprovante_file = request.files['comprovante']

        if boleto_file.filename == '' or comprovante_file.filename == '':
            return jsonify(error="Por favor, selecione ambos os arquivos."), 400

        if boleto_file.mimetype != 'application/pdf':
            return jsonify(error=f"Arquivo '{boleto_file.filename}' não é um PDF válido."), 400

        if not comprovante_file.mimetype.startswith('image/'):
            return jsonify(error=f"Arquivo '{comprovante_file.filename}' não é uma imagem válida."), 400
        # --- FIM VALIDAÇÃO ---

        boleto_bytes = boleto_file.read()
        comprovante_bytes = comprovante_file.read()

        # ---------- ABRIR PDF COM PyMuPDF (SEM POPPLER) ----------
        # Abre o PDF a partir dos bytes
        doc = fitz.open(stream=boleto_bytes, filetype="pdf")
        if doc.page_count == 0:
            return jsonify(error="PDF do boleto está vazio."), 400

        page = doc.load_page(0)

        # Extrair texto nativo do PDF (dispensa OCR/Tesseract)
        texto_do_boleto = page.get_text("text") or ""

        # Renderizar a página como imagem (equivalente ao convert_from_path)
        # 300 DPI -> zoom = 300/72
        zoom = 300 / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Converter Pixmap -> PIL.Image
        img_bytes = pix.tobytes("png")
        imagem_boleto = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        # ----------------------------------------------------------

        # --------- EXTRAÇÕES (iguais) ----------
        nome_pagador_completo = extrair_nome_pagador(texto_do_boleto)
        data_vencimento = extrair_data_vencimento(texto_do_boleto)

        nome_do_arquivo = "comprovante_final.pdf"

        if nome_pagador_completo and data_vencimento:
            primeiro_nome = nome_pagador_completo.split(' ')[0].capitalize()
            mes_num, ano = data_vencimento
            meses_pt = {
                "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
                "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
                "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
            }
            mes_nome = meses_pt.get(mes_num, mes_num)
            nome_do_arquivo = f"{primeiro_nome} - Pagamento Mensal Bolsa Faculdade - [{mes_nome}-{ano}].pdf"
        # ---------------------------------------

        # --------- CROP (mesma lógica) ----------
        imagem_invertida = ImageOps.invert(imagem_boleto.convert('RGB'))
        bbox = imagem_invertida.getbbox()
        if bbox:
            imagem_boleto = imagem_boleto.crop(bbox)
        # ----------------------------------------

        # --------- TRATAR COMPROVANTE (igual) ----------
        imagem_comprovante = Image.open(io.BytesIO(comprovante_bytes)).convert("RGB")
        imagem_comprovante_rotacionada = imagem_comprovante.rotate(90, expand=True)

        largura_boleto, altura_boleto = imagem_boleto.size
        proporcao_comprovante = imagem_comprovante_rotacionada.height / imagem_comprovante_rotacionada.width
        nova_largura_comprovante = largura_boleto
        nova_altura_comprovante = int(proporcao_comprovante * nova_largura_comprovante)
        imagem_comprovante_final = imagem_comprovante_rotacionada.resize(
            (nova_largura_comprovante, nova_altura_comprovante)
        )

        espacamento_meio_pixels = 300
        margem_inferior_pixels = 80

        altura_total = altura_boleto + espacamento_meio_pixels + nova_altura_comprovante + margem_inferior_pixels
        imagem_final = Image.new('RGB', (largura_boleto, altura_total), 'white')

        imagem_final.paste(imagem_boleto, (0, 0))
        imagem_final.paste(imagem_comprovante_final, (0, altura_boleto + espacamento_meio_pixels))
        # -----------------------------------------------

        # --------- GERAR PDF EM MEMÓRIA ----------
        buffer_saida = io.BytesIO()
        imagem_final.save(buffer_saida, "PDF", resolution=300.0)
        buffer_saida.seek(0)
        # -----------------------------------------

        return send_file(
            buffer_saida,
            as_attachment=True,
            download_name=nome_do_arquivo,
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"\n--- [ERRO GRAVE NO BACKEND] ---")
        print(f"TIPO DE ERRO: {type(e).__name__}")
        print(f"MENSAGEM DE ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("--- FIM DO RELATÓRIO DE ERRO ---\n")
        return jsonify(error="Ocorreu um erro inesperado no servidor."), 500
