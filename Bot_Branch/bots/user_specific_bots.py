from .virtual_users_engine import User
import time
import re
import random

applications_page = "/applications"
accepted_aps_page = "/applications_accepted"
process_page = "/process"
users_page = "/users"
history_page = "/history"

class MarriageBot(User):

    bot_counter = 0

    def __init__(self):
        MarriageBot.bot_counter += 1
        self.username = 'botmar' + str(MarriageBot.bot_counter)
        self.password = 'B0tMarriage' + str(MarriageBot.bot_counter)
        super().__init__(self.username, self.password)
        self.reg_form['accounttype'] = 'marriageoff'
        self.app_form = self.generic_app()
        self.app_file = None

    def certificate(self, app_type):
        if app_type == 'marriage':
            self.app_form['app_type'] = 'marriage'
            self.app_file = {'upload': open('./pdf_certificates/marriage.pdf', 'rb')}
        elif app_type == 'divorce':
            self.app_form['app_type'] = 'divorce'
            self.app_file = {'upload': open('./pdf_certificates/divorce.pdf', 'rb')}
        else:
            return 'Invalid Application Type'

    # Performs valid actions
    def scenario_one(self):
        self.visit_page("/home")
        time.sleep(1)
        self.login()
        time.sleep(1)
        self.visit_page("/download")
        time.sleep(1)
        self.visit_page("/application_form")
        time.sleep(1)
        self.visit_page("/download")
        time.sleep(1)
        self.download_resource("/pdf_certificates/marriage.pdf")
        time.sleep(1)
        self.certificate("marriage")
        self.enter_app(self.app_form, self.app_file)
        self.visit_page("/history")
        time.sleep(1)
        self.logout()

    # Attempts to login with the wrong password
    def scenario_two(self):
        self.visit_page("/home")
        time.sleep(1)
        self.visit_page("/about")
        time.sleep(1)
        self.login_details['password'] = "bottomMarried555"
        self.login()
        time.sleep(1)
        self.login_details['password'] = self.password
        self.login()
        time.sleep(1)
        self.certificate("divorce")
        self.enter_app(self.app_form, self.app_file)
        self.certificate("marriage")
        self.enter_app(self.app_form, self.app_file)
        self.visit_page("/history")
        time.sleep(1)
        self.logout()


class MedicalBot(User):

    bot_counter = 0

    def __init__(self):
        MedicalBot.bot_counter += 1
        self.username = 'botmed' + str(MedicalBot.bot_counter)
        self.password = 'B0tMedical' + str(MedicalBot.bot_counter)
        super().__init__(self.username, self.password)
        self.reg_form['accounttype'] = 'medprac'
        self.app_form = self.generic_app()
        self.app_file = None

    def certificate(self, app_type):
        if app_type == 'birth':
            self.app_form['app_type'] = 'birth'
            self.app_file = {'upload': open('./pdf_certificates/birth.pdf', 'rb')}
        elif app_type == 'death':
            self.app_form['app_type'] = 'death'
            self.app_file = {'upload': open('./pdf_certificates/death.pdf', 'rb')}
        else:
            return 'Invalid Application Type'

    # Attempts to upload an invalid application type
    def scenario_one(self):
            self.visit_page("/home")
            time.sleep(1)
            self.login()
            time.sleep(1)
            self.visit_page("/application_form")
            time.sleep(1)
            self.certificate("birth")
            self.enter_app(self.app_form, self.app_file)
            time.sleep(1)
            self.visit_page("/history")
            time.sleep(1)
            self.download_resource("/pdf_certificates/marriage.pdf")
            time.sleep(1)
            self.certificate("marriage")
            self.enter_app(self.app_form, self.app_file)
            time.sleep(1)
            self.certificate("death")
            self.enter_app(self.app_form, self.app_file)
            time.sleep(1)
            self.visit_page("/history")
            time.sleep(1)
            self.visit_page("/about")
            self.logout()

    # Attempts to go to unauthorised webpages
    def scenario_two(self):
        self.visit_page("/applications")
        time.sleep(1)
        self.visit_page("/login")
        time.sleep(3)
        self.visit_page("/users")
        time.sleep(3)
        self.visit_page("/home")
        time.sleep(3)
        self.visit_page("/login")
        time.sleep(1)
        self.login()
        time.sleep(3)
        self.certificate("death")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(1)
        self.certificate("birth")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(1)
        self.visit_page("/history")
        time.sleep(1)
        self.logout()


