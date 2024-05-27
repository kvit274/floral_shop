'''
My system has two kind of users: visitors and owners.
Any user can register his own shop and as many as he wishes.
On the main page users can see list of shops and products with different prices, if they find price attractive the can visit the shop.
If user owns shop he is then able to modify it and add/delete flowers/bouquets to the shop (at the bottom right of floral_shop page), he can also see the income that his shop has.
If there is no flower that owner wish to add then he can add a new flower in database.
Please, notice that I wrote a code so that user can not get assess to some functions through urls if he's not the owner!
My web has not only different products but also different stores which was tricky to do.
You can delete items from the cart.
If there is an item in the cart and the owner deletes it from the shop item gets automatically deleted from users cart.
On the main page bouquets are chosen randomly.

I've written some functions in functions.py which I've imported to app.py

I've already created some shops, if you wish to access them: user_id = 'kvit', password = '123'.
Enjoy.

I used import files function which I have taken from here https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/

I used SelectMultipleField in form, info taken from here https://wtforms.readthedocs.io/en/2.3.x/fields/
'''



from flask import Flask, render_template, session, redirect, url_for, g, request
from flask_session import Session
from database import get_db, close_db
from forms import RegistrationForm, LoginForm, Register_shopForm, Modify_shopFrom, Add_flowersForm, New_flowerForm, New_bouquetForm, Modify_bouquetForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps 
from functions import *
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import random

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.teardown_appcontext(close_db) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


Session(app)

@app.before_request
def logged_in_user():
    g.user = session.get("user_id", None)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect( url_for ("login", next = request.url))
        return view(*args, **kwargs)
    return wrapped_view


# @app.route("/")
# def redirection():
#     return redirect(url_for('index'))

@app.route("/")
def index():
    db = get_db()
    floral_shops = db.execute("""SELECT * FROM floral_shops; """).fetchall()

    flowers = db.execute("""SELECT * FROM flowers_in_shop JOIN flowers ON flowers_in_shop.name = flowers.name;""").fetchall()

    bouquets = db.execute("""SELECT * FROM bouquets_in_shop;""").fetchall()

    if bouquets:
        amount_of_bouquets = len(bouquets)
        if amount_of_bouquets > 4:
            random_bouquets = []
            while len(random_bouquets) != 4:
                random_number = random.randint(0 , amount_of_bouquets - 1)
                if bouquets[random_number] not in random_bouquets:
                    random_bouquets.append(bouquets[random_number])
        else:
            random_bouquets = bouquets

    return render_template("index.html", floral_shops = floral_shops, flowers = flowers, random_bouquets = random_bouquets)

    


@app.route("/registration", methods=["GET", "POST"])

