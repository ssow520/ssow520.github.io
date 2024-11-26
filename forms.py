from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, IntegerField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Email, ValidationError
from gestion_produit import Client, Produit


#-------------class add form produit------------
class AddProductForm(FlaskForm):
    nom = StringField('Nom du produit', validators=[DataRequired(), Length(max=50)])  
    # Champ pour saisir le prix avec validation numérique et précision de 2 décimales
    prix = DecimalField('Prix', validators=[DataRequired(), NumberRange(min=0)], places=2)  
    # Champ pour une description avec validation de longueur maximale
    description = TextAreaField('Description', validators=[Length(max=200)])  
    # Champ pour le stock avec une validation pour garantir un nombre entier positif
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])  
    # Liste déroulante pour sélectionner un type de produit, avec des choix prédéfinis
    type_produit = SelectField('Type de produit', choices=[
        ('Fruits et légumes', 'Fruits et légumes'),
        ('Produits laitiers', 'Produits laitiers'),
        ('Viandes et protéines', 'Viandes et protéines'),
        ('Produits de boulangerie', 'Produits de boulangerie'),
        ('Céréales et grains', 'Céréales et grains'),
        ('Conserves et produits secs', 'Conserves et produits secs'),
        ('Condiments et épices', 'Condiments et épices'),
        ('Boissons', 'Boissons'),
        ('Produits surgelés', 'Produits surgelés'),
        ('Snacks et confiseries', 'Snacks et confiseries'),
        ('Produits non alimentaires', 'Produits non alimentaires')
    ], validators=[DataRequired()])  # Validation pour s'assurer qu'une option est sélectionnée
    # Bouton de soumission pour le formulaire
    submit = SubmitField('Effectuer')

#-------------class add form client------------
class AddClientForm(FlaskForm):
    # Champ pour le nom du client, obligatoire
    nom = StringField('Nom du client', validators=[DataRequired()])  
    # Champ pour l'email du client avec validation de format
    email = EmailField('Email', validators=[DataRequired(), Email()])  
    # Champ pour l'adresse du client, obligatoire
    adresse = StringField('Adresse', validators=[DataRequired()])  
    # Bouton de soumission pour ajouter un client
    submit = SubmitField('Ajouter')

#-------------Edit Client------------
class EditClientForm(FlaskForm):
    # Champ pour modifier le nom du client, obligatoire
    nom = StringField('Nom du client', validators=[DataRequired()])  
    # Champ pour modifier l'email avec validation de format
    email = EmailField('Email', validators=[DataRequired(), Email()])  
    # Champ pour modifier l'adresse, obligatoire
    adresse = StringField('Adresse', validators=[DataRequired()])  
    # Bouton de soumission pour enregistrer les modifications
    submit = SubmitField('Modifier')

#-------------class add form commande------------
class AddOrderForm(FlaskForm):
    # Liste déroulante pour sélectionner un client par ID (converti en entier)
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])  
    # Liste déroulante pour sélectionner un produit par ID (converti en entier)
    produit_id = SelectField('Produit', coerce=int, validators=[DataRequired()])  
    # Champ pour indiquer la quantité de produit commandée, avec validation pour être un entier >= 1
    quantite = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=1)])  
    # Bouton de soumission pour valider la commande
    submit = SubmitField('Effectuer')

    def validate_client_id(self, field):
        # Méthode pour valider que l'ID du client existe dans la base de données
        client = Client()  # Instanciation de la classe `Client`
        if not client.exists(field.data):  # Vérifie si le client avec l'ID donné n'existe pas
            raise ValidationError("Le client sélectionné n'existe pas.")  # Lève une erreur si le client est introuvable

    def validate_produit_id(self, field):
        # Méthode pour valider que l'ID du produit existe dans la base de données
        produit = Produit()  # Instanciation de la classe `Produit`
        if not produit.exists(field.data):  # Vérifie si le produit avec l'ID donné n'existe pas
            raise ValidationError('Le produit sélectionné n\'existe pas.')  # Lève une erreur si le produit est introuvable