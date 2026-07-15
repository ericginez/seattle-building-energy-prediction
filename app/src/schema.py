"""
Définition des schémas Pydantic pour :

- la validation des données entrantes (BuildingInput),
- la structure des données retournées par les endpoints de l'API.

Ces schémas servent à plusieurs niveaux :

1. Validation automatique des requêtes
   Les données envoyées à l'API sont contrôlées avant d'être
   transmises au pipeline de prédiction.

2. Structuration des réponses JSON
   Chaque endpoint renvoie un format clair, stable et documenté.

3. Génération automatique de la documentation OpenAPI
   BentoML s'appuie sur ces schémas pour produire la documentation
   interactive de l'API.

4. Sécurisation du service
   Les champs inattendus, incohérents ou hors bornes sont rejetés
   avant d'atteindre le modèle.
"""

from pydantic import BaseModel, Field, ConfigDict


class BuildingInput(BaseModel):
    """
    Schéma décrivant les données attendues par le modèle.

    Toutes les contraintes sont basées :
    - sur les bornes physiques réalistes,
    - sur les valeurs observées dans le dataset nettoyé,
    - sur les variables effectivement utilisées pour l'entraînement.

    Ce schéma représente le contrat d'entrée du endpoint /predict.
    """

    # Configuration du modèle Pydantic.
    #
    # populate_by_name=True :
    #   permet d'utiliser les noms internes des champs ainsi que leurs alias.
    #
    # extra="forbid" :
    #   interdit les champs non déclarés pour éviter d'envoyer au modèle
    #   des variables inattendues ou mal orthographiées.
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid"
    )

    # =======================
    # Variables catégorielles
    # =======================

    BuildingType: str = Field(
        ...,
        min_length=1,
        description="Type de bâtiment (catégorie générale)."
    )

    PrimaryPropertyType: str = Field(
        ...,
        min_length=1,
        description="Type de propriété principal."
    )

    LargestPropertyUseType: str = Field(
        ...,
        min_length=1,
        description="Usage principal du bâtiment (le plus important)."
    )

    # ====================
    # Variables numériques
    # ====================

    Latitude: float = Field(
        ...,
        ge=45,
        le=50,
        description="Latitude du bâtiment dans la zone étudiée (Seattle)."
    )

    Longitude: float = Field(
        ...,
        ge=-125,
        le=-120,
        description="Longitude du bâtiment dans la zone étudiée (Seattle)."
    )

    DistToDowntown_km: float = Field(
        ...,
        ge=0,
        le=20,
        description="Distance entre le bâtiment et le centre-ville, en kilomètres."
    )

    BuildingAge: int = Field(
        ...,
        ge=0,
        le=200,
        description="Âge du bâtiment, calculé à partir de l'année de construction."
    )

    NumberofBuildings: float = Field(
        ...,
        gt=0,
        le=200,
        description="Nombre de bâtiments associés à la propriété."
    )

    NumberofFloors: int = Field(
        ...,
        gt=0,
        le=200,
        description="Nombre d'étages du bâtiment."
    )

    # Alias important :
    # le modèle a été entraîné avec le nom exact
    # 'PropertyGFABuilding(s)'.
    #
    # Le champ interne Python est donc nommé PropertyGFABuildings
    # mais l'API accepte/renvoie l'alias attendu par le pipeline.
    PropertyGFABuildings: int = Field(
        ...,
        alias="PropertyGFABuilding(s)",
        ge=100,
        le=100_000_000,
        description="Surface brute (GFA) du bâtiment, exprimée en square feet."
    )

    NbPropertyUses: int = Field(
        ...,
        ge=1,
        le=30,
        description="Nombre d'usages déclarés pour la propriété."
    )

    # ===================================
    # Variables booléennes encodées en 0/1
    # ===================================

    UseSteam: int = Field(
        ...,
        ge=0,
        le=1,
        description="Indique si la vapeur est utilisée (1) ou non (0)."
    )

    UseElectricity: int = Field(
        ...,
        ge=0,
        le=1,
        description="Indique si l'électricité est utilisée (1) ou non (0)."
    )

    UseNaturalGas: int = Field(
        ...,
        ge=0,
        le=1,
        description="Indique si le gaz naturel est utilisé (1) ou non (0)."
    )


class PredictionOutput(BaseModel):
    """
    Structure de la réponse retournée par l'endpoint /predict.

    Cette réponse contient uniquement la prédiction du modèle.
    """

    SiteEUIWN_kBtu_per_sf: float = Field(
        ...,
        description="Prédiction de l'intensité énergétique normalisée du bâtiment."
    )


class HealthOutput(BaseModel):
    """
    Schéma de réponse pour l'endpoint /health.

    Cet endpoint fournit un indicateur simple de disponibilité
    applicative du service.

    Contrairement aux endpoints techniques BentoML
    (/healthz, /livez, /readyz), cet endpoint expose une réponse
    plus lisible pour un humain ou un outil de supervision simple.

    Objectifs :
    - vérifier que le service API est démarré,
    - vérifier que le modèle est chargé en mémoire,
    - exposer l'identité du service et la version du modèle utilisée.
    """

    status: str
    service: str
    model_tag: str


class MetadataOutput(BaseModel):
    """
    Schéma de réponse pour l'endpoint /metadata.

    Cet endpoint expose les métadonnées générales du service
    de Machine Learning déployé.

    Ces informations permettent notamment :
    - d'identifier la version du service,
    - de documenter la cible prédite par le modèle,
    - de tracer la version du modèle actuellement en production,
    - d'identifier la technologie utilisée pour l'inférence.
    """

    service_name: str
    model_tag: str
    target: str
    api_version: str
    framework: str


class ModelInfoOutput(BaseModel):
    """
    Schéma de réponse pour l'endpoint /model-info.

    Cet endpoint fournit des informations détaillées sur
    le modèle chargé en mémoire par le service BentoML.

    Ces informations permettent notamment :
    - de vérifier la version exacte du modèle déployé,
    - d'identifier le type d'algorithme utilisé,
    - de documenter la structure du pipeline de preprocessing,
    - de vérifier le nombre de variables attendues en entrée.
    """

    model_tag: str
    model_class: str
    pipeline_class: str
    prediction_target: str
    features_count: int


class FeaturesOutput(BaseModel):
    """
    Schéma de réponse pour l'endpoint /features.

    Cet endpoint expose la liste des variables attendues
    par le modèle en entrée.

    Objectifs :
    - documenter l'API,
    - faciliter l'intégration côté client,
    - permettre un contrôle rapide des variables utilisées
      par le modèle en production.
    """

    features: list[str]