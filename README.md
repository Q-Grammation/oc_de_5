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
