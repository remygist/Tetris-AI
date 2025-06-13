import random
from settings import TETROMINOS

class BagGenerator:
    def __init__(self):
        self.bag = []
        self._fill_bag()

    def _fill_bag(self):
        # one of each tetromino key, shuffled
        self.bag = list(TETROMINOS.keys())
        random.shuffle(self.bag)
    
    def get_next(self):
        if not self.bag:
            self._fill_bag()
        return self.bag.pop(0)