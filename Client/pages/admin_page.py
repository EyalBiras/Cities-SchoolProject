import threading
import tkinter as tk
from tkinter import ttk

from networking import Command, Codes
from Client.client_socket import ClientSocket

class AdminPage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.tournament = tk.Button(self, text="Run tournament", command=self.start_tournament)
        self.tournament.pack()
        self.num_iters = 1
        self.running = False
        self.current_iter = 0
        self.lock = threading.Lock()

    def start_tournament(self):
        if self.running:
            return
        self.running = True
        self.current_iter = 0
        self.run_tournament()

    def run_tournament(self):
        _, response = self.client_socket.send_command(Command.RUN_TOURNAMENT)

        self.num_iters = int(response)
        self.num_iters = (self.num_iters ** 2 - self.num_iters) // 2 + 1

        self.progress["maximum"] = self.num_iters
        self.progress["value"] = 0

        threading.Thread(target=self.receive_updates, daemon=True).start()

        self.simulate_progress()

    def receive_updates(self):
        for _ in range(self.num_iters):
            response = self.client_socket.receive_message()
            _, response, _ = response.split("|")
            print(response)
            if response == Codes.FINISHED.value:
                self.running = False
                self.after(0, self.finish_progress)
                return

        self.running = False

    def simulate_progress(self, step: float = 0):
        if not self.running:
            return
        if step >= self.num_iters:
            return

        self.progress["value"] = step
        self.after(50, self.simulate_progress, step + 0.05)

    def finish_progress(self):
        self.progress["value"] = self.num_iters
        self.progress.update_idletasks()
