class Group:
    def __init__(self, name: str, users: list[str], owner: str) -> None:
        self.__name = name
        self.__users = users
        self.__owner = owner

    @property
    def name(self):
        return self.__name

    @property
    def users(self):
        return self.__users

    @property
    def owner(self):
        return self.__owner

    def __str__(self):
        return f"{self.__name},{self.__users},{self.__owner}"

    def __repr__(self):
        return f"Group: {self.__name},{self.__users},{self.__owner}"
