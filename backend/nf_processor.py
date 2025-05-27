import os
import json
import re
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter # Adicionadas ImageEnhance e ImageFilter
from pdf2image import convert_from_path
import pytesseract
import openai
import traceback # Adicionado para melhor log de erros

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class NotaFiscalProcessor:
    def __init__(self):
        """
        Inicializa o processador de notas fiscais.
        Configura o caminho do Tesseract OCR e as credenciais da API OpenAI.
        """
        # Configura o Tesseract OCR
        tesseract_path_env = os.getenv('TESSERACT_CMD_PATH') # Tente carregar do .env primeiro
        default_tesseract_path = r'C:\Users\enzo.bettini\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' # Caminho padrão

        if tesseract_path_env and os.path.exists(tesseract_path_env):
            tesseract_path_to_use = tesseract_path_env
        elif os.path.exists(default_tesseract_path):
            tesseract_path_to_use = default_tesseract_path
        else:
            print("Aviso: Caminho do Tesseract não configurado explicitamente nem encontrado no local padrão. Tentando usar a instalação global.")
            tesseract_path_to_use = 'tesseract' # Padrão se não especificado e não encontrado

        try:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path_to_use
            version = pytesseract.get_tesseract_version() # Verifica se o Tesseract está acessível
            print(f"Tesseract OCR versão {version} encontrado e configurado em: {pytesseract.pytesseract.tesseract_cmd}")
            self.pytesseract = pytesseract
        except Exception as e:
            print(f"Erro ao configurar o Tesseract: {e}")
            print("Verifique se o Tesseract está instalado e se o caminho está correto no código ou na variável de ambiente TESSERACT_CMD_PATH.")
            raise RuntimeError(f"Tesseract não pôde ser configurado. Detalhes: {e}")

        # Configura API Key e modelo da OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL')

        if not self.api_key:
            raise ValueError("Chave da API OpenAI (OPENAI_API_KEY) não encontrada no arquivo .env")
        if not self.model:
            raise ValueError("Modelo OpenAI (OPENAI_MODEL) não especificado no arquivo .env")

        openai.api_key = self.api_key
        print(f"Modelo OpenAI configurado: {self.model}")

    def convert_pdf_to_images(self, pdf_path):
        """
        Converte um arquivo PDF em uma lista de objetos de imagem PIL.
        """
        try:
            poppler_path_env = os.getenv('POPPLER_PATH')
            default_poppler_path = r'C:\Users\enzo.bettini\Desktop\Library\poppler-23.11.0\Library\bin'
            path_to_use = poppler_path_env if poppler_path_env and os.path.exists(poppler_path_env) else default_poppler_path

            if not os.path.exists(path_to_use):
                 print(f"Aviso: Caminho do Poppler não configurado em POPPLER_PATH nem encontrado no local padrão ('{default_poppler_path}'). A conversão de PDF pode falhar se o Poppler não estiver no PATH do sistema.")
                 path_to_use_param = None # Usa o Poppler do PATH do sistema
            else:
                 path_to_use_param = path_to_use

            print(f"Convertendo PDF para imagens usando Poppler em: {path_to_use if path_to_use_param else 'PATH do sistema'}")
            images = convert_from_path(pdf_path, dpi=300, poppler_path=path_to_use_param)
            print(f"PDF convertido em {len(images)} imagem(ns).")
            return images
        except Exception as e:
            print(f"Erro ao converter PDF para imagens: {str(e)}")
            print("Verifique se o Poppler está instalado e se o caminho (POPPLER_PATH) está configurado corretamente.")
            return None

    def preprocess_image(self, image):
        """
        Aplica técnicas de pré-processamento em um objeto de imagem PIL para
        melhorar a qualidade (simulando uma "digitalização melhorada") para OCR.
        Argumentos:
            image (PIL.Image.Image): A imagem a ser pré-processada.
        Retorna:
            PIL.Image.Image: A imagem pré-processada.
        """
        print("Iniciando pré-processamento para 'digitalização melhorada'...")
        img = image.copy() # Trabalhar com uma cópia

        # 1. Converter para escala de cinza ('L')
        img = img.convert('L')
        print(f"- Convertida para escala de cinza. Modo: {img.mode}")

        # 2. Redimensionamento (Scaling) - Aumentar se a imagem for pequena
        original_width, original_height = img.size
        # Defina uma largura mínima desejada, por exemplo, para que o texto não seja muito pequeno.
        # Ajuste 'target_width' conforme necessário após testes.
        target_width = 2000 # pixels (exemplo)
        if original_width < target_width:
            scale_factor = target_width / original_width
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            print(f"- Redimensionando de ({original_width}x{original_height}) para ({new_width}x{new_height}) com Lanczos.")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"- Imagem redimensionada. Modo: {img.mode}")

        # 3. Ajuste de Contraste
        enhancer_contrast = ImageEnhance.Contrast(img)
        img = enhancer_contrast.enhance(1.5) # Experimente valores como 1.2 a 2.0
        print(f"- Contraste aumentado. Modo: {img.mode}")

        # 4. Remoção de Ruído (Opcional, aplicar com cuidado)
        # Descomente e teste se suas imagens tiverem muito ruído.
        # img = img.filter(ImageFilter.MedianFilter(size=3))
        # print(f"- Aplicado filtro de mediana (se descomentado). Modo: {img.mode}")

        # img = img.filter(ImageFilter.SMOOTH) # Alternativa mais suave
        # print(f"- Aplicado filtro SMOOTH (se descomentado). Modo: {img.mode}")

        # 5. Aumento da Nitidez (Sharpening)
        enhancer_sharpness = ImageEnhance.Sharpness(img)
        img = enhancer_sharpness.enhance(1.7) # Experimente valores como 1.5 a 2.5
        print(f"- Nitidez aumentada. Modo: {img.mode}")

        # 6. Binarização (Thresholding) - Crucial para o Tesseract
        threshold_value = 140  # Experimente valores entre 120 e 170.
        img = img.point(lambda x: 0 if x < threshold_value else 255, '1')
        print(f"- Aplicada binarização com limiar {threshold_value}. Modo: {img.mode}")

        # 7. GARANTIR MODO CORRETO PARA TESSERACT:
        # Se o Tesseract tiver problemas com o modo '1' diretamente (raro se a binarização for boa),
        # você pode converter de volta para 'L'. O Tesseract fará sua própria binarização interna.
        # if img.mode == '1':
        #     print(f"- Imagem está em modo '1'. Convertendo para 'L' para Tesseract.")
        #     img = img.convert('L')

        # Salve a imagem para depuração visual
        try:
            debug_image_path = "debug_preprocessed_scan_effect.png"
            img.save(debug_image_path)
            print(f"- Imagem de depuração ('scan effect') salva como: {debug_image_path}")
        except Exception as e:
            print(f"- Erro ao salvar imagem de depuração: {e}")

        print(f"Pré-processamento 'scan effect' concluído. Modo final para Tesseract: {img.mode}")
        return img

    def clean_ocr_text(self, text: str) -> str:
        """
        Limpa o texto extraído pelo OCR, removendo caracteres indesejados.
        """
        if not text:
            return ""

        # Caracteres a serem removidos. Você pode expandir esta string.
        # O caractere pipe '|' está incluído aqui, assim como outros comuns.
        chars_to_remove = "|\"$%*&()[]{}\\`~<>^" # Adicione outros conforme necessário

        cleaned_text = text
        for char in chars_to_remove:
            cleaned_text = cleaned_text.replace(char, "")

        # Opcional: Substituir múltiplos espaços por um único espaço e remover espaços nas extremidades
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        # Não vamos printar aqui para manter o log mais limpo, já temos o print do texto bruto.
        return cleaned_text

    def extract_text_from_image(self, image):
        """
        Executa OCR em um objeto de imagem PIL (após pré-processamento) e retorna o texto extraído.
        """
        try:
            processed_image = self.preprocess_image(image)

            # --- EXPERIMENTE DIFERENTES MODOS PSM ---
            # psm_mode = 6  # Assume um único bloco uniforme de texto.
            psm_mode = 4  # Assume uma única coluna de texto de tamanhos variáveis. (Bom para documentos)
            # psm_mode = 7  # Trata a imagem como uma única linha de texto.
            # psm_mode = 11 # Texto esparso.
            # psm_mode = 3  # Segmentação de página totalmente automática. (Padrão do Tesseract)

            custom_config = f'-l por --oem 3 --psm {psm_mode}'
            print(f"Extraindo texto com Tesseract usando config: '{custom_config}'")

            raw_text = self.pytesseract.image_to_string(processed_image, config=custom_config)

            if not raw_text.strip():
                print("Aviso: OCR não retornou texto. A imagem pode estar em branco ou o texto não é legível.")
                return ""
            else:
                print("\nTexto BRUTO extraído pelo OCR (antes da limpeza):\n", raw_text)

            cleaned_text = self.clean_ocr_text(raw_text)
            print("\nTexto LIMPO extraído pelo OCR (após remoção de caracteres indesejados):\n", cleaned_text)
            return cleaned_text # Retorna o texto já limpo

        except self.pytesseract.TesseractNotFoundError:
            print("Erro Crítico: Executável do Tesseract não encontrado. Verifique a instalação e a configuração do caminho.")
            raise
        except Exception as e:
            print(f"Erro durante a execução do OCR: {str(e)}")
            print(traceback.format_exc()) # Imprime o traceback completo do erro
            return ""

    def extract_json_block(self, text):
        """
        Extrai o primeiro bloco JSON válido de uma string de texto.
        """
        if not text:
            return None
        match = re.search(r'```json\s*({.*?})\s*```|({.*?})', text, re.DOTALL)
        if match:
            json_str = match.group(1) or match.group(2)
            if json_str:
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                    print(f"String JSON problemática (primeiros 500 chars): {json_str[:500]}")
                    return None
            else:
                print("Regex encontrou um padrão, mas o grupo de captura JSON estava vazio.")
                return None
        print("Nenhum bloco JSON encontrado na resposta com a regex.")
        return None

    def extract_invoice_data(self, text):
        """
        Envia o texto extraído para o modelo da OpenAI para extrair dados estruturados.
        """
        if not text or not text.strip():
            print("Texto de entrada para OpenAI está vazio. Retornando erro.")
            return {"erro": "Nenhum texto legível foi extraído da imagem para enviar à OpenAI."}

        system_prompt = (
            "Você é um assistente altamente especializado em extrair informações detalhadas de textos de notas fiscais brasileiras (NF-e ou NFS-e).\n"
            "Analise o texto fornecido e responda SOMENTE com um objeto JSON válido.\n"
            "O JSON deve conter os seguintes campos:\n"
            "- 'numero_nota_fiscal': (string) O número da nota fiscal.\n"
            "- 'data_emissao': (string) A data de emissão no formato 'DD/MM/AAAA'.\n"
            "- 'valor_total': (float) O valor total da nota. Use ponto como separador decimal. Se não encontrar, use null.\n"
            "- 'cnpj_emitente': (string) O CNPJ do emitente, contendo apenas números (remova pontos, barras e traços).\n"
            "- 'nome_razao_social_emitente': (string) O nome ou razão social do emitente.\n"
            "- 'endereco_emitente': (string) O endereço completo do emitente.\n"
            "- 'chave_acesso': (string) A chave de acesso da NF-e (44 dígitos numéricos). Se não for uma NF-e ou não encontrar, use null.\n"
            "- 'itens': (lista de objetos) Uma lista de itens da nota. Cada item deve ser um objeto com os campos:\n"
            "  - 'descricao': (string) Descrição do item/serviço.\n"
            "  - 'quantidade': (float) Quantidade do item. Use ponto como separador decimal.\n"
            "  - 'valor_unitario': (float) Valor unitário do item. Use ponto como separador decimal.\n"
            "  - 'valor_total_item': (float) Valor total do item (quantidade * valor_unitario). Use ponto como separador decimal.\n"
            "O número da nota NUNCA virá acompanhado de 'RPS'.\n"
            "O número da NFS geralmente vem próximo de frases como 'Número da NF-E' ou 'Numero da nota' ou frases semelhantes.\n"
            "Sempre utilize ponto como separador decimal e não utilize separador de milhar.\n"
            "Ao colocar o emitente da nota fiscal, esse deve estar próximo a frases como 'prestador de serviço' ou 'emitente' vinculado a uma razão social.\n"
            "Se um campo específico não puder ser encontrado no texto, seu valor no JSON deve ser null.\n"
            "Se partes de um campo estiverem fragmentadas no texto (por exemplo, endereço quebrado em várias linhas), una essas partes logicamente para preencher o campo completo.\n"
            "Campos numéricos (quantidade, valor_unitario, valor_total, etc.) devem ser representados como números reais (sem aspas). Verifique a coerência entre valor_total_item = quantidade × valor_unitario.\n"
            "Se o CNPJ ou a chave de acesso estiverem incompletos, com menos dígitos ou em formato inválido, retorne null.\n"
            "Se houver múltiplos valores possíveis para um campo (por exemplo, mais de uma data ou valor), escolha o que estiver mais fortemente associado ao contexto da emissão da nota fiscal.\n"
            "O texto de entrada pode conter erros de OCR. Tente interpretar e corrigir erros comuns (ex: '1' por 'I', '0' por 'O', letras trocadas, caracteres faltando ou sobrando) ao preencher os campos, baseando-se no contexto de uma nota fiscal brasileira e na estrutura esperada para cada campo.\n"
            "Se o texto fornecido não parecer ser de uma nota fiscal ou se a extração falhar significativamente, responda com: {\"erro\": \"Não foi possível extrair dados da nota fiscal a partir do texto fornecido.\"}"
        )
        user_prompt = f"Por favor, extraia os dados da seguinte nota fiscal, conforme as instruções:\n\n```text\n{text}\n```"

        print("Enviando texto para o modelo OpenAI...")
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
            )
            reply_content = response.choices[0].message.content
            print("\nResposta bruta do modelo OpenAI:\n", reply_content)
            extracted_json = self.extract_json_block(reply_content)

            if extracted_json:
                if "erro" in extracted_json and extracted_json["erro"] == "Não foi possível extrair dados da nota fiscal a partir do texto fornecido.":
                    print(f"Modelo OpenAI indicou erro na extração: {extracted_json['erro']}")
                return extracted_json
            else:
                print("Não foi possível parsear um bloco JSON da resposta do modelo OpenAI usando a regex.")
                try:
                    direct_parsed_json = json.loads(reply_content)
                    print("Conteúdo da resposta foi parseado diretamente como JSON.")
                    return direct_parsed_json
                except json.JSONDecodeError:
                    print("A resposta completa do modelo também não é um JSON válido.")
                    return {"erro": "Resposta do modelo OpenAI não é um JSON válido ou não foi possível extrair o bloco JSON."}
        except openai.APIError as e:
            print(f"Erro na API do OpenAI: {str(e)}")
            return {"erro": f"Erro na comunicação com a API OpenAI: {str(e)}"}
        except Exception as e:
            print(f"Erro inesperado ao chamar a API OpenAI: {str(e)}")
            print(traceback.format_exc())
            return {"erro": f"Erro inesperado ao processar resposta da OpenAI: {str(e)}"}

    def process_document(self, file_path):
        """
        Processa um arquivo (PDF ou imagem) para extrair dados da nota fiscal.
        """
        print(f"\n--- Iniciando processamento do documento: {file_path} ---")
        try:
            text = ""
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                images = self.convert_pdf_to_images(file_path)
                if not images:
                    print(f"Falha ao converter PDF '{file_path}' para imagem.")
                    return {"erro": f"Falha ao converter PDF '{file_path}' para imagem."}
                if images:
                    print("Processando a primeira página do PDF.")
                    text = self.extract_text_from_image(images[0])
            elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
                print(f"Abrindo arquivo de imagem: {file_path}")
                image = Image.open(file_path)
                text = self.extract_text_from_image(image)
            else:
                print(f"Formato de arquivo não suportado: {file_path}")
                return {"erro": f"Formato de arquivo não suportado: {file_extension}. Use PDF, PNG, JPG, JPEG, TIFF, BMP ou GIF."}

            if not text or not text.strip():
                print("Nenhum texto foi extraído do documento após OCR e limpeza.")
                return {"erro": "Nenhum texto legível foi extraído do documento."}

            extracted_data = self.extract_invoice_data(text)
            print(f"--- Processamento do documento {file_path} concluído. ---")
            return extracted_data
        except Exception as e:
            print(f"\nErro inesperado durante o processamento do documento '{file_path}': {str(e)}")
            print(traceback.format_exc())
            return {"erro": f"Erro inesperado durante o processamento do documento: {str(e)}"}

