# importing the modules required in the route.py
import os
import secrets
from fileinput import filename

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from mens_fashion import app, bcrypt, db
from mens_fashion.forms import (LoginForm, ProductForm, Purchasing,
                                RegistrationForm, SearchForm,
                                UpdateProfileForm)
from mens_fashion.models import Products, User

# -------------------------------- The home page --------------------------

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

# ---------------------------------The about page -------------------------

@app.route("/about")
def about():
    return render_template("about.html")

# ---------------------------The registration page -------------------------

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, type=form.type.data)
        db.session.add(user) 
        db.session.commit()
        flash(f'Account created', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)

# ------------------------------- The login page ---------------------------

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            abort(400, 'Not registered.')
    return render_template("login.html", title="Login", form=form)

# --------------------------------logout page --------------------------------

@app.route("/logout")
def logout(): 
    logout_user()
    return redirect(url_for('home'))

# ------------------------------- Products page ------------------------------

@app.route("/products")
def products():
    page = request.args.get('page', 1, type=int)
    product = Products.query.paginate(page=page,per_page=8)
    return render_template("products.html", products=product)

# ------------------------------- Gallery page ------------------------------

@app.route("/gallery")
def gallery():
    product = Products.query.filter()
    return render_template("gallery.html", products=product)

# -----------------------------The Product page------------------------------

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('product.html', title=product.product_name, product=product)

# ---------------------------- Buy product page ------------------------------

@app.route('/product/<int:product_id>/buy', methods=['GET','POST'])
@login_required
def buy_product(product_id):
    if current_user.type != "User":
        abort(403, 'You are not authorized to buy a product.')
    product = Products.query.get_or_404(product_id)
    form = Purchasing()
    if form.validate_on_submit():
        product.numberOfItems = form.numberOfItems.data
        product.status = False
        db.session.commit()
        product.user_id = current_user.id
        db.session.commit()
        flash('Bought product')
        return redirect(url_for('cat'))
    return render_template('buy.html', title = 'Buy product', form = form, legend="Book product")

# ---------------------------- Add new product page --------------------------

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/new_product", methods=['GET', 'POST'])
@login_required
def new_product():
    if current_user.type != "Admin":
        abort(403, 'You are not authorized to access this page.')
    form = ProductForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            image_file = picture_file
        product = Products(product_name=form.product_name.data, description=form.description.data, price=form.price.data, product_type=form.product_type.data, image_file=image_file)
        db.session.add(product)
        db.session.commit()
        flash(f'Product added', 'success')        
        return redirect(url_for('home'))
    return render_template("add.html", title='new product', form=form, legend="New product")

# ------------------------------ product update --------------------------------

@app.route('/product/<int:product_id>/update', methods=['GET','POST'])
@login_required
def update_product(product_id):
    if current_user.type == "User":
        abort(403, 'You are not authorized to delete a resource.')
    product = Products.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.product_name = form.product_name.data
        product.description = form.description.data
        product.price = form.price.data
        product.product_type = form.product_type.data
        db.session.commit()
        flash('Product Updated', 'success')
    elif request.method =='GET': 
        form.product_name.data = product.product_name
        form.description.data = product.description
        form.price.data = product.price
    return render_template('add.html', title = 'Update product', form = form, legend="Update product")

# -------------------------- product delete ------------------------------------

@app.route('/product/<int:product_id>/delete', methods=['GET','POST'])
@login_required
def delete_product(product_id):
    if current_user.type != "Admin":
        abort(403, 'You are not authorized to access this page.')
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product Deleted', 'danger')
    return redirect(url_for('home'))

# ---------------------------Purchased page ------------------------------------

@app.route("/purchased")
@login_required
def purchased():
    if current_user.type == "User":
        abort(401, 'You are not authorized to access this page.')
    product = Products.query.filter(Products.status == False)
    page = request.args.get('page', 1, type=int)
    product = product.paginate(page=page,per_page=6)
    return render_template("products.html", products=product)


# ----------------------------- cat page --------------------------------------

@app.route('/cat')
@login_required
def cat():
    if current_user.type != "User":
        abort(403, 'You are not authorized to access this page.')
    product = Products.query.filter(Products.user_id == current_user.id) # Get the items purchased only by the current user
    return render_template('catalogue.html', products = product) 

# ---------------------------- payment page ----------------------------------

@app.route('/payment')
@login_required
def payment():
    if current_user.type != "User":
        abort(403, 'You are not authorized to puchase an Item. Please log in as a User')
    products = Products.query.filter(Products.user_id == current_user.id) # Get the items purchased only by the current user
    total = 0
    for product in products:
        total += int(product.price) # To get the total cost of all items purchased
    return render_template('payment.html', products = products, total = total)



# -------------------------- account page ------------------------


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.username.data = current_user.username
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account', profile_picture = image_file, form = form)

# -------------------------- Users page ------------------------

@app.route("/users", methods=['GET','POST'])
@login_required
def users():
    if current_user.type != "Admin":
        abort(403, 'You are not authorized to access this page.')
    user = User.query.filter()
    return render_template("users.html", users=user)


# -------------------------- Search page ------------------------

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    products = Products.query
    if form.validate_on_submit():
        product.searched = form.searched.data
        products = products.filter(Products.product_name.like('%'+ product.searched + '%'), Products.description.like('%'+ product.searched + '%'))
        products = products.order_by(Products.product_name).all()
        return render_template('search.html', form=form, seached = product.searched, products = products)