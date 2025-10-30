from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_for_passwords' # A strong secret key is crucial

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hotel_admin:postgres@localhost/hotel_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- Flask-Login Configuration ---
login_manager = LoginManager()
login_manager.init_app(app)
# If a user tries to access a protected page, redirect them to the 'login' page.
login_manager.login_view = 'login' 


# --- Database Models ---

# The UserMixin is required by Flask-Login. It adds default user methods.
class User(db.Model, UserMixin):
    __tablename__ = 'users' # Renamed to 'users' for clarity
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False) # Store hashed passwords
    orders = db.relationship('Order', backref='user', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100))
    hotel = db.Column(db.String(100), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    # Link orders to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# --- User Loader for Flask-Login ---
# This function is required by Flask-Login to load the current user from the session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Application Routes ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user or email already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))
        if email_exists:
            flash('Email address already registered. Please use a different one.', 'error')
            return redirect(url_for('signup'))

        # Hash the password for security and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))

        # If correct, log the user in
        login_user(user)
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
@login_required # Only logged-in users can log out
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/')
def home():
    hotels_query = db.session.query(MenuItem.hotel).distinct().all()
    hotel_names = sorted([h[0] for h in hotels_query])
    return render_template('index.html', hotel_names=hotel_names)

@app.route('/hotel/<hotel_name>')
def hotel_page(hotel_name):
    items = MenuItem.query.filter(MenuItem.hotel.ilike(hotel_name)).order_by(MenuItem.id).all()
    if not items:
        flash(f"Sorry, the hotel '{hotel_name}' was not found.", "error")
        return redirect(url_for('home'))
    return render_template('hotel_menu.html', items=items, hotel_name=hotel_name)


@app.route('/address_form', methods=['GET', 'POST'])
@login_required # PROTECT THIS ROUTE: User must be logged in to order
def address_form():
    if request.method == 'POST':
        # Name and mobile can be pre-filled or taken from user profile in a real app
        name = request.form.get('fname')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        items_str = request.form.get('items')
        total_str = request.form.get('total')

        if not all([name, mobile, address, items_str, total_str]):
            flash('Please fill all fields to submit your order.', 'error')
            return redirect(url_for('home'))
        
        # Save the new order to the database, linking it to the logged-in user
        new_order = Order(
            name=name, mobile=mobile, address=address, items=items_str, 
            total=float(total_str), 
            user_id=current_user.id # Use the ID of the logged-in user
        )
        db.session.add(new_order)
        db.session.commit()

        return render_template('order_confirmation.html',
                               name=name, phone=mobile, address=address,
                               items=items_str, total=total_str)
    
    items = request.args.getlist('items')
    total = request.args.get('total', '0.00')
    if not items or not total:
        flash('Your cart is empty. Please select items to order.', 'error')
        return redirect(url_for('home'))

    return render_template('address_form.html', items=items, total=total)


@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')


if __name__ == '__main__':
    with app.app_context():
        # This will create the database tables from your models if they don't exist.
        db.create_all()
    app.run(debug=True)