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
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PASS,
            authSource='admin' # Authentification avec l'utilisateur admin
        )
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

    for role_info in roles_to_create:
        role_name = role_info["role"]
        db.command("createRole", role_name, privileges=role_info["privileges"], roles=[])
        print(f"Rôle '{role_name}' créé avec succès.")
    
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
        print(f"Utilisateur '{user_name}' créé avec succès.")


if __name__ == "__main__":
    
    df = pd.read_csv('healthcare_dataset.csv')
    
    df.drop_duplicates(inplace=True)
    df["Name"] = df["Name"].apply(lambda x: x.title())
    
    data = df.to_dict('records')

    client = connect_to_mongo()
    
    if not client:
        raise Exception("Erreur lors de la connection à la BDD")

    setup_users_and_roles(client)

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    if collection.count_documents({}) > 0:
        print("La collection n'est pas vide. Suppression des données existantes...")
        collection.delete_many({})
    
    collection.insert_many(data)
    cursor = collection.find().limit(5)

    for i in range(5):
        print(cursor[i])

    client.close()
    
    