# --- Exemplo de Uso ---
if __name__ == "__main__":
    print("--- Iniciando Demonstração do Processador de Notas Fiscais ---")
    try:
        processor = NotaFiscalProcessor()

        # Substitua pelo caminho do seu arquivo de nota fiscal (PDF ou imagem)
        file_to_process = "documento_exemplo.jpg" #  <--- COLOQUE SEU ARQUIVO DE TESTE AQUI (PDF ou imagem)

        if not os.path.exists(file_to_process):
            print(f"\nATENÇÃO: Arquivo de exemplo '{file_to_process}' não encontrado.")
            print("Por favor, crie um arquivo PDF ou de imagem com este nome no diretório do script,")
            print("ou altere a variável 'file_to_process' no código para apontar para seu arquivo de teste.")
        else:
            print(f"\nProcessando o arquivo: {file_to_process}")
            dados_nota = processor.process_document(file_to_process)

            if dados_nota:
                print("\n--- Resultado Final do Processamento ---")
                if "erro" in dados_nota:
                    print(f"Erro ao processar a nota fiscal: {dados_nota['erro']}")
                else:
                    print("Dados da Nota Fiscal Extraídos com Sucesso:")
                    print(json.dumps(dados_nota, indent=4, ensure_ascii=False)) # ensure_ascii=False para imprimir acentos corretamente
            else:
                print("\nNenhum dado foi retornado do processamento.")

    except ValueError as ve:
        print(f"\nErro de Configuração: {ve}")
    except RuntimeError as rte:
        print(f"\nErro de Runtime: {rte}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado na execução principal: {e}")
        print(traceback.format_exc())

    print("\n--- Demonstração Concluída ---")
