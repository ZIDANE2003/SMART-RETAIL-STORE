from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_login import current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '9f998c14028f209b9381c2e40c6b1ba7'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Your list of products
product_names = [
    '5050_Britannia', '7up', '7up_Can', 'Agni_Tea', 'Amul_Butter', 'Amul_Cheese', 'Amul_Cream', 'Amul_Ghee',
    'Amul_Gold', 'Amul_Kool', 'Amul_Lassi', 'Amul_Masti', 'Amul_Pro', 'Amul_Taaza', 'Amulya', 'Anik_Ghee',
    'Annapurna_Ghee', 'AppyFizz', 'BNatural', 'Bambino', 'BestFarms', 'Bourbon_Biscuit', 'Bournvita',
    'Britannia_Cheese', 'Britannia_Lassi', 'Catch', 'Cavins', 'Chings_Noodle', 'ChocoPie', 'Chocos_Kellogs',
    'Chutney_Chings', 'Chutney_Dabur', 'Cocacola', 'Cocacola_Can', 'CoconutWater_Paperboat', 'CoconutWater_Real',
    'Coffee_Nescafe', 'Comfort', 'Complan', 'CornFlakes_Aarambh', 'CornFlakes_Bagrrys', 'CornFlakes_Kellogs',
    'Daawat_Brown', 'Daawat_Devaaya', 'Daawat_Rice', 'DarkFantasy', 'DarkFantasy_Biscuit', 'Delicious', 'DietCoke',
    'Domex', 'Dove_Soap', 'Enzo', 'Everest', 'Fanta', 'Fiama_Soap', 'Fortune_Refined', 'Fortune_Rice', 'Frooti',
    'GluconD', 'Go_Cheese', 'GoodDay_Britannia', 'GoodLife', 'GoodLife_Rice', 'Govardhan_Ghee', 'HOrlicks', 'Henko',
    'Hersheys_ChocolateShake', 'Hersheys_Milkshake', 'Honey_Dabur', 'Honey_HealthyLife', 'Honey_Himalaya',
    'Honey_Patanjali', 'Honey_Suffola', 'IndiaGate_BrownRice', 'IndiaGate_Dubar', 'IndiaGate_Rice', 'Jubilee_Rice',
    'Kaffe', 'Ketchup_Kissan', 'Ketchup_Maggi', 'KrackJack_Parle', 'Lays', 'Lipton', 'Lizol', 'MIlkyMist_Cheese',
    'MTR', 'Maaza', 'Madhusudan_Ghee', 'Magg', 'Maggi', 'MarieGold_Britannia', 'Mayo_DelMonte', 'Mayo_DrOetker',
    'Mayo_Wingreens', 'McVities', 'Milkbikies', 'Milkmaid', 'MilkyMist_CheeseSlices', 'Mirinda', 'MomsMagic',
    'Monaco_Parle', 'Monster', 'Muesli_Aarambh', 'Muesli_Bagrrys', 'Muesli_Kellogs', 'Namkeen', 'Nescafe', 'Nutella',
    'Nutralite', 'NutriChoice_Britannia', 'Oats_Aarambh', 'Oats_Bagrrys', 'Oats_Suffola', 'Oats_Tata',
    'OrganicIndia_Tea', 'Osom_Paneer', 'Paperboat', 'Paras_Ghee', 'Parle-G_Parle', 'Patanjali_Ghee',
    'PeanutButter_DiSano', 'PeanutButter_Sundrop', 'Pears_Soap', 'Pepsi', 'Pepsi_Can', 'Pickle_Mothers',
    'Pickle_Sachet_Mothers', 'Pringles', 'Raw', 'Raw_CoconutWater', 'Real', 'Real_Active', 'Real_Guava', 'RedBull',
    'RedLabel', 'RefinedOil', 'Revive', 'Rock_Salt', 'Roohafza', 'Rusk_Parle', 'Santoor_Soap', 'Shampoo', 'Slice',
    'SnacTac', 'Soda_Kinley', 'Sofit_SoyaMilk', 'Sprite', 'Sprite_Can', 'Sting', 'Storia', 'Storia_Shake',
    'Sunfeast_ChocolateDrink', 'Sunfeast_MangoeDrink', 'Sunfeast_StrawberryDrink', 'SurfExcel', 'Taaza', 'TajMahal',
    'Tang', 'Tata_Gold', 'Tata_Premium', 'Tata_Salt', 'ThumpsUp', 'ThumpsUp_Can', 'Tide', 'Tiger_Britannia',
    'Toothpaste_Colgate', 'Toothpaste_Dabur', 'Toothpaste_Pepsodent', 'Toothpaste_Sensodine', 'Tropicana',
    'Water_Kinley', 'Weikfield', 'WinkinCow_Chocolate', 'WinkinCow_LAssi', 'Yeah', 'p'
]

