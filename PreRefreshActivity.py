from sap_system_refresh.pre_system_refresh.PreSystemRefresh import *

def main():

    s = PreSystemRefresh()

    users_list = s.users_list()
    print("List of users from USR02 table =>", users_list)

    f = open("locked_user_list.txt", "w")
    f.write(str(s.locked_users()))
    f.close()

    print("List of users whose status is already set to administrator lock  =>", s.locked_users())

    f = open("exception_users.txt", "r")
    exception_users_list = f.read()

    print("List of users that needs to be kept unlocked[exception list] =>", exception_users_list)


if __name__ == '__main__':
    main()

