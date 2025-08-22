# api/process.py
import os
import io
import tempfile
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps
import fitz  # PyMuPDF

app = Flask(__name__)

# Se estiver na Vercel, a URL pública é /api/process
# Dentro do Flask, use "/" para a function.
# Para ambiente local, também exponho "/api/process" para facilitar testes.

@app.post("/")
@app.post("/api/process")
def process_files():
    try:
        # validação
        if "boleto" not in request.files or "comprovante" not in request.files:
            return jsonify({"error": "Envie 'boleto' (PDF) e 'comprovante' (imagem)."}), 400

        boleto_file = request.files["boleto"]
        comprovante_file = request.files["comprovante"]

        boleto_bytes = boleto_file.read()
        comprovante_bytes = comprovante_file.read()

        # --- Renderiza a 1ª página do PDF sem Poppler (PyMuPDF) ---
        doc = fitz.open(stream=boleto_bytes, filetype="pdf")
        page = doc.load_page(0)
        # dpi ~300 para boa definição
        pix = page.get_pixmap(dpi=300, alpha=False)
        imagem_boleto = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # --- “Crop inteligente” (como você fazia com invert+getbbox) ---
        imagem_invertida = ImageOps.invert(imagem_boleto.convert("RGB"))
        bbox = imagem_invertida.getbbox()
        if bbox:
            imagem_boleto = imagem_boleto.crop(bbox)

        # --- Trata o comprovante ---
        imagem_comprovante = Image.open(io.BytesIO(comprovante_bytes)).convert("RGB")
        # rotaciona 90° (se não precisar, remova)
        imagem_comprovante = imagem_comprovante.rotate(90, expand=True)

        # redimensiona comprovante para a mesma largura do boleto
        largura_boleto, altura_boleto = imagem_boleto.size
        proporcao = imagem_comprovante.height / imagem_comprovante.width
        nova_largura = largura_boleto
        nova_altura = int(proporcao * nova_largura)
        imagem_comprovante = imagem_comprovante.resize((nova_largura, nova_altura))

        # layout final
        espacamento_meio = 200
        margem_inferior = 500
        altura_total = altura_boleto + espacamento_meio + nova_altura + margem_inferior

        imagem_final = Image.new("RGB", (largura_boleto, altura_total), "white")
        imagem_final.paste(imagem_boleto, (0, 0))
        imagem_final.paste(imagem_comprovante, (0, altura_boleto + espacamento_meio))

        # gera PDF em memória
        buffer_saida = io.BytesIO()
        imagem_final.save(buffer_saida, "PDF", resolution=300.0)
        buffer_saida.seek(0)

        return send_file(
            buffer_saida,
            as_attachment=True,
            download_name="comprovante_final.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        # log simples
        return jsonify({"error": str(e)}), 500
