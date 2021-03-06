from sap_system_refresh.src.PreSystemRefresh import *


def prGreen(text):
    print("\033[92m {}\033[00m" .format(text))


def main():

    # -------------------- Instance for class PreSystemRefresh--------------------
    lock = PreSystemRefresh()

    # --------------------Step: 1 > Fetch list of users from USR02 table----------

    option = input("\nStep: 1 > Fetch list of users from USR02 table [proceed | cancel]: ")

    users_list = None
    while True:
        if option == "proceed":
            users_list = lock.users_list()
            print("\nList of users from USR02 table =>")
            prGreen(users_list)
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
            print("\nList of users whose status is already set to administrator lock  =>")
            prGreen(locked_users)
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
            user = input("\nEnter the list of users one by one and type [Done] once completed: \n")
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue 

    exception_list = [user]
    while True:
        if user == "Done":
            exception_list.pop(0)
            break
        user = input()
        if user == "Done":
            break
        else:
            exception_list.append(user)

    print("\nException user list entered are =>")
    prGreen(exception_list)

    # --------------------- Step: 4 > Lock all users except the list of users obtained from customer-------------

    option = input("\nStep: 4 > lock all the users before starting quality refresh [proceed | cancel]: ")

    user_list = [elem for elem in users_list if elem not in locked_users]

    while True:
        if option == "proceed":
            users_locked = lock.user_lock(user_list, exception_list)
            print("\nLocked user's list =>")
            prGreen(users_locked)
            break
        elif option == "cancel":
            break
        else:
            option = input("\nPlease check the option specified [proceed | cancel]: ")
            continue


if __name__ == '__main__':
    main()

