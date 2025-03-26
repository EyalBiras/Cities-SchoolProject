import json
import pathlib
import tkinter as tk
from tkinter import ttk

from networking import Command, Codes
from Client.client_socket import ClientSocket


class TournamentPage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        username_label = tk.Label(self, text="Tournament")
        username_label.pack()
        self.show_results()
        self.current_group = ""

    def show_results(self):
        return_code, _ = self.client_socket.send_command(Command.GET_RESULTS)
        if return_code == Codes.OK:
            self.client_socket.receive_file(pathlib.Path(f"results.json"))

        try:
            with open("results.json", "r") as file:
                self.games = json.load(file)
        except Exception as e:
            return
        columns = ("Group", "Total Score", "Wins", "Losses", "Draws")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("Group", text="Group")
        self.tree.heading("Total Score", text="Total Score")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        for group, stats in self.games.items():
            self.tree.insert("", tk.END,
                             values=(group, stats["total score"], stats["wins"], stats["losses"], stats["draws"]))

        self.tree.pack(expand=True, fill="both")

        self.details_window = None
        self.tree.bind("<ButtonRelease-1>", self.on_group_click)

    def on_group_click(self, event):
        selected_item = self.tree.selection()
        group_name = self.tree.item(selected_item)["values"][0]

        if self.current_group == group_name:
            return
        self.current_group = group_name
        if self.details_window and self.details_window.winfo_exists():
            self.details_window.destroy()

        self.details_window = tk.Toplevel(self)
        self.details_window.title(f"Download Options for {group_name}")
        self.details_window.geometry("300x100")

        for group in self.games:
            if group != group_name:
                download_button = tk.Button(self.details_window, text=f"{group} download",
                                            command=lambda g1=group_name, g=group: self.download_game(g1, g))
                download_button.pack(pady=5)

    def download_game(self, group_name, enemy_name):
        self.client_socket.send_command(Command.DOWNLOAD_RESULTS_INFO, details=f"{group_name}|{enemy_name}")
        self.client_socket.receive_file(pathlib.Path(f"tournament/{group_name} vs {enemy_name}.json.gzip"))
