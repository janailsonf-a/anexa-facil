from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    # Se a chamada do React chegar aqui, esta mensagem DEVE aparecer no terminal
    print("\n--- [DIAGNÓSTICO] A ROTA DE TESTE /api/test FOI CHAMADA COM SUCESSO! ---\n")
    return jsonify(message="Olá! A comunicação com o backend Python está funcionando!")