import sqlite3

#--------------------Class Produit--------------------#

class Produit:
    def __init__(self, nom="", prix=0.0, description="", stock=0, type_produit="", id=None):
        # Initialise les attributs d'un produit
        self.nom = nom  
        self.prix = prix  
        self.description = description  
        self.stock = stock  
        self.type_produit = type_produit  
        self.id = id 

#methode pour créer la table des produits
    def create_table_product(self):
        try:
            with sqlite3.connect("app_database.db") as connection:  
                cursor = connection.cursor() 
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT NOT NULL,  
                        prix REAL NOT NULL,  
                        description TEXT NOT NULL,  
                        stock INTEGER NOT NULL,  
                        type_produit TEXT NOT NULL  
                    )
                """)
        except sqlite3.Error as e:
            # Gestion des erreurs SQL
            print(f"Erreur lors de la création de la table : {e}")

    #methode pour verifier l'existence d'un produit
    def exists(self, produit_id):
        # Vérifie si un produit avec l'ID donné existe dans la base
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
            cursor = connection.cursor()  # Création d'un curseur
            cursor.execute("SELECT 1 FROM produits WHERE id = ?", (produit_id,))  # Requête pour vérifier l'existence
            result = cursor.fetchone()  # Récupère le premier résultat (s'il existe)
            return result is not None 

    def add_product(self):
        # Ajoute un produit dans la base de données
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
                cursor = connection.cursor()  # Création d'un curseur
                cursor.execute("""
                    INSERT INTO produits (nom, prix, description, stock, type_produit)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.nom, format(self.prix, ".2f"), self.description, self.stock, self.type_produit))  # Insertion des valeurs
                self.id = cursor.lastrowid  # Récupération de l'ID généré
                connection.commit()  # Sauvegarde des modifications
        except sqlite3.Error as e:
            # Gestion des erreurs SQL
            print(f"Erreur lors de l'ajout du produit : {e}")

    def get_products(self):
        # Récupère tous les produits de la base de données
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
                cursor = connection.cursor()  # Création d'un curseur
                cursor.execute("SELECT * FROM produits")  # Requête pour récupérer tous les produits
                produits = cursor.fetchall()  # Récupère toutes les lignes de la table
                # Retourne une liste d'instances `Produit` créée à partir des données récupérées
                return [Produit(nom=row[1], prix=row[2], description=row[3], stock=row[4], type_produit=row[5], id=row[0]) for row in produits]
        except sqlite3.Error as e:
            # Gestion des erreurs SQL
            print(f"Erreur lors de la récupération des produits : {e}")
            return []

    def filter_products_by_type(self, type_produit):
        # Filtre les produits par type
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
            cursor = connection.cursor()  # Création d'un curseur
            cursor.execute("""
                SELECT id, nom, prix, type_produit, description, stock
                FROM produits
                WHERE type_produit = ?
            """, (type_produit,))  # Requête pour sélectionner les produits par type
            rows = cursor.fetchall()  # Récupère les résultats
            # Transforme les résultats en une liste de dictionnaires
            columns = ['id', 'nom', 'prix', 'type_produit', 'description', 'stock']
            produits = [dict(zip(columns, row)) for row in rows]
            return produits

    def update_product(self, produit_id, nom, prix, description, stock, type_produit):
        # Met à jour un produit dans la base de données
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
                cursor = connection.cursor()  # Création d'un curseur
                cursor.execute("""
                    UPDATE produits
                    SET nom = ?, prix = ?, description = ?, stock = ?, type_produit = ?
                    WHERE id = ?
                """, (nom, prix, description, stock, type_produit, produit_id))  # Requête de mise à jour
                connection.commit()  # Sauvegarde des modifications
                print(f"Produit avec ID {produit_id} mis à jour.")
        except sqlite3.Error as e:
            # Gestion des erreurs SQL
            print(f"Erreur lors de la mise à jour du produit : {e}")

    def delete_product(self, product_id):
        # Supprime un produit de la base de données
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
                cursor = connection.cursor()  # Création d'un curseur
                cursor.execute("DELETE FROM produits WHERE id = ?", (product_id,))  # Requête de suppression
                connection.commit()  # Sauvegarde des modifications
        except sqlite3.Error as e:
            # Gestion des erreurs SQL
            print(f"Erreur lors de la suppression du produit : {e}")

# Exemple d'utilisation : Création de la table des produits
produit = Produit()
produit.create_table_product()


#--------------------Class Client--------------------#