# Create a DataFrame from the product names
data = {'product': product_names}
df = pd.DataFrame(data)

# Create a product profile using TF-IDF representation
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
product_profiles = tfidf_vectorizer.fit_transform(df['product'])

# Calculate similarity between products
cosine_similarities = linear_kernel(product_profiles, product_profiles)

# Function to get recommendations based on user's purchase history
def get_recommendations_for_user(username, product_profiles, cosine_similarities, df):
    user_history = customers.get(username, {}).get('history', [])
    user_history_lower = [product.lower() for product in user_history]
    user_profile = tfidf_vectorizer.transform(user_history_lower)
    
    # Calculate similarity between user's profile and product profiles
    user_product_similarity = linear_kernel(user_profile, product_profiles).flatten()
    
    # Sort products by similarity
    similar_products_indices = user_product_similarity.argsort()[::-1]
    
    # Exclude already purchased products and ensure the index is within bounds
    recommendations = [
        {'name': df['product'].iloc[i]}
        for i in similar_products_indices 
        if i < len(df) and df['product'].iloc[i].lower() not in user_history_lower
    ]

    # Add offers to the recommendations based on product categories (customize as needed)
    for rec in recommendations:
        category = rec['name'].split('_')[-1]  # Assuming categories are in the product names
        if category.lower() in ['biscuit', 'snack', 'chocolate']:
            rec['offer'] = '20% off'
        elif category.lower() in ['tea', 'coffee']:
            rec['offer'] = '15% off'
        else:
            rec['offer'] = '10% off'

    return recommendations

# Simulated customer data with usernames and passwords
customers = {
    'piyush': {'password': 'password123', 'history': ['7up', 'Bournvita']},
    'benson': {'password': 'password456', 'history': ['Sprite', 'Lays']},

    'dastur123': {'password': 'dastur', 'history': ['TajMahal', 'Sunfeast_MangoeDrink','Pickle_Sachet_Mothers', 'Pringles', 'Raw', 'Raw_CoconutWater', 'Real', 'Real_Active', 'Real_Guava', 'RedBull',
    'RedLabel', 'RefinedOil', 'Revive', 'Rock_Salt', 'Roohafza', 'Rusk_Parle', 'Santoor_Soap', 'Shampoo', 'Slice',
    'SnacTac', 'Soda_Kinley', 'Sofit_SoyaMilk', 'Sprite', 'Sprite_Can', 'Sting', 'Storia', 'Storia_Shake',
    'Sunfeast_ChocolateDrink', 'Sunfeast_MangoeDrink', 'Sunfeast_StrawberryDrink', 'SurfExcel', 'Taaza', 'TajMahal',
    'Tang', 'Tata_Gold', 'Tata_Premium', 'Tata_Salt', 'ThumpsUp', 'ThumpsUp_Can',]},

     'piyushwagh': {'password': 'piyush', 'history': ['TajMahal', 'Sunfeast_MangoeDrink','Pickle_Sachet_Mothers', 'Pringles', 'Raw', 'Raw_CoconutWater', 'Real', 'Real_Active', 'Real_Guava', 'RedBull',
    'RedLabel', 'RefinedOil', 'Revive', 'Rock_Salt', 'Roohafza', 'Rusk_Parle', 'Santoor_Soap', 'Shampoo', 'Slice',
    'SnacTac', 'Soda_Kinley', 'Sofit_SoyaMilk', 'Sprite', 'Sprite_Can', 'Sting']},

     'john_doe': {'password': 'john', 'history': ['TajMahal', 'Bournvita', 'Frooti' 'Rusk_Parle', 'Santoor_Soap', 'Shampoo', 'Slice',
    'SnacTac', 'Soda_Kinley', 'Sofit_SoyaMilk', 'Sprite', 'Sprite_Can', 'Sting']}





}

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))

        new_user = User(username=username)
        new_user.set_password(password)

        # Store username and password in the customers dictionary
        customers[username] = {'password': password, 'history': []}

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/offers2')
@login_required
def offers2():
    return render_template('offers2.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # Redirect to the offers page after successful login
            return redirect(url_for('offers'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/offers')
@login_required
def offers():
    # Ensure the current user is authenticated
    if current_user.is_authenticated:
        # Get recommendations based on the current user's username
        recommendations = get_recommendations_for_user(current_user.username, product_profiles, cosine_similarities, df)
        return render_template('offers.html', recommendations=recommendations)
    else:
        # Redirect to the login page if the user is not authenticated
        flash('You need to login first.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
