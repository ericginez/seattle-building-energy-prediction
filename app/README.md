# SeattleEnergyAPI -- Version Déploiement (app/)

## Description

SeattleEnergyAPI est une API REST de prédiction de consommation
énergétique des bâtiments.

Elle expose un endpoint `/predict` permettant d'estimer :

    SiteEUIWN_kBtu_per_sf

Le modèle utilisé est un RandomForestRegressor optimisé (GridSearchCV)
et packagé avec BentoML.

------------------------------------------------------------------------

## Structure du dossier app/

app/
├── src/
│   ├── service.py
│   ├── schema.py
│   └── __init__.py
├── bentofile.yaml
├── pyproject.toml
├── poetry.lock
└── README.md

-   service.py : définition du service BentoML
-   schema.py : validation des entrées/sorties via Pydantic
-   bentofile.yaml : configuration du packaging Bento
-   pyproject.toml : dépendances runtime
-   poetry.lock : verrouillage des versions

------------------------------------------------------------------------

## Stack technique

-   Python 3.14
-   BentoML 1.4.35
-   Scikit-learn
-   Pandas
-   NumPy
-   Docker
-   GCP Cloud Run

------------------------------------------------------------------------

## Installation et build

Depuis le dossier app/

1.  Installer les dépendances :

    poetry install

2.  Construire le Bento :

    poetry run bentoml build

3.  Lister les Bentos disponibles :

    poetry run bentoml list

------------------------------------------------------------------------

## Containerisation

Créer l'image Docker :

    poetry run bentoml containerize seattle_energyapi:<TAG> -t seattle-energy-api:latest

Vérifier l'image :

    docker images

------------------------------------------------------------------------

## Lancement local du container

    docker run --rm -p 3000:3000 seattle-energy-api:latest

L'API sera disponible sur :

    http://localhost:3000

------------------------------------------------------------------------

## Health check

    GET http://localhost:3000/readyz

Doit retourner HTTP 200.

------------------------------------------------------------------------

## Endpoint principal

### POST /predict

### Exemple de requête

{ "BuildingType": "NonResidential", "PrimaryPropertyType": "Office",
"LargestPropertyUseType": "Office", "Latitude": 47.61, "Longitude":
-122.33, "YearBuilt": 1999, "NumberofBuildings": 1, "NumberofFloors":
10, "PropertyGFABuilding(s)": 250000, "NbPropertyUses": 1, "UseSteam":
0, "UseElectricity": 1, "UseNaturalGas": 0 }

### Exemple de réponse

{ "SiteEUIWN_kBtu_per_sf": 67.25 }

------------------------------------------------------------------------

## Déploiement Cloud Run (exemple)

1.  Pousser l'image vers Artifact Registry.

2.  Déployer :

    gcloud run deploy seattle-energy-api --image
    europe-west1-docker.pkg.dev/PROJECT_ID/seattle-repo/seattle-energy-api:latest
    --allow-unauthenticated --port 3000

------------------------------------------------------------------------

## Validation production

Tester :

    GET https://DEPLOYED_URL/readyz
    POST https://DEPLOYED_URL/predict

------------------------------------------------------------------------

## Validation des entrées

La validation Pydantic garantit :

-   Types stricts
-   Contraintes numériques (ex : NumberofBuildings ≤ 200)
-   Rejet des payloads invalides (400 Bad Request)

------------------------------------------------------------------------

## Objectif

Le dossier app/ représente la version production-ready de l'API :

-   Dépendances runtime minimales
-   Packaging BentoML reproductible
-   Image Docker autonome
-   Déploiement cloud prêt
