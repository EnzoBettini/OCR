import os
import json
import re
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import openai

# Carrega variáveis de ambiente
load_dotenv()

class NotaFiscalProcessor:
    def __init__(self):
        # Configura o Tesseract OCR
        tesseract_path = r'C:\Users\enzo.bettini\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            print(f"Tesseract encontrado em: {tesseract_path}")
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            self.pytesseract = pytesseract
        else:
            raise RuntimeError("Tesseract não encontrado no caminho padrão.")

        # Configura API Key e modelo
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL')

        if not self.api_key:
            raise ValueError("Chave da API OpenAI não encontrada no .env")

        if not self.model:
            raise ValueError("Modelo OpenAI não especificado no .env")

        # Aponta a chave diretamente no client
        openai.api_key = self.api_key

    def convert_pdf_to_images(self, pdf_path):
        """Converte um PDF em uma lista de imagens."""
        try:
            poppler_path = r'C:\Users\enzo.bettini\Desktop\Library\poppler-23.11.0\Library\bin'
            return convert_from_path(pdf_path, poppler_path=poppler_path)
        except Exception as e:
            print(f"Erro ao converter PDF: {str(e)}")
            return None

    def extract_text_from_image(self, image):
        """Executa OCR em uma imagem e retorna o texto extraído."""
        try:
            text = self.pytesseract.image_to_string(image, lang='por')
            print("\nTexto extraído do OCR:\n", text[:1000])  # Log para debug
            return text
        except Exception as e:
            print(f"Erro no OCR: {str(e)}")
            return ""

    def extract_json_block(self, text):
        """Extrai o primeiro bloco JSON válido de uma resposta textual."""
        match = re.search(r'{.*}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                print("JSON extraído, mas inválido.")
                return None
        return None

    def extract_invoice_data(self, text):
        """Envia o texto para o modelo da OpenAI para extrair os dados estruturados."""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um assistente especializado em extrair informações de notas fiscais brasileiras.\n"
                            "Responda com um JSON válido contendo os seguintes campos:\n"
                            "- número da nota fiscal\n"
                            "- data de emissão\n"
                            "- valor total\n"
                            "- CNPJ do emitente\n"
                            "- nome/razão social do emitente\n"
                            "- endereço do emitente\n"
                            "- chave de acesso (44 dígitos)\n"
                            "- lista de itens (com descrição, quantidade, valor unitário e valor total)\n\n"
                            "Caso não seja possível extrair as informações, responda apenas:\n"
                            "{\"erro\": \"Erro na extração de dados\"}"
                        )
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )

            reply_content = response.choices[0].message.content
            print("\nResposta do modelo:\n", reply_content)

            # Primeiro tenta o JSON direto
            try:
                return json.loads(reply_content)
            except json.JSONDecodeError:
                print("Tentando extrair JSON com regex...")
                return self.extract_json_block(reply_content)

        except Exception as e:
            print(f"Erro na API do OpenAI: {str(e)}")
            return None

    def process_document(self, file_path):
        """Processa um PDF ou imagem para extrair dados da nota fiscal."""
        print("Iniciando processamento da nota fiscal...")

        try:
            if file_path.lower().endswith('.pdf'):
                images = self.convert_pdf_to_images(file_path)
                if not images:
                    return None
                text = self.extract_text_from_image(images[0])
            else:
                image = Image.open(file_path)
                text = self.extract_text_from_image(image)

            if not text:
                print("Nenhum texto extraído do documento.")
                return None

            return self.extract_invoice_data(text)

        except Exception as e:
            print(f"\nErro inesperado durante o processamento: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
