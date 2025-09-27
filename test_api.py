"""
🧪 Script de test pour l'API House Price Predictor

Ce script teste rapidement le service de prédiction sans lancer l'API complète.
"""

import json
import pickle
from pathlib import Path
import sys
import os

# Configuration du path pour les imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))


def load_model():
    """Charge le modèle sauvegardé"""
    models_path = Path("models")

    # Chercher le fichier de modèle
    model_files = list(models_path.glob("best_model_*.pkl"))
    if not model_files:
        print("❌ Aucun modèle trouvé dans le dossier 'models/'")
        return None, None

    model_file = model_files[0]
    print(f"📋 Chargement du modèle: {model_file.name}")

    # Charger le modèle
    with open(model_file, "rb") as f:
        model = pickle.load(f)

    # Charger les métadonnées si disponibles
    metadata_files = list(models_path.glob("model_metadata_*.json"))
    metadata = None
    if metadata_files:
        with open(metadata_files[0], "r") as f:
            metadata = json.load(f)

    return model, metadata


def test_prediction():
    """Test rapide de prédiction"""
    print("🧪 TEST DU SERVICE DE PRÉDICTION")
    print("=" * 40)

    # Charger le modèle
    model, metadata = load_model()
    if model is None:
        return False

    print(f"✅ Modèle chargé: {type(model).__name__}")
    if metadata:
        print(f"📊 Performance R²: {metadata['performance']['test_r2']:.4f}")
        print(f"📉 RMSE: {metadata['performance']['test_rmse']:,.0f}")

    # Exemple de données de test
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

    print(f"\n🏠 Test avec une maison exemple:")
    print(f"   📊 Surface: {test_data['area']:,} sq ft")
    print(
        f"   🛏️ Chambres: {test_data['bedrooms']} | Salles de bain: {test_data['bathrooms']}"
    )
    print(f"   🏢 Étages: {test_data['stories']} | Parking: {test_data['parking']}")

    try:
        # Importer et utiliser le service de prédiction
        from api import HousePricePredictor

        # Créer le service
        if metadata:
            predictor = HousePricePredictor(
                model=model, feature_names=metadata["data_info"]["feature_names"]
            )
        else:
            print("⚠️ Métadonnées non disponibles, test limité")
            return False

        # Faire la prédiction
        result = predictor.predict(test_data)

        print(f"\n🎯 RÉSULTAT:")
        print(f"   💰 Prix estimé: {result['formatted_price']}")
        print(f"   📊 Prix/sq ft: {result['price_per_sqft']:.2f}")
        print(f"   ✅ Confiance: {result['confidence']}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def main():
    """Fonction principale"""
    print("🏠 House Price Predictor - Test Rapide")
    print("=" * 50)

    # Vérifier que nous sommes dans le bon répertoire
    if not Path("notebooks").exists():
        print("❌ Répertoire 'notebooks' non trouvé")
        print("💡 Exécutez ce script depuis la racine du projet price-predictor")
        return

    # Lancer le test
    success = test_prediction()

    if success:
        print(f"\n✅ Test réussi ! Le service de prédiction fonctionne.")
        print(f"🚀 Vous pouvez maintenant lancer l'API avec:")
        print(f"   python run_api.py")
        print(f"   ou")
        print(f"   uvicorn notebooks.04_deployment_api:app --reload")
    else:
        print(f"\n❌ Test échoué. Vérifiez les prérequis:")
        print(f"   1. Modèle entraîné (étape 3)")
        print(f"   2. Dépendances installées (pip install -r requirements.txt)")


if __name__ == "__main__":
    main()
