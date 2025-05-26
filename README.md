# Processador de Notas Fiscais com IA

Este projeto utiliza OCR (Reconhecimento Ótico de Caracteres) e a API da OpenAI para extrair informações de notas fiscais em formato PDF ou imagem. O sistema possui uma interface web moderna construída com Vue.js e um backend em Python/Flask.

## Requisitos do Sistema

### Backend

- Python 3.8 ou superior
- Tesseract OCR instalado no sistema
- Poppler (para processamento de PDFs)
- Chave de API da OpenAI

### Frontend

- Node.js 16 ou superior
- NPM ou Yarn

## Instalação

### 1. Configuração do Backend

1. Instale o Tesseract OCR:

   - Windows: Baixe e instale do [instalador oficial](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

2. Instale o Poppler:

   - Windows: Baixe de [poppler para Windows](http://blog.alivate.com.au/poppler-windows/)
   - Linux: `sudo apt-get install poppler-utils`
   - Mac: `brew install poppler`

3. Configure o ambiente Python:

```bash
# Entre no diretório backend
cd backend

# Instale as dependências
pip install -r requirements.txt
```

4. Configure suas credenciais da OpenAI:
   - Crie um arquivo `.env` no diretório `backend` com:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   OPENAI_MODEL=gpt-3.5-turbo
   ```

### 2. Configuração do Frontend

1. Instale as dependências do frontend:

```bash
# Entre no diretório do frontend
cd frontend/nf_reader

# Instale as dependências
npm install
```

## Executando o Projeto

1. Inicie o backend:

```bash
# No diretório backend
python app.py
```

O servidor Flask iniciará em `http://localhost:5000`

2. Em outro terminal, inicie o frontend:

```bash
# No diretório frontend/nf_reader
npm run dev
```

O servidor de desenvolvimento Vue iniciará em `http://localhost:5173`

3. Acesse a aplicação em seu navegador em `http://localhost:5173`

## Uso

1. Acesse a interface web
2. Arraste e solte uma nota fiscal (PDF ou imagem) ou clique para selecionar o arquivo
3. O sistema processará automaticamente o documento e exibirá as informações extraídas:
   - Número da nota fiscal
   - Data de emissão
   - Valor total
   - CNPJ do emitente
   - Nome/Razão Social do emitente
   - Endereço do emitente
   - Chave de acesso
   - Lista de itens com detalhes

## Estrutura do Projeto

```
.
├── backend/
│   ├── app.py              # Servidor Flask
│   ├── nf_processor.py     # Processamento de notas fiscais
│   └── requirements.txt    # Dependências Python
│
└── frontend/
    └── nf_reader/         # Aplicação Vue.js
        ├── src/           # Código fonte
        ├── public/        # Arquivos estáticos
        └── package.json   # Dependências Node.js
```

## Solução de Problemas

### Backend

- Verifique se o Tesseract está instalado e acessível no PATH do sistema
- Confirme se o Poppler está instalado e configurado corretamente
- Verifique se a chave da API OpenAI está configurada no arquivo `.env`

### Frontend

- Certifique-se de que todas as dependências foram instaladas com `npm install`
- Verifique se o backend está rodando antes de iniciar o frontend
- Limpe o cache do navegador se houver problemas de exibição

## Tecnologias Utilizadas

- Backend:

  - Python
  - Flask
  - Tesseract OCR
  - OpenAI API
  - PDF2Image/Poppler

- Frontend:
  - Vue 3
  - Vite
  - CSS Moderno
