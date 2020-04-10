from sap_system_refresh.src.PreSystemRefresh import *


def main():

    # -------------------- Instance for class PreSystemRefresh--------------------
    lock = PreSystemRefresh()

    # --------------------Step: 1 > Fetch list of users from USR02 table----------

    option = input("\nStep: 1 > Fetch list of users from USR02 table [proceed | cancel]: ")

    users_list = None
    while True:
        if option == "proceed":
            users_list = lock.users_list()
            print("\nList of users from USR02 table =>", users_list)
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue

    # ------------------- Step: 2 > list of users who's status is already set to administrator lock---------------

    option = input("\nStep: 2 > Fetch users who's status is already set to administrator lock [proceed | cancel]: ")

    locked_users = None
    while True:
        if option == "proceed":
            locked_users = lock.locked_users()
            print("\nList of users whose status is already set to administrator lock  =>", locked_users)
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue

    # -------------------- Step: 3 > Enter the Exception user list provided by customer-------------------------

    option = input("\nStep: 3 > Pass Exception user list to kept unlocked from administer locking [proceed | cancel]: ")

    user = None
    while True:
        if option == "proceed":
            user = input("\nEnter the list of users one by one and type [Done] once completed: ")
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue

    my_list = [user]
    while True:
        user = input()
        if user == "Done":
            break
        else:
            my_list.append(user)

    print("\nException user list entered are =>", my_list)

    # --------------------- Step: 4 > Lock all users except the list of users obtained from customer-------------

    option = input("\n Step: 4 > lock all the users before starting quality refresh [proceed | cancel]: ")

    while True:
        if option == "proceed":
            users_locked = lock.user_lock(users_list, my_list)
            print("\nLocked user's list =>", users_locked)
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue


if __name__ == '__main__':
    main()

