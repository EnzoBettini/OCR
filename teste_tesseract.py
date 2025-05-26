import pytesseract
from PIL import Image
import os

# Configuração do caminho do Tesseract
tesseract_path = r'C:\Users\enzo.bettini\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def test_tesseract():
    print("Iniciando teste do Tesseract OCR...")

    # Verifica se o executável existe
    if os.path.exists(tesseract_path):
        print(f"✓ Tesseract encontrado em: {tesseract_path}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        print(f"✗ Erro: Tesseract não encontrado em: {tesseract_path}")
        return False

    try:
        # Tenta obter a versão do Tesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Versão do Tesseract: {version}")

        # Lista idiomas disponíveis
        languages = pytesseract.get_languages()
        print(f"✓ Idiomas instalados: {', '.join(languages)}")

        # Verifica se português está instalado
        if 'por' in languages:
            print("✓ Idioma português encontrado")
        else:
            print("! Aviso: Idioma português não encontrado")

        print("\nTesseract está instalado e funcionando corretamente!")
        return True

    except Exception as e:
        print(f"\n✗ Erro ao testar Tesseract: {str(e)}")
        print("\nVerifique se:")
        print("1. O Tesseract está instalado corretamente")
        print("2. O caminho está correto")
        print("3. A instalação inclui os arquivos de idioma necessários")
        return False

if __name__ == "__main__":
    test_tesseract()
