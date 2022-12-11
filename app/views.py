import copy
from flask import request, flash, render_template, url_for, redirect, session, json
from app import app, db
import datetime
from .forms import LoginForm, AddItemForm, PurchaseForm
from .models import User, Item, Order, Cart, Collection
from datetime import datetime
import base64


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        identity = form.identity.data
        user = User.query.filter(User.username == username, User.password == password, User.job == identity).all()
        if not user:
            return render_template('login.html', form=form)
        else:
            if user[0].job == 0:
                session['user'] = [user[0].username, user[0].password, user[0].phone, user[0].name, user[0].job,
                                   user[0].id]
                return render_template('userIndex.html', form=form)
            elif user[0].job == 1:
                session['user'] = [user[0].username, user[0].password, user[0].phone, user[0].name, user[0].job,
                                   user[0].id]
                return render_template('adminIndex.html', form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    return redirect(url_for('add'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddItemForm()
    item = Item.query.all()
    item_list = []
    for i in item:
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        item_list.append([i, byte_str])
    if form.validate_on_submit():
        file = request.files['image'].read()
        name = form.item_name.data
        description = form.description.data
        price = form.price.data
        item = Item(item_name=name, description=description, price=price, image=file)
        db.session.add(item)
        db.session.commit()
        flash('ok')
        return redirect(url_for('login'))
    return render_template('home.html', form=form, ds=item_list, base64=base64)


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    item = Item.query.all()
    user_id = session.get('user')[5]
    item_list = []
    for i in item:
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        favor = Collection.query.filter(Collection.item_id == i.id, Collection.user_id == user_id).all()
        a = 1
        if not favor:
            a = 0
        item_list.append([i, byte_str, a])
    return render_template('item.html', item=item_list, base64=base64, page=1)


@app.route('/information', methods=['GET', 'POST'])
def information():
    user = session.get("user")
    return render_template('userInformation.html', user=user)


@app.route('/getSession', methods=['GET', 'POST'])
def getSession():
    user = session.get('user')
    return user


@app.route('/itemDetail', methods=['GET'])
def itemDetail():
    form = PurchaseForm()
    item_id = request.args.get('id')
    item = Item.query.filter(Item.id == item_id).first()
    temp = base64.b64encode(item.image)
    temp = str(temp)
    byte_str = copy.deepcopy(temp[2:len(temp) - 1])
    return render_template('itemDetail.html', item=[item, byte_str], form=form)


@app.route('/test', methods=['GET', 'POST'])
def test():
    item = request.form.get('item')
    print(item)
    return 1


@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    user_id = session.get('user')[5]
    curr_time = datetime.now()
    province = request.form.get('province')
    city = request.form.get('city')
    item_id = request.form.get('item_id')
    number = int(request.form.get('number'))
    destination = '' + province + city
    item = Item.query.filter(Item.id == item_id).first()
    price = item.price
    money = float(price) * number
    order = Order(user_id=user_id, item_id=item_id, time=curr_time, number=number, destination=destination, money=money)
    db.session.add(order)
    db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    user_id = session.get('user')[5]
    item_id = request.form.get('item_id')
    number = int(request.form.get('number'))
    item = Item.query.filter(Item.id == item_id).first()
    price = item.price
    money = float(price) * number
    province = request.form.get('province')
    city = request.form.get('city')
    destination = '' + province + city
    cart = Cart(user_id=user_id, item_id=item_id, number=number, money=money, destination=destination)
    db.session.add(cart)
    db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/order', methods=['GET', 'POST'])
def order():
    user_id = session.get('user')[5]
    order = db.session.query(Order.id, Order.user_id, Order.item_id, Order.time, Order.money, Order.destination,
                             Order.number, Item.image, Item.price, Item.item_name, Item.description)\
        .join(Item, Order.item_id == Item.id).filter(Order.user_id == user_id).all()
    order_list = []
    for i in order:
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        a = i.time
        day = datetime(a.year, a.month, a.day, a.hour, a.minute, int(a.second))
        order_list.append([i, byte_str, i.number * 500, day])
    return render_template('order.html', order=order_list, base64=base64)


@app.route('/collection', methods=['GET', 'POST'])
def collection():
    user_id = session.get('user')[5]
    collection = db.session.query(Collection.id, Collection.user_id, Collection.item_id, Item.image, Item.price,
                                  Item.item_name).join(Item, Collection.item_id == Item.id)\
        .filter(Collection.user_id == user_id).all()
    collection_list = []
    for i in collection:
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        collection_list.append([i, byte_str, 1])
    return render_template('item.html', item=collection_list, base64=base64, page=2)


@app.route('/cartItem', methods=['GET', 'POST'])
def cartItem():
    user_id = session.get('user')[5]
    cart = db.session.query(Cart.id, Cart.user_id, Cart.item_id, Cart.money, Cart.destination, Cart.number, Item.image,
                            Item.price, Item.item_name, Item.description).join(Item, Cart.item_id == Item.id)\
        .filter(Cart.user_id == user_id).all()
    cart_list = []
    for i in cart:
        print(i)
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        cart_list.append([i, byte_str, i.number * 500])
    return render_template('shoppingCart.html', cart=cart_list, base64=base64)


@app.route('/cancelOrder', methods=['GET', 'POST'])
def cancelOrder():
    order_id = request.args.get('id')
    order = Order.query.filter_by(id=order_id).first()
    db.session.delete(order)
    db.session.commit()
    return redirect('order')


@app.route('/cancelCart', methods=['GET', 'POST'])
def cancelCart():
    cart_id = request.args.get('id')
    cart = Cart.query.filter_by(id=cart_id).first()
    db.session.delete(cart)
    db.session.commit()
    return redirect('cartItem')


@app.route('/purchaseCart', methods=['GET', 'POST'])
def purchaseCart():
    cart_id = request.args.get('id')
    cart = Cart.query.filter_by(id=cart_id).first()
    curr_time = datetime.now()
    order = Order(user_id=cart.user_id, item_id=cart.item_id, time=curr_time, number=cart.number,
                  destination=cart.destination, money=cart.money)
    db.session.delete(cart)
    db.session.commit()
    db.session.add(order)
    db.session.commit()
    return redirect('cartItem')


@app.route('/makeFavor', methods=['GET', 'POST'])
def makeFavor():
    user_id = session.get('user')[5]
    item_id = request.form.get('item_id')
    collection = Collection(user_id=user_id, item_id=item_id)
    db.session.add(collection)
    db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/cancelFavor', methods=['GET', 'POST'])
def cancelFavor():
    user_id = session.get('user')[5]
    item_id = request.form.get('item_id')
    collection = Collection.query.filter(Collection.user_id == user_id, Collection.item_id == item_id).all()
    for i in collection:
        db.session.delete(i)
        db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/deleteFavor', methods=['GET', 'POST'])
def deleteFavor():
    favor_id = request.args.get('id')
    collection = Collection.query.filter(Collection.id == favor_id).first()
    db.session.delete(collection)
    db.session.commit()
    return redirect('collection')


@app.route('/orderAdmin', methods=['GET', 'POST'])
def orderAdmin():
    order = db.session.query(Order.id, Order.user_id, Order.item_id, Order.money, Order.destination, Order.number,
                             Order.time, Item.price, Item.item_name, User.name, User.phone)\
        .join(Item, Order.item_id == Item.id).join(User, Order.user_id == User.id).all()
    order_list = []
    for i in order:
        price = i.number * 500
        a = i.time
        day = datetime(a.year, a.month, a.day, a.hour, a.minute, int(a.second))
        order_list.append([i, price, day])
    return render_template('orderAdmin.html', order=order_list)


@app.route('/itemAdmin', methods=['GET', 'POST'])
def itemAdmin():
    item = Item.query.all()
    user_id = session.get('user')[5]
    item_list = []
    for i in item:
        temp = base64.b64encode(i.image)
        temp = str(temp)
        byte_str = copy.deepcopy(temp[2:len(temp) - 1])
        favor = Collection.query.filter(Collection.item_id == i.id, Collection.user_id == user_id).all()
        a = 1
        if not favor:
            a = 0
        item_list.append([i, byte_str, a])
    return render_template('itemAdmin.html', item=item_list, base64=base64)


@app.route('/userAdmin', methods=['GET', 'POST'])
def userAdmin():
    user_list = User.query.all()
    user = []
    for i in user_list:
        temp = ''
        num = 0
        length = len(i.password)
        for j in i.password:
            if (num >= 0 and num <= 1) or (num >= length - 3 and num <= length - 1):
                temp = temp + j
            else:
                temp = temp + '*'
            num += 1
        user.append([i, temp])
    return render_template('userAdmin.html', user=user)


@app.route('/', methods=['GET', 'POST'])
def logout():
    session.pop('user')
    form = LoginForm
    return render_template('login.html', form=form)


@app.route('/deleteOrder', methods=['GET', 'POST'])
def deleteOrder():
    order_id = request.form.get('id')
    order = Order.query.filter_by(id=order_id).first()
    db.session.delete(order)
    db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/batchDeleteOrder', methods=['GET', 'POST'])
def batchDeleteOrder():
    order_id = request.form.get('id')
    temp = str(order_id)
    temp2 = copy.deepcopy(temp[0:len(temp) - 1])
    a = temp2.split(' ')
    id_list = []
    for i in a:
        id_list.append(int(i))
    for i in id_list:
        order = Order.query.filter_by(id=i).first()
        db.session.delete(order)
        db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/deleteItem', methods=['GET', 'POST'])
def deleteItem():
    item_id = request.form.get('id')
    item = Item.query.filter_by(id=item_id).first()
    favor = Collection.query.filter_by(item_id=item.id).all()
    cart = Cart.query.filter_by(item_id=item.id).all()
    order = Order.query.filter_by(item_id=item.id).all()
    for i in favor:
        db.session.delete(i)
        db.session.commit()
    for i in cart:
        db.session.delete(i)
        db.session.commit()
    for i in order:
        db.session.delete(i)
        db.session.commit()
    db.session.delete(item)
    db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/batchDeleteItem', methods=['GET', 'POST'])
def batchDeleteItem():
    item_id = request.form.get('id')
    temp = str(item_id)
    temp2 = copy.deepcopy(temp[0:len(temp) - 1])
    a = temp2.split(' ')
    id_list = []
    for i in a:
        id_list.append(int(i))
    for i in id_list:
        item = Item.query.filter_by(id=i).first()
        favor = Collection.query.filter_by(item_id=item.id).all()
        cart = Cart.query.filter_by(item_id=item.id).all()
        order = Order.query.filter_by(item_id=item.id).all()
        for j in favor:
            db.session.delete(j)
            db.session.commit()
        for j in cart:
            db.session.delete(j)
            db.session.commit()
        for j in order:
            db.session.delete(j)
            db.session.commit()
        db.session.delete(item)
        db.session.commit()
    data = {'word': 1}
    return json.dumps(data)


@app.route('/addItem', methods=['GET', 'POST'])
def addItem():
    form = AddItemForm()
    if form.validate_on_submit():
        name = form.item_name.data
        price = form.price.data
        description = form.description.data
        image = request.files['image'].read()
        item = Item(item_name=name, description=description, price=price, image=image)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('itemAdmin'))
    return render_template('edit.html', form=form, base64=base64)


# @app.route('/editItem', methods=['GET', 'POST'])
# def editItem():
#     order_id = request.form.get('id')
#     temp = str(order_id)
#     temp2 = copy.deepcopy(temp[0:len(temp) - 1])
#     a = temp2.split(' ')
#     id_list = []
#     for i in a:
#         id_list.append(int(i))
#     for i in id_list:
#         order = Order.query.filter_by(id=i).first()
#         db.session.delete(order)
#         db.session.commit()
#     data = {'word': 1}
   # return json.dumps(data)