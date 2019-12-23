from enum import Enum
from enum import IntEnum


class Header(Enum):
    LOGIN = """<li><a href="/login">Login</a></li>"""
    REGISTER = """<li><a href="/register">Register</a></li>"""
    LOGOUT = """<li><a href="/logout">Logout</a></li>"""

    APPLICATION_FORM = """<li><a href="/application_form">New Certificate</a></li>"""
    APPLICATIONS = """<li><a href="/applications">Pending Applications</a></li>"""
    APPLICATIONS_ACCEPTED = """<li><a href="/applications_accepted">Accepted Applications</a></li>"""
    APPLICATION_HISTORY = """<li><a href="/history">Application History</a></li>"""
    USERS = """<li><a href="/users">Users</a></li>"""
    DOWNLOAD = """<li><a href="/download">Downloads</a></li>"""

    @classmethod
    def get_header(cls, access=None):

        if access is Access.ADMIN:
            return cls.USERS.value + cls.LOGOUT.value
        if access is Access.STAFF:
            return cls.APPLICATIONS.value + cls.APPLICATIONS_ACCEPTED.value + \
                   cls.APPLICATION_HISTORY.value + cls.USERS.value + cls.LOGOUT.value
        if access in Access.get_users():
            return cls.APPLICATION_FORM.value + cls.APPLICATION_HISTORY.value + cls.DOWNLOAD.value + cls.LOGOUT.value

        return cls.LOGIN.value + cls.REGISTER.value


# Alternatively use Enums and override __int__ or use self.value
class Gender(IntEnum):
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


class Access(IntEnum):
    ADMIN = 1
    STAFF = 2
    M_OFFICIATOR = 3
    F_DIRECTOR = 4
    M_PRACTITIONER = 5

    @classmethod
    def get_users(cls):
        return [cls.M_OFFICIATOR, cls.M_PRACTITIONER, cls.F_DIRECTOR]

    def __str__(self):
        switch = {
            1: "admin",
            2: "staff",
            3: "marriageoff",
            4: "fundir",
            5: "medprac"
        }
        return switch.get(self.value)


class AppType(IntEnum):
    MARRIAGE = 1
    DIVORCE = 2
    BIRTH = 3
    DEATH = 4
    FUNERAL = 5

    def __str__(self):
        switch = {
            1: "marriage",
            2: "divorce",
            3: "birth",
            4: "death",
            5: "funeral"
        }
        return switch.get(self.value)


class AppState(IntEnum):
    REVOKED = -2
    REJECTED = -1
    PENDING = 0
    ACCEPTED = 1
    INVESTIGATING = 2

    def __str__(self):
        switch = {
            -2: "revoked",
            -1: "rejected",
            0: "pending",
            1: "accepted",
            2: "investigating"
        }
        return switch.get(self.value)
