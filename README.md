# Projet 06 -- Anticipez les besoins en consommation de bâtiments

## Objectif

Exposer un modèle de prédiction de consommation énergétique via une API
REST avec **BentoML**.

Le modèle utilisé est un **RandomForest optimisé par GridSearchCV**,
sauvegardé dans le Model Store BentoML.

------------------------------------------------------------------------

# Lancer l'API

Depuis la racine du projet :

``` powershell
poetry run bentoml serve src.service:SeattleEnergyAPI
```

API disponible sur :\
http://localhost:3000

------------------------------------------------------------------------

# Documentation OpenAPI

La spécification OpenAPI générée par BentoML est disponible sur :

http://localhost:3000/docs.json

L'endpoint peut être testé avec PowerShell, Postman, curl ou tout autre
client HTTP compatible avec une API REST.

------------------------------------------------------------------------
# Endpoint

**POST /predict**\
Content-Type : application/json

------------------------------------------------------------------------

# Exemple de requête valide (PowerShell)

``` powershell
$payload = @{
  BuildingType="NonResidential"
  PrimaryPropertyType="Office"
  LargestPropertyUseType="Office"
  Latitude=47.61
  Longitude=-122.33
  YearBuilt=1999
  NumberofBuildings=1
  NumberofFloors=10
  "PropertyGFABuilding(s)"=250000
  NbPropertyUses=1
  UseSteam=0
  UseElectricity=1
  UseNaturalGas=0
}

Invoke-RestMethod `
  -Uri "http://localhost:3000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body ($payload | ConvertTo-Json)
```

### Réponse attendue

``` json
{
  "SiteEUIWN_kBtu_per_sf": 67.25049996494747
}
```

------------------------------------------------------------------------

# Exemple de requête invalide (validation métier)

``` powershell
$payload.NumberofBuildings = 5000

Invoke-RestMethod `
  -Uri "http://localhost:3000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body ($payload | ConvertTo-Json)
```

### Résultat attendu

-   Code HTTP : 400
-   Champ en erreur : NumberofBuildings
-   Règle : valeur ≤ 200

------------------------------------------------------------------------

# Validation des données

La validation est réalisée avec **Pydantic** :

-   Contraintes réalistes basées sur le dataset
-   Bornes numériques strictes
-   Gestion des alias (PropertyGFABuilding(s))
-   Blocage des valeurs incohérentes
-   Retour d'erreurs structurées

------------------------------------------------------------------------

# Architecture du service

Client (Postman / PowerShell / client HTTP)\
→ API BentoML\
→ Validation Pydantic\
→ Pipeline scikit-learn\
→ RandomForest optimisé\
→ Réponse JSON structurée

------------------------------------------------------------------------

# Modèle utilisé

Tag BentoML :

seattle_energy_rf:6iuuoyyzhwbgekgq

Modèle : RandomForestRegressor optimisé via GridSearchCV

------------------------------------------------------------------------

# Stack technique

-   Python
-   Poetry
-   scikit-learn
-   BentoML 1.4.35
-   Pydantic v2
-   pandas

------------------------------------------------------------------------
