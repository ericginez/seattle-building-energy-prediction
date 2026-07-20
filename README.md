# Projet 06 — Anticipez les besoins en consommation de bâtiments

Développement et exposition d’un modèle de Machine Learning destiné à prédire
la consommation énergétique de bâtiments non résidentiels de Seattle.

## Contexte de la mission

La ville de Seattle souhaite mieux anticiper la consommation énergétique de
ses bâtiments non résidentiels afin d’orienter ses actions de maîtrise de
l’énergie et de contribuer à son objectif de neutralité carbone.

Le projet repose sur le jeu de données public
`2016_Building_Energy_Benchmarking`, issu du portail Seattle Open Data. Il
contient des informations relatives à la localisation, aux caractéristiques
structurelles, aux usages et aux consommations énergétiques des bâtiments.

La mission consiste à construire un modèle de Machine Learning capable de
prédire l’intensité énergétique normalisée d’un bâtiment :

```text
SiteEUIWN(kBtu/sf)
```

Le projet comprend :

- le nettoyage et la sélection des données pertinentes ;
- le traitement des valeurs manquantes ;
- la création de variables métier ;
- la comparaison de plusieurs modèles de régression ;
- l’optimisation du meilleur modèle ;
- l’interprétation du modèle avec SHAP ;
- l’exposition du modèle final au moyen d’une API REST BentoML.

## Présentation

- [Consulter la présentation de soutenance au format PDF](presentation/projet-06-prediction-energetique-batiments-seattle.pdf)

## Objectifs

La solution répond aux objectifs suivants :

- préparer et transformer les données pour l’apprentissage supervisé ;
- limiter les variables redondantes et les risques de fuite de données ;
- créer des variables adaptées aux caractéristiques des bâtiments ;
- comparer plusieurs modèles de régression ;
- optimiser les hyperparamètres du modèle retenu ;
- interpréter les facteurs influençant les prédictions ;
- enregistrer le pipeline complet dans le Model Store BentoML ;
- exposer le modèle au moyen d’une API REST ;
- valider les données entrantes avec Pydantic ;
- retourner des réponses JSON structurées.

## Architecture du projet

Le projet couvre l’ensemble du cycle de préparation, d’apprentissage et
d’exposition du modèle prédictif.

```text
Dataset Seattle Open Data
          |
          v
Nettoyage et sélection des variables
          |
          v
Feature engineering
          |
          v
Préprocesseur scikit-learn
          |
          v
Comparaison des modèles de régression
          |
          v
Optimisation du Random Forest avec GridSearchCV
          |
          v
Enregistrement dans le Model Store BentoML
          |
          v
API REST de prédiction
```

### Architecture du service de prédiction

```text
Client HTTP
    |
    v
API BentoML
    |
    v
Validation Pydantic
    |
    v
Pipeline scikit-learn
    |
    v
RandomForestRegressor optimisé
    |
    v
Réponse JSON structurée
```

Le pipeline chargé par l’API contient le prétraitement des variables et le
modèle final. Il est chargé une seule fois au démarrage du service.

## Arborescence du projet

Le dépôt est organisé en deux niveaux :

- la racine contient les données, le notebook de modélisation et une première
  version du service BentoML ;
- le dossier `app/` contient une application BentoML autonome avec ses propres
  dépendances et sa configuration de construction.

```text
.
├── app/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── service.py
│   ├── bentofile.yaml
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
├── notebooks/
│   └── template_modelistation_supervisee.ipynb
├── presentation/
│   └── projet-06-prediction-energetique-batiments-seattle.pdf
├── src/
│   ├── __init__.py
│   ├── schema.py
│   └── service.py
├── 2016_Building_Energy_Benchmarking.csv
├── Dictionnary.csv
├── LargestPropertyUseType.csv
├── bentoml.yaml
├── poetry.lock
├── pyproject.toml
├── .gitignore
└── README.md
```

Le modèle entraîné est enregistré dans le Model Store BentoML local. Ce Model
Store n’est pas versionné dans Git. La configuration de construction de
l’application autonome se trouve dans `app/bentofile.yaml`.

## Données et fichiers sources

Le dépôt contient trois fichiers liés aux données :