class Client:
    def __init__(self, id=None, nom=None, email=None, adresse=None):
        # Initialisation d'une instance de Client avec des attributs par défaut
        self.id = id  # ID du client (peut être None pour un nouveau client)
        self.nom = nom  # Nom du client
        self.email = email  # Email du client
        self.adresse = adresse  # Adresse du client

    def create_table_client(self):
        with sqlite3.connect("app_database.db") as connection:  
            cursor = connection.cursor()  # Création d'un curseur pour exécuter les requêtes
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    nom TEXT NOT NULL,  
                    email TEXT NOT NULL, 
                    adresse TEXT NOT NULL 
                )
            """)  # Requête SQL pour créer la table si elle n'existe pas
            connection.commit()  # Validation des changements

    def exists(self, client_id):
        # Méthode pour vérifier si un client avec un ID donné existe
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base de données
            cursor = connection.cursor()  # Création du curseur
            cursor.execute("SELECT 1 FROM clients WHERE id = ?", (client_id,))  # Vérification de l'existence
            result = cursor.fetchone()  # Récupération du résultat
            return result is not None  # Retourne True si le client existe, False sinon
        
    def add_client(self):
        # Méthode pour ajouter un nouveau client dans la base de données
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base
                cursor = connection.cursor()  # Création du curseur
                cursor.execute("""
                    INSERT INTO clients (nom, email, adresse) 
                    VALUES (?, ?, ?)
                """, (self.nom, self.email, self.adresse))  # Insertion des données du client
                connection.commit()  # Validation de l'opération
        except sqlite3.Error as e:
            connection.close()  # Fermeture de la connexion en cas d'erreur

    def get_clients(self):
        # Méthode pour récupérer tous les clients depuis la base de données
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base
            cursor = connection.cursor()  # Création du curseur
            cursor.execute("SELECT id, nom, email FROM clients")  # Requête pour récupérer les clients
            return cursor.fetchall()  # Retourne une liste de tuples avec les clients

    def get_client_by_id(self, client_id):
        # Méthode pour récupérer un client spécifique par son ID
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base
            cursor = connection.cursor()  # Création du curseur
            cursor.execute("SELECT id, nom, email, adresse FROM clients WHERE id = ?", (client_id,))  # Requête SQL
            return cursor.fetchone()  # Retourne les informations du client ou None s'il n'existe pas

    def update_client(self, client_id):
        # Méthode pour mettre à jour les informations d'un client existant
        with sqlite3.connect("app_database.db") as connection:  # Connexion à la base
            cursor = connection.cursor()  # Création du curseur
            cursor.execute("""
                UPDATE clients
                SET nom = ?, email = ?, adresse = ?
                WHERE id = ?
            """, (self.nom, self.email, self.adresse, client_id))  # Mise à jour des données du client
            connection.commit()  # Validation des changements

    def delete_client(self, client_id):
        # Méthode pour supprimer un client par son ID
        try:
            with sqlite3.connect("app_database.db") as connection:  # Connexion à la base
                cursor = connection.cursor()  # Création du curseur
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))  # Suppression du client
                connection.commit()  # Validation de l'opération
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du client : {str(e)}")  # Affichage d'une erreur si elle se produit

# Création d'une instance de la classe Client
client = Client()
# Appel de la méthode pour créer la table clients (si elle n'existe pas)
client.create_table_client()


#--------------------Class Commande--------------------#

class Commande:
    def __init__(self, client_id=0, produit_id=0, quantite=0):
        self.client_id = client_id
        self.produit_id = produit_id
        self.quantite = quantite

    def create_table_commande(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    produit_id INTEGER NOT NULL,
                    quantite INTEGER NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (produit_id) REFERENCES produits (id)
                )
            """)
            connection.commit()

    def add_commande(self):
        produit = Produit()
        if not produit.exists(self.produit_id):
            raise ValueError("Le produit n'existe pas.")
        if not client.exists(self.client_id):
            raise ValueError("Le client n'existe pas.")
        
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO commandes (client_id, produit_id, quantite)
                VALUES (?, ?, ?)
            """, (self.client_id, self.produit_id, self.quantite))
            connection.commit()

    def get_commandes(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM commandes")
            commandes = cursor.fetchall()
            return commandes

    def get_commandes_with_details(self):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT c.id, cl.nom, p.nom, c.quantite
                    FROM commandes c
                    JOIN clients cl ON c.client_id = cl.id
                    JOIN produits p ON c.produit_id = p.id
                """)
                orders = cursor.fetchall()
                return orders
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des commandes: {e}")
            return []

    def get_order_by_id(self, order_id):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT id, client_id, produit_id, quantite
                    FROM commandes
                    WHERE id = ?
                """, (order_id,))
                order = cursor.fetchone()
                return order
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de la commande: {e}")
            return None

    def update_commande(self, commande_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE commandes
                SET client_id = ?, produit_id = ?, quantite = ?
                WHERE id = ?
            """, (self.client_id, self.produit_id, self.quantite, commande_id))
            connection.commit()

    def delete_commande(self, commande_id):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM commandes WHERE id = ?", (commande_id,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de la commande : {str(e)}")


commande = Commande()
commande.create_table_commande()