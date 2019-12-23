from bottle import route, get, run, post, request, redirect, static_file, response, abort
from base64 import b64encode
import os
import hashlib
import re

from backend.frame_engine import FrameEngine
from backend.db_engine import DBEngine
from backend.log_engine import LogEngine
import backend.constants as const

SESSION_COOKIE_NAME = 'session'


# Todo add a timeout to a session cookie

# Allow image loading
@route('/img/<picture>')
def serve_pictures(picture):
    return static_file(picture, root='img/')


# Allow CSS
@route('/css/<css>')
def serve_css(css):
    return static_file(css, root='css/')


"""
# Allow javascript
@route('/js/<js>')
def serve_js(js):
    return static_file(js, root='js/')
"""


# -----------------------------------------------------------------------------

# Check the credentials
def check_login(username, password):
    """Check db to see if user exists and password is correct, return true, false if not"""
    auth = False
    user_details = dEngine.get_user_details(username)
    if user_details is not None:
        auth = check_password(password, user_details[2])

    return auth


def hash_password(password):
    """Hashes password and returns the string ready for db sha256 100k times then dkf"""
    salt_length = 12
    hash_fun = 'sha256'
    n_iter = 100000  # recommended from docs

    password = password.encode()  # default utf-8
    salt = b64encode(os.urandom(salt_length))

    # decode from b64 byte_arr to utf-8 so we can store in db, change derived key length to make it faster
    return 'PBKDF2${}${}${}${}'.format(hash_fun, n_iter, salt.decode(),
                                       b64encode(
                                           hashlib.pbkdf2_hmac(hash_fun, password, salt, n_iter)).decode())


def check_password(password, hash):
    """Checks the password against a hash intended to come from db returns true if correct"""
    algo, hash_fun, n_iter, salt, hash_a = hash.split('$')
    assert algo == 'PBKDF2'

    salt = salt.encode()
    password = password.encode()
    hash_b = b64encode(hashlib.pbkdf2_hmac(hash_fun, password, salt, int(n_iter))).decode()
    assert len(hash_a) == len(hash_b)

    diff = 0
    for char_a, char_b in zip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)  # xor all chars to see if they are all the same
    return diff == 0


def check_password_strength(user, password):
    # Denies passwords less han 8 characters
    if len(password) < 8:
        return False
        # Denies passwords containing names and email names commented it, breaks something
        # elif user[1] in password or user[5].split("@") in password:
        # return False
    # Denies passwords containing only alphabetical Characters
    elif password.isalpha():
        return False
    # Denies passwords in list of most common passwords
    with open("password_check.txt") as f:
        for line in f:
            if password == line.rstrip():
                return False
    return True


def sanitize_reg(username, hash, first_name, last_name, email, access_code, house_number,
                 street, suburb, state, phone, gender):
    """Returns tuple entry for db"""
    street = "+".join(street.split())
    address = "+".join((house_number, street, suburb, state))
    return (username, hash, first_name, last_name, email, access_code, address, phone, gender,)


# Todo someone please review this for cases
def check_reg(username, password, first_name, last_name, email, access_code, house_number,
              street, suburb, state, phone, gender):
    """Check all user input fields for proper characters"""
    if not str.isalnum(username):
        return 'Invalid username.', False

    if not check_password_strength(username, password):
        return 'Password too weak.', False

    if not (str.isalpha(first_name) and str.isalpha(last_name)):
        return 'Invalid name', False

    if not str.isalpha(suburb):
        return 'Invalid suburb', False

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return 'Email format is not valid.', False

    if not str.isalnum(house_number):
        return 'Invalid house number', False

    if not re.match(r"[a-z ]+", street):
        return 'Invalid street name', False

    if access_code not in [str(e) for e in const.Access] or access_code in str(const.Access.ADMIN):
        return 'Invalid account type', False

    if state not in const.states:
        return 'Invalid state', False

    if not str.isnumeric(phone):
        return 'Invalid phone number', False

    if gender not in [str(e) for e in const.Gender]:
        return 'Gender not found', False

    return None, True


def check_unique_fields(username, email):
    """Check db for duplicate user and email return error string and False or True"""
    found_user = dEngine.get_user_details(username=username)

    if found_user is not None:
        return "Username is taken", False

    found_email = dEngine.get_user_details(email=email)
    if found_email is not None:
        return "Email already exists", False

    return None, True


# -----------------------------------------------------------------------------
# Redirect to login
@route('/')
@route('/home')
def index():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)

    if dEngine.is_already_authenticated(session_uuid) is not None:
        return fEngine.load_and_render("index", header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)
    return fEngine.load_and_render("index")


@route('/logout')
def do_logout():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    dEngine.delete_session(session_uuid)
    return fEngine.load_and_render("message", message="You have successfully logged out.")


