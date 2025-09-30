# oc_de_5

# Projet de Migration de Données : CSV vers MongoDB avec Docker

Ce projet met en place un pipeline simple pour migrer des données depuis un fichier CSV vers une base de données MongoDB. L'ensemble de l'environnement est orchestré à l'aide de Docker et Docker Compose, garantissant une installation et une exécution faciles et reproductibles.

Le script principal (`main.py`) ne se contente pas de transférer les données ; il configure également un ensemble de rôles et d'utilisateurs avec des permissions spécifiques au sein de la base de données MongoDB, instaurant ainsi une base de sécurité solide.

---

## 🚀 Utilisation

### Prérequis
* **Docker**
* **Docker Compose**

### Lancement
1.  Assurez-vous que le fichier source `healthcare_dataset.csv` est présent à la racine du projet.
2.  Ouvrez un terminal et exécutez la commande suivante :
    ```bash
    docker-compose up --build
    ```
Cette commande va construire l'image du service de migration  et démarrer les deux conteneurs. Une fois la migration terminée, le conteneur `data_migrator_healthcare` s'arrêtera, mais la base de données MongoDB restera active.

Pour arrêter et supprimer les conteneurs, utilisez :
```bash
docker-compose down
```

## ⚙️ Déroulement de l'Exécution

Lorsque vous lancez `docker-compose up`, voici les étapes qui s'enchaînent :

1.  **Orchestration Docker Compose** : Le fichier `docker-compose.yml` définit deux services principaux.
    * `mongodb` : Lance un conteneur basé sur l'image `mongo:latest`. Les identifiants de l'utilisateur root (`administratore` et `strongPassword!`) sont définis via des variables d'environnement. Un volume nommé `mongodb_data` est utilisé pour assurer la persistance des données.
    * `data_migrator` : Ce service dépend de `mongodb` et ne démarrera qu'une fois la base de données prête. Il est construit à partir du `Dockerfile` local.

2.  **Construction de l'Image du Migrator** : Docker utilise le `Dockerfile` pour construire l'image du service `data_migrator`.
    * Il part d'une image Python (`python:3.11-slim`).
    * Il copie le fichier `requirements.txt` et installe les dépendances nécessaires, à savoir `pymongo` et `pandas`.
    * Enfin, il copie le script `main.py` qui contient toute la logique de migration.

3.  **Exécution du Script `main.py`** : Une fois le conteneur `data_migrator_healthcare` lancé, le script `main.py` s'exécute et effectue les opérations suivantes :

    * **Lecture des Données** : Le script charge le fichier `healthcare_dataset.csv` dans un DataFrame Pandas. Un léger nettoyage est appliqué : les doublons sont supprimés et les noms sont standardisés (première lettre en majuscule).
    * **Connexion à MongoDB** : Il se connecte à l'instance MongoDB en utilisant les identifiants de l'utilisateur root (`MONGO_USER`, `MONGO_PASS`) fournis via les variables d'environnement.
    * **Configuration de la Sécurité** : Avant d'insérer les données, le script met en place une structure de contrôle d'accès :
        * **Création de Rôles** : Trois rôles personnalisés sont créés dans la base `healthcare` : `admin_role`, `editor_role`, et `reader_role`, chacun avec des privilèges spécifiques.
        * **Création d'Utilisateurs** : Six utilisateurs sont créés (`admin1`, `admin2`, `editor1`, `editor2`, `reader1`, `reader2`) et se voient assigner les rôles précédents. Leurs mots de passe sont également récupérés depuis les variables d'environnement.
    * **Migration des Données** :
        * Le script vérifie si la collection `patients` contient déjà des documents. Si c'est le cas, il la vide complètement (`delete_many({})`).
        * Les données du DataFrame Pandas sont converties en une liste de dictionnaires et insérées en masse (`insert_many(data)`) dans la collection `patients`.
    * **Vérification** : Pour confirmer que l'opération a réussi, le script affiche les 5 premiers documents de la collection dans les logs du conteneur et vérifie que le nombre d'entrées dans la base correspond bien au nombre initial après déduplication.
    * **Fin du Processus** : La connexion à la base de données est fermée (`client.close()`), le script se termine, et le conteneur `data_migrator_healthcare` s'arrête.
