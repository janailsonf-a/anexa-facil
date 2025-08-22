from flask import Flask, request, send_file
from PIL import Image, ImageOps
from pdf2image import convert_from_path
import io

# Inicializa a aplicação Flask
app = Flask(__name__)

# Define a rota da API. O React vai chamar "/api/process"
@app.route('/api/process', methods=['POST'])
def process_files():
    try:
        # Pega os arquivos que o React enviou
        boleto_file = request.files['boleto']
        comprovante_file = request.files['comprovante']

        # Converte os arquivos para bytes em memória
        boleto_bytes = boleto_file.read()
        comprovante_bytes = comprovante_file.read()

        # --- A MESMA LÓGICA DE PROCESSAMENTO QUE JÁ TEMOS ---
        # (copiada e colada da nossa versão anterior)

        # Etapa 1: Converter o PDF
        imagens_boleto = convert_from_path(boleto_bytes, dpi=300)
        imagem_boleto = imagens_boleto[0]

        # Etapa 2: Cortar o boleto
        imagem_invertida = ImageOps.invert(imagem_boleto.convert('RGB'))
        bbox = imagem_invertida.getbbox()
        imagem_boleto = imagem_boleto.crop(bbox)

        # Etapa 3: Processar o Comprovante
        imagem_comprovante = Image.open(io.BytesIO(comprovante_bytes))
        imagem_comprovante_rotacionada = imagem_comprovante.rotate(90, expand=True)

        # Etapa 4: Redimensionar
        largura_boleto, altura_boleto = imagem_boleto.size
        proporcao_comprovante = imagem_comprovante_rotacionada.height / imagem_comprovante_rotacionada.width
        nova_largura_comprovante = largura_boleto
        nova_altura_comprovante = int(proporcao_comprovante * nova_largura_comprovante)
        imagem_comprovante_final = imagem_comprovante_rotacionada.resize((nova_largura_comprovante, nova_altura_comprovante))

        # Etapa 5: Espaçamentos
        espacamento_meio_pixels = 60
        margem_inferior_pixels = 80

        # Etapa 6: Criar imagem final
        altura_total = altura_boleto + espacamento_meio_pixels + nova_altura_comprovante + margem_inferior_pixels
        imagem_final = Image.new('RGB', (largura_boleto, altura_total), 'white')

        # Etapa 7: Colar
        imagem_final.paste(imagem_boleto, (0, 0))
        imagem_final.paste(imagem_comprovante_final, (0, altura_boleto + espacamento_meio_pixels))

        # Etapa 8: Salvar em memória
        buffer_saida = io.BytesIO()
        imagem_final.save(buffer_saida, "PDF", resolution=300.0)
        buffer_saida.seek(0)

        # Envia o arquivo PDF de volta para o React
        return send_file(
            buffer_saida,
            as_attachment=True,
            download_name='comprovante_final.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        # Se der erro, envia uma mensagem de erro
        return {"error": str(e)}, 500