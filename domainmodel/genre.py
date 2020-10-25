class Genre:
    def __init__(self, genre_name: str):
        if genre_name == "" or type(genre_name) is not str:
            self.__genre_name = None
        else:
            self.__genre_name = genre_name.strip()

    @property
    def genre_name(self) -> str:
        return self.__genre_name

    def __repr__(self):
        # defines the unique string representation of the object
        return f"<Genre {self.__genre_name}>"

    def __eq__(self, other):
        # check for equality of two Genre object instances by comparing the genre names
        return self.__genre_name == other.__genre_name

    def __lt__(self, other):
        # implement a sorting order defined by the genre name
        return self.__genre_name < other.__genre_name

    def __hash__(self):
        # defines which attribute is used for computing a hash value as used in set or dictionary keys
        return hash(self.__genre_name)
