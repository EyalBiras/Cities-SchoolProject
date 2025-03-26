class UpdateFlag:
    def __init__(self) -> None:
        self.__allow = False

    def allow(self) -> None:
        self.__allow = True

    def disallow(self) -> None:
        self.__allow = False

    def is_allowed(self) -> bool:
        return self.__allow


internal_update_flag = UpdateFlag()
