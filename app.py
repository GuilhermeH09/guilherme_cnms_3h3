
from time import time
import threading
import serial
import time

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

dados_sensor = {
    "distancia":0,
    "timestamp":"--:--",
    "ultima_gravacao_data":"--:--:--",
    "ultima_valor_gravado":"--"
}

PORTA_SERIAL = 'COM7'
BAUD_RATE = 9600
INTERVALO = 5

distancia_atual = 0.0

def ler_porta_serial():
    global distancia_atual
    flag = 0
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Conectado na porta: {PORTA_SERIAL}")
        while True:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8').strip()

                if "distancia - " in linha:
                    try:
                        valor_str = linha.split("-")[1].strip()
                        distancia_atual = float(valor_str)
                        dados_sensor["distancia"] = distancia_atual
                        dados_sensor["timestamp"] = time.time()
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Erro na comunicação a porta serial: {e}")
        print("Verifique a porta está correta")
        time.sleep(INTERVALO)
        print("Tentando Conectar...")

HTML_TEMPLATE = """ 
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leitura de Sensor Arduino</title>
    <style>
        body{
            font-family:'Segoe UI, Tahoma, Geneva, Verdana, sans-serif';
            text-align: center;
            background-color: #f4f4f9;
            padding-top: 100px;
        }
        .card{
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            display: inline;
        }
        h1{
            color: #333;
            margin-top: 0;
        }
        .valor{
            font-size: 5em;
            font-weight: bold;
            color: #0078d7;
        }
        .unidade{
            font-size: 0.3em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Distancia Atual</h1>
        <div class="valor" id="distancia-display"> -- 
            <span class="unidade">cm</span>
        </div>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <h3 style="color: #666; font-size: 1.2em; margin-bottom: 10px">Registros</h3>
    </div>
    <script>
        function buscaDistancia(){
            fetch('/api/dados')
            .then(response => response.json())
            .then(data =>{
                document.getElementById('distancia-display').innerHTML = Fixed(2) + '<span class="unidade">cm</span>'
            })
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dados')
def api_dados():
    return jsonify(dados_sensor)

if __name__ == '__main__':
    thread_arduino = threading.Thread(target=ler_porta_serial, daemon=True)
    thread_arduino.start()

    print("Iniciando servidor web na porta 80...")
    app.run(host='0.0.0.0', port=80)