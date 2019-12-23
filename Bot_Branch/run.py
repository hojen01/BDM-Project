from bottle import route, get, run, post, request, redirect, static_file, response, abort
from base64 import b64encode
import os
import hashlib
import re

from backend.constants import Header, Access, AppState, AppType, Gender
from backend.frame_engine import FrameEngine
from backend.db_engine import DBEngine
from backend.log_engine import LogEngine

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

# Allow PDF Downloads
@get('/pdf_certificates/<name>')
def serve_pdf(name):
    return static_file(name, root='pdf_certificates/')


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


def check_password(password, hash_s):
    """Checks the password against a hash intended to come from db returns true if correct"""
    algo, hash_fun, n_iter, salt, hash_a = hash_s.split('$')
    assert algo == 'PBKDF2'

    salt = salt.encode()
    password = password.encode()
    hash_b = b64encode(hashlib.pbkdf2_hmac(hash_fun, password, salt, int(n_iter))).decode()
    assert len(hash_a) == len(hash_b)

    diff = 0
    for char_a, char_b in zip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)  # xor all chars to see if they are all the same
    return diff == 0


def sanitize_reg(username, hash_s, first_name, last_name, email, access_code, house_number,
                 street, suburb, state, phone, gender):
    """Returns tuple entry for db"""
    street = "+".join(street.split())
    address = "+".join((house_number, street, suburb, state))
    return (username, hash_s, first_name, last_name, email, access_code, address, phone, gender,)


# Todo someone please review this for cases
def check_reg(username, password, first_name, last_name, email, access_code, house_number,
              street, suburb, state, phone, gender):
    """Check all user input fields for proper characters"""

    states = ('nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa')

    if not str.isalnum(username):
        return 'Invalid username.', False

    if not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}", password):
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

    if access_code not in [str(e) for e in Access] or access_code in str(Access.ADMIN):
        return 'Invalid account type', False

    if state not in states:
        return 'Invalid state', False

    if not str.isnumeric(phone):
        return 'Invalid phone number', False

    if gender not in [str(e) for e in Gender]:
        return 'Gender not found', False

    return None, True


def check_cert(first_name, last_name, app_type):
    """Check certificate upload forms"""
    if not (str.isalpha(first_name) and str.isalpha(last_name)) and len(first_name) <= 50 and len(last_name) <= 50:
        return 'Invalid name', False

    if app_type not in [str(e) for e in AppType]:
        return 'Invalid app type', False

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


def is_authenticated():
    """Checks to see if the users session cookie is in the session database and returns user_id, access enum
    and bool to check if logged if"""
    session_uuid = request.get_cookie(SESSION_COOKIE_NAME)
    val = dEngine.is_already_authenticated(session_uuid)
    if val is not None:
        return val[0], Access(val[1]), True

    return None, None, False


# -----------------------------------------------------------------------------
# Redirect to login
@route('/')
@route('/home')
def index():
    user_id, access_level, auth = is_authenticated()

    if auth:
        return fEngine.load_and_render("index", header_buttons=Header.get_header(access_level))
    return fEngine.load_and_render("index")


@route('/logout')
def do_logout():
    user_id, access_level, auth = is_authenticated()

    if auth:
        dEngine.delete_session(request.get_cookie(SESSION_COOKIE_NAME))
        return fEngine.load_and_render("message", message="You have successfully logged out.")
    return fEngine.load_and_render("message", message="You are not logged in.")


# Display the login page
@get('/login')
def login():
    user_id, access_level, auth = is_authenticated()

    if auth:
        return fEngine.load_and_render("message", message="Already logged in.",
                                       header_buttons=Header.get_header(access_level))
    return fEngine.load_and_render("login")


# Display the registration page
@get('/register')
def register():
    user_id, access_level, auth = is_authenticated()

    if auth:
        return fEngine.load_and_render("message", message="Already logged in, please logout first.",
                                       header_buttons=Header.get_header(access_level))

    return fEngine.load_and_render("register", message='Create an account below.')


# Attempt the login
@post('/login')
def do_login():
    user_id, access_level, auth = is_authenticated()
    if auth:
        return fEngine.load_and_render("message", message="You must logout first.",
                                       header_buttons=Header.get_header(access_level))

    # Todo sanitize login
    username = str(request.forms.get('username')).strip()
    password = str(request.forms.get('password')).strip()
    auth = check_login(username, password)
    if auth:
        user_entry = dEngine.get_user_details(username)
        user_id, access_code = user_entry[0], user_entry[6]

        session_uuid, ts = dEngine.new_session(user_id)
        access_level = Access(access_code)
        # Only create new cookie on authentication
        response.set_cookie(SESSION_COOKIE_NAME, session_uuid, expires=ts, httponly=True)
        return fEngine.load_and_render("message", message="Login successful.",
                                       header_buttons=Header.get_header(access_level))
    return fEngine.load_and_render("message", message="Login Unsuccessful.")


