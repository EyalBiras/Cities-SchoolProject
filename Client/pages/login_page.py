import tkinter as tk

from Client.client_socket import ClientSocket


class LoginPage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.client_socket = client_socket
        self.username_label = tk.Label(self, text="Userid:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self, text="Login", command=self.validate_login)
        self.login_button.pack()
        self.master = master

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.client_socket.username = username
        self.client_socket.password = password
        if self.client_socket.validate_user():
            for button in self.master.buttons:
                button.pack(side="left")
            self.master.log_out_button.pack(side="right")
            self.master.username_label.pack(side="right")
            self.master.username_label.config(text=f"{username}")
            if username == "admin":
                self.master.is_admin = True
                self.master.admin_page_button.pack(side="left")
            else:
                self.master.is_admin = False

            for button in self.master.buttons2:
                button.pack_forget()
            self.master.create_group_page()
            # self.master.is_logged_in = True
            # self.l = tk.Label(self, text="Correct!")
            # self.l.pack()
        else:
            self.master.is_logged_in = False
            self.l = tk.Label(self, text="Incorrect username or password!")
            self.l.pack()
