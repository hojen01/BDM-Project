import requests
import time
import random
import string
import re

target_address = "http://localhost"
target_port = "8080"
login_page = "/login"
application_upload_page = "/application_form"
application_upload_post = "/upload_certificate"
rego_page = "/register"

# Could have a little better regex
src_re = re.compile(r'src=[^ <>]+')
css_re = re.compile(r'type=\"text/css\"[^<>]* href=[^ <>]+')

# ----------------------

target_url = '{address}:{port}'.format(address=target_address, port=target_port)

# ----------------------------


def gen_letters():
    letters = ''
    for i in range(0, 6):
        letters += random.choice(string.ascii_lowercase)
    return letters


def gen_numbers():
    numbers = ''
    for i in range(0, 8):
        numbers += random.choice(string.digits)
    return numbers


class User(object):
    def __init__(self, username, password):
        self.session = requests.Session()
        self.resources = []
        self.username = username
        self.password = password
        self.login_details = {
            'username': self.username,
            'password': self.password
        }
        self.reg_form = self.generic_form()
        self.reg_form.update(self.login_details)

    def login(self):
        self.visit_page(login_page)
        time.sleep(3)
        return self.session.post("{url}{page}".format(url=target_url, page=login_page), self.login_details)

    def visit_page(self, page):
        r = self.session.get("{url}{page}".format(url=target_url, page=page))
        if ('Unauthorized' not in r.text):
            for x in re.findall(src_re, r.text):
                src = x.split("src=")[1].replace('"', "")
                if src not in self.resources:
                    self.session.get("{url}{page}".format(url=target_url, page=src))
                    self.resources.append(src)

            # Horrible coding below
            css_file = re.findall(css_re, r.text)[0].split("href=")[1].replace('"', "")
            if css_file not in self.resources:
                self.session.get("{url}{page}".format(url=target_url, page=css_file))
                self.resources.append(css_file)
        return r


    def enter_form(self, page, form_details):
        return self.session.post("{url}{page}".format(url=target_url, page=page), data=form_details)

    def enter_app(self, form_details, file_details):
        self.visit_page(application_upload_page)
        time.sleep(3)
        return self.session.post("{url}{page}".format(url=target_url, page=application_upload_post), data=form_details, files=file_details)

    def download_resource(self, resource):
        return self.session.get("{url}{page}".format(url=target_url, page=resource))

    def generic_form(self):
        generic = {
            'firstname': "bot" + gen_letters(),
            'lastname': gen_letters(),
            'gender': random.choice(['male', 'female', 'other']),
            'housenumber': random.choice(string.digits),
            'street': gen_letters() + " " + random.choice(['ct', 'st', 'ave', 'rd', 'dr', 'cct', 'lane']),
            'suburb': gen_letters(),
            'state': random.choice(['nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa']),
            'email': gen_letters() + "@" + random.choice(['hotmail.com', 'gmail.com', 'outlook.com', 'yahoo.com']),
            'phone': gen_numbers()
        }
        return generic

    def generic_app(self):
        generic_app = {
            'firstname': gen_letters(),
            'lastname': gen_letters(),
        }
        return generic_app

    def register(self):
        self.visit_page("/")
        time.sleep(1)
        self.visit_page(rego_page)
        time.sleep(5)
        self.enter_form(rego_page, self.reg_form)

    def invalid_register(self):
        self.reg_form['suburb'] = 'wR0ngsu8ur8'
        self.visit_page(rego_page)
        self.enter_form(rego_page, self.reg_form)
        time.sleep(1)
        self.reg_form['suburb'] =  gen_letters()
        self.reg_form['phone'] = 'invalidphone'
        self.enter_form(rego_page, self.reg_form)
        time.sleep(5)
        self.reg_form['phone'] =  gen_numbers()
        self.reg_form['firstname'] = "bot12345" + gen_letters()
        self.enter_form(rego_page, self.reg_form)
        time.sleep(3)
        self.reg_form['firstname'] = "bot" + gen_letters()
        self.reg_form['lastname'] = "123" + gen_letters()
        self.enter_form(rego_page, self.reg_form)
        time.sleep(2)
        self.reg_form['lastname'] = gen_letters()
        self.enter_form(rego_page, self.reg_form)
        time.sleep(2)
        self.reg_form['housenumber'] = gen_letters()
        self.enter_form(rego_page, self.reg_form)
        time.sleep(3)
        self.reg_form['housenumber'] = random.choice(string.digits)
        self.enter_form(rego_page, self.reg_form)


    def logout(self):
        self.visit_page('/logout')
