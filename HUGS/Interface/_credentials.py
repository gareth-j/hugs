__all__ = ["get_login", "create_user"]

from ipywidgets import (GridspecLayout, GridBox, VBox, HBox, HTML, Layout, Text,
                        Button, Output, Checkbox, Label, Password)

from Acquire.Client import User
from HUGS.Interface import generate_password

def get_login():
    login_text = HTML(value="<b>Please click the buton below to create a login link</b>")
    username_text = Text(value=None, placeholder="username", description="Username: ")
    status_text = HTML(value=f"<font color='black'>Waiting for login</font>")
    login_button = Button(description="Login", button_style="success")
    login_link_box = Output()
    base_url = "https://hugs.acquire-aaai.com/t"
    
    user = None

    def login(a):
        global user
        user = User(username=username_text.value, identity_url=f"{base_url}/identity")
        
        with login_link_box:
            print(username_text.value)
            response = user.request_login()

        if user.wait_for_login():
            status_text.value = f"<font color='green'>Login success</font>"
        else:
            status_text.value = f"<font color='red'>Login failure</font>"

    login_button.on_click(login)
    return user, VBox(children=[username_text, login_button, status_text, login_link_box])


def create_user():
    username_box = Text(value=None, placeholder="username", description="Username: ")
    suggested_password = Label(value=f"Suggested password : {generate_password()}")
    password_box = Password(description="Password: ", placeholder="")
    conf_password_box = Password(description="Confirm: ", placeholder="")
    register_button = Button(description="Register", button_style="primary")
    status_text = HTML(value=f"<font color='blue'>Enter credentials</font>")
    output_box = Output()

    base_url = "https://hugs.acquire-aaai.com/t"

    def register_user(a):
        if password_box.value != conf_password_box.value:
            with output_box:
                status_text.value = f"<font color='red'>Passwords do not match</font>"
        else:
            result = User.register(username=username_box.value, password=password_box.value, identity_url=f"{base_url}/identity")

            with output_box:
                status_text.value = f"<font color='green'>Please scan QR code with authenticator app</font>"
                display(result["qrcode"])

    register_button.on_click(register_user)

    return VBox(children=[username_box, suggested_password, password_box, conf_password_box, register_button, status_text, output_box])

