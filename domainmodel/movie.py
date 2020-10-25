from domainmodel.genre import Genre
from domainmodel.actor import Actor
from domainmodel.director import Director


class Movie:
    _actors = []
    _genres = []

    def __init__(self, title: str, year: int):
        if not isinstance(title, str) or title.strip() == "":
            self._title = None
        else:
            self._title = title.strip()
        if not isinstance(year, int) or year < 1900:
            self._year = None
        else:
            self._year = year

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def description(self):
        return self._description

    @property
    def director(self):
        return self._director

    @property
    def actors(self):
        return self._actors

    @property
    def genres(self):
        return self._genres

    @property
    def runtime_minutes(self):
        return self._runtime_minutes

    """Setters"""

    @actors.setter
    def actors(self, val):
        self._actors = val

    @genres.setter
    def genres(self, val):
        self._genres = val

    @description.setter
    def description(self, val):
        if not isinstance(val, str):
            self._description = None
            return
        self._description = val.strip()

    @director.setter
    def director(self, val):
        if not isinstance(val, Director):
            self._director = None
            return
        self._director = val

    @runtime_minutes.setter
    def runtime_minutes(self, val):
        if not isinstance(val, int) or val <= 0:
            raise ValueError
        self._runtime_minutes = val

    @title.setter
    def title(self, val):
        if not isinstance(val, str) or val.strip() == "":
            self._title = None
        else:
            self._title = val

    def add_actor(self, val):
        if not isinstance(val, Actor):
            self._actors = None
            return
        if val not in self._actors:
            self._actors.append(val)

    def remove_actor(self, val):
        try:
            idx = self._actors.index(val)
            self._actors.pop(idx)
        except ValueError:
            pass

    def add_genre(self, val):
        if not isinstance(val, Genre):
            return
        if val not in self._genres:
            self._genres.append(val)

    def remove_genre(self, val):
        try:
            idx = self._genres.index(val)
            self._genres.pop(idx)
        except ValueError:
            pass

    def __repr__(self):
        return f"<Movie {self.title}, {self.year}>"

    def __lt__(self, other):
        if not type(other) == type(self):
            raise ValueError
        if self.title < other.title:
            return True
        elif self.title > other.title:
            return False
        return self.year < other.year

    def __eq__(self, other):
        if not type(other) == type(self):
            raise ValueError
        rv = self.title == other.title
        return rv and self.year == other.year

    def __hash__(self):
        return hash(self._title) + hash(self._year) * 31
