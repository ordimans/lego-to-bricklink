# LEGO to BrickLink Converter

[🇬🇧 English version](README.md)

Convertit une liste d'**Element IDs LEGO** (depuis un manuel LEGO) en fichier **XML compatible BrickLink** pour importer une Wanted List.

Utile quand tu as un set LEGO incomplet et que tu veux commander les pièces manquantes sur BrickLink.

## Fonctionnalités

- Convertit les Element IDs LEGO en Part Numbers BrickLink
- Récupère automatiquement la couleur correcte via l'API BrickLink
- Agrégation automatique des doublons (quantités additionnées)
- Génère un XML prêt à importer sur BrickLink
- Aucune dépendance externe (Python standard library uniquement)

## Prérequis

- Python 3.6+
- Clés API BrickLink (gratuites)

## Installation

```bash
git clone https://github.com/ordimans/lego-to-bricklink.git
cd lego-to-bricklink
```

## Configuration

### Obtenir les clés API BrickLink

1. Connecte-toi sur [BrickLink.com](https://www.bricklink.com)
2. Va dans **My BrickLink > API** ou directement : https://www.bricklink.com/v2/api/register_consumer.page
3. Crée une nouvelle "Consumer Key"
4. Note les 4 clés fournies

### Configurer les variables d'environnement

Copie le fichier d'exemple et remplis-le avec tes clés :

```bash
cp .env.example .env
nano .env  # ou ton éditeur préféré
```

Puis charge les variables :

```bash
source .env
```

Ou exporte-les directement :

```bash
export BRICKLINK_CONSUMER_KEY=ta_consumer_key
export BRICKLINK_CONSUMER_SECRET=ton_consumer_secret
export BRICKLINK_TOKEN=ton_token
export BRICKLINK_TOKEN_SECRET=ton_token_secret
```

## Utilisation

### Format du fichier CSV

Crée un fichier CSV avec les Element IDs et quantités (séparateur : point-virgule) :

```csv
element_id;quantity
4211221;1
4585493;2
4211412;4
```

Les Element IDs se trouvent dans les manuels LEGO, à côté de chaque pièce dans la liste d'inventaire.

### Lancer la conversion

```bash
python3 lego_to_bricklink.py input.csv output.xml
```

### Exemple

```bash
$ python3 lego_to_bricklink.py missing_parts.csv wanted_list.xml

Reading missing_parts.csv...
Found 40 unique element IDs

Querying BrickLink API...
----------------------------------------------------------------------
Element ID   Part No      Color    Qty    Status
----------------------------------------------------------------------
302223       3022         7        1      OK
306226       3062         11       1      OK
4211221      3660         88       1      OK
...
----------------------------------------------------------------------
Success: 40 | Errors: 0

XML saved to: wanted_list.xml
Total parts: 40
Total pieces: 61
```

### Importer sur BrickLink

1. Va sur [BrickLink.com](https://www.bricklink.com)
2. **Want > Upload** ou directement : https://www.bricklink.com/v2/wanted/upload.page
3. Sélectionne ton fichier XML
4. Importe !

## Structure du projet

```
lego-to-bricklink/
├── lego_to_bricklink.py   # Script principal
├── example_parts.csv      # Exemple de fichier CSV
├── .env.example           # Template pour les variables d'environnement
├── .gitignore
├── README.md              # Documentation anglaise
└── README.fr.md           # Documentation française
```

## Comment trouver les Element IDs

Les Element IDs sont les numéros à 6-7 chiffres que tu trouves :

- Dans les **manuels LEGO** (liste des pièces à la fin)
- Sur les **sachets de pièces** LEGO
- Sur le site LEGO dans les inventaires de sets

Exemple dans un manuel LEGO :
```
Pièce : Slope, Inverted 45 2 x 2
Element ID : 4211221
```

## API BrickLink

Ce script utilise l'endpoint `/item_mapping/{element_id}` de l'API BrickLink pour convertir les Element IDs LEGO en :
- **Part Number** BrickLink (ex : `3660`)
- **Color ID** BrickLink (ex : `88` = Reddish Brown)

Documentation API : https://www.bricklink.com/v3/api.page

## Licence

MIT License - Fais-en ce que tu veux !

## Contribuer

Les PRs sont les bienvenues ! Si tu trouves un bug ou veux ajouter une fonctionnalité :

1. Fork le repo
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit (`git commit -m 'Add ma feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvre une PR
