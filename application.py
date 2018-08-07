from flask import Flask
import json
from flask import render_template, flash, redirect, url_for, request, abort
from flask import make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, Item, Offer
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import requests
import httplib2


engine = create_engine("sqlite:///itemCatalog.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

SECRET_KEY = "".join(random.choice(string.digits + string.ascii_uppercase +
                     string.ascii_lowercase)
                     for i in range(16))
CLIENT_ID = json.loads(
                open('client_secrets.json', 'r').read())['web']['client_id']
app = Flask(__name__)


@app.route('/catalog/login/')
def login():
    state = ''.join(random.choice(string.digits + string.ascii_uppercase +
                    string.ascii_lowercase) for i in range(24))
    print(state)
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/google_connect', methods=['POST'])
def google_connect():
    # validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid State Parameter!!'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    auth_code = request.data

    # Get Access token using auth_code
    try:
        flow = flow_from_clientsecrets('client_secrets.json', scope='')
        flow.redirect_uri = "postmessage"
        credentials = flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to get credentials!!'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check validity of access token
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" %
           access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    content = json.loads(result)

    if content.get('error') is not None:
        response = make_response(json.dumps(content.decode().get('error')),
                                 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check access token is for intended user or not

    google_plus_id = credentials.id_token['sub']
    if content['user_id'] != google_plus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check access token is intended to this app or not

    if content['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_plus_id = login_session.get('google_plus_id')
    if stored_access_token is not None and stored_google_plus_id == \
            google_plus_id:
                response = make_response(json.dumps('already connected.'), 200)
                response.headers['Content-Type'] = 'application/json'
                flash("You are already logged in")
                return response
    login_session['access_token'] = access_token
    login_session['google_plus_id'] = google_plus_id

    # access user info
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    output = requests.get(url, params=params)
    data = output.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']
    user = session.query(User).filter(User.email == login_session['email']) \
        .one_or_none()
    if user is None:
        new_user = User(name=login_session['username'],
                        email=login_session['email'],
                        picture=login_session['picture']
                        )
        session.add(new_user)
        session.commit()
        return ''
    else:
        return ''


@app.route('/catalog/logout/')
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        abort(400)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_plus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("Successfully Disconnected")
        return redirect(url_for('index'))
    else:
        response = make_response(json.dumps('Failed to revoke token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# index route
@app.route('/')
@app.route('/catalog/')
def index():
    categories = session.query(Category).limit(7).all()
    items = session.query(Item, Category) \
        .filter(Item.category_id == Category.id_) \
        .order_by(desc(Item.id_)).limit(7).all()
    offers = session.query(Offer).limit(7).all()
    if login_session.get('username') is None:
        return render_template("public_index.html",
                               categories=categories,
                               items=items,
                               offers=offers,
                               login_session=login_session)
    else:
        user = session.query(User) \
            .filter(User.email == login_session['email']) \
            .one_or_none()
        return render_template("index.html", categories=categories,
                               items=items, offers=offers,
                               login_session=login_session,
                               user=user)


# read category route (c.R)
@app.route('/catalog/categories/')
def show_category():
    categories = session.query(Category).all()
    if login_session.get('username') is None:
        return render_template('public_category.html', categories=categories)
    else:
        return render_template('category.html',
                               categories=categories,
                               login_session=login_session)


# create category route(c.C)
@app.route('/catalog/<string:user_id>/categories/new/',
           methods=["GET", "POST"])
def create_category(user_id):
    if request.method == 'GET':
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                return render_template("create_new_category.html",
                                       user=user,
                                       login_session=login_session)
            else:
                abort(401)
        else:
            abort(401)
    elif request.method == "POST":
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                try:
                    category_name = request.form.get('category_name')
                    if category_name is not None:
                        new_category = Category(name=category_name,
                                                user=user)
                        session.add(new_category)
                        session.commit()
                        flash("Category Created!!")
                        return redirect(url_for('show_users_categories',
                                        user_id=user.id_))
                    else:
                        abort(400)
                except Exception:
                    abort(400)
            else:
                abort(401)
        else:
            abort(401)


# edit category route(c.U)
@app.route('/catalog/<string:user_id>/categories/<string:category_id>/edit/',
           methods=["GET", "POST"])
def edit_users_category(user_id, category_id):
    if request.method == "GET":
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category) \
                    .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if category.user_id == user.id_:
                        return render_template('edit_users_category.html',
                                               login_session=login_session,
                                               user=user, category=category)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    elif request.method == "POST":
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category) \
                    .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if category.user_id == user.id_:
                        category = session.query(Category) \
                            .filter(Category.id_ == category_id).one_or_none()
                        if category is not None:
                            try:
                                category.name = str(request.form.get(
                                                    'category_name'))
                                flash("Category Updated!!")
                                return redirect(url_for(
                                                'show_users_categories',
                                                user_id=user_id))
                            except Exception:
                                abort(400)
                        else:
                            abort(401)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(405)


# delete category route(c.D)
@app.route('/catalog/<string:user_id>/categories/<string:category_id>/delete/',
           methods=["POST", "GET"])
def delete_users_category(user_id, category_id):
    if request.method == "GET":
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category) \
                           .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if category.user_id == user.id_:
                        return render_template(
                            'delete_users_category_warning.html',
                            login_session=login_session,
                            user=user,
                            category=category)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    elif request.method == "POST":
        user = session.query(User).filter(User.id_ == user_id).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category) \
                           .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if category.user_id == user.id_:
                        category = session.query(Category) \
                                   .filter(Category.id_ == category_id) \
                                   .one_or_none()
                        if category is not None:
                            try:
                                if request.form.get('delete') == 'yes':
                                    items = session.query(Item) \
                                     .filter(Item.category_id == category.id_)\
                                     .all()
                                    item_ids = []
                                    for item in items:
                                        item_ids.append(item.id_)

                                    offers = session.query(Offer)\
                                        .filter(Offer.item_id.in_(item_ids))\
                                        .all()
                                    for offer in offers:
                                        session.delete(offer)
                                        session.commit()
                                    for item in items:
                                        session.delete(item)
                                        session.commit()
                                        session.delete(category)
                                        session.commit()
                                    flash("Category Deleted!!")
                                    return redirect(url_for(
                                                    'show_users_categories',
                                                    user_id=user_id))
                                elif request.form.get('delete') == 'no':
                                    return redirect(url_for(
                                                    'show_users_categories',
                                                    user_id=user_id))
                                else:
                                    abort(400)
                            except Exception:
                                abort(400)
                        else:
                            abort(401)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)

    else:
        abort(405)


