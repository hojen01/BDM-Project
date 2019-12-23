from datetime import datetime, timedelta
import sqlite3
import uuid
import settings

# Todo add all methods related to db and use it like the frame engine
"""If it hasn't got a query it does not go in here"""

# # Todo change this to something stronger before submission password is 1234
ADMIN_ENTRY = ('admin', 'PBKDF2$sha256$100000$1ZfvfrPhCJlBxtEW$GE1ebBnw+ZshnROY1S28/gIKM2pThPq22Zc1siwitTI=',
               'john', 'doe',
               'john.doe@gmail.com', 1, '11+theloststreet+nsw', '0101010101', 3)


class DBEngine(object):
    def __init__(self):
        # Todo add exception handling for db in use
        self._connection = sqlite3.connect(settings.DB_FILE)
        self._curr = self._connection.cursor()
        self.init_db()

    def __del__(self):
        self._connection.close()

    def init_db(self):
        """ Create db from scratch if not already there"""

        # Create user db
        self._curr.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                hash VARCHAR(100) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                access_code INTEGER NOT NULL,
                address VARCHAR(200) NOT NULL,
                phone VARCHAR(16) NOT NULL,
                gender INTEGER NOT NULL
            )""")

        # Todo add more session fields eg ip and more security
        # Create session cookie db
        self._curr.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_uuid CHAR(36) PRIMARY KEY,
                expires_at TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )""")

        # Todo create application db
        """Possibly application id, state(revoked, accepted, waiting) etc etc"""
        """Coroner investigation required is only for deaths"""
        self._curr.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                app_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                app_type VARCHAR(50) NOT NULL,
                app_state VARCHAR(50) NOT NULL,
                coroner_inv VARCHAR(50) NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)

            )""")
        self._curr.execute("""SELECT * FROM users 
                                WHERE users.username=? AND users.hash=? AND users.first_name=? AND
                                users.last_name=? AND users.email=? AND users.access_code=? AND 
                                users.address=? AND users.phone=? AND users.gender=?""", ADMIN_ENTRY)

        if self._curr.fetchone() is None:
            self.set_user_details(ADMIN_ENTRY)

    def reset_db(self):
        """Resets database for administrators"""

        self._curr.execute("DROP TABLE IF EXISTS users")
        self._curr.execute("DROP TABLE IF EXISTS sessions")
        self._curr.execute("DROP TABLE IF EXISTS applications")
        self.init_db()

    def get_application_details(self, username=None, user_id=None):
        """Returns user details if username or user_id or email matches else None"""

        # Just in case, so you can save time and return faster however they should never be both none
        if user_id is None and username is None:
            return None

        self._curr.execute(
            "SELECT * FROM applications JOIN users USING user_id WHERE applications.user_id = ? OR users.username = ?",
            (user_id, username))
        return self._curr.fetchone()

    def get_user_details(self, username=None, user_id=None, email=None):
        """Returns user details if username or user_id or email matches else None"""

        if user_id is None and username is None and email is None:
            return None

        self._curr.execute("SELECT * FROM users WHERE users.user_id = ? OR users.username = ? OR users.email = ? ",
                           (user_id, username, email))
        return self._curr.fetchone()

    def get_users_with_code_between(self, access_code_a, access_code_b, admin=False):
        """Returns all users with access code between two values, inclusive"""
        if admin:
            self._curr.execute("""SELECT users.user_id, users.email, users.access_code, users.address, users.phone, users.gender 
                                    FROM users WHERE users.access_code >= ? AND users.access_code <= ? """,
                               (access_code_a, access_code_b))
        else:
            self._curr.execute("""SELECT * FROM users WHERE users.access_code >= ? AND users.access_code <= ? """,
                               (access_code_a, access_code_b))

        return self._curr.fetchall()

    def set_user_details(self, user_entry, modify_id=None):
        """Returns new user key if insert, returns nothing if update
            Tuple does not contain user_id, if modify pass in id, if insert id will be generated"""

        if modify_id is not None:
            self._curr.execute(
                """UPDATE users SET username=?,hash=?,first_name=?,last_name=?,email=?,access_code=?,address=?phone=?,gender=?
                    WHERE users.user_id = ?)""", user_entry + (modify_id,))

        else:
            # Todo add exception for non-unique username and email this throws an Integrity Error
            self._curr.execute(
                """INSERT INTO users(username, hash, first_name, last_name, email, access_code, address, phone, gender)
                    VALUES (?,?,?,?,?,?,?,?,?)""", user_entry)
        self._connection.commit()
        return self._curr.lastrowid

    def new_session(self, user_id, days_to_expire=7):
        """Generates a new session cookie value and inserts it, returns the value with intent of sending to user"""

        session_uuid = str(uuid.uuid4())
        ts = datetime.now() + timedelta(days=days_to_expire)
        self._curr.execute("INSERT INTO sessions VALUES (?, ?, ?)", (session_uuid, ts, user_id))
        self._connection.commit()
        return session_uuid, ts

    def is_already_authenticated(self, session_uuid):
        """Returns all user details if the user has an active session"""
        # Todo check session_uuid before it goes into the database
        if session_uuid is None:
            return session_uuid

        now = str(datetime.now())
        self._curr.execute("""SELECT users.* FROM users, sessions 
        WHERE sessions.session_uuid = ? AND sessions.expires_at > ?""", (session_uuid, now))

        return self._curr.fetchone()

    def delete_session(self, session_uuid):
        """Deletes a session from the database"""
        self._curr.execute("""DELETE FROM sessions WHERE sessions.session_uuid = ? """, (session_uuid,))
        self._connection.commit()

    def delete_all_sessions(self, user_id):
        """Deletes all sessions for the user id (logs out from all devices associated with that user)"""
        self._curr.execute("""DELETE FROM sessions WHERE sessions.user_id = ? """, (user_id,))
        self._connection.commit()

    # Used for testing
    def get_all(self):
        """Get all db contents generator returns tuples"""

        self._curr.execute("SELECT * FROM users")
        for row in self._curr.fetchall():
            yield row

        self._curr.execute("SELECT * FROM sessions")
        for row in self._curr.fetchall():
            yield row

    # Used for testing
    def get_all_tables(self):
        """Get all db contents generator returns tuples"""

        self._curr.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
        for table in self._curr.fetchall():
            yield table
