// Configuration
        const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
    health: '/health',
    predict: '/predict',
    modelInfo: '/model/info',
    importance: '/model/importance'
};

// État de l'application
let appState = {
    apiConnected: false,
    modelInfo: null,
    lastPrediction: null
};

// Presets de maisons
const HOUSE_PRESETS = {
    standard: {
        area: 7420,
        bedrooms: 4,
        bathrooms: 1,
        stories: 3,
        mainroad: 1,
        guestroom: 0,
        basement: 0,
        hotwaterheating: 0,
        airconditioning: 1,
        parking: 2,
        prefarea: 1,
        furnishingstatus: 1
    },
    luxury: {
        area: 12000,
        bedrooms: 5,
        bathrooms: 3,
        stories: 2,
        mainroad: 1,
        guestroom: 1,
        basement: 1,
        hotwaterheating: 1,
        airconditioning: 1,
        parking: 4,
        prefarea: 1,
        furnishingstatus: 2
    },
    budget: {
        area: 3500,
        bedrooms: 2,
        bathrooms: 1,
        stories: 1,
        mainroad: 1,
        guestroom: 0,
        basement: 0,
        hotwaterheating: 0,
        airconditioning: 0,
        parking: 1,
        prefarea: 0,
        furnishingstatus: 0
    }
};

// Utilitaires
const utils = {
    // Format des nombres
    formatNumber: (num, decimals = 0) => {
        return new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },

    // Format des prix
    formatPrice: (price) => {
        if (price >= 1000000) {
            return `${utils.formatNumber(price / 1000000, 2)}M`;
        } else if (price >= 1000) {
            return `${utils.formatNumber(price / 1000, 0)}K`;
        }
        return utils.formatNumber(price);
    },

    // Génération de valeurs aléatoires
    getRandomInt: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Animation des éléments
    animateElement: (element, animationClass) => {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, 600);
    }
};