# Create the account
@post('/register')
def do_register():
    username = str(request.forms.get('username')).strip()
    password = str(request.forms.get('password')).strip()
    first_name = str(request.forms.get('firstname')).strip().lower()
    last_name = str(request.forms.get('lastname')).strip().lower()
    email = str(request.forms.get('email')).strip()
    account_type = str(request.forms.get('accounttype')).strip().lower()
    house_number = str(request.forms.get('housenumber')).strip()
    street = str(request.forms.get('street')).strip().lower()
    suburb = str(request.forms.get('suburb')).strip().lower()
    state = str(request.forms.get('state')).strip().lower()
    phone = str(request.forms.get('phone')).strip()
    gender = str(request.forms.get('gender')).strip().lower()

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

    for e in Access:
        if str(e) == account_type:
            access_code = int(e)
            break

    for e in Gender:
        if str(e) == gender:
            gender_val = int(e)
            break

    # A little defense, should never happen
    if access_code is None or gender_val is None:
        return fEngine.load_and_render("register")

    user_entry = sanitize_reg(username, hash_password(password), first_name, last_name, email, access_code,
                              house_number, street, suburb, state, phone, gender_val)
    dEngine.set_user_details(user_entry)

    return fEngine.load_and_render("message", message="Registered successfully, please login.")


@get('/about')
def about():
    user_id, access_level, auth = is_authenticated()
    if auth:
        return fEngine.load_and_render("about", header_buttons=Header.get_header(access_level))
    return fEngine.load_and_render("about")


def restricted():
    abort(401, "Sorry, access denied.")


@get('/users')
def get_users():
    user_id, access_level, auth = is_authenticated()

    if not auth and access_level is not Access.STAFF:
        if not auth and access_level is not Access.ADMIN:
            restricted()

    if access_level is Access.ADMIN:
        all_users = dEngine.get_users_with_code_between(int(Access.M_OFFICIATOR),
                                                        int(Access.M_PRACTITIONER), admin=True)

        # Here we could expand the list one index at a time and make gender readable however we can leave that
        # to the client side(javascript). Javascript is not included in this assignment

        contents = ''
        for row in all_users:
            contents += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>""".format(*[col for col in row[:-1]] + [str(Gender(row[-1]))])

        return fEngine.load_and_render('admin_users', header_buttons=Header.get_header(access_level), contents=contents)

    elif access_level is Access.STAFF:
        all_users = dEngine.get_users_with_code_between(int(Access.M_OFFICIATOR), int(Access.M_PRACTITIONER))

        contents = ''
        for row in all_users:
            contents += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>""".format(*[col for col in row[:-1]] + [str(Gender(row[-1]))])

        return fEngine.load_and_render('staff_users', header_buttons=Header.get_header(access_level), contents=contents)
    restricted()  # Should never happen


@get('/application_form')
def application_form():
    user_id, access_level, auth = is_authenticated()
    if not auth and access_level in Access.get_users():
        restricted()

    return fEngine.load_and_render('new_certificate', header_buttons=Header.get_header(access_level),
                                   message='Please fill in all fields.')

@get('/download')
def download_form():
    user_id, access_level, auth = is_authenticated()
    if not auth or access_level not in [Access.M_OFFICIATOR, Access.M_PRACTITIONER, Access.F_DIRECTOR]:
        restricted()
    return fEngine.load_and_render('download_template_certificate', header_buttons=Header.get_header(access_level), message='Please download the relevant application form.')

@post('/upload_certificate')
def upload_certificate():
    user_id, access_level, auth = is_authenticated()
    if not auth or access_level not in [Access.M_OFFICIATOR, Access.M_PRACTITIONER, Access.F_DIRECTOR]:
        restricted()

    first_name = str(request.forms.get('firstname')).lower()
    last_name = str(request.forms.get('lastname')).lower()
    app_type = str(request.forms.get('app_type')).lower()
    upload = request.files.get('upload')

    error_str, valid = check_cert(first_name, last_name, app_type)

    if not valid:
        return fEngine.load_and_render('new_certificate', header_buttons=Header.get_header(access_level),
                                       message=error_str)

    if upload is None:
        return fEngine.load_and_render('new_certificate', header_buttons=Header.get_header(access_level),
                                       message='File is required')

    name, ext = os.path.splitext(upload.filename)
    contents = upload.file.read()
    if ext not in '.pdf':
        return fEngine.load_and_render('new_certificate', header_buttons=Header.get_header(access_level),
                                       message='File type not allowed')
    app_code = None

    for e in AppType:
        if str(e) == app_type:
            app_code = int(e)
            break

    dEngine.insert_certificate(user_id, first_name, last_name, app_code, int(AppState.PENDING), contents)

    return fEngine.load_and_render('message', header_buttons=Header.get_header(access_level),
                                   message='Application Successful')