# read items from category (i.R)
@app.route('/catalog/categories/<string:category_id>/')
@app.route('/catalog/categories/<string:category_id>/items/')
def show_category_item(category_id):
    category = session.query(Category).filter(Category.id_ == category_id)\
                                    .one_or_none()
    items = session.query(Item, Category)\
        .filter(Item.category_id == Category.id_)\
        .filter(Item.category_id == category.id_)\
        .all()
    if login_session.get('username') is None:
        return render_template('public_category_item.html', items=items,
                               category=category)
    else:
        return render_template('category_item.html', items=items,
                               category=category, login_session=login_session)


@app.route('/catalog/categories/<string:category_id>/items/<string:item_id>/')
def show_category_item_detail(category_id, item_id):
    category = session.query(Category)\
                        .filter(Category.id_ == category_id).one_or_none()
    item = session.query(Item).filter(Item.category_id == category.id_)\
                              .filter(Item.id_ == item_id).one_or_none()
    offers = session.query(Offer).filter(Offer.item_id == item_id).all()
    if login_session.get('username') is None:
        return render_template('public_category_item_detail.html',
                               item=item,
                               category=category,
                               offers=offers)
    else:
        return render_template('category_item_detail.html',
                               item=item,
                               category=category,
                               offers=offers,
                               login_session=login_session)


# create items from category (i.C)
@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items/new/', methods=["GET", "POST"])  # noqa
def create_users_new_item(user_id, category_id):
    if request.method == "GET":
        user = session.query(User).filter(user_id == User.id_).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category)\
                           .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if str(category.user_id) == user_id:
                        return render_template('create_users_new_item.html',
                                               user=user,
                                               login_session=login_session,
                                               category=category)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)

    elif request.method == "POST":
        user = session.query(User).filter(user_id == User.id_).one_or_none()
        if user is not None:
            if user.email == login_session.get('email'):
                category = session.query(Category)\
                 .filter(Category.id_ == category_id).one_or_none()
                if category is not None:
                    if str(category.user_id) == user_id:
                        try:
                            new_item = Item(name=request.form.get('name'),
                                            description=request.form.get('description'),  # noqa
                                            price=request.form.get('price'),
                                            category=category)
                            session.add(new_item)
                            session.commit()
                            flash("New Item Created!!")
                            return redirect(
                                        url_for('show_user_categories_items',
                                                user_id=user.id_,
                                                category_id=category.id_))
                        except Exception as e:
                            abort(405)
                    else:
                        abort(401)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


