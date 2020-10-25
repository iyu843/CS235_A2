import unittest
import pytest
from domainmodel.movie import Movie
from domainmodel.actor import Actor
from domainmodel.genre import Genre
from datafilereaders.movie_file_csv_reader import MovieFileCSVReader
from domainmodel.review import Review


class MyTestCase(unittest.TestCase):
    def test_repr_review(self):
        review = Review("moana", "epic", 10)
    """
    def test_csv(self):
        reader = MovieFileCSVReader("../datafiles/Data1000Movies.csv")
        reader.read_csv_file()
        self.assertNotEqual(reader.dataset_of_movies, None)
        self.assertNotEqual(reader.dataset_of_actors, None)
        self.assertNotEqual(reader.dataset_of_directors, None)
        self.assertNotEqual(reader.dataset_of_genres, None)
    """

    def test_init(self):
        movie1 = Movie("Saw", 2004)
        self.assertEqual(repr(movie1),"<Movie Saw, 2004>")
        movie2 = Movie("", 2004)
        self.assertEqual(movie2.title, None)
        movie3 = Movie(42, 2004)
        self.assertEqual(movie3.title,None)

    def test_repr(self):
        movie1 = Movie("Saw", 2004)
        movie2 = Movie("", 2004)
        self.assertIsNone(movie2.title)
        self.assertEqual(repr(movie1), "<Movie Saw, 2004>")
        self.assertEqual(repr(movie2), "<Movie None, 2004>")

    def test_setters(self):
        movie1 = Movie("Shrek", 6969)
        movie1.genres = [Genre("Horror")]
        self.assertEqual(repr(movie1.genres),"[<Genre Horror>]")
        movie2 = Movie("Shrek 2", 6969)
        movie2.actors = [Actor("bob")]
        self.assertEqual(repr(movie2.actors),"[<Actor bob>]")

    def test_1900(self):
        movie1 = Movie("Saw", 123)
        self.assertEqual(repr(movie1), "<Movie Saw, None>")

    def test_description(self):
        movie1 = Movie("Saw", 2004)
        movie1.description = " haha saw go brr   "
        movie2 = Movie("Shrek", 6969)
        movie2.description = 1
        self.assertEqual(movie1.description,"haha saw go brr")
        self.assertEqual(movie2.description,None)

    def test_genres(self):
        movie1 = Movie("Shrek", 6969)
        genre_list = [Genre("Horror"), Genre("Horror"), Genre("Comedy"), Genre("Sci-fi"), Genre("Romance"), Genre("")]
        for genre in genre_list:
            movie1.add_genre(genre)

    def test_eq(self):
        movie1 = Movie("Saw", 2004)
        movie2 = Movie("Saw 2", 2005)
        movie3 = Movie("Saw 2", 2005)
        self.assertNotEqual(movie1, movie2)
        self.assertEqual(movie2, movie3)

    def test_lt(self):
        movie1 = Movie("Saw", 2004)
        movie2 = Movie("Saw 2", 2005)
        self.assertGreater(movie2, movie1)

    def test_hash(self):
        movie1 = Movie("Saw", 2004)
        movie2 = Movie("Saw 2", 2005)
        movie3 = Movie("Saw 2", 2005)
        self.assertEqual(hash(movie2), hash(movie3))
        self.assertNotEqual(hash(movie1), hash(movie2))

    """
    def test_add_colleague(self):
        movie1 = Movie("Angelina Jolie")
        movie2 = Movie("Saw 2")
        bradset = set()
        bradset.add(movie2)
        movie1.add_movie_colleague(movie2)
        self.assertEqual(movie1.colleague_set, bradset)

    def test_check_colleague(self):
        movie1 = Movie("Angelina Jolie")
        movie2 = Movie("Saw 2")
        movie3 = Movie("Tom Cruise")
        movie1.add_movie_colleague(movie2)
        self.assertTrue(movie1.check_if_this_movie_worked_with(movie2))
        self.assertFalse(movie1.check_if_this_movie_worked_with(movie3))
    """

if __name__ == "__main__":
    unittest.main()
