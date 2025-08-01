// Configuración global
const API_BASE = '';
const POLL_INTERVAL = 1000; // 1 segundo

// Estado de la aplicación
let currentTaskId = null;
let pollInterval = null;

// Elementos del DOM
const elements = {
    tiktokUrl: document.getElementById('tiktok-url'),
    pasteBtn: document.getElementById('paste-btn'),
    urlValidation: document.getElementById('url-validation'),
    platformYoutube: document.getElementById('platform-youtube'),
    platformInstagram: document.getElementById('platform-instagram'),
    customTitle: document.getElementById('custom-title'),
    titleCharCount: document.getElementById('title-char-count'),
    customDescription: document.getElementById('custom-description'),
    charCount: document.getElementById('char-count'),
    processBtn: document.getElementById('process-btn'),
    downloadOnlyBtn: document.getElementById('download-only-btn'),
    progressSection: document.getElementById('progress-section'),
    progressTitle: document.getElementById('progress-title'),
    progressPercentage: document.getElementById('progress-percentage'),
    progressFill: document.getElementById('progress-fill'),
    progressMessage: document.getElementById('progress-message'),
    resultsSection: document.getElementById('results-section'),
    videoPreview: document.getElementById('video-preview'),
    uploadResults: document.getElementById('upload-results'),
    newProcessBtn: document.getElementById('new-process-btn'),
    loadingOverlay: document.getElementById('loading-overlay'),
    toastContainer: document.getElementById('toast-container')
};

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeValidation();
    checkBrowserFeatures();
});

