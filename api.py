"""
🚀 API de Prédiction des Prix Immobiliers

FastAPI service pour servir les prédictions de prix de maisons.
Basé sur le notebook 04_deployment_api.ipynb
"""

import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HouseFeatures(BaseModel):
    """Modèle de validation pour les caractéristiques de la maison"""

    area: float = Field(..., gt=0, description="Surface en pieds carrés")
    bedrooms: int = Field(..., ge=1, le=10, description="Nombre de chambres")
    bathrooms: int = Field(..., ge=1, le=10, description="Nombre de salles de bain")
    stories: int = Field(..., ge=1, le=5, description="Nombre d'étages")
    mainroad: int = Field(..., ge=0, le=1, description="Accès route principale (0/1)")
    guestroom: int = Field(..., ge=0, le=1, description="Chambre d'amis (0/1)")
    basement: int = Field(..., ge=0, le=1, description="Sous-sol (0/1)")
    hotwaterheating: int = Field(
        ..., ge=0, le=1, description="Chauffage eau chaude (0/1)"
    )
    airconditioning: int = Field(..., ge=0, le=1, description="Climatisation (0/1)")
    parking: int = Field(..., ge=0, le=5, description="Places de parking")
    prefarea: int = Field(..., ge=0, le=1, description="Zone préférée (0/1)")
    furnishingstatus: int = Field(
        ...,
        ge=0,
        le=2,
        description="État ameublement (0=vide, 1=semi-meublé, 2=meublé)",
    )

    @validator("area")
    def validate_area(cls, v):
        if v < 1000 or v > 20000:
            raise ValueError("Surface doit être entre 1,000 et 20,000 sq ft")
        return v


class PredictionResponse(BaseModel):
    """Modèle de réponse pour les prédictions"""

    price: float = Field(..., description="Prix prédit")
    formatted_price: str = Field(..., description="Prix formaté")
    price_per_sqft: float = Field(..., description="Prix par pied carré")
    confidence: str = Field(..., description="Niveau de confiance")
    features_used: Dict[str, Any] = Field(..., description="Caractéristiques utilisées")
    prediction_time: str = Field(..., description="Timestamp de la prédiction")


class ModelInfo(BaseModel):
    """Informations sur le modèle"""

    model_type: str
    performance_metrics: Optional[Dict]
    feature_names: List[str]
    training_date: Optional[str]
    model_version: str


