from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catagory, Item
# Imports for anti session tokens
from flask import session as login_session
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


@app.route('/')
@app.route('/home/')
def home_page():
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    catagories = session.query(Catagory).all()
    items = session.query(Item).all()
    return render_template('homepage.html', credentials=credentials, username=username, catagories=catagories, items=items)


@app.route('/<int:catagory_id>/view/')
def home_page_single(catagory_id):
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    catagories = session.query(Catagory).all()
    items = session.query(Item).all()
    return render_template('homepagesingle.html', catagory=catagory,
    catagories=catagories, credentials=credentials, username=username,
    items=items)


@app.route('/<int:item_id>/read/')
def read_item(item_id):
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('readitem.html', item=item, username=username,
    credentials=credentials)


@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/add-item/')
def add_item():
    if login_session.get('credentials') is None:
        return redirect('/')
    return render_template('additem.html')


@app.route('/add-new-item/', methods=['GET', 'POST'])
def newItem():
    if login_session.get('credentials') is None:
        return redirect('/')
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                           'description'], image=request.form['image'], catagory_id=request.form['catagory_id'])
        session.add(newItem)
        session.commit()
        flash("new item created!")
        return redirect('/')
    else:
        return render_template('additem.html')


@app.route('/<int:item_id>/delete/')
def delete(item_id):
    credentials = login_session.get('credentials')
    username = login_session.get('username')
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('delete.html', credentials=credentials,
    username=username, item=item)


@app.route('/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect('/')
    else:
        return render_template(url_for('delete.html', item_id=item_id))


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
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials'].access_token
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
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


if __name__ == '__main__':
    app.secret_key = 'zUApyycp2Hn9W4lekdEGTWmR'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
