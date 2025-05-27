# Invoice Processor with AI

This project uses OCR (Optical Character Recognition) and the OpenAI API to extract information from invoices in PDF or image formats. The system features a modern web interface built with Vue.js and a backend in Python/Flask.

## System Requirements

### Backend

- Python 3.8 or higher
- Tesseract OCR installed on the system
- Poppler (for PDF processing)
- OpenAI API Key

### Frontend

- Node.js 16 or higher
- NPM or Yarn

## Installation

### 1. Backend Setup

1. Install Tesseract OCR:

   - Windows: Download and install from the [official installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

2. Install Poppler:

   - Windows: Download from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
   - Linux: `sudo apt-get install poppler-utils`
   - Mac: `brew install poppler`

3. Configure the Python environment:

   ```bash
   # Enter the backend directory
   cd backend

   # Install dependencies
   pip install -r requirements.txt

4. Set up your OpenAI credentials:
   Create a `.env` file in the `backend` directory with:

   ```
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

### 2. Frontend Setup

1. Install frontend dependencies:

   ```bash
   # Enter the frontend directory
   cd frontend/nf_reader

   # Install dependencies
   npm install
   ```

## Running the Project

1. Start the backend:

   ```bash
   # In the backend directory
   python app.py
   ```

   The Flask server will start at `http://localhost:5000`

2. In another terminal, start the frontend:

   ```bash
   # In the frontend/nf_reader directory
   npm run dev
   ```

   The Vue development server will start at `http://localhost:5173`

3. Open the application in your browser at `http://localhost:5173`

## Usage

1. Access the web interface
2. Drag and drop an invoice (PDF or image), or click to select the file
3. The system will automatically process the document and display the extracted information:

   * Invoice number
   * Issue date
   * Total amount
   * Issuer's CNPJ
   * Issuer’s name or legal name
   * Issuer’s address
   * Access key
   * List of items with details

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask server
│   ├── nf_processor.py     # Invoice processing
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    └── nf_reader/          # Vue.js application
        ├── src/            # Source code
        ├── public/         # Static files
        └── package.json    # Node.js dependencies
```

## Troubleshooting

### Backend

* Ensure Tesseract is installed and accessible in the system PATH
* Confirm Poppler is installed and configured correctly
* Verify that the OpenAI API key is set in the `.env` file

### Frontend

* Make sure all dependencies were installed with `npm install`
* Check if the backend is running before starting the frontend
* Clear your browser cache if you encounter display issues

## Technologies Used

* Backend:

  * Python
  * Flask
  * Tesseract OCR
  * OpenAI API
  * PDF2Image/Poppler

* Frontend:

  * Vue 3
  * Vite
  * Modern CSS

