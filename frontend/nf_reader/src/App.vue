<script setup>
import { ref } from "vue";

// --- Lógica original da sua aplicação (mantida) ---
const API_URL = "http://localhost:5000"; // Sua URL de API

const fileInput = ref(null);
const isDragging = ref(false);
const isProcessing = ref(false);
const error = ref(null);
const result = ref(null); // Este vai armazenar o JSON da API

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
      throw new Error(data.erro || data.error || "Erro ao processar nota fiscal"); // data.erro para seu backend Python
    }

    result.value = data; // 'data' já é o JSON parseado

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
  isDragging.value = false;
};

// --- Funções Utilitárias para Formatação ---
const formatCurrency = (value) => {
  if (value === null || value === undefined) return "N/A";
  const number = Number(value);
  if (isNaN(number)) return "Valor inválido";
  return number.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
};

const formatCNPJ = (cnpj) => {
  if (!cnpj) return "N/A";
  // Remove caracteres não numéricos
  const cleaned = ('' + cnpj).replace(/\D/g, '');
  // Aplica a máscara
  if (cleaned.length === 14) {
    return cleaned.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      "$1.$2.$3/$4-$5"
    );
  }
  return cnpj; // Retorna original se não tiver 14 dígitos
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  // A data já vem em DD/MM/AAAA, então podemos apenas retornar
  // Se precisasse de formatação:
  // const [day, month, year] = dateString.split('/');
  // return `${day}/${month}/${year}`;
  return dateString;
};

const formatChaveAcesso = (chave) => {
  if (!chave) return "N/A";
  // Formata em blocos de 4 dígitos
  return chave.replace(/\s/g, '').replace(/(.{4})/g, '$1 ').trim();
};

// --- Lógica para o layout AdminLTE (mantida) ---
const activeTab = ref('processar_nf');
const sidebarOpen = ref(true); // Deixar aberto por padrão em telas maiores

