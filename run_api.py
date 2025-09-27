#!/usr/bin/env python3
"""
🚀 Lanceur pour l'API House Price Predictor

Ce script lance automatiquement l'API FastAPI avec les bonnes configurations.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_packages = ["fastapi", "uvicorn", "pydantic"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print(f"💡 Installation: pip install {' '.join(missing_packages)}")
        return False

    return True


def check_model_files():
    """Vérifie que les fichiers de modèle existent"""
    models_path = Path("models")

    if not models_path.exists():
        print("❌ Dossier 'models' non trouvé")
        print("💡 Exécutez d'abord le notebook 03_modeling_evaluation.ipynb")
        return False

    model_files = list(models_path.glob("best_model_*.pkl"))
    if not model_files:
        print("❌ Aucun fichier de modèle trouvé dans 'models/'")
        print("💡 Exécutez d'abord le notebook 03_modeling_evaluation.ipynb")
        return False

    print(f"✅ Modèle trouvé: {model_files[0].name}")
    return True


def launch_api(host="127.0.0.1", port=8000, reload=True):
    """Lance l'API FastAPI"""

    print("🔍 Vérification des prérequis...")

    # Vérifier les dépendances
    if not check_dependencies():
        return False

    # Vérifier les fichiers de modèle
    if not check_model_files():
        return False

    print("✅ Tous les prérequis sont satisfaits")
    print()

    # Configuration de l'environnement
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    # Commande uvicorn
    cmd = [
        "uvicorn",
        "api:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload:
        cmd.append("--reload")

    print(f"🚀 Lancement de l'API...")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📖 Documentation: http://{host}:{port}/docs")
    print(f"🧪 Interface de test: http://{host}:{port}/static/index.html")
    print()
    print("🛑 Pour arrêter l'API: Ctrl+C")
    print("=" * 50)

    try:
        # Lancer uvicorn
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 API arrêtée par l'utilisateur")
        return True
    except FileNotFoundError:
        print("❌ uvicorn non trouvé. Installez-le avec: pip install uvicorn")
        return False


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(
        description="🏠 House Price Predictor API Launcher"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host de l'API (défaut: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port de l'API (défaut: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Désactiver le rechargement automatique",
    )

    args = parser.parse_args()

    print("🏠 House Price Predictor API Launcher")
    print("=" * 40)

    success = launch_api(host=args.host, port=args.port, reload=not args.no_reload)

    if success:
        print("✅ API lancée avec succès")
    else:
        print("❌ Échec du lancement de l'API")
        sys.exit(1)


if __name__ == "__main__":
    main()