class FuneralBot(User):

    bot_counter = 0

    def __init__(self):
        FuneralBot.bot_counter += 1
        self.username = 'botfun' + str(FuneralBot.bot_counter)
        self.password = 'B0tFuneral' + str(FuneralBot.bot_counter)
        super().__init__(self.username, self.password)
        self.reg_form['accounttype'] = 'fundir'
        self.app_form = self.generic_app()
        self.app_file = None

    def certificate(self, app_type):
        if app_type == 'funeral':
            self.app_form['app_type'] = 'funeral'
            self.app_file = {'upload': open('./pdf_certificates/funeral.pdf', 'rb')}
        else:
            return 'Invalid Application Type'

    def scenario_one(self):
        # Make application but forgot to upload file
        # Make application but forgot to login
        self.login()
        time.sleep(1)
        self.visit_page('/about')
        time.sleep(3)
        self.certificate("funeral")
        self.app_file = None
        self.enter_app(self.app_form, self.app_file)
        time.sleep(2)
        self.app_file = {'upload': open('./pdf_certificates/funeral.pdf', 'rb')}
        self.enter_app(self.app_form, self.app_file)
        time.sleep(3)
        self.logout()
        self.enter_app(self.app_form, self.app_file)
        time.sleep(3)
        self.login()
        self.certificate("funeral")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(2)
        self.visit_page('/history')
        time.sleep(3)
        self.logout

    # Try to make application of every type
    def scenario_two(self):
        self.login()
        self.download_resource("/pdf_certificates/marriage.pdf")
        self.download_resource("/pdf_certificates/death.pdf")
        time.sleep(1)
        self.certificate("marriage")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(2)
        self.certificate("death")
        self.enter_app(self.app_form, self.app_file)
        self.visit_page('/history')
        time.sleep(3)
        self.download_resource("/pdf_certificates/birth.pdf")
        self.download_resource("/pdf_certificates/funeral.pdf")
        self.certificate("birth")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(1)
        self.certificate("funeral")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(4)
        self.download_resource("/pdf_certificates/divorce.pdf")
        self.certificate("divorce")
        self.enter_app(self.app_form, self.app_file)
        time.sleep(1)
        self.visit_page('/history')
        self.visit_page('/home')
        time.sleep(1)
        self.logout()


class StaffBot(User):

    bot_counter = 0

    def __init__(self):
        StaffBot.bot_counter += 1
        self.username = 'botstaff' + str(StaffBot.bot_counter)
        self.password = 'B0tStaff' + str(StaffBot.bot_counter)
        super().__init__(self.username, self.password)
        self.reg_form['accounttype'] = 'staff'
        self.app_form = self.generic_app()
        self.app_file = None

    def scan_ap_ids(self, text):
        apids = []
        x = re.compile(r'<tr>[^<]*<td>[0-9]+</td>')
        for ap_id_row in re.findall(x, text):
            ap_id = ""
            seen_num = False
            for char in ap_id_row:
                if char.isdigit():
                    seen_num = True
                    ap_id = ap_id + char
                elif seen_num:
                    break
            apids.append(ap_id)
        return apids

<<<<<<< HEAD
=======
    def prepare_application(self, pending):
        app_id = 0
        app_state = None
        if pending:
            if len(self.scan_ap_ids(self.visit_page(applications_page).text)) != 0:
                app_id = random.choice(self.scan_ap_ids(self.visit_page(applications_page).text))
            app_state = random.choice(["accepted", "rejected", "investigating"])
            app_action = random.choice(["Submit", "View Application"])
        else:
            if len(self.scan_ap_ids(self.visit_page(accepted_aps_page).text)) != 0:
                app_id = random.choice(self.scan_ap_ids(self.visit_page(accepted_aps_page).text))
            app_action = random.choice(["View Application", "Revoke"])
        form = {
            "app_id": app_id,
            "app_state": app_state,
            "action": app_action
        }

        return form

>>>>>>> 0586841983c72889d9469609adacbdf6db2941d2
    # Logs on and views an application and acts in some way. If no applications they simply check the users
    def scenario_one(self):
        self.visit_page("/")
        time.sleep(1 + random.random())
        self.login()
        time.sleep(1 + random.random())
        if len(self.scan_ap_ids(self.visit_page(applications_page).text)) > 0:
            time.sleep(2 + random.random())
            application = self.prepare_application(True)
            application["action"] = "View Application"
            self.enter_form(process_page, application)
            time.sleep(3 + random.random())
            self.visit_page(applications_page)
            time.sleep(1+random.random())
            application["action"] = "Submit"
            self.enter_form(process_page, application)
            time.sleep(2+random.random())
            self.visit_page(accepted_aps_page)
        else:
            self.visit_page(users_page)
        time.sleep(1+random.random())
        self.logout()

    # Goes through looks at a previously approved application and revokes it. If none just goes to the home page
    def scenario_two(self):
        self.visit_page("/")
        time.sleep(1 + random.random())
        self.login()
        time.sleep(1 + random.random())
        if len(self.scan_ap_ids(self.visit_page(accepted_aps_page).text)) > 0:
            time.sleep(2 + random.random())
            application = self.prepare_application(False)
            application["action"] = "View Application"
            self.enter_form(process_page, application)
            time.sleep(3 + random.random())
            self.visit_page(accepted_aps_page)
            time.sleep(1+random.random())
            application["action"] = "Revoke"
            self.enter_form(process_page, application)
            time.sleep(2+random.random())
            self.visit_page(history_page)
        else:
            self.visit_page("/")
        time.sleep(1+random.random())
        self.logout()
