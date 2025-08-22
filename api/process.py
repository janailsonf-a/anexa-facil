from flask import Flask, request, send_file
from PIL import Image, ImageOps
from pdf2image import convert_from_path
import io
import tempfile

# ESTA LINHA ESTAVA FALTANDO. ELA CRIA A APLICAÇÃO.
app = Flask(__name__)


@app.route('/api/process', methods=['POST'])
def process_files():
    print("\n--- [DEBUG] ROTA /api/process FOI CHAMADA ---")

    try:
        print("[DEBUG] Tentando pegar os arquivos do request...")
        boleto_file = request.files['boleto']
        comprovante_file = request.files['comprovante']
        print(f"[DEBUG] Arquivos recebidos: {boleto_file.filename}, {comprovante_file.filename}")

        boleto_bytes = boleto_file.read()
        comprovante_bytes = comprovante_file.read()

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
            temp_pdf.write(boleto_bytes)

            print("[DEBUG] Iniciando conversão do PDF a partir de um arquivo temporário...")
            imagens_boleto = convert_from_path(temp_pdf.name, dpi=300, poppler_path="/usr/bin")

        imagem_boleto = imagens_boleto[0]
        print("[DEBUG] Conversão do PDF concluída com sucesso.")

        imagem_invertida = ImageOps.invert(imagem_boleto.convert('RGB'))
        bbox = imagem_invertida.getbbox()
        imagem_boleto = imagem_boleto.crop(bbox)

        imagem_comprovante = Image.open(io.BytesIO(comprovante_bytes))
        imagem_comprovante_rotacionada = imagem_comprovante.rotate(90, expand=True)

        largura_boleto, altura_boleto = imagem_boleto.size
        proporcao_comprovante = imagem_comprovante_rotacionada.height / imagem_comprovante_rotacionada.width
        nova_largura_comprovante = largura_boleto
        nova_altura_comprovante = int(proporcao_comprovante * nova_largura_comprovante)
        imagem_comprovante_final = imagem_comprovante_rotacionada.resize((nova_largura_comprovante, nova_altura_comprovante))

        espacamento_meio_pixels = 200
        margem_inferior_pixels = 500

        altura_total = altura_boleto + espacamento_meio_pixels + nova_altura_comprovante + margem_inferior_pixels
        imagem_final = Image.new('RGB', (largura_boleto, altura_total), 'white')

        imagem_final.paste(imagem_boleto, (0, 0))
        imagem_final.paste(imagem_comprovante_final, (0, altura_boleto + espacamento_meio_pixels))

        buffer_saida = io.BytesIO()
        imagem_final.save(buffer_saida, "PDF", resolution=300.0)
        buffer_saida.seek(0)

        print("[DEBUG] Processo concluído. Enviando o arquivo PDF.")
        return send_file(
            buffer_saida,
            as_attachment=True,
            download_name='comprovante_final.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"\n--- [ERRO GRAVE NO BACKEND] ---")
        print(f"TIPO DE ERRO: {type(e).__name__}")
        print(f"MENSAGEM DE ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("--- FIM DO RELATÓRIO DE ERRO ---\n")
        return {"error": str(e)}, 500