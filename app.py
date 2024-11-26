from flask import Flask, render_template, redirect, url_for, flash,session, current_app, request
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from decimal import Decimal
import logging
from functools import wraps
import matplotlib
matplotlib.use('Agg')
from gestion_produit import Produit, Client, Commande
from forms import AddProductForm, AddClientForm, AddOrderForm, EditClientForm
import matplotlib.pyplot as plt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey' # Clef de cryptage
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Chemin vers ta base de données SQLite des utilisateurs
db = SQLAlchemy(app) # Création de l'instance de SQLAlchemy

#--------------création des decorateurs-----------------

logging.basicConfig(filename='user_actions.log', level=logging.INFO) # Configuration du logging
def log_action(func): # Création du decorateur
    @wraps(func) # Utilisation du decorateur
    def wrapper(*args, **kwargs): 
        user_id = request.cookies.get('user_id') 
        action = func.__name__ 
        logging.info(f"User ID: {user_id}, Action: {action}") 
        return func(*args, **kwargs) 
    return wrapper 


#------------------------Classe, Methodes et Routes pour accéder au site------------------------

# Création de la classe User
class User(db.Model): # Création de la classe User
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), unique=True, nullable=False) 
    password = db.Column(db.String(120), nullable=False) 

    def __repr__(self):
        return '<User %r>' % self.username 
    

# Création de la classe RegisterForm
class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])  # Champ de saisie pour le nom d'utilisateur
    password = PasswordField('Mot de passe', validators=[DataRequired()])   # Champ de saisie pour le mot de passe
    submit = SubmitField('S\'inscrire') # Bouton de soumission


# Création de la classe LoginForm
class LoginForm(FlaskForm): # Création de la classe LoginForm
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()]) # Champ de saisie pour le nom d'utilisateur
    password = PasswordField('Mot de passe', validators=[DataRequired()]) # Champ de saisie pour le mot de passe
    submit = SubmitField('Connexion') # Bouton de soumission


# Création de la fonction create_user
def create_user(username, password):
    user = User(username=username, password=password) # Création d'un nouvel utilisateur
    db.session.add(user)
    db.session.commit() # Sauvegarde des modifications

# Création de la fonction check_login
def check_login(username, password):# Création de la fonction check_login
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return True
    return False

# Création de la route '/' index
@app.route('/')
def index():
    user = session.get('user')
    if user:
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=None)

# Création de la route '/register'
@app.route('/register', methods=['GET', 'POST']) # Création de la route '/register'
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        create_user(username, password)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Création de la route '/login'
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if check_login(username, password):
            user = {'username': username}
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', form=form, error='Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if user:
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nom, description FROM produits ORDER BY id ASC LIMIT 5")  # Limite à 5 produits
            products_data = cursor.fetchall()

            static_images = ["pomme.jpg", "banane.webp", "tomate.webp", "salade.webp", "brocoli.webp"]
        
        # Crée une liste de dictionnaires pour les produits avec des images
        products = [
            {
                "image_url": static_images[i % len(static_images)],  # Associe les images en boucle
                "name": row[0],
                "description": row[1]
            }
            for i, row in enumerate(products_data)
        ]
        return render_template('dashboard.html', user=user, products=products)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

#------------------------Routes pour les produits------------------------


# Route pour ajouter un nouveau produit
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        # Créer un nouvel objet Produit avec les données du formulaire
        new_produit = Produit(
            nom=form.nom.data,
            prix=form.prix.data,
            description=form.description.data,
            stock=form.stock.data,
            type_produit=form.type_produit.data
        )
        new_produit.add_product()  # Appeler la méthode pour ajouter le produit dans la base de données
        #flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('list_produits'))

    return render_template('add_product.html', form=form)


# Route pour modifier un produit
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    produit = Produit()  # Créer une instance de la classe Produit
    produit_to_update = next((p for p in produit.get_products() if p.id == id), None)  # Trouver le produit à modifier
    
    if produit_to_update is None:
        flash('Produit non trouvé', 'danger')
        return redirect(url_for('list_produits'))

    form = AddProductForm(obj=produit_to_update)
    
    if form.validate_on_submit():
        # Convertir le prix en float si nécessaire
        prix = float(form.prix.data) if isinstance(form.prix.data, Decimal) else form.prix.data
        produit.update_product(id, form.nom.data, prix, form.description.data, form.stock.data, form.type_produit.data)
        #flash('Produit mis à jour avec succès!', 'success')
        return redirect(url_for('list_produits'))

    return render_template('edit_product.html', form=form, produit=produit_to_update)


# Route pour supprimer un produit
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    produit = Produit()  # Créer une instance de la classe Produit
    produit.delete_product(id)  # Appeler la méthode pour supprimer le produit de la base de données
    flash('Produit supprimé avec succès!', 'danger')
    return redirect(url_for('list_produits'))


