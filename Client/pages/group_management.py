import re
import tkinter as tk

from Client.group import Group
from networking import Command, Codes
from Client.client_socket import ClientSocket


class GroupManagementPage(tk.Frame):
    def __init__(self, client_socket: ClientSocket, *args, **kwargs) -> None:
        tk.Frame.__init__(self, *args, **kwargs)
        self.client_socket = client_socket
        self.selected_group = None
        self.l = None
        self.members_label = None
        self.join_requests_label = None
        if self.can_create_group():
            self.create_widgiets_for_non_grouper()
        else:
            self.create_widgiets_for_grouper()
        self.client_socket.send_command(Command.GET_FILES)

    def lift(self):
        super().lift()

    def create_widgiets_for_non_grouper(self):
        self.username_label = tk.Label(self, text="Group name:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        self.create_group_button = tk.Button(self, text="Create group", command=self.create_group)
        self.create_group_button.pack()
        self.join_button = tk.Button(self, text="Join", font=("Arial", 12), command=self.send_join_request)
        self.join_button.pack(pady=10)
        self.show_available_groups()

    def destroy_widgiets_for_non_grouper(self):
        self.username_label.destroy()
        self.username_entry.destroy()
        self.create_group_button.destroy()
        self.join_button.destroy()

    def create_widgiets_for_grouper(self):
        self.leave_group = tk.Button(self, text="Leave group", command=self.leave_group)
        self.leave_group.pack()
        self.requests_frame = tk.Frame(self)
        self.requests_frame.pack(pady=5)
        self.show_group_members()
        if self.is_group_owner():
            print("hi")
            self.show_join_requests()

    def destroy_widgiets_for_grouper(self):
        self.leave_group.destroy()
        self.requests_frame.destroy()
        if self.members_label is not None:
            self.members_label.destroy()
        if self.join_requests_label is not None:
            self.join_requests_label.destroy()

    def can_create_group(self) -> bool:
        return_code, m = self.client_socket.send_command(command=Command.IS_IN_GROUP)
        print(f"{return_code}, {m=}")
        if m != Codes.HAS_GROUP:
            return True
        return False

    def leave_group(self) -> None:
        return_code, _ = self.client_socket.send_command(command=Command.LEAVE_GROUP)
        if return_code != Codes.OK:
            return
        self.destroy_widgiets_for_grouper()
        self.create_widgiets_for_non_grouper()

    def show_available_groups(self) -> None:
        return_code, groups_message = self.client_socket.send_command(command=Command.GET_GROUPS)
        print(f"{return_code=}, {groups_message=}")

        if return_code != Codes.OK:
            return

        pattern = r"\((\w+),\[(.*?)\],(\w+)\)"

        matches = re.findall(pattern, groups_message)
        self.groups = []
        for match in matches:
            group_name, users, owner = match
            users = users.replace("'", "")
            users = users.replace(" ", "")
            self.groups.append(Group(group_name, users.split(","), owner))

        self.listbox = tk.Listbox(self, font=("Arial", 14))
        for group in self.groups:
            self.listbox.insert(tk.END, group.name)
        self.listbox.pack(pady=10)

        self.users_label = tk.Label(self, text="Select a group", font=("Arial", 12), justify="left")
        self.users_label.pack(pady=5)

        self.listbox.bind("<<ListboxSelect>>", self.show_users)

    def show_users(self, event):
        if self.l is not None:
            self.l.destroy()
        selected_group_name = self.listbox.get(self.listbox.curselection())
        self.selected_group = next(group for group in self.groups if group.name == selected_group_name)
        text = f"Users in {self.selected_group.name}:\nOwner: {self.selected_group.owner}\n"
        for user in self.selected_group.users:
            if user != self.selected_group.owner:
                text += f"{user}\n"
        self.users_label.config(text=text)


    def create_group(self) -> None:
        self.client_socket.send_command(Command.CREATE_GROUP, details=self.username_entry.get())
        self.destroy_widgiets_for_non_grouper()
        self.create_widgiets_for_grouper()

    def show_group_members(self) -> None:
        return_code, message = self.client_socket.send_command(Command.GET_GROUP_MEMBERS)
        if return_code != Codes.OK:
            return
        self.members_label = tk.Label(self, text="Group members", font=("Arial", 12), justify="left")
        self.members_label.pack(pady=5)
        text = "Your group members\n"
        members = message.split(",")
        for member in members:
            text += f"{member}\n"
        self.members_label.config(text=text)

    def is_group_owner(self) -> bool:
        return_code, m = self.client_socket.send_command(Command.IS_GROUP_OWNER)
        print(return_code, m)
        if m == Codes.GROUP_OWNER:
            return True
        return False

    def show_join_requests(self) -> None:
        return_code, join_requests = self.client_socket.send_command(Command.GET_JOIN_REQUESTS)
        print(f"{return_code=}, {join_requests=}")
        if return_code != Codes.OK:
            return

        for widget in self.requests_frame.winfo_children():
            widget.destroy()

        requesters = join_requests.split(",")
        for user in requesters:
            print(user)
            if user.strip():
                frame = tk.Frame(self.requests_frame)
                frame.pack(anchor="w", pady=2)

                label = tk.Label(frame, text=user, font=("Arial", 10))
                label.pack(side="left", padx=5)

                accept_button = tk.Button(frame, text="Accept", command=lambda u=user: self.accept_join_request(u, frame))
                accept_button.pack(side="left")

    def accept_join_request(self, request, frame):
        self.client_socket.send_command(Command.ACCEPT_JOIN_REQUEST, details=request)
        frame.destroy()
        self.destroy_widgiets_for_grouper()
        self.create_widgiets_for_grouper()

    def send_join_request(self) -> None:
        if self.selected_group is None:
            self.l = tk.Label(self, text="Select a group please!")
            self.l.pack()
            return
        self.client_socket.send_command(Command.JOIN_GROUP, self.selected_group.name)
