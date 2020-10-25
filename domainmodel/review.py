from datetime import datetime

from domainmodel.movie import Movie


class Review:
    _movie = None
    _review_text = None
    _rating = None

    def __init__(self, movie, review_text, rating):
        if isinstance(movie, Movie):
            self._movie = movie
        self._review_text = review_text
        if isinstance(rating, int) and 1 <= rating <= 10:
            self._rating = rating
        self._timestamp = datetime.now()

    @property
    def movie(self):
        return self._movie

    @property
    def review_text(self):
        return self._review_text

    @property
    def rating(self):
        return self._rating

    @property
    def timestamp(self):
        return self._timestamp

    def __repr__(self):
        return f"<{repr(self.movie)}, {self.review_text}, {self.rating}, {self.timestamp}>"

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        rv = self.movie == other.movie and self.review_text == other.review_text
        return rv and self.rating == other.rating and self.timestamp == other.timestamp
