"""
🔍 Script de débogage pour identifier le problème
"""

import json
import pickle
from pathlib import Path
import traceback


def debug_prediction():
    """Debug détaillé de la prédiction"""
    print("🔍 DEBUG - Analyse détaillée")
    print("=" * 40)

    # Charger le modèle
    models_path = Path("models")
    model_files = list(models_path.glob("best_model_*.pkl"))

    if not model_files:
        print("❌ Aucun modèle trouvé")
        return

    model_file = model_files[0]
    print(f"📋 Chargement: {model_file.name}")

    with open(model_file, "rb") as f:
        model = pickle.load(f)

    # Charger métadonnées
    metadata_files = list(models_path.glob("model_metadata_*.json"))
    if metadata_files:
        with open(metadata_files[0], "r") as f:
            metadata = json.load(f)
        print(f"✅ Métadonnées chargées")
        feature_names = metadata["data_info"]["feature_names"]
        print(f"📊 Features: {feature_names}")
    else:
        print("❌ Pas de métadonnées")
        return

    # Données de test
    test_data = {
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
        "furnishingstatus": 1,
    }

    print(f"🏠 Données test: {test_data}")

    try:
        # Préparer les données
        print("🔧 Préparation des données...")
        feature_values = [test_data[name] for name in feature_names]
        print(f"📊 Valeurs: {feature_values}")

        import numpy as np

        feature_array = np.array(feature_values).reshape(1, -1)
        print(f"🔢 Array shape: {feature_array.shape}")

        # Prédiction
        print("🎯 Prédiction...")
        predicted_price = model.predict(feature_array)[0]
        print(f"💰 Prix prédit: ${predicted_price:,.0f}")

        # Calcul prix/m²
        area_value = test_data["area"]
        print(f"📏 Surface: {area_value}")
        price_per_sqft = predicted_price / area_value
        print(f"📊 Prix/sqft: ${price_per_sqft:.2f}")

        print("✅ Test réussi !")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("🔍 Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    debug_prediction()
