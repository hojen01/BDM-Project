from bots.user_specific_bots import MarriageBot, MedicalBot, FuneralBot, StaffBot


def main():

    marriage_bots = []
    medical_bots = []
    funeral_bots = []
    staff_bots = []

    '''Creation of a few Marriage bots and running simulations'''
    for x in range(0, 3):
        marriage_bots.append(MarriageBot())
    marriage_bots[0].register()
    marriage_bots[0].scenario_one()  # Performs normal action
    marriage_bots[1].register()
    marriage_bots[2].register()
    marriage_bots[2].scenario_two()  # Attempts to login with wrong password
    marriage_bots[1].scenario_one()

    '''Creation of a few Medical bots with some scenarios'''
    for x in range(0, 2):
        medical_bots.append(MedicalBot())
    medical_bots[0].invalid_register()  # Registers with invalid information types
    medical_bots[0].scenario_one()  # Attempts to upload invalid application (marriage instead of birth/death)
    medical_bots[1].register()
    medical_bots[1].scenario_two()  # Attempts to enter unauthorised pages

    '''Creation of a few Funeral bots with some scenarios'''
    for x in range(0, 2):
        funeral_bots.append(FuneralBot())
    funeral_bots[0].register()
    funeral_bots[0].scenario_one()  # Attempts application but forgets to login, forgets to upload file
    funeral_bots[1].register()
    funeral_bots[1].scenario_two()  # Attempts to make application of every type, will get some invalid app types

    '''Creation of a few Staff bots with some scenarios'''
    for x in range(0, 2):
        staff_bots.append(StaffBot())
    staff_bots[0].register()
    staff_bots[0].scenario_one()  # Logs in and takes action on a pending application
    staff_bots[1].register()
    staff_bots[1].scenario_one()  # Logs in and takes action on a pending application
    staff_bots[1].scenario_two()  # Logs in and revokes a previously accepted application

if __name__ == '__main__':
    main()