# Display the login page
@get('/login')
def login():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    if dEngine.is_already_authenticated(session_uuid):
        return fEngine.load_and_render("message", message="Already logged in.",
                                       header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)
    return fEngine.load_and_render("login")


# Display the registration page
@get('/register')
def register():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    if dEngine.is_already_authenticated(session_uuid):
        return fEngine.load_and_render("message", message="Already logged in, please logout first.",
                                       header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)

    return fEngine.load_and_render("register", message='Create an account below.')


# Display the accounts page
@get('/accounts')
def accounts():
    return fEngine.load_and_render("accounts")


# Attempt the login
@post('/login')
def do_login():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    if dEngine.is_already_authenticated(session_uuid):
        return fEngine.load_and_render("message", message="You must logout first.",
                                       header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)

    username = request.forms.get('username')
    password = request.forms.get('password')
    auth = check_login(username, password)
    if auth:
        user_id = dEngine.get_user_details(username)[0]
        session_uuid, ts = dEngine.new_session(user_id)
        # Only create new cookie on authentication
        response.set_cookie(SESSION_COOKIE_NAME, session_uuid, expires=ts, httponly=True)
        lEngine.info("user authenticated @ {0}".format(username))
        return fEngine.load_and_render("message", message="You are in bro",
                                       header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)
    else:
        lEngine.warn("failed login attempt @ {0}".format(username))
        redirect("https://www.youtube.com/watch?v=oHg5SJYRHA0")
        # return fEngine.load_and_render("invalid", reason="Try again idiot")


# Create the account
@post('/register')
def do_register():
    username = request.forms.get('username').strip()
    password = request.forms.get('password').strip()
    first_name = str(request.forms.get('firstname').strip()).lower()
    last_name = str(request.forms.get('lastname').strip()).lower()
    email = request.forms.get('email').strip()
    account_type = str(request.forms.get('accounttype').strip()).lower()
    house_number = request.forms.get('housenumber').strip()
    street = str(request.forms.get('street').strip()).lower()
    suburb = str(request.forms.get('suburb').strip()).lower()
    state = str(request.forms.get('state').strip()).lower()
    phone = request.forms.get('phone').strip()
    gender = str(request.forms.get('gender').strip()).lower()

    # Checks all fields valid since we can go behind html and edit values
    error_str, valid = check_reg(username, password, first_name, last_name, email, account_type, house_number,
                                 street, suburb, state, phone, gender)

    if not valid:
        return fEngine.load_and_render("register", message=error_str)

    # Checks username and email to see if exists duplicate in db
    error_str, unique = check_unique_fields(username, email)

    if not unique:
        return fEngine.load_and_render("register", message=error_str)

    access_code, gender_val = None, None

    for e in const.Access:
        if str(e) == account_type:
            access_code = e.value
            break

    for e in const.Gender:
        if str(e) == gender:
            gender_val = e.value
            break

    # A little defense, should never happen
    if access_code is None and gender_val is None:
        return fEngine.load_and_render("register")

    user_entry = sanitize_reg(username, hash_password(password), first_name, last_name, email, access_code,
                              house_number, street, suburb, state, phone, gender_val)
    user_id = dEngine.set_user_details(user_entry)

    lEngine.info("User created account @ user_id: {0}".format(user_id))

    return fEngine.load_and_render("message", message="Registered successfully, please login.")


@get('/about')
def about():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    if dEngine.is_already_authenticated(session_uuid):
        return fEngine.load_and_render("about", header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD)
    return fEngine.load_and_render("about")


def restricted():
    abort(401, "Sorry, access denied.")  # or redirect to a funny page


@get('/panel')
def get_panel():
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    user = dEngine.is_already_authenticated(session_uuid)
    if user is None:
        restricted()

    username, access_code = user[1], user[6]
    # Todo go to correct panel based on access level
    if access_code == const.Access.ADMIN.value:

        all_users = dEngine.get_users_with_code_between(const.Access.MOFFICIATOR.value,
                                                        const.Access.MPRACTITIONER.value, admin=True)
        contents = ''
        for row in all_users:
            contents += """
            <tr>
                <td>{}</td>
                <td contenteditable="true">{}</td>
                <td contenteditable="true">{}</td>
                <td contenteditable="true">{}</td>
                <td contenteditable="true">{}</td>
                <td contenteditable="true">{}</td>
            </tr>""".format(*[col for col in row])

            print(row)
        return fEngine.load_and_render('admin_panel',
                                       header_buttons=const.PANEL_HEAD + const.LOGOUT_HEAD, contents=contents)

    restricted()


# -----------------------------------------------------------------------------


fEngine = FrameEngine()
dEngine = DBEngine()
lEngine = LogEngine()._logger
run(host='localhost', port=8080, debug=False)