const navigateTo = (tabName) => {
  activeTab.value = tabName;
  if (window.innerWidth < 768 && sidebarOpen.value) { // Fecha a sidebar em mobile ao navegar
    sidebarOpen.value = false;
  }
};

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const menuItems = [
  { id: 'processar_nf', label: 'Processar NF', icon: 'M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2zM7 8v2h10V8H7zm0 4v2h10v-2H7zm0 4v2h7v-2H7z' },
  { id: 'historico', label: 'Histórico', icon: 'M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' },
  { id: 'configuracoes', label: 'Configurações', icon: 'M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.58-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41H9.72a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.58.22l-1.92 3.32a.49.49 0 0 0 .12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.33.58.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.34.36.6.68.6h3.84c.32 0 .63-.26.68-.6l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47-.02.58-.22l1.92-3.32a.49.49 0 0 0-.12-.61l-2.01-1.58zM12 15.6a3.6 3.6 0 1 1 0-7.2 3.6 3.6 0 0 1 0 7.2z' },
  { id: 'ajuda', label: 'Ajuda', icon: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1.18 15.03L9.5 17V9.83l.03-.58.18-.45.9-.88c.6-.6 1-1 1-1.47a1 1 0 0 0-1-1 .94.94 0 0 0-.7.29l-.28.33L7.1 9.17l.02-.02a2.77 2.77 0 0 1 2.1-1.03c1.3 0 2.3.88 2.3 2.17 0 .66-.33 1.21-.88 1.7l-1 1v.7h3.03v1.68h-3.2zM12 18.88a1.2 1.2 0 1 1 0-2.4 1.2 1.2 0 0 1 0 2.4z' }
];

// Garantir que a sidebar comece aberta em telas maiores
// e fechada em telas menores ao carregar
import { onMounted } from 'vue';
onMounted(() => {
  if (window.innerWidth < 768) {
    sidebarOpen.value = false;
  } else {
    sidebarOpen.value = true;
  }
});

</script>

<template>
<div class="admin-layout">
  <header class="admin-header">
    <button class="sidebar-toggle" @click="toggleSidebar" aria-label="Toggle Sidebar">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>
    <div class="app-logo-header">Leitor NF-e Admin</div>
    </header>

  <aside class="admin-sidebar" :class="{ 'open': sidebarOpen }">
    <div class="sidebar-header">
      <span class="app-logo-sidebar">Leitor NF-e</span>
    </div>
    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in menuItems" :key="item.id" :class="{ 'active': activeTab === item.id }">
          <a @click.prevent="navigateTo(item.id)">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="currentColor" stroke="none" width="20" height="20">
              <path :d="item.icon" />
            </svg>
            <span>{{ item.label }}</span>
          </a>
        </li>
      </ul>
    </nav>
  </aside>

  <main class="admin-content" :class="{ 'sidebar-pushed': sidebarOpen }">
    <div v-if="activeTab === 'processar_nf'">
      <header class="page-header">
        <h1>Leitor de Notas Fiscais</h1>
        <p>Faça o upload de notas fiscais em PDF ou imagem para extração automática dos dados.</p>
      </header>

      <div class="content-area">
        <div class="upload-area-wrapper">
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
              <p class="upload-hint">Formatos suportados: PDF, PNG, JPG ou JPEG</p>
            </div>

            <div v-if="isProcessing" class="processing-indicator">
              <div class="spinner"></div>
              <p>Processando nota fiscal, por favor aguarde...</p>
            </div>
          </div>
        </div>


        <div v-if="error" class="error-message">
            <strong>Erro:</strong> {{ error }}
        </div>

        <div v-if="result && !result.erro" class="results-section"> <h2 class="results-title">Dados Extraídos da Nota Fiscal</h2>

          <div class="card results-card">
            <div class="results-grid">
              <div class="result-item">
                <p class="result-label">Número da NF</p>
                <p class="result-value">{{ result.numero_nota_fiscal || 'N/A' }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">Data de Emissão</p>
                <p class="result-value">{{ formatDate(result.data_emissao) }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">Valor Total</p>
                <p class="result-value primary-value">{{ formatCurrency(result.valor_total) }}</p>
              </div>
              <div class="result-item">
                <p class="result-label">CNPJ Emitente</p>
                <p class="result-value">{{ formatCNPJ(result.cnpj_emitente) }}</p>
              </div>
            </div>

            <div class="result-group-flex">
              <div class="flex-item-emitente-nome">
                <p class="result-label">Nome / Razão Social do Emitente</p>
                <p class="result-value">
                  {{ result.nome_razao_social_emitente || 'N/A' }}
                </p>
              </div>
              <div class="flex-item-emitente-endereco">
                <p class="result-label">Endereço do Emitente</p>
                <p class="result-value">{{ result.endereco_emitente || 'N/A' }}</p>
              </div>
            </div>

            <div class="result-group" v-if="result.chave_acesso">
              <p class="result-label">Chave de Acesso</p>
              <p class="result-value break-all code-like">{{ formatChaveAcesso(result.chave_acesso) }}</p>
            </div>
             <div class="result-group" v-else>
              <p class="result-label">Chave de Acesso</p>
              <p class="result-value">N/A</p>
            </div>


            <div v-if="result.itens && result.itens.length > 0" class="result-group">
              <h3 class="items-title">Itens da Nota</h3>
              <div class="items-list">
                <div v-for="(item, index) in result.itens" :key="index" class="item-entry card-inset">
                  <p class="item-description">{{ index + 1 }}. {{ item.descricao || 'Descrição não informada' }}</p>
                  <div class="item-details-grid">
                    <div>
                      <span class="item-detail-label">Qtd: </span>
                      <span class="item-detail-value">{{ typeof item.quantidade === 'number' ? item.quantidade.toFixed(2) : 'N/A' }}</span>
                    </div>
                    <div>
                      <span class="item-detail-label">Vl. Unit.: </span>
                      <span class="item-detail-value">{{ formatCurrency(item.valor_unitario) }}</span>
                    </div>
                    <div>
                      <span class="item-detail-label">Vl. Total Item: </span>
                      <span class="item-detail-value">{{ formatCurrency(item.valor_total_item) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
             <div v-else class="result-group">
                <h3 class="items-title">Itens da Nota</h3>
                <p class="result-value">Nenhum item encontrado.</p>
            </div>
          </div>

          <div class="new-invoice-action">
            <button @click="resetForm" class="btn btn-primary btn-gradient-hover">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
              Processar Nova Nota
            </button>,
          </div>
        </div>
        <div v-if="result && result.erro" class="error-message"> <strong>Erro da API:</strong> {{ result.erro }}
        </div>

      </div>
    </div>

    <div v-if="activeTab === 'historico'" class="placeholder-content card">
      <h2>Histórico de Notas</h2>
      <p>Esta seção exibirá o histórico de notas fiscais processadas. (Funcionalidade futura)</p>
    </div>
    <div v-if="activeTab === 'configuracoes'" class="placeholder-content card">
      <h2>Configurações</h2>
      <p>Esta seção permitirá configurar a aplicação. (Funcionalidade futura)</p>
    </div>
    <div v-if="activeTab === 'ajuda'" class="placeholder-content card">
      <h2>Ajuda & Suporte</h2>
      <p>Informações de ajuda e contato para suporte. (Funcionalidade futura)</p>
    </div>
  </main>
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

:root {
  --cor-principal: #00a9b3; /* Azul esverdeado moderno */
  --cor-secundaria: #007E8A; /* Tom mais escuro da principal */
  --cor-destaque: #FF8A3D; /* Laranja para destaque/gradientes */
  --cor-gradiente-inicio: #00a9b3;
  --cor-gradiente-fim: #007E8A; /* Gradiente sutil */

  --cor-sidebar-bg: #2c3e50; /* Azul escuro acinzentado */
  --cor-sidebar-texto: #ecf0f1; /* Cinza claro */
  --cor-sidebar-texto-hover: #ffffff;
  --cor-sidebar-item-ativo-bg: var(--cor-principal);
  --cor-sidebar-item-ativo-texto: #ffffff;

  --cor-conteudo-bg: #f4f6f9; /* Cinza muito claro, padrão AdminLTE */
  --cor-texto-padrao: #34495e; /* Azul acinzentado escuro */
  --cor-header-texto: #ffffff;

  --cor-sucesso: #2ecc71;
  --cor-erro: #e74c3c;
  --cor-aviso: #f39c12;

  --card-bg: #ffffff;
  --card-border-radius: 0.5rem; /* 8px */
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);

  --sidebar-width: 260px;
  --header-height: 60px;

  --font-principal: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

body {
  font-family: var(--font-principal);
  background-color: var(--cor-conteudo-bg);
  color: var(--cor-texto-padrao);
  line-height: 1.6;
  font-size: 16px; /* Base font size */
}

.admin-layout {
  display: flex;
  flex-direction: column; /* Para o header ficar acima de tudo */
  min-height: 100vh;
}

.admin-header {
  height: var(--header-height);
  background: var(--cor-principal); /* Usando gradiente */
  color: var(--cor-header-texto);
  display: flex;
  align-items: center;
  padding: 0 25px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1030; /* Alto z-index, comum em admin */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.sidebar-toggle {
  background: none;
  border: none;
  color: var(--cor-header-texto);
  cursor: pointer;
  font-size: 1.6rem; /* Aumentado um pouco */
  margin-right: 20px;
  padding: 5px;
  display: none; /* Escondido por padrão, aparece em mobile */
}
.sidebar-toggle:hover {
  opacity: 0.8;
}

.app-logo-header {
  font-size: 1.6rem; /* Aumentado */
  font-weight: 600;
  letter-spacing: -0.5px; /* Pequeno ajuste */
}

.admin-sidebar {
  width: var(--sidebar-width);
  background-color: var(--cor-sidebar-bg);
  color: var(--cor-sidebar-texto);
  position: fixed;
  top: 0; /* Começa do topo */
  left: 0;
  bottom: 0;
  padding-top: var(--header-height); /* Espaço para o header fixo */
  transition: transform 0.3s ease-in-out;
  z-index: 1020; /* Abaixo do header */
  overflow-y: auto;
  box-shadow: 3px 0 10px rgba(0,0,0,0.1); /* Sombra sutil na lateral */
}

.admin-sidebar .sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 15px;
}

.app-logo-sidebar {
  font-size: 1.4rem; /* Ajustado */
  font-weight: 500;
  color: var(--cor-header-texto); /* Branco para contraste */
}

.sidebar-nav ul {
  list-style: none;
}

.sidebar-nav li a {
  display: flex;
  align-items: center;
  padding: 14px 25px; /* Ajustado padding */
  color: var(--cor-sidebar-texto);
  text-decoration: none;
  transition: background-color 0.2s ease, color 0.2s ease;
  gap: 12px; /* Espaçamento entre ícone e texto */
  font-size: 0.95rem; /* Levemente menor para mais itens */
}

.menu-icon {
  color: var(--cor-sidebar-texto); /* Cor do ícone inicial */
  opacity: 0.8;
  min-width: 20px;
  transition: color 0.2s ease, opacity 0.2s ease;
}

.sidebar-nav li a:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: var(--cor-sidebar-texto-hover);
}
.sidebar-nav li a:hover .menu-icon {
  color: var(--cor-principal); /* Ícone muda para a cor principal no hover */
  opacity: 1;
}

.sidebar-nav li.active a {
  background-color: var(--cor-sidebar-item-ativo-bg);
  color: var(--cor-sidebar-item-ativo-texto);
  font-weight: 600; /* Mais destaque */
}
.sidebar-nav li.active a .menu-icon {
  color: var(--cor-sidebar-item-ativo-texto); /* Mantém cor do texto ativo */
  opacity: 1;
}

.admin-content {
  margin-top: var(--header-height);
  margin-left: var(--sidebar-width); /* Padrão para quando a sidebar está aberta */
  padding: 25px 30px; /* Padding ajustado */
  flex-grow: 1;
  transition: margin-left 0.3s ease-in-out;
  background-color: var(--cor-conteudo-bg);
}
/* Classe para empurrar o conteúdo quando a sidebar estiver aberta em mobile */
.page-header {
  text-align: left; /* Alinhado à esquerda */
  margin-bottom: 2rem; /* Reduzido um pouco */
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.page-header h1 {
  font-size: 1.8rem; /* Reduzido */
  font-weight: 600; /* Ajustado */
  color: var(--cor-texto-padrao);
  margin-bottom: 0.25rem;
}

.page-header p {
  font-size: 0.95rem;
  color: #6c757d; /* Cinza mais suave */
}

.content-area {
  max-width: 900px; /* Aumentado para acomodar melhor os dados */
  margin: 0 auto;
}

.upload-area-wrapper {
  margin-bottom: 2rem; /* Espaçamento após a área de upload */
}

.upload-area {
  border: 2px dashed #d1d8e0; /* Cinza mais suave */
  border-radius: var(--card-border-radius);
  padding: 2.5rem;
  text-align: center;
  background-color: var(--card-bg);
  transition: border-color 0.2s ease, background-color 0.2s ease;
  box-shadow: var(--card-shadow);
}
.upload-area.is-dragging {
  border-color: var(--cor-principal);
  background-color: #f0f9fa; /* Fundo muito claro ao arrastar */
}

.file-input-hidden { display: none; }

.upload-icon {
  margin: 0 auto 1rem auto;
  height: 3.5rem; /* Aumentado */
  width: 3.5rem;
  color: var(--cor-principal); /* Cor do ícone */
  opacity: 0.7;
}

.upload-text {
  margin-top: 0.5rem; /* Reduzido */
  font-size: 1.05rem; /* Aumentado */
  color: var(--cor-texto-padrao);
}

.upload-browse-button {
  color: var(--cor-principal);
  font-weight: 600;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}
.upload-browse-button:hover {
  color: var(--cor-secundaria); /* Tom mais escuro no hover */
  text-decoration: underline;
}

.upload-hint {
  margin-top: 0.75rem;
  font-size: 0.85rem; /* Reduzido */
  color: #6c757d;
}

.processing-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0; /* Adiciona padding vertical */
  color: var(--cor-texto-padrao);
}
.spinner {
  animation: spin 1s linear infinite;
  border-radius: 50%;
  height: 3rem; /* Aumentado */
  width: 3rem;
  border: 4px solid #e0e7ff; /* Borda mais grossa */
  border-top-color: var(--cor-principal);
  margin-bottom: 1.25rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-message {
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
  background-color: #ffebee; /* Vermelho claro */
  color: var(--cor-erro);
  border-radius: var(--card-border-radius);
  border: 1px solid #f44336; /* Vermelho */
  font-size: 0.9rem;
  box-shadow: 0 2px 4px rgba(231, 76, 60, 0.2);
}
.error-message strong {
  font-weight: 600;
}

.results-section {
  margin-top: 2.5rem;
}

.results-title {
  font-size: 1.6rem; /* Ajustado */
  font-weight: 600;
  color: var(--cor-texto-padrao);
  margin-bottom: 1.5rem;
  text-align: left;
}

.card { /* Estilo base para todos os cards, incluindo results e placeholders */
  background-color: var(--card-bg);
  border-radius: var(--card-border-radius);
  box-shadow: var(--card-shadow);
  padding: 2rem; /* Padding padrão */
}


.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); /* Ajustado minmax */
  gap: 1.75rem 2rem; /* Ajustado gap */
  margin-bottom: 2rem;
}

.result-group-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 1.75rem 2rem;
  margin-bottom: 2rem;
}
.flex-item-emitente-nome {
  flex: 1 1 280px; /* Ajustado base */
}
.flex-item-emitente-endereco {
  flex: 2 1 380px; /* Ajustado base */
}

.result-group { margin-bottom: 2rem; }
.result-group:last-child { margin-bottom: 0; }


.result-label {
  font-size: 0.8rem; /* Menor para dar mais espaço ao valor */
  color: #6c757d; /* Cinza */
  margin-bottom: 0.3rem; /* Espaçamento ajustado */
  font-weight: 500; /* Mais leve */
  text-transform: uppercase; /* Para um look mais "label" */
  letter-spacing: 0.5px;
}

.result-value {
  font-size: 1rem; /* Tamanho padrão para valores */
  color: var(--cor-texto-padrao);
  font-weight: 500; /* Peso normal */
  line-height: 1.4; /* Melhor legibilidade para textos longos */
}
.result-value.primary-value { /* Para o Valor Total da NF */
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--cor-principal);
}
.result-value.break-all { word-break: break-all; }
.result-value.code-like { /* Para Chave de Acesso */
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    background-color: #f8f9fa;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    display: inline-block;
    border: 1px solid #e9ecef;
}

.items-title {
  font-size: 1.3rem; /* Ajustado */
  font-weight: 600;
  color: var(--cor-texto-padrao);
  margin-top: 2rem; /* Separar mais dos dados principais */
  margin-bottom: 1.25rem;
  border-top: 1px solid #e9ecef;
  padding-top: 1.5rem;
}

.items-list > .item-entry:not(:last-child) {
  margin-bottom: 1.25rem; /* Aumentado espaçamento entre itens */
}
.item-entry {
  padding: 1rem; /* Adiciona padding interno ao item */
  border-bottom: none; /* Removida borda, .card-inset cuida disso */
}
.item-entry.card-inset { /* Novo estilo para cada item parecer um pequeno card */
    background-color: #f8f9fa; /* Fundo levemente diferente */
    border-radius: 6px;
    border: 1px solid #e9ecef;
}

.item-description {
  font-weight: 600;
  color: var(--cor-texto-padrao);
  margin-bottom: 0.75rem; /* Ajustado */
  font-size: 0.95rem;
}

.item-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); /* Ajustado minmax */
  gap: 0.5rem 1rem; /* Ajustado gap */
  font-size: 0.9rem; /* Ajustado */
}
.item-detail-label { color: #6c757d; }
.item-detail-value { color: var(--cor-texto-padrao); font-weight: 500; }

.btn {
  display: inline-flex; /* Para alinhar ícone e texto */
  align-items: center; /* Alinha ícone e texto verticalmente */
  justify-content: center;
  padding: 0.8rem 1.8rem; /* Padding ajustado */
  font-size: 0.95rem; /* Ajustado */
  font-weight: 500;
  text-align: center;
  border-radius: var(--card-border-radius);
  cursor: pointer;
  transition: all 0.25s ease-in-out;
  border: 1px solid transparent;
  text-transform: uppercase; /* Botões com texto maiúsculo */
  letter-spacing: 0.5px;
}

.btn-primary {
  background-color: var(--cor-principal);
  color: #ffffff;
  border-color: var(--cor-principal);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.btn-primary:hover {
  background-color: var(--cor-secundaria);
  border-color: var(--cor-secundaria);
  transform: translateY(-2px); /* Pequeno efeito de elevação */
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn-gradient-hover { /* Mantido se você gostar do efeito, mas simplificado acima */
  position: relative;
  z-index: 1;
  overflow: hidden;
}
.btn-gradient-hover::before {
  content: "";
  position: absolute; top: 0; right: 0; bottom: 0; left: 0;
  background-image: linear-gradient(92.99deg, var(--cor-destaque) 6.23%, var(--cor-gradiente-fim) 99.16%); /* Usando novas cores */
  z-index: -1;
  transition: opacity 0.3s ease-in-out;
  opacity: 0;
  border-radius: inherit;
}
.btn-gradient-hover:hover::before { opacity: 1; }
.btn-gradient-hover:hover {
  background-color: var(--cor-principal); /* Fallback caso o gradiente não seja o desejado */
  color: #ffffff;
  border-color: transparent;
}

.new-invoice-action {
  margin-top: 2.5rem; /* Aumentado */
  text-align: center;
}

.placeholder-content { /* Herda de .card agora */
  margin-top: 1rem; /* Espaçamento se houver múltiplos placeholders */
}
.placeholder-content h2 {
  color: var(--cor-texto-padrao); /* Consistência */
  margin-bottom: 10px;
  font-weight: 600;
}

/* Media Queries */
@media (max-width: 992px) { /* Ponto de quebra para tablets */
    .results-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }
    .flex-item-emitente-nome,
    .flex-item-emitente-endereco {
        flex-basis: calc(50% - 1rem); /* Tenta manter 2 colunas se possível */
    }
}

@media (max-width: 768px) {
  .sidebar-toggle { display: flex; align-items: center; }
  .admin-sidebar {
    transform: translateX(calc(-1 * var(--sidebar-width))); /* Esconde a sidebar */
    box-shadow: 3px 0 15px rgba(0, 0, 0, 0.2); /* Sombra mais pronunciada quando aberta */
    padding-top: 0; /* Header cobre o topo */
    top:0;
  }
  .admin-sidebar.open { transform: translateX(0); }
  .admin-content { margin-left: 0; } /* Conteúdo ocupa toda a largura */

  .app-logo-header {
    flex-grow: 1; /* Permite que o logo centralize se não houver outros itens */
    text-align: center;
    margin-right: -40px; /* Ajuste para compensar o botão da sidebar */
  }

  .results-grid {
    grid-template-columns: 1fr; /* Uma coluna em telas pequenas */
    gap: 1.5rem 0;
  }
  .result-group-flex {
    flex-direction: column; /* Empilha os itens do emitente */
    gap: 1.5rem 0;
  }
  .flex-item-emitente-nome,
  .flex-item-emitente-endereco {
    flex-basis: 100%;
    min-width: unset;
  }
  .item-details-grid {
    grid-template-columns: 1fr; /* Uma coluna para detalhes do item */
  }
  .page-header { text-align: center; }
  .results-title { text-align: center; }
}
</style>
