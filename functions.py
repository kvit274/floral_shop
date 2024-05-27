from database import get_db, close_db

#whether user exist
def User_exist(user_id):
    db = get_db()
        
    exist_user = db.execute("""SELECT *
                                FROM users 
                                WHERE user_id = ?;""", (user_id,)).fetchone()
    
    if exist_user is not None:
        return True

    else:
        return False
    
#whether shop exist
def Shop_exist(name):
    db = get_db()
    name = name.upper()
    exist_shop = db.execute(""" SELECT name FROM floral_shops;""").fetchall()
    names = []
    for shop in exist_shop:
        shop = shop['name']
        shop = shop.upper()
        names.append(shop)
    if name in names:
        return True
    else:
        return False
    
def Flower_exist(name):
    db = get_db()
    name = name.upper()
    exist_flower = db.execute(""" SELECT name FROM flowers;""").fetchall()
    names = []
    for flower in exist_flower:
        flower = flower['name']
        flower = flower.upper()
        names.append(flower)
    if name in names:
        return True
    else:
        return False
    
def Bouquet_exist(name):
    db = get_db()
    name = name.upper()
    exist_bouquet = db.execute(""" SELECT name FROM bouquets_in_shop;""").fetchall()
    names = []
    for bouquet in exist_bouquet:
        bouquet = bouquet['name']
        bouquet = bouquet.upper()
        names.append(bouquet)
    if name in names:
        return True
    else:
        return False
    

#list the data when modifying a shop
def data_from_table(number,floral_id):
    
    db = get_db()

    floral_data = db.execute("""SELECT * FROM floral_shops
                                 WHERE floral_id = ? ;""", (floral_id,)).fetchone()
    position = 0
    for data in floral_data:
        if position == number:
            return data
        else:
            position += 1

#whether user owns shop
def Own_shop(user_id, floral_id):

    db = get_db()
    own_shop = db.execute("""SELECT * FROM floral_shops
                            WHERE user_id = ?
                            AND floral_id = ?;""",(user_id,floral_id)).fetchone()
    
    if own_shop is not None:
        return True
    else:
        return False
    
# Add flower to the shop
def Add_flowers(floral_id, name, price, quantity):
    db = get_db()

    if db.execute("""SELECT * FROM flowers_in_shop
                                    WHERE name = ?
                                    AND floral_id = ?;""",(name,floral_id)).fetchone() is not None:
                    
        db.execute("""UPDATE flowers_in_shop
                        SET quantity = quantity + ?, price = ?
                        WHERE name = ?
                        AND floral_id = ?;""",(quantity,price,name,floral_id))
        db.commit()
    
    else:
        db.execute("""INSERT INTO flowers_in_shop (floral_id, name, price, quantity)
                        VALUES (?, ?, ?, ?);""", (floral_id, name, price, quantity))
        db.commit()

    message = "Successfully added!"

    return message

# get floral shop

def Get_floral_shop(floral_id):
    db = get_db()

    floral_shop = db.execute("""SELECT * FROM floral_shops 
                                 WHERE floral_id = ?;""",(floral_id,)).fetchone()
    
    return floral_shop
    