# Route pour afficher la liste des produits
@app.route('/list', methods=['GET'])
def list_produits():
    type_produit = request.args.get('type_produit')  # Récupère le type sélectionné depuis l'URL
    produit = Produit()  # Crée une instance de la classe Produit
    
    if type_produit and type_produit != "":
        produits = produit.filter_products_by_type(type_produit)  # Filtre par type
    else:
        produits = produit.get_products()  # Affiche tous les produits
    
    types_produits = [
        'Fruits et légumes', 'Produits laitiers', 'Viandes et protéines', 
        'Produits de boulangerie', 'Céréales et grains', 'Conserves et produits secs', 
        'Condiments et épices', 'Boissons', 'Produits surgelés', 
        'Snacks et confiseries', 'Produits non alimentaires'
    ]
    
    return render_template('list_produits.html', produits=produits, types_produits=types_produits, selected_type=type_produit)



# ----------------------- Routes pour les Clients -----------------------
# Ajouter un client
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    form = AddClientForm()
    if form.validate_on_submit():
        print("Formulaire validé :")
        print(f"Nom: {form.nom.data}, Email: {form.email.data}, Adresse: {form.adresse.data}")
        client = Client(
            nom=form.nom.data,
            email=form.email.data,
            adresse=form.adresse.data
        )
        client.add_client()
        return redirect(url_for('list_clients'))
    else:
        print("Erreur de validation : ", form.errors)
    return render_template('add_client.html', form=form)


# Route d'édition du client
@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client_instance = Client("", "", "")  # Crée une instance de Client
    client_data = client_instance.get_client_by_id(client_id)  # Appelle la méthode pour récupérer un client par ID

    if not client_data:
        return "Client non trouvé", 404  # Si le client n'existe pas dans la base de données

    # Convertir les données du client en un dictionnaire
    client_dict = {
        'id': client_id,
        'nom': client_data[1],
        'email': client_data[2],
        'adresse': client_data[3]
    }

    # Initialiser le formulaire avec les données actuelles du client
    form = EditClientForm(data=client_dict)

    if form.validate_on_submit():
        # Créer une instance de Client avec les nouvelles données
        client = Client(id=client_id,
                        nom=form.nom.data,
                        email=form.email.data,
                        adresse=form.adresse.data)
        
        # Mettre à jour le client dans la base de données
        client.update_client(client_id)

        # Rediriger vers la liste des clients
        return redirect(url_for('list_clients'))

    # Si la méthode est GET, ou si le formulaire n'est pas valide, afficher le formulaire avec les données actuelles
    return render_template('edit_client.html', form=form, client_id=client_id)



# Supprimer un client
@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    try:
        # Créez une instance de la classe Client avec l'ID du client à supprimer
        client = Client(nom=None, email=None, adresse=None)  # Utilisez des valeurs par défaut pour les autres attributs
        client.delete_client(client_id)  # Appelez la méthode d'instance delete_client
        flash("Client supprimé avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression du client : {str(e)}", "danger")
    
    return redirect(url_for('list_clients'))  # Redirige vers la liste des clients


# Afficher la liste des clients
@app.route('/list_clients')
def list_clients():
    client_instance = Client()  # Créer une instance de Client
    clients = client_instance.get_clients()  # Appeler la méthode d'instance
    return render_template('list_clients.html', clients=clients)




# ----------------------- Routes pour les Commandes -----------------------

@app.route('/commandes')
def list_commandes():
    commande = Commande(client_id=None, produit_id=None, quantite=None)
    orders = commande.get_commandes_with_details()
    clients = Client("", "", "")
    clients = clients.get_clients()
    produits = Produit()
    produits = produits.get_products()
    
    return render_template('list_commandes.html', 
                         orders=orders,
                         clients=clients, 
                         produits=produits)


