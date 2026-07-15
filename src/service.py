"""
Service BentoML exposant le modèle de prédiction de consommation énergétique.

Ce service :

- Charge un modèle RandomForest optimisé (sauvegardé avec BentoML)
- Expose un endpoint HTTP POST /predict
- Valide les entrées via Pydantic
- Retourne une prédiction structurée
- Expose plusieurs endpoints de monitoring et de documentation
- Autorise les requêtes cross-origin (CORS) pour Swagger UI local

Architecture :
Client (Swagger/Postman) → API BentoML → Pipeline sklearn → RandomForest
"""

import bentoml
import pandas as pd

# Import des schémas Pydantic correspondant aux différents endpoints :
#
# - BuildingInput : structure des données envoyées au endpoint /predict
# - PredictionOutput : structure de la réponse retournée par /predict
# - HealthOutput : réponse de l'endpoint de monitoring applicatif /health
# - MetadataOutput : informations générales sur le service et le modèle déployé
# - ModelInfoOutput : informations détaillées sur le modèle chargé en mémoire
# - FeaturesOutput : liste des variables attendues par le modèle en entrée
from .schema import (
    BuildingInput,
    PredictionOutput,
    HealthOutput,
    MetadataOutput,
    ModelInfoOutput,
    FeaturesOutput,
)

# Tag du modèle sauvegardé dans le Model Store BentoML.
# Ce tag doit correspondre à la version validée et réellement utilisée
# pour le déploiement.
MODEL_TAG = "seattle_energy_rf:6iuuoyyzhwbgekgq"

# Métadonnées générales du service.
SERVICE_NAME = "SeattleEnergyAPI"
TARGET_NAME = "SiteEUIWN_kBtu_per_sf"
API_VERSION = "1.0.0"


@bentoml.service(
    # Configuration HTTP du service.
    http={
        # Activation du CORS pour permettre, en développement local,
        # à une interface Swagger UI exécutée sur un autre port
        # (par exemple localhost:8081) d'interroger l'API BentoML.
        "cors": {
            "enabled": True,
            # En environnement local de développement, on autorise toutes
            # les origines pour simplifier les tests. En production réelle,
            # il serait préférable de restreindre cette liste.
            "access_control_allow_origins": ["*"],
            "access_control_allow_methods": ["GET", "POST", "OPTIONS"],
            "access_control_allow_headers": ["*"],
            "access_control_allow_credentials": False,
        }
    }
)
class SeattleEnergyAPI:
    """
    Service BentoML encapsulant le modèle de prédiction.

    L'utilisation d'une classe permet :

    - de charger le modèle une seule fois au démarrage,
    - d'éviter son rechargement à chaque requête,
    - d'améliorer les performances d'inférence,
    - de centraliser les endpoints métier et de monitoring.
    """

    def __init__(self) -> None:
        """
        Méthode appelée au démarrage du service.

        Étapes :
        1. Récupération du modèle depuis le Model Store BentoML
        2. Chargement en mémoire du pipeline complet

        Le pipeline contient :
        - le préprocessing (ColumnTransformer)
        - le modèle RandomForest final

        On mémorise aussi le nombre de variables attendues en entrée,
        ce qui permet de documenter le service via l'endpoint /model-info.
        """
        bento_model = bentoml.sklearn.get(MODEL_TAG)
        self.pipeline = bento_model.load_model()

        # Nombre de features attendues par le schéma d'entrée.
        self.features_count = len(BuildingInput.model_fields)

    @bentoml.api(
        route="/predict",
        input_spec=BuildingInput,
        output_spec=PredictionOutput
    )
    def predict(self, **data) -> PredictionOutput:
        """
        Endpoint POST /predict

        Pipeline d'exécution :

        1. Validation automatique via Pydantic
           → Si les données sont invalides, BentoML renvoie HTTP 400

        2. Conversion en DataFrame pandas
           → Format requis par le pipeline scikit-learn

        3. Prédiction via le pipeline complet
           → préprocessing + modèle

        4. Retour d'une réponse JSON structurée
        """
        # Validation des données entrantes.
        input_obj = BuildingInput.model_validate(data)

        # Conversion en dictionnaire avec les alias exacts attendus
        # par le pipeline entraîné, notamment "PropertyGFABuilding(s)".
        payload = input_obj.model_dump(by_alias=True)

        # Le pipeline sklearn attend un DataFrame 2D.
        X_one = pd.DataFrame([payload])

        # Exécution de la prédiction.
        pred = float(self.pipeline.predict(X_one)[0])

        # Retour de la prédiction dans un schéma de sortie structuré.
        return PredictionOutput(
            SiteEUIWN_kBtu_per_sf=pred
        )

    @bentoml.api(route="/health", output_spec=HealthOutput)
    def health(self) -> HealthOutput:
        """
        Endpoint de santé applicative.

        Cet endpoint complète les endpoints techniques BentoML
        (/healthz, /livez, /readyz) avec une réponse plus lisible
        et plus directement exploitable par un humain.

        Il permet de vérifier rapidement :
        - que le service est démarré,
        - que le modèle est chargé,
        - quel modèle est actuellement utilisé.
        """
        return HealthOutput(
            status="ok",
            service=SERVICE_NAME,
            model_tag=MODEL_TAG
        )

    @bentoml.api(route="/metadata", output_spec=MetadataOutput)
    def metadata(self) -> MetadataOutput:
        """
        Endpoint de métadonnées du service.

        Il expose des informations générales utiles pour :
        - la documentation de l'API,
        - la traçabilité des déploiements,
        - le debugging,
        - l'audit d'un service ML en production.

        Les données retournées décrivent :
        - le nom du service,
        - la version de l'API,
        - la cible prédite,
        - le framework utilisé,
        - le tag du modèle déployé.
        """
        return MetadataOutput(
            service_name=SERVICE_NAME,
            model_tag=MODEL_TAG,
            target=TARGET_NAME,
            api_version=API_VERSION,
            framework="BentoML"
        )

    @bentoml.api(route="/model-info", output_spec=ModelInfoOutput)
    def model_info(self) -> ModelInfoOutput:
        """
        Endpoint d'information sur le modèle chargé.

        Cet endpoint permet de documenter le service ML et de vérifier
        en production les éléments suivants :
        - la version exacte du modèle déployé,
        - la classe d'algorithme utilisée,
        - la nature du pipeline de traitement,
        - le nombre de variables attendues,
        - la cible prédite.
        """
        return ModelInfoOutput(
            model_tag=MODEL_TAG,
            model_class=type(self.pipeline.named_steps["model"]).__name__,
            pipeline_class=type(self.pipeline).__name__,
            prediction_target=TARGET_NAME,
            features_count=self.features_count
        )

    @bentoml.api(route="/features", output_spec=FeaturesOutput)
    def features(self) -> FeaturesOutput:
        """
        Endpoint exposant la liste des variables attendues par le modèle.

        Cet endpoint est utile pour :
        - documenter l'API ML,
        - faciliter l'intégration côté client,
        - vérifier rapidement les champs requis par /predict,
        - améliorer la lisibilité de l'API en production.

        Les noms retournés ici correspondent aux noms internes du schéma
        Pydantic. L'alias "PropertyGFABuilding(s)" reste bien accepté
        côté API grâce à la configuration du schéma d'entrée.
        """
        return FeaturesOutput(
            features=list(BuildingInput.model_fields.keys())
        )