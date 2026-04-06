import copy

class Fileparser:

    def __init__(self, file_soups):
        self.file_soups = file_soups
        self.base_file = file_soups[0][1]
        self.Duplicate_file = copy.deepcopy(self.base_file)