class HousePricePredictor:
    """Service de prédiction des prix de maisons"""

    def __init__(self, model=None, feature_names=None):
        self.model = model
        self.feature_names = feature_names or [
            "area",
            "bedrooms",
            "bathrooms",
            "stories",
            "mainroad",
            "guestroom",
            "basement",
            "hotwaterheating",
            "airconditioning",
            "parking",
            "prefarea",
            "furnishingstatus",
        ]
        self.model_info = {}

        if model is None:
            self.load_model()

    def load_model(self):
        """Charge le modèle et ses métadonnées"""
        models_path = Path("models")

        if not models_path.exists():
            raise FileNotFoundError("Dossier 'models' non trouvé")

        # Chercher le modèle
        model_files = list(models_path.glob("best_model_*.pkl"))
        if not model_files:
            raise FileNotFoundError("Aucun modèle trouvé dans 'models/'")

        model_file = model_files[0]  # Prendre le premier trouvé
        logger.info(f"Chargement du modèle: {model_file.name}")

        # Charger le modèle
        with open(model_file, "rb") as f:
            self.model = pickle.load(f)

        # Charger les métadonnées
        metadata_files = list(models_path.glob("model_metadata_*.json"))
        if metadata_files:
            with open(metadata_files[0], "r") as f:
                metadata = json.load(f)
                self.model_info = metadata
                if "data_info" in metadata and "feature_names" in metadata["data_info"]:
                    self.feature_names = metadata["data_info"]["feature_names"]

        logger.info(f"Modèle chargé: {type(self.model).__name__}")

    def predict(self, features: Dict) -> Dict:
        """Prédit le prix d'une maison"""
        if self.model is None:
            raise Exception("Modèle non chargé")

        try:
            # Créer un DataFrame avec feature engineering
            df = pd.DataFrame([features])

            # Feature engineering (identique à l'entraînement)
            df["price_per_sqft"] = 0  # Placeholder, sera calculé après prédiction
            df["rooms_total"] = df["bedrooms"] + df["bathrooms"]
            df["area_per_room"] = df["area"] / df["rooms_total"]
            df["bathroom_bedroom_ratio"] = df["bathrooms"] / df["bedrooms"]
            df["luxury_score"] = (
                df["airconditioning"]
                + df["parking"] / 2
                + df["prefarea"]
                + df["guestroom"]
                + df["basement"]
            )
            df["has_luxury"] = (df["luxury_score"] > 2).astype(int)
            df["area_bedrooms_interaction"] = df["area"] * df["bedrooms"]
            df["luxury_area_interaction"] = df["luxury_score"] * df["area"]

            # Catégories de taille
            size_conditions = [
                (df["area"] <= 3000),
                (df["area"] <= 6000),
                (df["area"] <= 10000),
                (df["area"] > 10000),
            ]
            size_choices = ["small", "medium", "large", "very_large"]
            df["size_category"] = np.select(
                size_conditions, size_choices, default="medium"
            )

            # One-hot encoding pour size_category
            for category in ["small", "medium", "very_large"]:
                df[f"size_category_{category}"] = (
                    df["size_category"] == category
                ).astype(int)

            # Sélectionner les features dans le bon ordre
            feature_values = []
            for name in self.feature_names:
                if name in df.columns:
                    feature_values.append(df[name].iloc[0])
                else:
                    logger.warning(f"Feature manquante: {name}")
                    feature_values.append(0)  # Valeur par défaut

            feature_array = np.array(feature_values).reshape(1, -1)

            # Prédiction
            predicted_price = self.model.predict(feature_array)[0]

            # Calculer le prix par pied carré réel
            area_value = features["area"]
            price_per_sqft_value = predicted_price / area_value

            # Déterminer le niveau de confiance
            confidence = self._calculate_confidence(features, predicted_price)

            result = {
                "price": float(predicted_price),
                "formatted_price": f"${predicted_price:,.0f}",
                "price_per_sqft": float(price_per_sqft_value),
                "confidence": confidence,
                "features_used": features,
                "prediction_time": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"Erreur de prédiction: {e}")
            raise Exception(f"Erreur de prédiction: {str(e)}")

    def _calculate_confidence(self, features: Dict, price: float) -> str:
        """Calcule un niveau de confiance basé sur les caractéristiques"""
        # Heuristiques simples pour la confiance
        area = features["area"]
        bedrooms = features["bedrooms"]

        # Vérifications de cohérence
        if area < 2000 and bedrooms > 4:
            return "Faible"
        elif area > 10000 and bedrooms < 3:
            return "Moyenne"
        elif 50 <= price / area <= 200:  # Prix par sq ft raisonnable
            return "Élevée"
        else:
            return "Moyenne"

    def get_model_info(self) -> Dict:
        """Retourne les informations du modèle"""
        return {
            "model_type": type(self.model).__name__ if self.model else "Non chargé",
            "performance_metrics": self.model_info.get("performance", {}),
            "feature_names": self.feature_names,
            "training_date": self.model_info.get("training_date", "Inconnue"),
            "model_version": self.model_info.get("model_version", "1.0.0"),
        }


# Initialisation de l'API
app = FastAPI(
    title="House Price Predictor API",
    description="API de prédiction des prix immobiliers basée sur l'apprentissage automatique",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    logger.warning("Dossier 'static' non trouvé - fichiers statiques non disponibles")

# Initialiser le service de prédiction
try:
    predictor = HousePricePredictor()
    logger.info("Service de prédiction initialisé avec succès")
except Exception as e:
    logger.error(f"Erreur d'initialisation du service: {e}")
    predictor = None


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "House Price Predictor API",
        "version": "1.0.0",
        "status": "active" if predictor else "error",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "model_info": "/model/info",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503, detail="Service non disponible - modèle non chargé"
        )

    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_price(features: HouseFeatures):
    """Prédit le prix d'une maison basé sur ses caractéristiques"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service non disponible")

    # Convertir en dictionnaire
    features_dict = features.dict()

    # Faire la prédiction
    result = predictor.predict(features_dict)

    return PredictionResponse(**result)


@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Retourne les informations sur le modèle actuel"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service non disponible")

    info = predictor.get_model_info()
    return ModelInfo(**info)


@app.get("/predict/example")
async def get_example_prediction():
    """Exemple de prédiction avec des données par défaut"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service non disponible")

    example_features = {
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

    result = predictor.predict(example_features)
    return {"example_input": example_features, "prediction": result}


if __name__ == "__main__":
    import uvicorn

    print("🏠 Démarrage de l'API House Price Predictor...")
    print("📋 Interface disponible sur: http://localhost:8000")
    print("📚 Documentation sur: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
