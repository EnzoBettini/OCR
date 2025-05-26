from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from nf_processor import NotaFiscalProcessor

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/process-invoice', methods=['POST'])
def process_invoice():
    try:
        # Verifica se há arquivo na requisição
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            print(f"[INFO] Arquivo recebido: {filename}")

            # Processamento
            processor = NotaFiscalProcessor()
            result = processor.process_document(filepath)

            # Remove arquivo após o processamento
            os.remove(filepath)

            if result:
                print("[INFO] Dados extraídos com sucesso.")
                return jsonify(result)
            else:
                print("[WARNING] Falha na extração de dados.")
                return jsonify({'error': 'Não foi possível extrair os dados da nota fiscal'}), 400

        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

    except Exception as e:
        print(f"[ERROR] Erro no processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno no servidor'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