@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    form = AddOrderForm()
    client = Client()
    produit = Produit()
    
    clients = client.get_clients()
    produits = produit.get_products()
    
    # Vérifiez si des clients ou produits sont disponibles
    if not clients:
        flash("Aucun client disponible pour passer une commande.", 'danger')
        return redirect(url_for('list_commandes'))
    if not produits:
        flash("Aucun produit disponible pour passer une commande.", 'danger')
        return redirect(url_for('list_commandes'))
    
    # Générer les choix pour le formulaire
    form.client_id.choices = [(c[0], c[1]) for c in clients]
    form.produit_id.choices = [(p.id, p.nom) for p in produits]

    if form.validate_on_submit():
        commande = Commande(
            client_id=form.client_id.data,
            produit_id=form.produit_id.data,
            quantite=form.quantite.data
        )
        try:
            commande.add_commande()
            flash('Commande ajoutée avec succès.', 'success')
            return redirect(url_for('list_commandes'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('add_order.html', form=form)

# Création de la route '/edit_order/<int:order_id>'
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    form = AddOrderForm()
    
    clients = Client("", "", "")
    clients_list = clients.get_clients()
    form.client_id.choices = [(c[0], c[1]) for c in clients_list]
    
    produits = Produit()
    produits_list = produits.get_products()
    form.produit_id.choices = [(p.id, p.nom) for p in produits_list]
    
    commande = Commande()
    current_order = commande.get_order_by_id(order_id)
    
    if request.method == 'GET':
        # Pre-fill the form with current values
        form.client_id.data = current_order[1]  
        form.produit_id.data = current_order[2] 
        form.quantite.data = current_order[3] 
    
    if form.validate_on_submit():
        try:
            updated_order = Commande(
                client_id=form.client_id.data,
                produit_id=form.produit_id.data,
                quantite=form.quantite.data
            )
            updated_order.update_commande(order_id)
            flash('Commande mise à jour avec succès.', 'success')
            return redirect(url_for('list_commandes'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('edit_order.html', form=form, order_id=order_id)

# Création de la route '/delete_order/<int:order_id>'
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    try:
        commande = Commande()
        order = commande.get_order_by_id(order_id)
        if not order:
            flash('Commande non trouvée.', 'error')
            return redirect(url_for('list_commandes'))

        produit = Produit()
        product = next((p for p in produit.get_products() if p.id == order[2]), None)  
        if product:
            product.stock += order[3]  
            produit.update_product(
                produit_id=product.id,
                nom=product.nom,
                prix=product.prix,
                description=product.description,
                stock=product.stock,
                type_produit=product.type_produit
            )

        commande.delete_commande(order_id)

        flash('Commande supprimée avec succès.', 'success')
    except Exception as e:
        flash(f"Erreur lors de la suppression de la commande : {str(e)}", 'error')

    return redirect(url_for('list_commandes'))
 


#-----------------------Methodes et Routes pour les Graphiques -----------------------

# Création de la fonction pour générer le graphique circulaire
def generate_pie_chart(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
        cursor = conn.cursor()

        # Requête pour récupérer les données des types de produits
        cursor.execute('SELECT type_produit, COUNT(*) FROM produits GROUP BY type_produit')
        rows = cursor.fetchall()

        # Extraire les types de produits et leurs comptes
        types = [row[0] for row in rows]
        counts = [row[1] for row in rows]

        # Créer le graphique circulaire
        plt.figure(figsize=(8, 6))  # Taille du graphique
        plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Assurer que le graphique est un cercle
        plt.title('Répartition des Produits par Type')

        # Sauvegarder le graphique dans un fichier
        plt.savefig('static/product_share.png', transparent=True)
        plt.close()

# Création de la fonction pour générer le graphique en barres
def generate_category_bar_chart(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
        cursor = conn.cursor()

        # Requête pour récupérer les données des catégories
        cursor.execute('SELECT stock, COUNT(*) FROM produits GROUP BY stock ORDER BY COUNT(*) DESC LIMIT 3')
        rows = cursor.fetchall()

        # Extraire les noms de catégories et les comptes
        categories = [row[0] for row in rows]
        counts = [row[1] for row in rows]

        # Créer le graphique en barres
        plt.bar(categories, counts)
        plt.xlabel('Catégorie')
        plt.ylabel('Nombre de Produits')
        plt.title('Top 5 des Catégories par Nombre de Produits')

        # Sauvegarder le graphique dans un fichier
        plt.savefig('static/category_bar_chart.png', transparent=True)
        plt.close()

# Création de la fonction pour générer l'histogramme
def generate_price_histogram(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
        cursor = conn.cursor()

        # Requête pour récupérer les données de prix
        cursor.execute('SELECT prix FROM produits')
        rows = cursor.fetchall()

        # Extraire les valeurs des prix
        prices = [row[0] for row in rows]

        # Créer l'histogramme
        plt.hist(prices, bins=50)
        plt.xlabel('Prix')
        plt.ylabel('Fréquence')
        plt.title('Répartition des Prix des Produits')

        # Sauvegarder le graphique dans un fichier
        plt.savefig('static/price_histogram.png', transparent=True)
        plt.close()

# Création de la route pour afficher les graphiques
@app.route('/graph')
def graph():
    # Générer les graphiques à chaque chargement de la page
    generate_pie_chart(current_app)
    generate_category_bar_chart(current_app)
    generate_price_histogram(current_app)

    # Rendre la page avec les graphiques
    return render_template('graph.html', 
        product_share='static/product_share.png', 
        category_bar_chart='static/category_bar_chart.png', 
        price_histogram='static/price_histogram.png')

if __name__ == '__main__':

    # Initialize the database by pushing the app context
    app.app_context().push()
    db.create_all()
    app.run(debug=True)

