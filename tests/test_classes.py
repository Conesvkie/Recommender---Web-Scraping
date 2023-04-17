import unittest
from classes import *


class Test_Classes(unittest.TestCase):
    def setUp(self) -> None:
        self.movies = Movies()
        self.TV_shows = TV_shows()
        self.movies.get_movies()
        self.TV_shows.get_tv_shows()
        self.num = 2589631

    def test_movies_filter_by_year(self):
        self.movies.filter_by_year('2010')
        self.assertEqual(5, len(self.movies.movies.iloc[0]))
        self.movies.clear_filters()

    def test_movies_empty_filter(self):
        self.movies.filter_by_year('2023')
        self.assertEqual(True, self.movies.empty_filter())
        self.movies.clear_filters()

    def test_add_commas(self):
        number = self.movies.add_commas(self.num)
        self.assertEqual(number, '2,589,631')

    def test_empty_filter(self):
        self.TV_shows.filter_by_period('2023', '2024')
        self.assertEqual(self.TV_shows.empty_filter(), True)
        self.TV_shows.clear_filters()


if __name__ == "__main__":
    unittest.main()
