from enum import Enum

# Todo probably put these html buttons in an html file or create a new folder since we might have more
LOGIN_HEAD = """<li><a href="/login">Login</a></li>"""
REGISTER_HEAD = """<li><a href="/register">Register</a></li>"""
LOGOUT_HEAD = """<li><a href="/logout">Logout</a></li>"""
PANEL_HEAD = """<li><a href="/panel">Panel</a></li>"""


# Todo define 2 html scrollable tables to laod as the content of staff and admins for them to process apps and accounts

states = ('nsw', 'nt', 'qld', 'sa', 'tasmania', 'victoria', 'wa')


class Gender(Enum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

    def __str__(self):
        switch = {
            1: "male",
            2: "female",
            3: "other"
        }
        # It is impossible to have anything other than 1-3 so no need for default value
        return switch.get(self.value)


class Access(Enum):
    ADMIN = 1
    STAFF = 2
    MOFFICIATOR = 3
    FDIRECTOR = 4
    MPRACTITIONER = 5

    def __str__(self):
        switch = {
            1: "admin",
            2: "staff",
            3: "marriageoff",
            4: "fundir",
            5: "medprac"
        }
        return switch.get(self.value)
