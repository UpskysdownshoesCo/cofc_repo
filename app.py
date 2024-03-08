import os
import logging
import hashlib
from datetime import datetime


from flask import Flask, redirect, render_template, request, send_from_directory, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


from forms import LoginForm, Register, SendCertificates

from azure.identity import DefaultAzureCredential
from azure.identity.aio import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder



app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


credential = DefaultAzureCredential()
account_url = "https://cofcstorage.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url, credential = credential)

container_name = "test2"

try:
    container_client = blob_service_client.get_container_client(container = container_name)
    container_client.get_container_properties()
except Exception as e:
    container_client = blob_service_client.create_container(container_name)


# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# ############################################################################################

#graph stuff

import json

import requests
from msal import ConfidentialClientApplication



tenant_id = "1aface79-3d26-4db1-9064-8140a2ce020c"
client_id = "ff3620ec-629b-42d5-b240-3cf85addcf16"
client_secret = "._p8Q~u0P~p9c0u0samKPj3vod~3a61E1sx3qdlc"

msal_authority = f"https://login.microsoftonline.com/{tenant_id}"

msal_scope = ["https://graph.microsoft.com/.default"]

msal_app = ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=msal_authority,
)

result = msal_app.acquire_token_silent(
    scopes=msal_scope,
    account=None,
)

if not result:
    result = msal_app.acquire_token_for_client(scopes=msal_scope)

if "access_token" in result:
    access_token = result["access_token"]
else:
    raise Exception("No Access Token found")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

response = requests.get(
    url="https://graph.microsoft.com/v1.0/users",
    headers=headers,
)

print(json.dumps(response.json(), indent=4))










##################################################################################################

# The import must be done after db initialization due to circular import issue
from models import Restaurant, Review, Users, SendCertificatesModel

@app.route('/', methods=['GET'])
@csrf.exempt
def index():
    print('Request for index page received')
    # sender_email = get_user()
    return render_template('dash.html')

@app.route('/send', methods=['POST', 'GET'])
@csrf.exempt
def send():    
    form = SendCertificates(csrf_enabled=False)
    if form.validate_on_submit():
        new_entry = SendCertificatesModel(
                sender= "sender",
                recipient=form.recipient.data,
                po_number=form.po_number.data,
                batch_number=form.batch_number.data,
                part_number=form.part_number.data,
                assembly_number=form.assembly_number.data,
                manufacturing_country=form.manufacturing_country.data,
                reach_compliant=form.reach_compliant.data,
                hazardous=form.hazardous.data,
                material_expiry_date=form.material_expiry_date.data,
                additional_notes=form.additional_notes.data
                # Add more fields as necessary
            )
        db.session.add(new_entry)
        db.session.commit()  
        flash('Certificate data and files submitted successfully.')
        # Adjusted to handle multiple files
        file_keys = ['material_file', 'plating_file', 'manufacturing_file']  # The names of your file inputs
        for key in file_keys:
            if key not in request.files:
                flash(f"No file part for {key}")
                continue

            file = request.files[key]
            if file and file.filename:
                filename = file.filename
                blob_name = filename
                blob_client = container_client.get_blob_client(blob_name)

                # Upload the file to Azure Blob Storage
                try:
                    blob_client.upload_blob(file)
                except Exception as e:
                    logging.exception("An error occurred during file upload.")
                    flash("An error occurred during file upload.")
                    return redirect('/')  # Adjust as needed if you want to return to the form
        
        flash('Certificate data and files submitted successfully.')
        return redirect('/')  # Ensure this is the correct endpoint for your dashboard
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"Error in {fieldName}: {err}")
        return render_template('send.html', form=form)


@app.route('/upload_blob', methods=['POST'])
@csrf.exempt
def upload_blob():
    try:
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        blob_name = file.filename
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the file to Azure Blob Storage
        blob_client.upload_blob(file)

        flash('Certificate data submitted successfully.')
        return ''
    except Exception as e:
        logging.exception("An error occurred:")
        return "Internal Server Error"
        
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #if form.validate_on_submit():
        #Check email is valid format
        # if not emailCheck(form.email.data):
        #     flash('invlalid email address')
        # else:
    users = Users.query.all()
    input_password = form.password.data

    if input_password is not None:
        hashed_input_password = hashlib.sha256(input_password.encode("utf-8")).hexdigest()
        for user in users:
            if user.password == hashed_input_password:
                return redirect('/index')
           
    #for u in user:
        #Hash enetered password using sha-256 and compare to database to find users account.
        #hashed = hashlib.sha256(form.password.data.encode("utf-8")).hexdigest()
                
        #return redirect('/index')
    #else:
    flash('Couldnt find an account with those details')
    print('Couldnt find an account with those details')

    return render_template("new_login.html", form=form, title="Login")

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        db.session.add(review)
        db.session.commit()

    return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.restaurant == id)

        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)
if __name__ == '__main__':
    app.run(debug=True)