@get('/history')
def history():
    user_id, access_level, auth = is_authenticated()
    if not auth or access_level not in Access.get_users() and access_level is not Access.STAFF:
        restricted()

    if access_level in Access.get_users():
        apps = dEngine.get_certificates(user_id)
        contents = ''
        for row in apps:
            contents += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>""".format(*[col for col in row[:-1]] + [str(AppState(row[-1]))])

        return fEngine.load_and_render('history_users', header_buttons=Header.get_header(access_level),
                                       contents=contents)

    elif access_level is Access.STAFF:
        # Everything that is not pending must be touched by a staff member and so has a staff id
        apps = dEngine.get_certificates_of_state(int(AppState.PENDING), negation=True)
        contents = ''
        for row in apps:
            contents += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>""".format(*[col for col in row[:-2]] + [str(AppType(row[-2])), str(AppState(row[-1]))])

        return fEngine.load_and_render('history_staff', header_buttons=Header.get_header(access_level),
                                       contents=contents)


@get('/applications')
def applications():
    return get_application()


@get('/applications_accepted')
def applications_accepted():
    return get_application(accepted=True)


def get_application(accepted=False):
    user_id, access_level, auth = is_authenticated()
    if not auth or access_level is not Access.STAFF:
        restricted()

    if accepted:
        apps = dEngine.get_certificates_of_state(int(AppState.ACCEPTED))
    else:
        apps = dEngine.get_certificates_of_state(int(AppState.PENDING))

    contents = ''
    for row in apps:
        contents += """
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>""".format(*[col for col in row[:-1]] + [str(AppType(row[-1]))])

    if accepted:
        return fEngine.load_and_render('applications_accepted', header_buttons=Header.get_header(access_level),
                                       contents=contents)
    else:
        return fEngine.load_and_render('applications', header_buttons=Header.get_header(access_level),
                                       contents=contents)


@post('/process')
def process():
    user_id, access_level, auth = is_authenticated()
    if not auth or access_level is not Access.STAFF:
        restricted()

    # Check the app_id to be valid
    app_id = str(request.forms.get('app_id'))
    action = str(request.forms.get('action')).strip().lower()
    if not str.isnumeric(app_id):
        redirect('/applications')

    if action == 'view application':
        return application_viewer(int(app_id), access_level)

    if action == 'submit':
        app_state = str(request.forms.get('app_state')).lower()
        action_e = None
        for e in [AppState.ACCEPTED, AppState.REJECTED, AppState.INVESTIGATING]:
            if str(e) == app_state:
                action_e = e
                break

        if action_e is None:
            redirect('/applications')  # Tampering

        process_cert(int(app_id), action_e, int(user_id))

    if action == 'revoke':
        process_cert(int(app_id), AppState.REVOKED, int(user_id))

    redirect('/applications')  # If action is tampered with it will just redirect here


def process_cert(app_id, action, staff_id):
    current_code = dEngine.get_certificate_state(app_id)
    current_state = AppState(current_code[0])
    if action in [AppState.ACCEPTED, AppState.REJECTED, AppState.INVESTIGATING] and current_state is AppState.PENDING:
        dEngine.update_certificate_state(app_id, int(action), staff_id)
        redirect('/applications')

    if action is AppState.REVOKED and current_state is AppState.ACCEPTED:
        dEngine.update_certificate_state(app_id, int(action), staff_id)
        redirect('/applications_accepted')

    redirect('/applications')


def application_viewer(app_id, access_level):
    # Serve the file if there is one
    contents_bin = dEngine.serve_file(app_id)
    if contents_bin is None:
        redirect('/applications')

    pdf = b64encode(contents_bin[0]).decode()

    return fEngine.load_and_render('application_viewer', header_buttons=Header.get_header(access_level),
                                   contents=pdf, app_id=app_id)


# -----------------------------------------------------------------------------


fEngine = FrameEngine()
# Note there is no need to open and close connections all the time so it's roughly 3 times faster this way.
# If we needed other processes to write to the db then we would be forced to either:
# connection pool or open and close all the time
dEngine = DBEngine()
run(host='localhost', port=8080, debug=False)
