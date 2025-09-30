import os
import pandas as pd
from pymongo import MongoClient

# Récupère les variables d'environnement
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')
DB_NAME = 'healthcare'
COLLECTION_NAME = 'patients'
CSV_FILE = 'healthcare_dataset.csv'

# Récupère les mots de passe des nouveaux utilisateurs
ADMIN1_PASS = os.getenv('MONGO_ADMIN1_PASS')
ADMIN2_PASS = os.getenv('MONGO_ADMIN2_PASS')
EDITOR1_PASS = os.getenv('MONGO_EDITOR1_PASS')
EDITOR2_PASS = os.getenv('MONGO_EDITOR2_PASS')
READER1_PASS = os.getenv('MONGO_READER1_PASS')
READER2_PASS = os.getenv('MONGO_READER2_PASS')

def connect_to_mongo():
    """Établit la connexion à MongoDB."""
    try:
        print("Création du client de connexion")
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PASS,
            authSource='admin' # Authentification avec l'utilisateur admin
        )
        print("Fait ✅ \n")
        return client
    except Exception as e:
        print(f"Erreur de connexion à MongoDB: {e}")
        return None

def setup_users_and_roles(client):
    """Crée les rôles et les utilisateurs spécifiés."""
    db = client[DB_NAME]

    # Création rôles utilisateur
    roles_to_create = [
        {
            "role": "admin_role",
            "privileges": [
                {"resource": {"db": DB_NAME, "collection": ""}, "actions": ["find", "insert", "update", "remove"]}
            ],
            "description": "Rôle pour les administrateurs de la base de données healthcare."
        },
        {
            "role": "editor_role",
            "privileges": [
                {"resource": {"db": DB_NAME, "collection": COLLECTION_NAME}, "actions": ["insert", "update", "remove"]}
            ],
            "description": "Rôle pour les éditeurs de la collection patients."
        },
        {
            "role": "reader_role",
            "privileges": [
                {"resource": {"db": DB_NAME, "collection": COLLECTION_NAME}, "actions": ["find"]}
            ],
            "description": "Rôle pour les lecteurs de la collection patients."
        }
    ]


    print("Création des rôles...")
    for role_info in roles_to_create:
        role_name = role_info["role"]
        db.command("createRole", role_name, privileges=role_info["privileges"], roles=[])
        print(f"Rôle '{role_name}' créé avec succès ✅")

    print("Création des rôles fait ✅ \n")
    
    # Création utilisateurs
    users_to_create = [
        {"user": "admin1", "pwd": ADMIN1_PASS, "roles": [{"role": "admin_role", "db": DB_NAME}]},
        {"user": "admin2", "pwd": ADMIN2_PASS, "roles": [{"role": "admin_role", "db": DB_NAME}]},
        {"user": "editor1", "pwd": EDITOR1_PASS, "roles": [{"role": "editor_role", "db": DB_NAME}]},
        {"user": "editor2", "pwd": EDITOR2_PASS, "roles": [{"role": "editor_role", "db": DB_NAME}]},
        {"user": "reader1", "pwd": READER1_PASS, "roles": [{"role": "reader_role", "db": DB_NAME}]},
        {"user": "reader2", "pwd": READER2_PASS, "roles": [{"role": "reader_role", "db": DB_NAME}]},
    ]

    for user_info in users_to_create:
        user_name = user_info["user"]
        db.command("createUser", user_name, pwd=user_info["pwd"], roles=user_info["roles"])
        print(f"Utilisateur '{user_name}' créé avec succès! ✅")

    print("Création des utilisateurs fait ✅")


if __name__ == "__main__":
    
    print("Début d'execution de la migration")

    print("Importation des données de healthcare_dataset.csv...")
    df = pd.read_csv('healthcare_dataset.csv')
    print(f"Le fichier contient {len(df)} entrées avant traitement")
    print("Fait ✅ \n")
    
    print("Suppression des duplicats...")
    df.drop_duplicates(inplace=True)
    df_row_count = len(df)
    print(f"Le jeu de données contient {df_row_count} entrées après traitement")
    print("Fait ✅ \n")

    print("Capitalisation des noms...")
    df["Name"] = df["Name"].apply(lambda x: x.title())
    print("Fait ✅ \n")
    
    print("Conversion des données en record...")
    data = df.to_dict('records')
    print("Fait ✅ \n")

    print("Connexion au serveur MongoDB...")
    client = connect_to_mongo()
    
    if not client:
        raise Exception("Erreur lors de la connection à la BDD")
    else:
        print("Fait ✅ \n")

    print("Création des rôles et utilisateur...")
    setup_users_and_roles(client)
    print("Création des rôles et utilisateur fait✅ \n")

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    if collection.count_documents({}) > 0:
        print("La collection n'est pas vide. Suppression des données existantes...")
        collection.delete_many({})
        print("Fait ✅ \n")
    
    print("Insertion des données dans MongoDB...✅")
    collection.insert_many(data)
    print("Fait ✅ \n")

    cursor = collection.find().limit(5)
    inserted_count = collection.count_documents({})

    print(f"{inserted_count} / {df_row_count} entrés insérées")

    for i in range(5):
        print(cursor[i])

    print("✅La migration a été effectuée avec succès !✅")
    client.close()
    
    
