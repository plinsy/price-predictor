
# 🤖 Modèle de Prédiction des Prix Immobiliers

## Informations Générales
- **Modèle**: Gradient Boosting
- **Date d'entraînement**: 2025-09-26 19:33:27
- **Fichier modèle**: `best_model_gradient_boosting.pkl`
- **Métadonnées**: `model_metadata_gradient_boosting.json`

## Performance
- **R² Score**: 0.9622
- **RMSE**: 350,259
- **MAE**: 210,129
- **MAPE**: 4.47%

## Utilisation
```python
import pickle
import pandas as pd

# Charger le modèle
with open('best_model_gradient_boosting.pkl', 'rb') as f:
    model = pickle.load(f)

# Faire des prédictions
# predictions = model.predict(X_new)
```

## Notes
- Les données doivent être normalisées avec RobustScaler
- 23 features sont nécessaires
- Modèle optimisé avec validation croisée 5-fold