def registration():

    form = RegistrationForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        owner = form.owner.data

        db = get_db()

        if User_exist(user_id):
            form.user_id.errors.append("This username already exists")

        else:
            db.execute("""INSERT INTO users (user_id, password)
                          VALUES  (?,?);""", (user_id,generate_password_hash(password)))
            db.commit()

            session.clear()
            session["user_id"] = user_id

            if owner == 'yes':
                return redirect(url_for("register_shop"))
            else:
                return redirect(url_for("index"))
    return render_template("registration.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()

        exist_user = db.execute("""SELECT *
                                   FROM users 
                                   WHERE user_id = ?;""", (user_id,)).fetchone()
        
        if not User_exist(user_id):
            form.user_id.errors.append("This username doesn't exist!")

        elif not check_password_hash(exist_user["password"], password):
            form.password.errors.append("Wrong password!")

        else:

            session.clear()
            session["user_id"] = user_id

            next_page = request.args.get("next")

            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
        
    return render_template("login.html", form=form)
            
@app.route("/logout")
def logout():
    session.clear()
    return redirect( url_for("login") )


@app.route("/register_shop", methods=["GET", "POST"])
@login_required
def register_shop():
    form = Register_shopForm()

    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        open_time = form.open_time.data
        close_time = form.close_time.data

        db = get_db()

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if Shop_exist(name):
                form.name.errors.append("This shop is already registered!")
            
            else:

                db.execute("""INSERT INTO floral_shops (name, address, open_time, close_time,picture_name, user_id)
                            VALUES (?, ?, ?, ?, ?, ?);""", (name,address,open_time,close_time,filename, session["user_id"]))
                db.commit()

                floral_shop = db.execute("""SELECT floral_id FROM floral_shops WHERE name = ? ;""",(name,)).fetchone()

                return redirect ( url_for("floral_shop", floral_id = floral_shop['floral_id']) )
        
    return render_template("register_shop.html", form=form)

@app.route("/floral_shop/<int:floral_id>")
def floral_shop(floral_id):
    modify_shop = ""
    add_flowers = ""
    delete_flower = ""
    new_bouquet = ""
    income = ""

    db = get_db()

    floral_shop = Get_floral_shop(floral_id)
    
    flowers = db.execute("""SELECT * FROM flowers_in_shop JOIN flowers ON flowers_in_shop.name = flowers.name
                             WHERE floral_id = ?;""",(floral_id,)).fetchall()
    
    bouquets = db.execute("""SELECT * FROM bouquets_in_shop WHERE floral_id = ?;""",(floral_id,)).fetchall()
    
    

    if "user_id" in session:
        if Own_shop(session["user_id"],floral_id):
            modify_shop = "Modify shop"
            add_flowers = "Add flowers"
            delete_flower = "Delete"
            new_bouquet = "New bouquet"

            income = db.execute("""SELECT income FROM floral_shops
                                    WHERE floral_id = ? ;""",(floral_id,)).fetchone()
            income = f'Income: {income["income"]}€'

        
    return render_template("floral_shop.html", modify_shop=modify_shop, add_flowers=add_flowers, floral_shop=floral_shop, flowers=flowers, income=income, delete_flower=delete_flower, bouquets=bouquets, new_bouquet = new_bouquet)

@app.route("/modify_shop/<int:floral_id>", methods = ["GET", "POST"])
def modify_shop(floral_id):

    db = get_db()
    form = ""
    if "user_id" in session:

        if Own_shop(session["user_id"], floral_id):
            form = Modify_shopFrom()

            if form.validate_on_submit():
                name = form.name.data
                address = form.address.data
                open_time = form.open_time.data
                close_time = form.close_time.data
                description = form.description.data

                
                if Shop_exist(floral_id):
                    form.name.errors.append("This name is already taken!") 
                    
                else:
                    db.execute("""UPDATE floral_shops
                                    SET name = ?,address = ?,open_time = ?,close_time = ?, description = ?
                                    WHERE floral_id = ?;""",(name,address,open_time,close_time,description,floral_id))
                    db.commit()
                    
                    return redirect( url_for('floral_shop', floral_id = floral_id) )

            #returns initial information about the shop    
            form.name.data = data_from_table(1,floral_id)
            form.address.data = data_from_table(2,floral_id)
            form.open_time.data = data_from_table(3,floral_id)
            form.close_time.data = data_from_table(4,floral_id)
            form.description.data = data_from_table(5,floral_id)
        else:
            return redirect( url_for('index') )
    else:
        return redirect( url_for('index') )
    
    return render_template('modify_shop.html', form = form, floral_id = floral_id)



@app.route("/add_flowers/<int:floral_id>", methods = ["GET", "POST"])
def add_flowers(floral_id):

    db = get_db()
    message = ""

    floral_shop = Get_floral_shop(floral_id)

    if "user_id" in session:
        
        if Own_shop(session["user_id"], floral_id):
            form = Add_flowersForm()
            db = get_db()

            list_flowers = db.execute("""SELECT name
                                        FROM flowers;""").fetchall()

            for flower in list_flowers:
                form.name.choices.append((flower["name"]))
            
            if form.validate_on_submit():
                name = form.name.data
                quantity = form.quantity.data
                price = float(form.price.data)

                message = Add_flowers(floral_id, name, price, quantity)
                
        else:
            return redirect( url_for('index') )
    
    else:
        return redirect(url_for('index'))

    return render_template("add_flowers.html", form = form, message = message, floral_shop = floral_shop)
            

@app.route("/new_flower/<int:floral_id>", methods = ["GET", "POST"])
def new_flower(floral_id):

    db = get_db()
    message = ""

    floral_shop = Get_floral_shop(floral_id)

    if "user_id" in session:
        
        if Own_shop(session["user_id"], floral_id):
            form = New_flowerForm()
            db = get_db()

            if form.validate_on_submit():
                name = form.name.data

                # check if the post request has the file part
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    if Flower_exist(name):
                        form.name.errors.append("This flower is already in the list!")
    
                    elif Bouquet_exist(name):
                        form.name.errors.append("Currently unavailable")

                    else:
                
                        db.execute("""INSERT INTO flowers (name, picture_name)
                                    VALUES (?,?);""",(name,filename))  
                        db.commit()
                    
                        message = "Successfully added!"

                else:
                    return redirect(url_for ("new_flower", floral_id = floral_id))
        else:
            return redirect( url_for('index') )

    else:
        return redirect(url_for('index'))
    return render_template("new_flower.html", form = form, message = message, floral_shop = floral_shop)

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if "cart" not in session:
        session["cart"] = []

    overall_price = 0
    for floral_shop in session["cart"]:
        for flower in floral_shop["flowers"]:
            overall_price += float(flower["price"])
    overall_price = round(overall_price,2)

    purchased = False
    message = ""

    db = get_db()

    for index, shop in enumerate(session["cart"]):
        floral_id = db.execute("""SELECT floral_id FROM floral_shops WHERE name =? ;""",(shop['floral_name'],)).fetchone()
        floral_id = floral_id['floral_id']
        for index, flower in enumerate(shop["flowers"]):
            product_not_deleted = db.execute(""" SELECT * FROM flowers_in_shop JOIN bouquets_in_shop 
                                                 ON flowers_in_shop.floral_id = bouquets_in_shop.floral_id 
                                                 WHERE flowers_in_shop.name = ? 
                                                 OR bouquets_in_shop.name = ?;""",(flower['name'], flower['name'])).fetchone()
            if product_not_deleted is None:
                del shop["flowers"][index]
        if len(shop["flowers"]) == 0:
            del session["cart"][index]

    if request.method == 'POST':
        for floral_shop in session["cart"]:
            income = 0
            floral_name = floral_shop["floral_name"]
            floral_id = db.execute("""SELECT floral_id
                                      FROM floral_shops
                                       WHERE name = ?; """,(floral_name,)).fetchone()
            floral_id = floral_id["floral_id"]

            for flower in floral_shop["flowers"]:
                name = flower["name"]
                quantity = flower["quantity"]
                income += float(flower["price"])
                income = round(income, 2)

                db.execute("""UPDATE bouquets_in_shop SET quantity = quantity - ? WHERE floral_id = ? AND name = ?;""",(quantity,floral_id,name))
                db.commit()
                bouquets_left = db.execute(""" SELECT quantity FROM bouquets_in_shop WHERE floral_id = ? AND name = ?;""",(floral_id,name)).fetchone()
                if bouquets_left:
                    if bouquets_left["quantity"] == 0:
                        delete_bouquet(floral_id,name)


                db.execute("""UPDATE flowers_in_shop
                              SET quantity = quantity - ? 
                              WHERE floral_id = ?
                              AND name = ?;""",(quantity,floral_id,name))
                db.commit()
                flowers_left = db.execute(""" SELECT quantity FROM flowers_in_shop WHERE floral_id = ? AND name = ?;""",(floral_id,name)).fetchone()
                if flowers_left:
                    if flowers_left["quantity"] == 0:
                        delete_flower(floral_id,name)

            db.execute("""UPDATE floral_shops 
                          SET income = income + ?
                          WHERE floral_id = ?;""",(income,floral_id))
            db.commit()

        purchased = True
        message = "Thanks for shopping"

        session["cart"].clear()
    return render_template("cart.html", cart = session['cart'], overall_price = overall_price, message = message, purchased = purchased)

    


@app.route("/add_to_cart/<int:floral_id>/<name>/<price>")
@login_required
def add_to_cart(floral_id, name, price, ):
    db = get_db()
    if "cart" not in session:
        session["cart"] = []

    # list = [{"floral_name": floral_name,"flowers": [{"name": name, "quantity": 1, "price": price}] }] }
    floral_name = db.execute("""SELECT name FROM floral_shops WHERE floral_id = ? ;""", (floral_id,)).fetchone()
    floral_name = floral_name["name"]
    flower_in_cart = False
    shop_in_cart = False

    for floral_shop in session["cart"]:
        if floral_shop["floral_name"] == floral_name:
            shop_in_cart = True
            for flower in floral_shop["flowers"]:
                if flower["name"] == name:
                    flower_in_cart = True
                    
                    check_if_flower = db.execute(""" SELECT name FROM flowers_in_shop WHERE name = ?;""",(name,)).fetchone()
                    if check_if_flower:

                        flower_quantity_overdose = db.execute("""SELECT quantity
                        FROM flowers_in_shop
                        WHERE name = ?
                        AND floral_id = ?;""", (name, floral_id)).fetchone()

                        if flower["quantity"]>= flower_quantity_overdose['quantity']:
                            flower["quantity"] = flower["quantity"]
                    
                        else:
                            flower["quantity"] += 1
                        
                    check_if_bouquet = db.execute("""SELECT name FROM bouquets_in_shop WHERE name = ?;""",(name,)).fetchone()
                    if check_if_bouquet:
                        bouquet_quantity_overdose = db.execute("""SELECT quantity FROM bouquets_in_shop WHERE name = ? AND floral_id = ? ;""",(name, floral_id)).fetchone()
                        if flower["quantity"] >= bouquet_quantity_overdose['quantity']:
                            flower["quantity"] = flower["quantity"]
                            
                        else:
                            flower["quantity"] += 1

                    flower["price"] = round(float(price) * int(flower["quantity"]),2)
                    

            if not flower_in_cart:
                floral_shop["flowers"].append({"name": name, "quantity": 1, "price": price})

    if not shop_in_cart:
        session["cart"].append({"floral_name":floral_name,"flowers": [{"name": name, "quantity": 1, "price": price}] })


    return redirect( url_for('floral_shop', floral_id = floral_id) )


#https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template("file_upload.html")

@app.route("/delete_from_cart/<floral_name>/<name>")
def delete_from_cart(floral_name, name):
    for index, shop in enumerate(session["cart"]):
        if shop["floral_name"] == floral_name:
            for index, flower in enumerate(shop["flowers"]):
                if flower["name"] == name:
                    del shop["flowers"][index]
            if len(shop["flowers"]) == 0:
                del session["cart"][index]

    return redirect(url_for('cart'))

@app.route("/delete_flower/<int:floral_id>/<name>")
def delete_flower(floral_id, name):
        
    if "user_id" in session:
        if Own_shop(session["user_id"], floral_id):
            db = get_db()
            db.execute("""DELETE FROM flowers_in_shop WHERE floral_id = ? AND name = ?;""",(floral_id,name))
            db.commit()

        else:
            return redirect( url_for('index') )    
    else:
        return redirect(url_for('index'))

    return redirect(url_for('floral_shop', floral_id = floral_id))


@app.route("/new_bouquet/<int:floral_id>", methods=["GET", "POST"])
def new_bouquet(floral_id):

    if "user_id" in session:
        if Own_shop(session["user_id"], floral_id):
            message = ""
            has_flower = ""
            form = New_bouquetForm()
            db = get_db()
            list_flowers = db.execute("""SELECT name
                                        FROM flowers;""").fetchall()
            choices = len(list_flowers)

            for flower in list_flowers:
                form.flowers.choices.append((flower["name"]))

            if form.validate_on_submit():
                name = form.name.data
                price = float(form.price.data)
                flowers = form.flowers.data

                for flower in flowers:
                    if flower == flowers[-1]:
                        has_flower += str(flower)
                    else:
                        has_flower += str(flower) + ", "
                quantity = int(form.quantity.data)
                
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    

                    if Flower_exist(name):
                        
                        form.name.errors.append("Bouquet can't be named as a name of flower!")

                    if Bouquet_exist(name):
                        form.name.errors.append("You already have this bouquet in your shop!")
                    # # return redirect(url_for('download_file', name=filename))
                    else:
                
                        db.execute("""INSERT INTO bouquets_in_shop (floral_id, name, price, flowers, quantity, picture_name)
                                    VALUES (?,?,?,?,?,?);""",(floral_id, name, price, has_flower,quantity, filename))  #переделать цветы, цены должны быть индивидуальны
                        db.commit()
                    
                        message = "Successfully added!"

                    # return redirect(url_for("new_flower", floral_id = floral_id))
                else:
                    return redirect(url_for ("new_flower", floral_id = floral_id))
        else:
            return redirect( url_for('index') )
    else:
        return redirect( url_for('index') )
                



    return render_template("new_bouquet.html", form = form, message = message, floral_id = floral_id, choices = choices)


@app.route("/delete_bouquet/<int:floral_id>/<name>")
def delete_bouquet(floral_id, name):
        
    if "user_id" in session:
        if Own_shop(session["user_id"], floral_id):
            db = get_db()
            db.execute("""DELETE FROM bouquets_in_shop WHERE floral_id = ? AND name = ?;""",(floral_id,name))
            db.commit()
        else:
            return redirect( url_for('index') )
    else:
        return redirect(url_for('index'))

    return redirect(url_for('floral_shop', floral_id = floral_id))


@app.route("/bouquet/<int:floral_id>/<name>", methods = ["GET", "POST"])
def bouquet(floral_id, name):

    db = get_db()

    bouquet = db.execute("""SELECT * FROM bouquets_in_shop WHERE name = ? AND floral_id = ?; """,(name, floral_id)).fetchone()
    own = False
    form = Modify_bouquetForm()

    if "user_id" in session:
        if Own_shop(session["user_id"],floral_id):
            own = True
            if form.validate_on_submit():
                quantity = form.quantity.data
                quantity = int(quantity)
                db.execute(""" UPDATE bouquets_in_shop SET quantity = quantity + ? WHERE name = ? AND floral_id = ?;""",(quantity,name,floral_id))
                db.commit()
                bouquet = db.execute("""SELECT * FROM bouquets_in_shop WHERE name = ? AND floral_id = ?; """,(name, floral_id)).fetchone()
    return render_template("bouquet.html", floral_id =floral_id, bouquet = bouquet, own = own, form = form)
    


