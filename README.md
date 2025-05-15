# Fichier de suivi DTNUM

## Initialisation du fichier post-migration

1. Récupérer la dernière version du fichier de suivi
2. Renommer la colonne "N° DataPass" en "N° DataPass v1"
3. Ajouter la colonne "Erreurs"
4. Renommer la colonne "N° DataPass rattaché (BAS ou FC)" en "N° DataPass FC rattaché"

5. Extraire les IDs de V2 des datapass du fichier de suivi depuis la prod (à faire par Valentin)

6. Insérer les IDs de v2 dans 2 nouvelles colonnes du fichier de suivi "N° Demande v2" et "N° Habilitation v2"
7. Générer des credentials d'accès à l'API pour un user dgfip -> Quel user ? (maimouna ?) (à faire par Valentin)

8. Faire tourner le script `main.py` et le fichier de suivi pour générer un nouveau fichier à jour

## Mise à jour du fichier après initialisation

Faire tourner le script `main.py` avec le dernier fichier de suivi

# Instructions pour installer le projet

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
- On Linux/Mac:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Add environnment variables
```
# Si besoin de proxy, typiquement pour la dgfip
PROXY_URL

# Credentials d'accès à l'API Datapass à récupérer dans le profil utilisateur sur Datapass
DATAPASS_CLIENT_ID
DATAPASS_CLIENT_SECRET
```

## Usage

The main script can be run with:
```bash
python3 main.py
```

Make sure to provide your client credentials as command line arguments when running the script. 

## Tests

```bash
pytest test_update_suivi_dtnum.py
```