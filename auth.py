import azure_kv

def login(user_name_in, password_in) -> bool:
    if user_name_in is None or password_in is None:
        return False
    login = azure_kv.get_secret("login")
    password = azure_kv.get_secret("password")
    if user_name_in == login and password_in == password:
        return True
    else:
        return False