# edit items from category (i.U)
@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items/<string:item_id>/edit/',  # noqa
           methods=["GET", "POST"])
def edit_users_items(user_id, category_id, item_id):
    flag = False
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    categories = session.query(Category)\
        .filter(Category.user_id == user_id).all()
    item = session.query(Item)\
        .filter(Item.id_ == item_id)\
        .filter(Item.category_id == category_id).one_or_none()
    offers = session.query(Offer).filter(Offer.item_id == item_id).all()
    if user.email == login_session.get('email'):
        for category in categories:
            if category_id == str(category.id_):
                flag = True
                break
        if flag is True:
            if request.method == "GET":
                if item is not None:
                    return render_template('edit_users_items.html',
                                           login_session=login_session,
                                           user=user,
                                           category=category,
                                           item=item)
                else:
                    abort(401)
            elif request.method == "POST":
                item = session.query(Item).filter(Item.id_ == item_id)\
                                        .one_or_none()
                if item is not None:
                    try:
                        item.name = request.form.get('name')
                        item.description = request.form.get('description')
                        item.price = request.form.get('price')
                        flash("Item Updated!!")
                        return redirect(url_for('show_user_categories_items',
                                                category_id=category.id_,
                                                user_id=user.id_))
                    except Exception as e:
                        abort(405)

                else:
                    abort(401)
            else:
                abort(405)
        else:
            abort(401)
    else:
        abort(401)


# delete items from category (i.D)
@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items/<string:item_id>/delete/',  # noqa
           methods=["GET", "POST"])
def delete_users_items(user_id, category_id, item_id):
    flag = False
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    categories = session.query(Category).filter(Category.user_id == user_id)\
                                        .all()
    item = session.query(Item)\
        .filter(Item.id_ == item_id)\
        .filter(Item.category_id == category_id).one_or_none()
    offers = session.query(Offer).filter(Offer.item_id == item_id).all()
    if user.email == login_session.get('email'):
        for category in categories:
            if category_id == str(category.id_):
                flag = True
                break
        if flag is True:
            if request.method == "GET":
                if item is not None:
                    return render_template('delete_users_items_warning.html',
                                           login_session=login_session,
                                           user=user,
                                           category=category,
                                           item=item)
                else:
                    abort(401)
            elif request.method == "POST":
                try:
                    offers = session.query(Offer)\
                        .filter(Offer.item_id == item_id).all()
                    if request.form.get('delete') == 'yes':
                        if offers is not None:
                            for offer in offers:
                                session.delete(offer)
                                session.commit()
                        session.delete(item)
                        session.commit()
                        flash("Item Deleted!!")
                        return redirect(url_for('show_user_categories_items',
                                                user_id=user_id,
                                                category_id=category.id_))
                    elif request.form.get('delete') == 'no':
                        return redirect(url_for('show_user_categories_items',
                                                user_id=user_id,
                                                category_id=category.id_))
                    else:
                        abort(400)
                except Exception as e:
                    abort(405)
            else:
                abort(405)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/offers')
def show_offers():
    offers = session.query(Offer).all()
    if login_session.get('username') is None:
        return render_template('public_offer.html', offers=offers)
    else:
        return render_template('offer.html',
                               offers=offers,
                               login_session=login_session)


@app.route('/catalog/offers/<string:offer_id>/')
def show_offer_details(offer_id):
    offer = session.query(Offer).filter(Offer.id_ == offer_id).one_or_none()
    items = session.query(Offer, Item).distinct(Item.name)\
        .filter(Offer.item_id == Item.id_)\
        .filter(Offer.id_ == offer_id)\
        .group_by(Item.name)\
        .all()
    if login_session.get('username') is None:
        return render_template('public_offer_detail.html',
                               offer=offer,
                               items=items)
    else:
        return render_template('offer_detail.html',
                               offer=offer,
                               items=items,
                               login_session=login_session)


@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items/<string:item_id>/offers/new',  # noqa
           methods=["GET", "POST"])