// Gestion de l'API
const apiManager = {
    // Requête générique
    async makeRequest(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Request failed for ${endpoint}:`, error);
            throw error;
        }
    },

    // Vérifier l'état de l'API
    async checkHealth() {
        try {
            const data = await this.makeRequest(API_ENDPOINTS.health);
            return data.status === 'healthy' && data.model_loaded;
        } catch (error) {
            return false;
        }
    },

    // Obtenir les informations du modèle
    async getModelInfo() {
        try {
            return await this.makeRequest(API_ENDPOINTS.modelInfo);
        } catch (error) {
            console.error('Failed to get model info:', error);
            return null;
        }
    },

    // Faire une prédiction
    async predict(houseData) {
        return await this.makeRequest(API_ENDPOINTS.predict, {
            method: 'POST',
            body: JSON.stringify(houseData)
        });
    }
};

// Gestion de l'interface utilisateur
const uiManager = {
    // Éléments DOM
    elements: {
        statusBar: document.getElementById('statusBar'),
        statusIndicator: document.getElementById('statusIndicator'),
        statusText: document.getElementById('statusText'),
        form: document.getElementById('houseForm'),
        predictBtn: document.getElementById('predictBtn'),
        btnText: document.getElementById('btnText'),
        btnSpinner: document.getElementById('btnSpinner'),
        resetBtn: document.getElementById('resetBtn'),
        randomBtn: document.getElementById('randomBtn'),
        resultsContainer: document.getElementById('resultsContainer'),
        errorModal: document.getElementById('errorModal'),
        errorMessage: document.getElementById('errorMessage'),
        presetCards: document.querySelectorAll('.preset-card')
    },

    // Initialiser l'interface
    init() {
        this.bindEvents();
        this.updateConnectionStatus(false);
    },

    // Lier les événements
    bindEvents() {
        // Formulaire
        this.elements.form.addEventListener('submit', this.handleFormSubmit.bind(this));
        this.elements.resetBtn.addEventListener('click', this.resetForm.bind(this));
        this.elements.randomBtn.addEventListener('click', this.fillRandomValues.bind(this));

        // Presets
        this.elements.presetCards.forEach(card => {
            card.addEventListener('click', this.handlePresetClick.bind(this));
        });

        // Modal
        const closeModal = document.querySelector('.close');
        closeModal.addEventListener('click', this.hideError.bind(this));
        window.addEventListener('click', (e) => {
            if (e.target === this.elements.errorModal) {
                this.hideError();
            }
        });

        // Auto-update des valeurs
        const inputs = this.elements.form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', utils.debounce(() => {
                this.updateFormPreview();
            }, 300));
        });
    },

    // Mettre à jour l'état de connexion
    updateConnectionStatus(connected) {
        appState.apiConnected = connected;
        const { statusBar, statusIndicator, statusText, predictBtn } = this.elements;

        if (connected) {
            statusIndicator.textContent = '🟢';
            statusText.textContent = 'Connecté à l\'API - Modèle chargé';
            statusBar.classList.add('connected');
            predictBtn.disabled = false;
        } else {
            statusIndicator.textContent = '🔴';
            statusText.textContent = 'Connexion à l\'API échouée';
            statusBar.classList.remove('connected');
            predictBtn.disabled = true;
        }
    },

    // Gérer la soumission du formulaire
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!appState.apiConnected) {
            this.showError('API non connectée', 'Veuillez vérifier la connexion à l\'API');
            return;
        }

        const formData = this.getFormData();
        await this.makePrediction(formData);
    },

    // Extraire les données du formulaire
    getFormData() {
        const formData = new FormData(this.elements.form);
        const data = {};

        // Convertir les données du formulaire
        for (const [key, value] of formData.entries()) {
            if (key === 'area') {
                data[key] = parseFloat(value);
            } else {
                data[key] = parseInt(value);
            }
        }

        // Gérer les checkboxes non cochées
        const checkboxes = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea'];
        checkboxes.forEach(checkbox => {
            if (!data.hasOwnProperty(checkbox)) {
                data[checkbox] = 0;
            }
        });

        return data;
    },

    // Faire une prédiction
    async makePrediction(houseData) {
        const { predictBtn, btnText, btnSpinner } = this.elements;

        // État de chargement
        predictBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline-block';
        
        try {
            const result = await apiManager.predict(houseData);
            appState.lastPrediction = result;
            this.displayResults(result, houseData);
            utils.animateElement(this.elements.resultsContainer.parentElement, 'success-flash');
            
        } catch (error) {
            this.showError('Erreur de prédiction', error.message);
            utils.animateElement(this.elements.resultsContainer.parentElement, 'error-flash');
        } finally {
            // Restaurer le bouton
            predictBtn.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
        }
    },

    // Afficher les résultats
    displayResults(result, inputData) {
        const { resultsContainer } = this.elements;
        
        resultsContainer.innerHTML = `
            <div class="results-content">
                <div class="result-item">
                    <span class="result-label">💰 Prix estimé</span>
                    <span class="result-value price-highlight">${result.formatted_price}</span>
                </div>
                
                <div class="result-item">
                    <span class="result-label">📊 Prix par pied carré</span>
                    <span class="result-value">${utils.formatNumber(result.price_per_sqft, 2)}</span>
                </div>
                
                <div class="result-item">
                    <span class="result-label">🤖 Modèle utilisé</span>
                    <span class="result-value">${result.model_type}</span>
                </div>
                
                <div class="result-item">
                    <span class="result-label">✅ Niveau de confiance</span>
                    <span class="result-value">${this.getConfidenceEmoji(result.confidence)} ${result.confidence}</span>
                </div>
                
                <div class="result-item">
                    <span class="result-label">📏 Surface totale</span>
                    <span class="result-value">${utils.formatNumber(inputData.area)} sq ft</span>
                </div>
                
                <div class="result-item">
                    <span class="result-label">🏠 Caractéristiques</span>
                    <span class="result-value">${inputData.bedrooms} ch. / ${inputData.bathrooms} sdb / ${inputData.stories} ét.</span>
                </div>
            </div>
        `;
    },

    // Obtenir l'emoji de confiance
    getConfidenceEmoji(confidence) {
        const emojiMap = {
            'high': '🟢',
            'medium': '🟡',
            'low': '🔴'
        };
        return emojiMap[confidence] || '⚪';
    },

    // Réinitialiser le formulaire
    resetForm() {
        this.elements.form.reset();
        this.applyPreset('standard');
        this.elements.resultsContainer.innerHTML = `
            <div class="results-placeholder">
                <p>👆 Remplissez le formulaire et cliquez sur "Prédire le Prix" pour voir les résultats</p>
            </div>
        `;
    },

    // Remplir avec des valeurs aléatoires
    fillRandomValues() {
        const randomData = {
            area: utils.getRandomInt(3000, 15000),
            bedrooms: utils.getRandomInt(2, 6),
            bathrooms: utils.getRandomInt(1, 4),
            stories: utils.getRandomInt(1, 3),
            mainroad: Math.random() > 0.2 ? 1 : 0,
            guestroom: Math.random() > 0.7 ? 1 : 0,
            basement: Math.random() > 0.6 ? 1 : 0,
            hotwaterheating: Math.random() > 0.5 ? 1 : 0,
            airconditioning: Math.random() > 0.4 ? 1 : 0,
            parking: utils.getRandomInt(0, 3),
            prefarea: Math.random() > 0.5 ? 1 : 0,
            furnishingstatus: utils.getRandomInt(0, 2)
        };

        this.applyPreset(null, randomData);
        utils.animateElement(this.elements.form, 'success-flash');
    },

    // Gérer le clic sur un preset
    handlePresetClick(e) {
        const presetType = e.currentTarget.dataset.preset;
        this.applyPreset(presetType);
        utils.animateElement(e.currentTarget, 'success-flash');
    },

    // Appliquer un preset
    applyPreset(presetType, customData = null) {
        const data = customData || HOUSE_PRESETS[presetType];
        if (!data) return;

        // Remplir les champs
        Object.entries(data).forEach(([key, value]) => {
            const element = this.elements.form.elements[key];
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value === 1;
                } else if (element.type === 'radio') {
                    const radioButton = this.elements.form.querySelector(`input[name="${key}"][value="${value}"]`);
                    if (radioButton) radioButton.checked = true;
                } else {
                    element.value = value;
                }
            }
        });
    },

    // Afficher une erreur
    showError(title, message) {
        this.elements.errorMessage.innerHTML = `
            <strong>${title}</strong><br>
            ${message}
        `;
        this.elements.errorModal.style.display = 'block';
    },

    // Masquer l'erreur
    hideError() {
        this.elements.errorModal.style.display = 'none';
    },

    // Mettre à jour l'aperçu du formulaire (placeholder pour futures fonctionnalités)
    updateFormPreview() {
        // Cette fonction pourrait être utilisée pour afficher un aperçu en temps réel
        // des caractéristiques de la maison pendant que l'utilisateur remplit le formulaire
    }
};

// Application principale
const app = {
    // Initialiser l'application
    async init() {
        console.log('🏠 House Price Predictor - Initializing...');
        
        // Initialiser l'interface
        uiManager.init();
        
        // Vérifier la connexion à l'API
        await this.checkApiConnection();
        
        // Charger les informations du modèle
        await this.loadModelInfo();
        
        // Appliquer le preset standard par défaut
        uiManager.applyPreset('standard');
        
        console.log('✅ Application initialized successfully');
    },

    // Vérifier la connexion API
    async checkApiConnection() {
        console.log('🔍 Checking API connection...');
        
        try {
            const isConnected = await apiManager.checkHealth();
            uiManager.updateConnectionStatus(isConnected);
            
            if (isConnected) {
                console.log('✅ API connection successful');
            } else {
                console.warn('⚠️ API connection failed');
            }
        } catch (error) {
            console.error('❌ Error checking API connection:', error);
            uiManager.updateConnectionStatus(false);
        }
    },

    // Charger les informations du modèle
    async loadModelInfo() {
        if (!appState.apiConnected) return;
        
        try {
            const modelInfo = await apiManager.getModelInfo();
            appState.modelInfo = modelInfo;
            console.log('📊 Model info loaded:', modelInfo);
        } catch (error) {
            console.warn('⚠️ Could not load model info:', error);
        }
    }
};

// Event Listeners pour le chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Gestion de la reconnexion automatique
window.addEventListener('online', () => {
    console.log('🌐 Connection restored, checking API...');
    app.checkApiConnection();
});

window.addEventListener('offline', () => {
    console.log('📱 Connection lost');
    uiManager.updateConnectionStatus(false);
});

// Export pour utilisation externe (si nécessaire)
window.HousePricePredictor = {
    app,
    uiManager,
    apiManager,
    utils,
    appState
};
