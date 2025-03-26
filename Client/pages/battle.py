import pathlib
import threading
import time
import tkinter as tk
from tkinter import ttk

from networking import Codes, Command
from Client.client_socket import ClientSocket


class BattlePage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        self.selected_group = None
        username_label = tk.Label(self, text="Battle")
        username_label.pack()
        self.file_buttons = []
        self.name_frame = tk.Frame(self)
        self.name_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = 2
        self.file_frame = tk.Frame(self)
        self.file_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        self.l = None
        self.error_label = tk.Label(self, text="Please choose a group")
        self.in_battle = False
        self.battle_button = tk.Button(self, text="Battle", font=("Arial", 12), command=self.battle)
        self.battle_button.pack(pady=10)
        self.show_available_groups()
        self.buttons = []
        self.show_battles()

    def show_battles(self):
        _, m = self.client_socket.send_command(Command.IS_IN_GROUP)
        if m != Codes.HAS_GROUP:
            return
        _, m = self.client_socket.send_command(Command.GET_BATTLES)
        try:
            group_files = m.split("|")
            battles = []
            for group_file in group_files:
                group, f = group_file.split(":")
                battles.append([group, f.split(",")])
            print(f"{battles=}")
            for name, files in battles:
                btn = tk.Button(self.name_frame, text=name, command=lambda n=name, f=files: self.show_files(n, f))
                btn.pack(fill=tk.X, pady=2)
                self.buttons.append(btn)
        except Exception as e:
            return

    def show_files(self, group_name, files):
        for btn in self.file_buttons:
            btn.destroy()
        self.file_buttons.clear()
        print(group_name)
        for file in files:
            btn = tk.Button(self.file_frame, text=file, command=lambda f=file: self.download_battle(group_name, f))
            btn.pack(fill=tk.X, pady=2)
            self.file_buttons.append(btn)

    def show_available_groups(self) -> None:
        return_code, groups_message = self.client_socket.send_command(command=Command.GET_GROUPS)
        return_code, groups_message = self.client_socket.send_command(command=Command.GET_GROUPS_TO_BATTLE)
        print(f"{return_code=}, {groups_message=}")
        _, user_group = self.client_socket.send_command(command=Command.GET_USER_GROUP)
        if return_code != Codes.OK:
            return

        self.groups = groups_message.split("|")
        if user_group in self.groups:
            self.groups.remove(user_group)

        self.listbox = tk.Listbox(self, font=("Arial", 14))
        for group in self.groups:
            self.listbox.insert(tk.END, group)
        self.listbox.pack(pady=10)

        self.users_label = tk.Label(self, text="Select a group", font=("Arial", 12), justify="left")
        self.users_label.pack(pady=5)

        self.listbox.bind("<<ListboxSelect>>", self.show_users)

    def show_users(self, event):
        if self.l is not None:
            self.l.destroy()
        selected_group_name = self.listbox.get(self.listbox.curselection())
        self.selected_group = next(group for group in self.groups if group == selected_group_name)
        self.error_label.pack_forget()
        # text = f"Users in {self.selected_group.name}:\nOwner: {self.selected_group.owner}\n"
        # for user in self.selected_group.users:
        #     if user != self.selected_group.owner:
        #         text += f"{user}\n"
        # self.users_label.config(text=text)

    def handle_battle(self):
        t1 = time.perf_counter()
        return_code, _ = self.client_socket.send_command(Command.BATTLE, details=self.selected_group)
        print(time.perf_counter() - t1)
        self.in_battle = False
        self.finish_progress()

    def download_battle(self, group_name, file_name):
        return_code, _ = self.client_socket.send_command(Command.DOWNLOAD_BATTLE, details=f"{group_name}/{file_name}")
        if return_code == Codes.OK:
            self.client_socket.receive_file(pathlib.Path(f"battles/{group_name}/{file_name}"))

    def battle(self):
        if not self.selected_group:
            self.error_label.pack()
            return
        t1 = time.perf_counter()

        thread_battle = threading.Thread(target=self.handle_battle, daemon=True)
        print("t")

        self.in_battle = True
        thread_battle.start()
        print(time.perf_counter() - t1)

        self.progress["value"] = 0
        self.simulate_progress()
        while self.in_battle:
            time.sleep(0.1)
        for button in self.buttons:
            button.destroy()
        self.show_battles()


    def simulate_progress(self, step: float = 0):
        if not self.in_battle:
            return
        if step >= 2:
            return

        self.progress["value"] = step
        self.progress.update_idletasks()
        time.sleep(50/1000)
        self.simulate_progress(step + 0.05)

    def finish_progress(self):
        self.progress["value"] = 2
        self.progress.update_idletasks()