def add_new_offers(user_id, category_id, item_id):
    flag = False
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    categories = session.query(Category)\
        .filter(Category.user_id == user_id).all()
    item = session.query(Item)\
        .filter(Item.id_ == item_id)\
        .filter(Item.category_id == category_id).one_or_none()
    offers = session.query(Offer).filter(Offer.item_id == item_id).all()
    if user.email == login_session.get('email'):
        for category in categories:
            if category_id == str(category.id_):
                flag = True
                break
        if flag is True:
            if request.method == "GET":
                if item is not None:
                    return render_template('add_new_offers.html',
                                           login_session=login_session,
                                           user=user,
                                           category=category,
                                           item=item)
                else:
                    abort(401)
            elif request.method == "POST":
                if item is not None:
                    try:
                        newOffer = Offer(name=request.form.get("name"),
                                         description=request.form.get("description"),  # noqa
                                         validity=request.form.get("validity"),
                                         item=item)
                        session.add(newOffer)
                        session.commit()
                        flash("New Offer Added!!")
                        return redirect(url_for(
                           'show_user_categories_items_details',
                           user_id=user_id,
                           category_id=category_id,
                           item_id=item_id))
                    except Exception as e:
                        abort(405)
                else:
                    abort(401)
            else:
                abort(405)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/<string:user_id>/categories/<string:category_id>/offers',
           methods=["GET", "POST"])
def delete_users_offers(user_id, category_id):
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    if user is not None:
        if user.email == login_session.get("email"):
            category = session.query(Category)\
                .filter(Category.id_ == category_id).one_or_none()
            if str(category.user_id) == str(user_id):
                if request.method == "GET":
                    items = session.query(Item)\
                        .filter(Item.category_id == category_id).all()
                    item_ids = []
                    for item in items:
                        item_ids.append(item.id_)
                    offers = session.query(Offer)\
                        .filter(Offer.item_id.in_(item_ids)).all()
                    return render_template('delete_users_offers.html',
                                           user=user,
                                           category=category,
                                           login_session=login_session,
                                           offers=offers)
                elif request.method == "POST":
                    try:
                        if request.form.get("delete") == "Delete":
                            try:
                                offer = session.query(Offer)\
                                    .filter(Offer.id_ == int(
                                        request.form.get("option")))\
                                    .one_or_none()
                                if offer is not None:
                                    session.delete(offer)
                                    session.commit()
                                    flash("Offer Deleted!!")
                                    return redirect(url_for('index'))
                                else:
                                    abort(401)
                            except Exception:
                                abort(400)
                        elif request.form.get("delete") == "Cancel":
                            return redirect(url_for('show_offers'))
                    except Exception as e:
                        abort(405)
                else:
                    abort(405)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/<string:user_id>/categories/')
def show_users_categories(user_id):

    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    if user is not None:
        if user.email == login_session.get('email'):
            categories = session.query(Category)\
                .filter(Category.user_id == user_id).all()
            return render_template('own_categories.html',
                                   categories=categories,
                                   login_session=login_session,
                                   user=user)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items')
def show_user_categories_items(user_id, category_id):
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    categories = session.query(Category)\
        .filter(Category.user_id == user_id).all()
    flag = False
    if user.email == login_session.get('email'):
        for category in categories:
            if category_id == str(category.id_):
                flag = True
                break
        if flag is True:
            category = session.query(Category)\
                .filter(Category.id_ == category_id).one()
            items = session.query(Item)\
                .filter(Item.category_id == category_id).all()
            return render_template('own_categories_items.html',
                                   category=category,
                                   login_session=login_session,
                                   user=user,
                                   items=items)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/<string:user_id>/categories/<string:category_id>/items/<string:item_id>/')  # noqa
def show_user_categories_items_details(user_id, category_id, item_id):
    flag = False
    user = session.query(User).filter(User.id_ == user_id).one_or_none()
    categories = session.query(Category)\
        .filter(Category.user_id == user_id).all()
    item = session.query(Item).filter(Item.id_ == item_id)\
        .filter(Item.category_id == category_id).one_or_none()
    offers = session.query(Offer).filter(Offer.item_id == item_id).all()
    if user.email == login_session.get('email'):
        for category in categories:
            if category_id == str(category.id_):
                flag = True
                break
        if flag is True:
            item = session.query(Item)\
                .filter(Item.id_ == item_id).one_or_none()
            if item is not None:
                if str(item.category_id) == category_id:
                    return render_template('own_categories_items_details.html',
                                           user=user,
                                           login_session=login_session,
                                           item=item,
                                           offers=offers)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/catalog/json')
def json_data():
    categories = session.query(Category).all()
    temp_response = [category.serialize for category in categories]
    for i in temp_response:
        items = session.query(Item)\
            .filter(Item.category_id == i.get("id")).all()
        temp = [item.serialize for item in items]
        i["items"] = temp

        for i in temp:
            offers = session.query(Offer)\
                .filter(Offer.item_id == i["id"]).all()
            temp2 = [offer.serialize for offer in offers]
            i["Offers"] = temp2

    response = jsonify(Category=temp_response)
    return response


if __name__ == '__main__':
    app.debug = True
    app.secret_key = SECRET_KEY
    app.run(host="0.0.0.0", port=8080)
