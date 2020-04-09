from sap_system_refresh.src.PreSystemRefresh import *


def main():

    # -------------------- Instance for class PreSystemRefresh--------------------
    lock = PreSystemRefresh()

    # --------------------Step: 1 > Fetch list of users from USR02 table----------

    option = input("Step: 1 > Fetch list of users from USR02 table: [proceed | cancel]\n")

    users_list = None
    if option == "proceed":
        users_list = lock.users_list()
        print("List of users from USR02 table =>", users_list)
    elif option == "cancel":
        pass
    else:
        print("Please check the option specified [proceed | cancel]")

    # ------------------- Step: 2 > list of users who's status is already set to administrator lock---------------

    option = input("Step: 2 > Fetch users who's status is already set to administrator lock [proceed | cancel]:\n")

    locked_users = None
    if option == "proceed":
        locked_users = lock.locked_users()
        print("List of users whose status is already set to administrator lock  =>", locked_users)
    elif option == "cancel":
        pass
    else:
        print("Please check the option specified [proceed | cancel]")

    # -------------------- Step: 3 > Enter the Exception user list provided by customer-------------------------

    option = input("Step: 3 > Pass Exception user list: [proceed | cancel]\n")
    if option == "proceed":
        user = input("Step: 3 > Enter the Exception user list to kept unlocked. Once done enter [Done] :\n")

        my_list = [user]
        while True:
            user = input()
            if user == "Done":
                break
            else:
                my_list.append(user)

        print("Exception user list entered are =>", my_list)
    elif option == "cancel":
        pass
    else:
        print("Please check the option specified [proceed | cancel]")

    # --------------------- Step: 4 > Lock all users except the list of users obtained from customer-------------

    option = input("Proceed to lock the users with exception to the user list provided: [proceed | cancel]\n")

    if option == "proceed":
        users_locked = lock.user_lock(users_list, locked_users)
        print("Locked user's list =>", users_locked)
    elif option == "cancel":
        pass
    else:
        print("Please check the option specified [proceed | cancel]")


if __name__ == '__main__':
    main()

