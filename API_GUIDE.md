# 🚀 API de Prédiction des Prix Immobiliers

## 📋 Guide de Démarrage Rapide

### 1. 📦 Installation des Dépendances

```bash
# Installer FastAPI et ses dépendances
pip install fastapi uvicorn python-multipart

# Installer les autres dépendances nécessaires
pip install pydantic
```

### 2. 🏃‍♂️ Lancement de l'API

Depuis le répertoire racine du projet :

```bash
# Méthode 1 : Lancement direct avec uvicorn
uvicorn notebooks.04_deployment_api:app --host 127.0.0.1 --port 8000 --reload

# Méthode 2 : Lancement depuis le script Python
python -c "
import sys
sys.path.append('notebooks')
from notebooks.04_deployment_api import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
"
```

### 3. 🌐 Accès aux Services

Une fois l'API démarrée, vous pouvez accéder à :

- **🏠 Interface de Test** : http://127.0.0.1:8000/static/index.html
- **📖 Documentation Swagger** : http://127.0.0.1:8000/docs
- **📋 Documentation ReDoc** : http://127.0.0.1:8000/redoc
- **💚 État de l'API** : http://127.0.0.1:8000/health
- **🤖 Infos du Modèle** : http://127.0.0.1:8000/model/info

### 4. 🧪 Test de l'API

#### Exemple de requête cURL :

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "area": 7420,
       "bedrooms": 4,
       "bathrooms": 1,
       "stories": 3,
       "mainroad": 1,
       "guestroom": 0,
       "basement": 0,
       "hotwaterheating": 0,
       "airconditioning": 1,
       "parking": 2,
       "prefarea": 1,
       "furnishingstatus": 1
     }'
```

#### Réponse attendue :

```json
{
  "predicted_price": 4617000.0,
  "price_per_sqft": 622.36,
  "formatted_price": "4,617,000",
  "confidence": "high",
  "model_type": "RandomForestRegressor",
  "timestamp": "2025-09-27T10:30:00"
}
```

### 5. 📁 Structure des Fichiers

```
price-predictor/
├── notebooks/
│   ├── 04_deployment_api.ipynb    # Notebook de l'API
│   └── 04_deployment_api.py       # Version Python de l'API
├── static/
│   ├── index.html                 # Interface de test
│   ├── style.css                  # Styles CSS
│   └── index.js                   # JavaScript pour l'interface
├── models/
│   ├── best_model_*.pkl          # Modèle sauvegardé
│   └── model_metadata_*.json     # Métadonnées du modèle
└── data/
    └── processed/
        └── metadata.json          # Métadonnées de preprocessing
```

### 6. 🔧 Configuration Avancée

#### Variables d'Environnement :

```bash
# Port personnalisé
export API_PORT=8080

# Host personnalisé
export API_HOST=0.0.0.0

# Mode debug
export DEBUG=True
```

#### Lancement avec variables d'environnement :

```bash
uvicorn notebooks.04_deployment_api:app --host $API_HOST --port $API_PORT
```

### 7. 🐳 Déploiement avec Docker

Créer un `Dockerfile` :

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "notebooks.04_deployment_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. 🚨 Dépannage

#### Problème : "Module not found"
```bash
# S'assurer que le répertoire notebooks est dans le PYTHONPATH
export PYTHONPATH=$PYTHONPATH:./notebooks
```

#### Problème : "Modèle non chargé"
- Vérifier que l'étape 3 (modélisation) a été exécutée
- S'assurer que les fichiers de modèle sont présents dans `/models`

#### Problème : "Port déjà utilisé"
```bash
# Changer le port
uvicorn notebooks.04_deployment_api:app --port 8001
```

### 9. 📊 Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/health` | GET | État de l'API |
| `/model/info` | GET | Informations du modèle |
| `/predict` | POST | Prédiction simple |
| `/predict/batch` | POST | Prédiction en lot |
| `/model/importance` | GET | Importance des features |
| `/docs` | GET | Documentation Swagger |
| `/redoc` | GET | Documentation ReDoc |

### 10. 🎯 Prochaines Étapes

1. **Sécurité** : Ajouter l'authentification
2. **Monitoring** : Intégrer des métriques de performance
3. **Cache** : Implémenter un système de cache Redis
4. **Tests** : Ajouter des tests unitaires et d'intégration
5. **CI/CD** : Configurer un pipeline de déploiement automatique
