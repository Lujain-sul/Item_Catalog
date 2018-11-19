#!/usr/bin/env python3
# Development guide from udacity classroom:
# https://github.com/udacity/ud330/tree/master/Lesson4/step2

# Import nedded modules
from flask import Flask, request, make_response
from flask import jsonify, url_for, redirect, render_template, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, Item, User
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests


app = Flask(__name__)

# Connect to catalog database
# check_same_thread to resolve multi threading issue
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

# Create session object
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Client ID for OAuth2
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']


# Implement JSON endpoint for catalog
@app.route('/catalog/JSON')
def catalogJSON():
    # Get all categories from the database
    categories = session.query(Category).all()
    # Generate categories dictionry, guide from:
    # https://stackoverflow.com/questions/50011349/return-joined-tables-in-json-format-with-sqlalchemy-and-flask-jsonify
    catDictionary = dict(Category=[dict(c.serialize, items=[
        i.serialize for i in c.items]) for c in categories])
    # Convert dictionary to JSON object and send it back as response to client
    return jsonify(catDictionary)


# Implement JSON endpoint for item
@app.route('/catalog/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    # Get the required item from the database
    item = session.query(Item).filter_by(id=item_id).first()
    if item is not None:
        return jsonify(item.serialize)

    # Item does not exist
    response = make_response(json.dumps('Item does not exist.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response


# Show catalog
@app.route('/')
@app.route('/catalog/')
def viewCatalog():
    # Get all categories from the database
    categories = session.query(Category).order_by(Category.name.asc()).all()
    # Get the latest 9 added items along with their catalog information
    recentItems = session.query(Item, Category).filter(
        Item.category_id == Category.id).order_by(
            Item.addition_dt.desc()).limit(9)
    # Check that the user is authorized to manage item (add)
    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               categories=categories, items=recentItems)
    else:
        return render_template('catalog.html',
                               categories=categories, items=recentItems)


# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    # Check that the user is authorized to add an item
    if 'username' not in login_session:
        return redirect('/login')

    # After submit add item form
    if request.method == 'POST':
        # Check that there is no other item with same title
        if findItem(request.form['title'], None):
            # Use flash function to generate notifications
            flash('There exists an item with same title, nothing changed!')
            # Get the first category
            itemCategory = session.query(Category).first()
            return redirect(url_for('viewCategory',
                                    category_name=itemCategory.name))
        # The title is not found, item could be added
        else:
            # Create new item object
            newItem = Item(
                title=request.form['title'],
                description=request.form['description'],
                category_id=request.form['category_id'],
                addition_dt=datetime.datetime.now(),
                user_id=login_session['user_id'])
            # Add the item into the database and save the changes
            session.add(newItem)
            session.commit()
            flash('New item %s successfully created!' % (newItem.title))
            # Get the category of the newly added item
            # to display it to the client
            itemCategory = session.query(Category).filter_by(
                id=newItem.category_id).first()
            return redirect(url_for('viewCategory',
                                    category_name=itemCategory.name))

    # Request is to Get add page
    else:
        # Get all categories to display them in listbox to the client
        categoryList = session.query(Category).all()
        return render_template('new_item.html', categories=categoryList)


# Show category's items
@app.route('/catalog/<string:category_name>/items/')
def viewCategory(category_name):
    # Get the requested category to display it to the client
    category = session.query(Category).filter_by(name=category_name).first()
    # Get all categories to display them in navigation bar to the client
    categoryList = session.query(Category).all()
    return render_template('category.html',
                           category=category, categories=categoryList)


# Show item details
@app.route('/catalog/<string:category_name>/<string:item_title>/')
def viewItem(category_name, item_title):
    # Get the requested item to display it to the client
    categoryItem = session.query(Item).filter_by(title=item_title).first()
    # Check that the user is authorized to manage an item (edit, delete)
    if 'username' not in login_session:
        return render_template('public_item.html', item=categoryItem)
    else:
        return render_template('item.html', item=categoryItem)


# Edit an item
@app.route('/catalog/<string:item_title>/edit/', methods=['GET', 'POST'])
def editItem(item_title):
    # Check that the user is authorized to edit an item
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(title=item_title).first()
    itemCategory = session.query(Category).filter_by(
        id=editedItem.category_id).first()

    # Check that the user is the creator of the item
    if login_session['user_id'] != editedItem.user_id:
        flash('You are not authorized to edit this item!')
        return redirect(url_for('viewCategory',
                                category_name=itemCategory.name))

    # After submit edit item form
    if request.method == 'POST':
        # Check that Post request contains title
        if request.form['title']:
            # Check that there is no other item with same title
            if findItem(request.form['title'], editedItem.id):
                flash('There exists an item with same title, nothing changed!')
                return redirect(url_for('viewCategory',
                                        category_name=itemCategory.name))
            # The title is not found, item could be edited
            else:
                editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_id']:
            editedItem.category_id = request.form['category_id']

        # Update item and save changes
        session.add(editedItem)
        session.commit()
        flash('Item %s edited successfully!' % (editedItem.title))
        # Category might be updated, get the new item category
        itemCategory = session.query(Category).filter_by(
            id=editedItem.category_id).first()
        return redirect(url_for('viewCategory',
                                category_name=itemCategory.name))
    # Request is to Get edit page
    else:
        # Get all categories to display them in listbox to the client
        categoryList = session.query(Category).all()
        return render_template('edit_item.html',
                               item=editedItem, category=itemCategory,
                               categories=categoryList)


# Delete an item
@app.route('/catalog/<string:item_title>/delete/', methods=['GET', 'POST'])
def deleteItem(item_title):
    # Check that the user is authorized to delete an item
    if 'username' not in login_session:
        return redirect('/login')
    # Get the item to be deleted
    deletedItem = session.query(Item).filter_by(title=item_title).first()

    # Get the category of the intended category,
    # to display it back to the client
    itemCategory = session.query(Category).filter_by(
        id=deletedItem.category_id).first()

    # Check that the user is the creator of the item
    if login_session['user_id'] != deletedItem.user_id:
        flash('You are not authorized to delete this item!')
        return redirect(url_for('viewCategory',
                                category_name=itemCategory.name))

    # After submit delete item form
    if request.method == 'POST':
        # Delete the item and save changes
        session.delete(deletedItem)
        session.commit()
        flash('Item %s deleted successfully!' % (deletedItem.title))
        return redirect(url_for('viewCategory',
                                category_name=itemCategory.name))

    # Request is to Get delete page
    else:
        return render_template('delete_item.html', item=deletedItem)


# Check if item with same title already exists,
# if similar item's titles exists,
# there would be an issue in the routing for edit and delete
def findItem(item_title, item_id):
    if item_id is None:
        item = session.query(Item).filter_by(title=item_title).first()
    else:
        item = session.query(Item).filter(
            Item.title == item_title, Item.id != item_id).first()

    # If nothing found None is returned
    if item is None:
        return False
    return True


# Below function is called when login link is clicked, it is from:
# https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
@app.route('/login')
def showLogin():
    # Generate a random session state
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# login function from:
# https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
# it uses OAuth2 and google sign in functionality
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check access token validity
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode())
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # Create the user if not exist
    user_id = findUser(data["email"])
    if not user_id:
        user_id = addUser(login_session)
    login_session['user_id'] = user_id

    flash("You are now logged in as %s" % login_session['username'])
    return 'Welcome %s' % (login_session['username'])


# Create new user
def addUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


# Check if the user already exists
def findUser(email):
    user = session.query(User).filter_by(email=email).first()
    if user is not None:
        return user.id
    return None


# lougout function from:
# https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # Disconnect a connected user only
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Clear session variables
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have successfully been logged out.")
        # Send the response back to the client
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Run the server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
