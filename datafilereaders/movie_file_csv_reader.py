import csv
from domainmodel.movie import Movie
from domainmodel.actor import Actor
from domainmodel.genre import Genre
from domainmodel.director import Director


class MovieFileCSVReader:
    _dataset_of_movies = []
    _dataset_of_actors = set()
    _dataset_of_directors = set()
    _dataset_of_genres = set()

    def __init__(self, file_name: str):
        self._file_name = file_name

    @property
    def file_name(self):
        return self._file_name

    @property
    def dataset_of_movies(self):
        return self._dataset_of_movies

    @property
    def dataset_of_actors(self):
        return self._dataset_of_actors

    @property
    def dataset_of_directors(self):
        return self._dataset_of_directors

    @property
    def dataset_of_genres(self):
        return self._dataset_of_genres

    def read_csv_file(self):
        with open(self.file_name, mode="r", encoding="utf-8-sig") as csvfile:
            movie_file_reader = csv.DictReader(csvfile)
            for row in movie_file_reader:
                title = row["Title"]
                release_year = int(row["Year"])
                movie_obj = Movie(title, release_year)
                actor_names = row["Actors"].split(",")
                actors = [Actor(name) for name in actor_names]
                for actor in actors:
                    self._dataset_of_actors.add(actor)
                movie_obj.actors = actors
                genre_names = row["Genre"].split(",")
                genres = [Genre(name) for name in genre_names]
                for genre in genres:
                    self._dataset_of_genres.add(genre)
                movie_obj.genres = genres
                movie_obj.description = row["Description"]
                director = Director(row["Director"])
                self._dataset_of_directors.add(director)
                movie_obj.director = director
                movie_obj.runtime_minutes = int(row["Runtime (Minutes)"])
                self._dataset_of_movies.append(movie_obj)
