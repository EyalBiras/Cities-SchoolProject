import tkinter as tk

from Client.client_socket import ClientSocket


class SignUpPage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        self.username_label = tk.Label(self, text="Userid:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self, text="Sign up", command=self.sign_up)
        self.login_button.pack()

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.client_socket.username = username
        self.client_socket.password = password
        if self.client_socket.sign_up():
            self.l = tk.Label(self, text="Signed up correctly")
            self.l.pack()
        else:
            self.l = tk.Label(self, text="Username already used!")
            self.l.pack()
