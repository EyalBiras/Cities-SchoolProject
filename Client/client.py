import pathlib
import socket
import ssl
import tkinter as tk

from networking import Command
from Client.pages import BattlePage
from Client.pages import CodePage
from Client.pages import GroupManagementPage
from Client.pages import LoginPage
from Client.pages import SignUpPage
from Client.pages import TournamentPage
from Client.pages.admin_page import AdminPage
from Client.client_socket import ClientSocket, SocketWrapper



class MainView(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        self.login_page = LoginPage(self.client_socket, self)
        self.code_page = CodePage(self.client_socket, self)
        self.group_page = GroupManagementPage(self.client_socket, self)
        self.tournament_page = TournamentPage(self.client_socket, self)
        self.admin_page = AdminPage(self.client_socket, self)
        self.battle_page = BattlePage(self.client_socket, self)
        self.sign_up_page = SignUpPage(self.client_socket, self)

        button_frame = tk.Frame(self)
        self.container = tk.Frame(self)
        button_frame.pack(side="top", fill="x", expand=False)
        self.container.pack(side="top", fill="both", expand=True)

        self.login_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.code_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.group_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.tournament_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.battle_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.sign_up_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.admin_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        login_page_button = tk.Button(button_frame, text="Login", command=self.create_login_page)
        code_page_button = tk.Button(button_frame, text="Code", command=self.create_code_page)
        group_page_button = tk.Button(button_frame, text="Group", command=self.create_group_page)
        tournament_page_button = tk.Button(button_frame, text="Tournament", command=self.create_tournament_page)
        battle_page_button = tk.Button(button_frame, text="Battle", command=self.create_battle_page)
        sign_up_page_button = tk.Button(button_frame, text="sign up", command=self.create_sign_up_page)
        self.admin_page_button = tk.Button(button_frame, text="Admin", command=self.create_admin_page)


        download_template_button = tk.Button(button_frame, text="download template", command=self.download_template)
        download_template_button.pack(side="left")

        self.log_out_button = tk.Button(button_frame, text="logout", command=self.logout)
        self.username_label = tk.Label(button_frame)

        login_page_button.pack(side="left")
        sign_up_page_button.pack(side="left")

        self.buttons = [code_page_button, group_page_button, tournament_page_button, battle_page_button]
        self.buttons2 = [login_page_button, sign_up_page_button]

        self.is_admin = False
        self.username_label.place(x=10, y=20)
        self.username_label.lift()
        self.login_page.lift()


    def download_template(self):
        self.client_socket.send_command(Command.DOWNLOAD_TEMPLATE)
        self.client_socket.receive_file(pathlib.Path("Template.rar"))

    def logout(self):
        self.client_socket.username = ""
        self.client_socket.password = ""
        self.username_label.pack_forget()
        for button in self.buttons:
            button.pack_forget()
        if self.is_admin:
            self.admin_page_button.pack_forget()
        for button in self.buttons2:
            button.pack(side="left")
        self.log_out_button.pack_forget()
        self.create_login_page()


    def create_admin_page(self):
        self.admin_page.destroy()
        self.admin_page = AdminPage(self.client_socket, self)
        self.admin_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.admin_page.lift()

    def create_sign_up_page(self):
        self.sign_up_page.destroy()
        self.sign_up_page = SignUpPage(self.client_socket, self)
        self.sign_up_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.sign_up_page.lift()

    def create_group_page(self):
        self.group_page.destroy()
        self.group_page = GroupManagementPage(self.client_socket, self)
        self.group_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.group_page.lift()

    def create_login_page(self):
        self.login_page.destroy()
        self.login_page = LoginPage(self.client_socket, self)
        self.login_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.login_page.lift()

    def create_code_page(self):
        self.code_page.destroy()
        self.code_page = CodePage(self.client_socket, self)
        self.code_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.code_page.lift()

    def create_tournament_page(self):
        self.tournament_page.destroy()
        self.tournament_page = TournamentPage(self.client_socket, self)
        self.tournament_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.tournament_page.lift()

    def create_battle_page(self):
        self.battle_page.destroy()
        self.battle_page = BattlePage(self.client_socket, self)
        self.battle_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.battle_page.lift()


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8081
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = context.wrap_socket(sock, server_side=False)

    sock.connect((host, port))
    s = ClientSocket(SocketWrapper(sock))
    root = tk.Tk()
    main = MainView(s, root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("700x700")
    root.mainloop()
