from sap_system_refresh.src.PreSystemRefresh import *


def main():

    # Instance for class PreSystemRefresh
    preRefresh = PreSystemRefresh()

    # Step: 1 > list of users from USR02 table
    users_list = preRefresh.users_list()
    print("List of users from USR02 table =>", users_list)

    # Step: 2 > list of users whose status is already set to administrator lock
    locked_users = preRefresh.locked_users()
    print("List of users whose status is already set to administrator lock  =>", locked_users)
    f = open("locked_user_list.txt", "w")
    f.write(locked_users)
    f.close()

    # Step: 3 > Exception list from customer
    f = open("exception_users.txt", "r")
    exception_users_list = f.read()
    print("List of users that needs to be kept unlocked[exception list] =>", exception_users_list)

    # Lock all users except the list of users obtained from customer


if __name__ == '__main__':
    main()

