class Director:
    def __init__(self, director_full_name: str):
        if director_full_name == "" or type(director_full_name) is not str:
            self.__director_full_name = None
        else:
            self.__director_full_name = director_full_name.strip()

    @property
    def director_full_name(self) -> str:
        return self.__director_full_name

    def __repr__(self):
        return f"<Director {self.__director_full_name}>"

    def __eq__(self, other):
        # check for equality of two Director object instances by comparing the names
        return self.__director_full_name == other.__director_full_name

    def __lt__(self, other):
        # implement a sorting order defined by the name
        return self.__director_full_name < other.__director_full_name

    def __hash__(self):
        # defines which attribute is used for computing a hash value as used in set or dictionary keys
        return hash(self.__director_full_name)
