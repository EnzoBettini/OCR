<script setup>
import { ref } from "vue";

const API_URL = "http://localhost:5000";

const fileInput = ref(null);
const isDragging = ref(false);
const isProcessing = ref(false);
const error = ref(null);
const result = ref(null);

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) processFile(file);
};

const handleDrop = (event) => {
  isDragging.value = false;
  const file = event.dataTransfer.files[0];
  if (file) processFile(file);
};

const processFile = async (file) => {
  const allowedTypes = ["application/pdf", "image/jpeg", "image/png"];
  if (!allowedTypes.includes(file.type)) {
    error.value = "Tipo de arquivo não suportado. Use PDF, PNG ou JPEG.";
    return;
  }

  try {
    error.value = null;
    isProcessing.value = true;
    result.value = null;

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/api/process-invoice`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Erro ao processar nota fiscal");
    }

    result.value = data;
  } catch (err) {
    console.error("Erro:", err);
    error.value = err.message;
  } finally {
    isProcessing.value = false;
  }
};

const resetForm = () => {
  result.value = null;
  error.value = null;
  if (fileInput.value) fileInput.value.value = "";
};
</script>

<template>
  <div class="app-wrapper">
    <div class="container">
      <header class="app-header">
        <h1>Leitor de Notas Fiscais</h1>
        <p>Faça o upload de notas fiscais em PDF ou imagem.</p>
      </header>

      <div class="content-area">
        <div class="upload-area" :class="{ 'is-dragging': isDragging }" @dragenter.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false" @dragover.prevent @drop.prevent="handleDrop">
          <input type="file" ref="fileInput" class="file-input-hidden" @change="handleFileSelect"
            accept=".pdf,.png,.jpg,.jpeg" />

          <div v-if="!isProcessing && !result" class="upload-area-content">
            <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3 3m0 0l-3-3m3 3V8" />
            </svg>
            <p class="upload-text">
              Arraste e solte um arquivo aqui ou
              <button type="button" @click="$refs.fileInput.click()" class="upload-browse-button">
                clique para selecionar
              </button>
            </p>
            <p class="upload-hint">PDF, PNG, JPG ou JPEG</p>
          </div>

          <div v-if="isProcessing" class="processing-indicator">
            <div class="spinner"></div>
            <p>Processando nota fiscal...</p>
          </div>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <div v-if="result" class="results-section">
          <h2 class="results-title">Dados Extraídos</h2>

          <div class="card results-card">
            <div class="results-grid">
              <div class="result-item">
                <p class="result-label">Número da NF</p>
                <p class="result-value">{{ result["numero_da_nota_fiscal"] }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">Data de Emissão</p>
                <p class="result-value">{{ result["data_de_emissao"] }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">Valor Total</p>
                <p class="result-value">R$ {{ result["valor_total"] }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">CNPJ Emitente</p>
                <p class="result-value">{{ result["CNPJ_do_emitente"] }}</p>
              </div>
            </div>

            <div class="result-group">
              <p class="result-label">Nome Emitente</p>
              <p class="result-value">
                {{ result["nome/razao_social_do_emitente"] }}
              </p>
              <p class="result-label mt-3">Endereço</p>
              <p class="result-value">{{ result["endereco_do_emitente"] }}</p>
            </div>

            <div class="result-group">
              <p class="result-label">Chave de Acesso</p>
              <p class="result-value break-all">{{ result["chave_de_acesso"] }}</p>
            </div>

            <div class="result-group">
              <h3 class="items-title">Itens da Nota</h3>
              <div class="items-list">
                <div v-for="(item, index) in result['lista_de_itens']" :key="index" class="item-entry">
                  <p class="item-description">{{ item["descricao"] }}</p>
                  <div class="item-details-grid">
                    <div>
                      <span class="item-detail-label">Valor: </span>
                      <span class="item-detail-value">R$ {{ item["valor_unitario"] }}</span>
                    </div>
                    <div>
                      <span class="item-detail-label">Qtd: </span>
                      <span class="item-detail-value">{{ item["quantidade"] }}</span>
                    </div>
                    <div>
                      <span class="item-detail-label">Total: </span>
                      <span class="item-detail-value">R$ {{ item["valor_total"] }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="new-invoice-action">
            <button @click="resetForm" class="btn btn-primary">
              Processar Nova Nota
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Estilos Globais e Reset Básico */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.app-wrapper {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  background-color: #f3f4f6; /* Cinza bem claro de fundo */
  color: #1f2937; /* Cor de texto principal (cinza escuro) */
  line-height: 1.6;
  padding: 1rem;
  min-height: 100vh;
}

.container {
  max-width: 800px; /* Aumentei um pouco para mais espaço */
  margin: 2rem auto; /* Centraliza e adiciona margem no topo/baixo */
  padding: 0 1rem; /* Padding lateral para telas menores */
}

/* Cabeçalho */
.app-header {
  text-align: center;
  margin-bottom: 2.5rem; /* Aumentei o espaçamento */
}

.app-header h1 {
  font-size: 2.25rem; /* Aumentei o tamanho */
  font-weight: 700; /* bold */
  color: #111827; /* Um pouco mais escuro para o título principal */
  margin-bottom: 0.5rem;
}

.app-header p {
  font-size: 1rem;
  color: #4b5563; /* Cinza médio para o subtítulo */
}

.content-area {
  max-width: 700px; /* Conteúdo principal um pouco mais estreito */
  margin: 0 auto;
}

/* Área de Upload */
.upload-area {
  border: 2px dashed #cbd5e1; /* Cinza claro para a borda */
  border-radius: 0.75rem; /* Bordas mais arredondadas */
  padding: 2.5rem; /* Mais padding interno */
  text-align: center;
  background-color: #ffffff;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  margin-bottom: 1.5rem;
}

.upload-area.is-dragging {
  border-color: #3b82f6; /* Azul ao arrastar */
  background-color: #eff6ff; /* Fundo azul bem claro ao arrastar */
}

.file-input-hidden {
  display: none;
}

.upload-area-content {
}

.upload-icon {
  margin: 0 auto 1rem auto;
  height: 3rem; /* 48px */
  width: 3rem; /* 48px */
  color: #9ca3af; /* Cinza para o ícone */
}

.upload-text {
  margin-top: 1rem;
  font-size: 1rem;
  color: #4b5563;
}

.upload-browse-button {
  color: #3b82f6; /* Azul */
  font-weight: 500;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.upload-browse-button:hover {
  color: #2563eb; /* Azul mais escuro no hover */
  text-decoration: underline;
}

.upload-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280; /* Cinza mais claro para a dica */
}

/* Indicador de Processamento */
.processing-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #4b5563;
}

.spinner {
  animation: spin 1s linear infinite;
  border-radius: 50%;
  height: 2.5rem; /* 40px */
  width: 2.5rem; /* 40px */
  border: 3px solid #e0e7ff; /* Borda do spinner mais clara */
  border-top-color: #3b82f6; /* Cor principal do spinner */
  margin-bottom: 1rem;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Mensagem de Erro */
.error-message {
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
  background-color: #fee2e2; /* Fundo vermelho claro */
  color: #b91c1c; /* Texto vermelho escuro */
  border-radius: 0.5rem;
  border: 1px solid #fca5a5; /* Borda vermelha clara */
  font-size: 0.9rem;
}

/* Seção de Resultados */
.results-section {
  margin-top: 2.5rem; /* Mais espaço acima dos resultados */
}

.results-title {
  font-size: 1.75rem; /* Tamanho do título "Dados Extraídos" */
  font-weight: 600; /* semibold */
  color: #111827;
  margin-bottom: 1.5rem;
  text-align: left; /* Alinhado à esquerda para melhor leitura */
}

.card {
  background-color: #ffffff;
  border-radius: 0.75rem; /* Bordas mais arredondadas */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Sombra mais suave e moderna */
  padding: 2rem; /* Padding interno do card */
}

.results-card {
} /* Classe específica se precisar de mais overrides */

.results-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fit,
    minmax(250px, 1fr)
  ); /* Grid responsivo */
  gap: 1.5rem; /* Espaçamento entre os itens do grid */
  margin-bottom: 2rem; /* Espaço abaixo do grid principal */
}

.result-item {
}

.result-group {
  margin-bottom: 2rem; /* Espaço entre grupos de informações */
}
.result-group:last-child {
  margin-bottom: 0;
}

.result-label {
  font-size: 0.875rem; /* 14px */
  color: #6b7280; /* Cinza para labels */
  margin-bottom: 0.25rem;
  font-weight: 500; /* Medium */
}

.result-value {
  font-size: 1rem; /* 16px */
  color: #1f2937; /* Cor principal do texto */
  font-weight: 500; /* Medium */
}

.result-value.break-all {
  /* Mantendo sua classe para chave de acesso */
  word-break: break-all;
}

/* Itens da Nota */
.items-title {
  font-size: 1.25rem; /* 20px */
  font-weight: 600; /* semibold */
  color: #1f2937;
  margin-bottom: 1.25rem; /* Espaço abaixo do título "Itens" */
  border-top: 1px solid #e5e7eb; /* Linha separadora acima de "Itens" */
  padding-top: 1.5rem;
}

.items-list {
  space-y-4 > * + * {
    /* Equivalente ao space-y-4 do Tailwind */
    margin-top: 1rem;
  }
}

.item-entry {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb; /* Linha separadora entre itens */
}
.items-list > .item-entry:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.item-description {
  font-weight: 600; /* Semibold para descrição do item */
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.item-details-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fit,
    minmax(120px, 1fr)
  ); /* Grid responsivo para detalhes */
  gap: 0.75rem;
  font-size: 0.875rem; /* Tamanho menor para detalhes do item */
}

.item-detail-label {
  color: #6b7280; /* Cinza para label do detalhe */
}

.item-detail-value {
  color: #1f2937;
  font-weight: 500;
}

/* Botões */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem; /* Padding dos botões */
  font-size: 1rem;
  font-weight: 500; /* Medium */
  text-align: center;
  border-radius: 0.5rem; /* Bordas arredondadas */
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease,
    border-color 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: #3b82f6; /* Azul */
  color: #ffffff; /* Texto branco */
}

.btn-primary:hover {
  background-color: #2563eb; /* Azul mais escuro no hover */
}

.new-invoice-action {
  margin-top: 2rem; /* Espaço acima do botão "Nova Nota" */
  text-align: center;
}

/* Classes utilitárias simples que você usou (mantidas caso precise) */
.hidden {
  display: none;
}
.mt-2 {
  margin-top: 0.5rem;
}
.mt-3 {
  margin-top: 0.75rem;
} /* Adicionei para consistência */
.text-sm {
  font-size: 0.875rem;
}
.font-semibold {
  font-weight: 600;
}
.font-medium {
  font-weight: 500;
}
</style>
