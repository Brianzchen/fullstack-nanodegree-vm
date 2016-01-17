from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random
import string
# Imports for loggin in
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

app = Flask(__name__)

engine = create_engine('sqlite:///itemlist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User helper functions for tracking the user
# ---------------------------------------------------------------------------
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
# ---------------------------------------------------------------------------


# Read related routes
# ---------------------------------------------------------------------------
# The main home page
@app.route('/')
@app.route('/home/')
def home_page():
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    catagories = session.query(Category).all()
    items = session.query(Item).all()
    for i in items:
        for c in catagories:
            if i.category_id == c.id:
                i.category_name = c.name
    return render_template('homepage.html', credentials=credentials,
                           username=username, catagories=catagories,
                           items=items)


# For vewing items in each category
@app.route('/<int:category_id>/')
def home_page_single(category_id):
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    category = session.query(Category).filter_by(id=category_id).one()
    catagories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category.id).all()
    item_length = len(items)
    return render_template('homepagesingle.html', category=category,
                           catagories=catagories, credentials=credentials,
                           username=username, items=items,
                           item_length=item_length)


# Read an individual item
@app.route('/<int:item_id>/read/')
def read_item(item_id):
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    item = session.query(Item).filter_by(id=item_id).one()
    user_id = login_session['user_id']
    return render_template('readitem.html', item=item, username=username,
                           credentials=credentials, user_id=user_id)
# ---------------------------------------------------------------------------


# Item adding related routes
# ---------------------------------------------------------------------------
# Loads page for adding an item
@app.route('/add-item/')
def add_item():
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    catagories = session.query(Category).all()
    if login_session.get('credentials') is None:
        return redirect('/')
    return render_template('additem.html', credentials=credentials,
                           username=username, catagories=catagories)


# Post request for adding an item
@app.route('/add-item/', methods=['GET', 'POST'])
def newItem():
    if login_session.get('credentials') is None:
        return redirect('/')
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                       'description'],
                       category_id=request.form['category_id'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect('/')
    else:
        return render_template('additem.html')
# ---------------------------------------------------------------------------


# Edit related routes
# ---------------------------------------------------------------------------
# Lods edit page for an item
@app.route('/<int:item_id>/edit/')
def edit(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if (login_session.get('credentials') is None or
            item.user_id != login_session['user_id']):
        return redirect('/')
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    return render_template('edititem.html', credentials=credentials,
                           username=username, item=item)


# Post request for editing an item
@app.route('/<int:item_id>/edit/', methods=['GET', 'POST'])
def edit_item(item_id):
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    if (login_session.get('credentials') is None or
            itemToEdit.user_id != login_session['user_id']):
        return redirect('/')
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        flash("Your item has successfully been modified!")
        return redirect(url_for('read_item', item_id=item_id))
    else:
        return render_template(url_for('edititem.html', item_id=item_id))
# ---------------------------------------------------------------------------


# Delete related routes
# ---------------------------------------------------------------------------
# Loads delete page for an item
@app.route('/<int:item_id>/delete/')
def delete(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if (login_session.get('credentials') is None or
            item.user_id != login_session['user_id']):
        return redirect('/')
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    return render_template('deleteitem.html', credentials=credentials,
                           username=username, item=item)


# Post request for deleting an item
@app.route('/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if (login_session.get('credentials') is None or
            itemToDelete.user_id != login_session['user_id']):
        return redirect('/')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("""You have successfully deleted the item, hope you
                don't regret it!""")
        return redirect('/')
    else:
        return render_template(url_for('deleteitem.html', item_id=item_id))
# ---------------------------------------------------------------------------


# Routes for JSONify requests
# ---------------------------------------------------------------------------
# Looking up the JSON for every item in a category
@app.route('/<int:category_id>/items/JSON')
def categoryItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Item=[i.serialize for i in items])


# Looking up a single item
@app.route('/category/item/<int:item_id>/JSON')
def ItemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)
# ---------------------------------------------------------------------------


# Account related routes
# ---------------------------------------------------------------------------
# The main login page
@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


# Logs in a user
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

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user is already
        connected.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Checks if user exists and if not create a new user for that email
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius:
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    print "done!"
    return output


# Logs the user out
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials'].access_token
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials'].access_token  # noqa
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(json.dumps(
                            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