| Fichier | Rôle |
|---|---|
| `2016_Building_Energy_Benchmarking.csv` | Jeu de données principal issu de Seattle Open Data |
| `Dictionnary.csv` | Dictionnaire des variables du jeu de données |
| `LargestPropertyUseType.csv` | Référentiel complémentaire utilisé pour le regroupement des usages principaux |

Le fichier principal contient initialement 3 376 bâtiments et 46 variables.
Les transformations et les choix de modélisation sont documentés dans le
notebook :

```text
notebooks/template_modelistation_supervisee.ipynb
```

## Préparation des données

Le jeu de données initial contient 3 376 bâtiments et 46 variables.

Les principales étapes de préparation sont :

- suppression des colonnes non pertinentes ou peu exploitables ;
- exclusion des bâtiments résidentiels ;
- exclusion des déclarations non conformes ;
- suppression des variables présentant trop de valeurs manquantes ;
- suppression des variables redondantes ;
- exclusion des variables d’émission susceptibles de provoquer une fuite de
  données ;
- traitement des valeurs manquantes résiduelles ;
- suppression des valeurs nulles de la variable cible.

Le jeu de données final utilisé pour la modélisation contient 1 536 bâtiments.

## Feature engineering

Les transformations principales comprennent :

- création de `NbPropertyUses` à partir de la liste des usages ;
- regroupement des modalités catégorielles rares ;
- création de `BuildingAge` à partir de l’année de construction ;
- création de `DistToDowntown_km` ;
- transformation du mix énergétique en indicateurs booléens :
  `UseSteam`, `UseElectricity` et `UseNaturalGas`.

Le préprocesseur applique :

- un `OneHotEncoder` aux variables catégorielles ;
- un `StandardScaler` aux variables numériques ;
- un passage direct des variables booléennes.

## Modèles comparés

Les modèles suivants ont été évalués avec une validation croisée en cinq
parties :

| Modèle | RMSE | MAE | R² |
|---|---:|---:|---:|
| Dummy | 78,6 | 43,0 | −0,084 |
| LinearRegression | 62,2 | 36,6 | 0,318 |
| SVR | 76,3 | 40,6 | −0,020 |
| RandomForest | 61,2 | 36,9 | 0,336 |
| GradientBoosting | 61,5 | 36,3 | 0,327 |

Le `RandomForestRegressor` a été retenu en raison de son meilleur coefficient
de détermination parmi les modèles comparés.

## Optimisation du modèle

Le modèle a été optimisé avec `GridSearchCV`.

La grille comprend notamment :

- le nombre d’arbres ;
- la profondeur maximale ;
- le nombre minimal d’observations par feuille ;
- le nombre minimal d’observations requis pour diviser un nœud ;
- le nombre de variables candidates à chaque division.

L’optimisation porte sur 288 combinaisons, soit 1 440 apprentissages avec la
validation croisée.

Le meilleur score obtenu est :

```text
R² = 0,383
```

## Interprétation avec SHAP

L’analyse SHAP montre que les prédictions dépendent principalement :

- du type d’activité du bâtiment ;
- du mix énergétique utilisé ;
- de l’âge du bâtiment ;
- de sa surface ;
- de certaines caractéristiques de localisation.

Cette interprétation permet de mieux comprendre le comportement du modèle et
de présenter ses principaux facteurs d’influence.

## Installation

Le projet utilise Poetry.

### Environnement principal

Depuis la racine du dépôt :

```powershell
poetry install
```

### Application BentoML autonome

Le dossier `app/` possède son propre environnement Poetry et sa propre
configuration BentoML :

```powershell
Set-Location "app"
poetry install
```

Revenir ensuite à la racine si l’API doit être lancée avec les fichiers
présents dans `src/` :

```powershell
Set-Location ".."
```

### Vérifier le modèle BentoML

Le service dépend d’un modèle enregistré dans le Model Store BentoML local :

```powershell
poetry run bentoml models list
```

Le tag attendu est :

```text
seattle_energy_rf:6iuuoyyzhwbgekgq
```

Si ce modèle n’est pas présent, le notebook de modélisation doit être exécuté
afin d’entraîner et d’enregistrer à nouveau le pipeline.

## Lancer l’API

Depuis la racine du projet :

```powershell
poetry run bentoml serve src.service:SeattleEnergyAPI
```

Depuis le dossier `app/`, la commande équivalente est :