// Event Listeners
function initializeEventListeners() {
    // URL input events
    elements.tiktokUrl.addEventListener('input', handleUrlInput);
    elements.tiktokUrl.addEventListener('paste', handleUrlPaste);
    elements.pasteBtn.addEventListener('click', handlePasteClick);

    // Platform selection
    elements.platformYoutube.addEventListener('change', updateProcessButton);
    elements.platformInstagram.addEventListener('change', updateProcessButton);

    // Title counter
    elements.customTitle.addEventListener('input', updateTitleCharCount);
    
    // Description counter
    elements.customDescription.addEventListener('input', updateCharCount);

    // Action buttons
    elements.processBtn.addEventListener('click', handleProcessClick);
    elements.downloadOnlyBtn.addEventListener('click', handleDownloadClick);
    elements.newProcessBtn.addEventListener('click', resetToInitialState);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Validación y UI updates
function initializeValidation() {
    updateProcessButton();
    updateCharCount();
}

function handleUrlInput(event) {
    const url = event.target.value.trim();
    validateTikTokUrl(url);
    updateProcessButton();
}

function handleUrlPaste(event) {
    setTimeout(() => {
        const url = event.target.value.trim();
        validateTikTokUrl(url);
        updateProcessButton();
    }, 100);
}

async function handlePasteClick() {
    try {
        if (navigator.clipboard && navigator.clipboard.readText) {
            const text = await navigator.clipboard.readText();
            elements.tiktokUrl.value = text.trim();
            validateTikTokUrl(text.trim());
            updateProcessButton();
            showToast('URL pegada desde el portapapeles', 'success');
        } else {
            showToast('Tu navegador no soporta esta función. Pega la URL manualmente.', 'warning');
        }
    } catch (error) {
        showToast('No se pudo acceder al portapapeles', 'error');
    }
}

function validateTikTokUrl(url) {
    const tiktokPatterns = [
        /^https?:\/\/(www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+/,
        /^https?:\/\/(www\.)?tiktok\.com\/t\/[\w]+/,
        /^https?:\/\/vm\.tiktok\.com\/[\w]+/,
        /^https?:\/\/(www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+/
    ];

    const isValid = url && tiktokPatterns.some(pattern => pattern.test(url));
    
    if (url === '') {
        elements.urlValidation.textContent = '';
        elements.urlValidation.className = 'url-validation';
    } else if (isValid) {
        elements.urlValidation.textContent = '✓ URL válida de TikTok';
        elements.urlValidation.className = 'url-validation valid';
    } else {
        elements.urlValidation.textContent = '✗ URL no válida. Debe ser una URL de TikTok';
        elements.urlValidation.className = 'url-validation invalid';
    }

    return isValid;
}

function updateProcessButton() {
    const url = elements.tiktokUrl.value.trim();
    const isValidUrl = validateTikTokUrl(url);
    const hasSelectedPlatform = elements.platformYoutube.checked || elements.platformInstagram.checked;
    
    elements.processBtn.disabled = !isValidUrl || !hasSelectedPlatform;
}

function updateTitleCharCount() {
    const count = elements.customTitle.value.length;
    elements.titleCharCount.textContent = count;
    
    if (count > 90) {
        elements.titleCharCount.style.color = 'var(--error-color)';
    } else if (count > 75) {
        elements.titleCharCount.style.color = 'var(--warning-color)';
    } else {
        elements.titleCharCount.style.color = 'var(--text-secondary)';
    }
}

function updateCharCount() {
    const count = elements.customDescription.value.length;
    elements.charCount.textContent = count;
    
    if (count > 1800) {
        elements.charCount.style.color = 'var(--warning-color)';
    } else if (count > 1950) {
        elements.charCount.style.color = 'var(--error-color)';
    } else {
        elements.charCount.style.color = 'var(--text-secondary)';
    }
}

// Funciones principales
async function handleProcessClick() {
    const url = elements.tiktokUrl.value.trim();
    const platforms = getSelectedPlatforms();
    const title = elements.customTitle.value.trim();
    const description = elements.customDescription.value.trim();

    if (!validateTikTokUrl(url)) {
        showToast('Por favor, ingresa una URL válida de TikTok', 'error');
        return;
    }

    if (platforms.length === 0) {
        showToast('Selecciona al menos una plataforma', 'error');
        return;
    }

    try {
        showLoadingOverlay(true);
        
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                platforms: platforms,
                title: title,
                description: description
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.task_id) {
            currentTaskId = data.task_id;
            showProgressSection();
            startPolling();
            showToast('Procesamiento iniciado', 'success');
        } else {
            throw new Error(data.error || 'Error desconocido');
        }

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingOverlay(false);
    }
}

async function handleDownloadClick() {
    const url = elements.tiktokUrl.value.trim();

    if (!validateTikTokUrl(url)) {
        showToast('Por favor, ingresa una URL válida de TikTok', 'error');
        return;
    }

    try {
        showLoadingOverlay(true);
        
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.task_id) {
            currentTaskId = data.task_id;
            showProgressSection();
            startPolling();
            showToast('Descarga iniciada', 'success');
        } else {
            throw new Error(data.error || 'Error desconocido');
        }

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingOverlay(false);
    }
}

function getSelectedPlatforms() {
    const platforms = [];
    if (elements.platformYoutube.checked) platforms.push('youtube');
    if (elements.platformInstagram.checked) platforms.push('instagram');
    return platforms;
}

// Polling para el estado de las tareas
function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }

    pollInterval = setInterval(async () => {
        if (!currentTaskId) {
            clearInterval(pollInterval);
            return;
        }

        try {
            const response = await fetch(`/api/task/${currentTaskId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            updateProgress(data);

            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(pollInterval);
                pollInterval = null;
                
                if (data.status === 'completed') {
                    showResults(data);
                } else {
                    showToast(`Error: ${data.message}`, 'error');
                    hideProgressSection();
                }
            }

        } catch (error) {
            console.error('Error polling task status:', error);
            clearInterval(pollInterval);
            pollInterval = null;
            showToast('Error obteniendo estado de la tarea', 'error');
            hideProgressSection();
        }
    }, POLL_INTERVAL);
}

function updateProgress(data) {
    const progress = Math.max(0, Math.min(100, data.progress || 0));
    
    elements.progressPercentage.textContent = `${Math.round(progress)}%`;
    elements.progressFill.style.width = `${progress}%`;
    elements.progressMessage.textContent = data.message || 'Procesando...';

    // Actualizar título basado en el estado
    if (data.status === 'downloading') {
        elements.progressTitle.textContent = 'Descargando video...';
    } else if (data.status === 'processing') {
        elements.progressTitle.textContent = 'Procesando video...';
    } else if (data.status === 'uploading') {
        elements.progressTitle.textContent = 'Subiendo a plataformas...';
    }
}

function showResults(data) {
    hideProgressSection();
    
    // Mostrar información del video
    if (data.video_info) {
        displayVideoInfo(data.video_info);
    }

    // Mostrar resultados de subida
    if (data.uploads) {
        displayUploadResults(data.uploads);
    }

    elements.resultsSection.style.display = 'block';
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    showToast('¡Procesamiento completado!', 'success');
}

function displayVideoInfo(videoInfo) {
    const metadata = videoInfo.metadata || {};
    
    const videoInfoHtml = `
        <div class="video-info">
            <h4><i class="fas fa-video"></i> Información del video</h4>
            <div class="video-details">
                <p><strong>Título:</strong> ${metadata.title || 'Sin título'}</p>
                <p><strong>Creador:</strong> ${metadata.creator || 'Desconocido'}</p>
                <p><strong>Duración:</strong> ${formatDuration(metadata.duration || 0)}</p>
                <p><strong>Resolución:</strong> ${metadata.width || 0}x${metadata.height || 0}</p>
                ${metadata.description ? `<p><strong>Descripción:</strong> ${metadata.description}</p>` : ''}
            </div>
        </div>
    `;
    
    elements.videoPreview.innerHTML = videoInfoHtml;
}

function displayUploadResults(uploads) {
    let resultsHtml = '<h4><i class="fas fa-upload"></i> Resultados de subida</h4>';
    
    for (const [platform, result] of Object.entries(uploads)) {
        const platformName = platform === 'youtube' ? 'YouTube Shorts' : 'Instagram Reels';
        const iconClass = platform === 'youtube' ? 'fab fa-youtube' : 'fab fa-instagram';
        const isSuccess = result.success;
        
        resultsHtml += `
            <div class="upload-result ${isSuccess ? 'success' : 'error'}">
                <div class="upload-header">
                    <h5><i class="${iconClass}"></i> ${platformName}</h5>
                    <span class="upload-status ${isSuccess ? 'success' : 'error'}">
                        <i class="fas fa-${isSuccess ? 'check-circle' : 'times-circle'}"></i>
                        ${isSuccess ? 'Exitoso' : 'Error'}
                    </span>
                </div>
                ${isSuccess ? `
                    <div class="upload-details">
                        <p><strong>URL:</strong> <a href="${result.video_url || result.reel_url}" target="_blank" rel="noopener">${result.video_url || result.reel_url}</a></p>
                        <p><strong>Fecha:</strong> ${formatDate(result.upload_date)}</p>
                        ${result.title ? `<p><strong>Título:</strong> ${result.title}</p>` : ''}
                    </div>
                ` : `
                    <div class="error-details">
                        <p>Error: ${result.error || 'Error desconocido'}</p>
                    </div>
                `}
            </div>
        `;
    }
    
    elements.uploadResults.innerHTML = resultsHtml;
}

// Funciones de UI
function showProgressSection() {
    hideAllSections();
    elements.progressSection.style.display = 'block';
    elements.progressSection.scrollIntoView({ behavior: 'smooth' });
}

function hideProgressSection() {
    elements.progressSection.style.display = 'none';
}

function hideAllSections() {
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
}

function showLoadingOverlay(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function resetToInitialState() {
    // Limpiar formulario
    elements.tiktokUrl.value = '';
    elements.customDescription.value = '';
    elements.urlValidation.textContent = '';
    elements.urlValidation.className = 'url-validation';
    
    // Resetear plataformas
    elements.platformYoutube.checked = true;
    elements.platformInstagram.checked = true;
    
    // Limpiar estado
    currentTaskId = null;
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
    
    // Ocultar secciones
    hideAllSections();
    
    // Actualizar UI
    updateProcessButton();
    updateCharCount();
    
    // Scroll al inicio
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Toast notifications
function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, duration);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

function getToastIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Utilidades
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Atajos de teclado
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + Enter para procesar
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        if (!elements.processBtn.disabled) {
            handleProcessClick();
        }
    }
    
    // Escape para resetear
    if (event.key === 'Escape') {
        resetToInitialState();
    }
}

// Verificar características del navegador
function checkBrowserFeatures() {
    // Verificar soporte para clipboard API
    if (!navigator.clipboard) {
        console.warn('Clipboard API no soportada en este navegador');
    }
    
    // Verificar soporte para fetch
    if (!window.fetch) {
        showToast('Tu navegador no es compatible. Por favor actualiza tu navegador.', 'error', 10000);
    }
}

// Manejo de errores globales
window.addEventListener('error', function(event) {
    console.error('Error global:', event.error);
    showToast('Ha ocurrido un error inesperado', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Promise rechazada:', event.reason);
    showToast('Error de conexión o procesamiento', 'error');
});

// Cleanup al cerrar la página
window.addEventListener('beforeunload', function() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
}); 