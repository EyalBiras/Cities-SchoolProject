import logging


class TurnFilter(logging.Filter):
    def __init__(self, turn):
        super().__init__()
        self.turn = turn

    def filter(self, record):
        record.turn = self.turn
        return True