```powershell
poetry run bentoml serve src.service:SeattleEnergyAPI
```

L’API est alors accessible à l’adresse suivante :

```text
http://localhost:3000
```

## Documentation OpenAPI

La spécification OpenAPI générée par BentoML est disponible à l’adresse :

```text
http://localhost:3000/docs.json
```

L’API peut être testée avec PowerShell, Postman, curl ou tout client HTTP
compatible.

## Endpoint de prédiction

```text
POST /predict
Content-Type: application/json
```

### Exemple de requête valide

```powershell
$payload = @{
    BuildingType = "NonResidential"
    PrimaryPropertyType = "Office"
    LargestPropertyUseType = "Office"
    Latitude = 47.61
    Longitude = -122.33
    YearBuilt = 1999
    NumberofBuildings = 1
    NumberofFloors = 10
    "PropertyGFABuilding(s)" = 250000
    NbPropertyUses = 1
    UseSteam = 0
    UseElectricity = 1
    UseNaturalGas = 0
}

Invoke-RestMethod `
    -Uri "http://localhost:3000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body ($payload | ConvertTo-Json)
```

### Réponse attendue

```json
{
  "SiteEUIWN_kBtu_per_sf": 67.25049996494747
}
```

### Exemple de requête invalide

```powershell
$payload.NumberofBuildings = 5000

Invoke-RestMethod `
    -Uri "http://localhost:3000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body ($payload | ConvertTo-Json)
```

Résultat attendu :

- code HTTP : `400` ;
- champ en erreur : `NumberofBuildings` ;
- règle : valeur inférieure ou égale à `200`.

## Validation des données

La validation des entrées est réalisée avec Pydantic :

- contraintes cohérentes avec le périmètre du dataset ;
- bornes numériques strictes ;
- gestion de l’alias `PropertyGFABuilding(s)` ;
- blocage des valeurs incohérentes ;
- retour d’erreurs structurées.

## Modèle utilisé

Le modèle final est un `RandomForestRegressor` optimisé avec
`GridSearchCV`, intégré dans un pipeline scikit-learn complet.

Tag BentoML :

```text
seattle_energy_rf:6iuuoyyzhwbgekgq
```

## Livrables

Le projet comprend :

- un notebook de préparation et de modélisation ;
- un pipeline scikit-learn complet ;
- un modèle Random Forest optimisé ;
- une analyse d’interprétabilité SHAP ;
- un modèle enregistré dans le Model Store BentoML ;
- une API REST BentoML ;
- des schémas Pydantic de validation ;
- les configurations BentoML de la racine et de l’application autonome ;
- une documentation d’exécution ;
- une présentation de soutenance au format PDF.

## Limites

Le projet présente plusieurs limites :

- le jeu de données porte uniquement sur l’année 2016 ;
- le meilleur coefficient de détermination reste modéré avec `R² = 0,383` ;
- le modèle dépend d’un Model Store BentoML local non versionné dans Git ;
- aucune image Docker de l’API n’est publiée dans le dépôt ;
- les tests automatisés de l’API et des schémas Pydantic ne sont pas encore
  présents ;
- la racine et le dossier `app/` contiennent deux versions du service, ce qui
  peut entraîner des divergences si elles évoluent séparément ;
- aucun suivi de dérive des données ou des performances n’est mis en place.

## Évolutions possibles

Les évolutions envisagées comprennent :

- regrouper le service BentoML dans une seule arborescence de référence ;
- ajouter des tests unitaires et des tests d’intégration de l’API ;
- mettre en place une intégration continue ;
- construire et publier une image Docker ou un Bento déployable ;
- ajouter une journalisation structurée des requêtes et des erreurs ;
- superviser la latence, les erreurs et la distribution des prédictions ;
- détecter la dérive des données et du modèle ;
- réentraîner le modèle avec des données plus récentes ;
- comparer d’autres algorithmes et stratégies d’optimisation ;
- versionner explicitement les modèles et leurs métriques.

## Stack technique

- Python ;
- Poetry ;
- pandas ;
- NumPy ;
- scikit-learn ;
- Random Forest ;
- GridSearchCV ;
- SHAP ;
- BentoML 1.4.35 ;
- Pydantic v2 ;
- Git ;
- GitHub.
