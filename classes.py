import random
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from urls import *
import re


class Movies():
    """ 
    This class holds all the functionalities concerning movies
    """

    imdb_top_250_movies_url = MOVIES_URL
    imdb_url = IMDB_URL

    def __init__(self) -> None:
        self.all_movies = pd.DataFrame({})
        self.movies = pd.DataFrame({})
        self.rejected_reccomendations = []

    def add_rejected(self, title) -> str:
        """
        Appends the rejected movie to rejected_reccomendations array

        Args:
            title (str): the title of the movie
        """
        self.rejected_reccomendations.append(title)

    def clear_filters(self):
        """
        Resets the movies object to all movies
        """
        self.movies = self.all_movies

    # helper methods for get_movies()
    def get_movies_info(self, scraped_movies) -> list:
        """
        Formatting the data that we got from the scraping 

        Args:
            scraped_movies (bs4.element.ResultSet): the content we get from scraping the movies

        Returns:
            list: returns lists in which the title, year and movie URl is stored from all the movies 
        """
        movies = []
        movie_url_list = []
        years = []
        for movie in scraped_movies:
            href = movie.find('a')['href']
            movie_url = self.imdb_url + href
            movie = movie.get_text().replace('\n', '')
            movie = movie.strip(' ')
            movie = movie[5:]
            movie = movie.strip(' ')
            year = movie[-5:len(movie) - 1]
            movie = movie[:-6]

            movies.append(movie)
            years.append(year)
            movie_url_list.append(movie_url)
        return movies, years, movie_url_list

    def get_ratings_info(self, scraped_ratings) -> list:
        """
        Formatting the data that we got from the scraping 

        Args:
            scraped_movies (bs4.element.ResultSet): the content we get from scraping the movies

        Returns:
            list: Returns lists in which the ratings and number of people rated is stored from all the movies
        """
        ratings = []
        people_rated = []
        for rating in scraped_ratings:
            rated_number = rating.find('strong')
            rated_number = str(rated_number)
            rated_number = rated_number[28:]
            rated_number = rated_number[:rated_number.find(
                ' ')]
            people_rated.append(rated_number)
            rating = rating.get_text().replace('\n', '')
            ratings.append(rating)
        return ratings, people_rated

    def get_movies(self) -> pd.DataFrame:
        """
        Scraping IMDB top 250 movies for title, year, movie URL, ratings of the movies and by how many people it was rated and then setting it in pandas data frame

        Returns:
            pd.DataFrame: information of all the movies
        """

        # getting the content
        page = requests.get(self.imdb_top_250_movies_url)
        soup = bs(page.content, 'html.parser')

        # scrapped movie names
        scraped_movies = soup.find_all('td', class_='titleColumn')

        titles, years, movie_urls = self.get_movies_info(scraped_movies)

        # scrap raring for movies
        scraped_ratings = soup.find_all('td', class_='ratingColumn imdbRating')

        # parse ratings
        ratings, people_rated = self.get_ratings_info(scraped_ratings)

        # setting the dictionary
        dict_data = {'Movie': titles, 'Year': years,
                     'Rating': ratings, 'Rated by': people_rated, 'Movie Url': movie_urls}

        # appending the data and setting the index to start from 1
        data = pd.DataFrame(dict_data, index=pd.RangeIndex(
            start=1, stop=251, name='Index'))

        self.all_movies = self.movies = data
        return data

    def recommend(self):
        """
        Recommends a random movie to the user

        Returns:
            pandas.core.series.Series: The recomendation for a movie
            or
            str: Empty string because no more recommendations are left
        """
        self.movies = self.movies.reset_index(drop=True)
        index = random.randint(0, len(self.movies) - 1)
        choice = self.movies.iloc[index]
        choice_title = str(self.movies.iloc[index, 0])
        if choice_title not in self.rejected_reccomendations:
            return choice
        elif len(self.rejected_reccomendations) == len(self.movies):
            print("No more reccomendations left.")
            return ""
        else:
            return self.recommend()

    def filter_by_year(self, year: str):
        """
        Filters movies by year

        Args:
            year (str): Year that we want to filter by
        """
        self.movies = self.movies.query("Year == @year")

    def filter_by_period(self, start: str, end: str):
        """
        Filters movies by period

        Args:
            start (str): start year
            end (str): end year
        """
        if start > end:
            start, end = end, start
        self.movies = self.movies.query("(Year >= @start) and (Year <= @end)")

    def add_commas(self, rated_by_int):
        """
        Helper function to sort_by_rating(), adds commas to 'Rated by' column to increase readability
        """
        item = str(rated_by_int)
        if len(item) > 6:
            item = item[:1] + ',' + item[1:4] + ',' + item[4:]
            return item
        elif len(item) > 5:
            item = item[:3] + ',' + item[3:]
            return item
        elif len(item) > 4:
            item = item[:2] + ',' + item[2:]
            return item
        else:
            return item

    def sort_by_rating(self):
        """
        Sorts the movies by ratings and how many people have rated it in descending order
        """
        # remove the commas from 'Rated by'
        self.movies['Rated by'] = self.movies['Rated by'].replace(
            ',', '', regex=True)
        # convert Rating and Rated by columns to float and int respectively
        self.movies = self.movies.astype({"Rating": float, "Rated by": int})
        # perform the sorting
        self.movies.sort_values(
            ['Rating', 'Rated by'], ascending=(False, False), inplace=True)
        # add back the commas to 'Rated by'
        self.movies['Rated by'] = self.movies['Rated by'].apply(
            lambda x: self.add_commas(x))

    def show_content(self):
        """
        Prints the movies
        """
        print(self.movies)

    def get_content(self) -> pd.DataFrame:
        """
        Gets the current movies 

        Returns:
            pd.DataFrame: current movies
        """
        return self.movies

    def get_all_content(self) -> pd.DataFrame:
        """
        Gets all the movies

        Returns:
            pd.DataFrame: all movies
        """
        return self.all_movies

    def empty_filter(self) -> bool:
        """
        Checks if we have preformed data manipulation on the movies

        Returns:
            bool
        """
        if self.movies.empty:
            return True
        else:
            return False


class TV_shows():
    """ 
    This class holds all the functionalities concerning TV-shows
    """
    imdb_top_250_tv_show_url = TV_SHOW_URL
    imdb_url = IMDB_URL

    def __init__(self) -> None:
        self.all_TV_shows = pd.DataFrame({})
        self.TV_shows = pd.DataFrame({})
        self.rejected_recommendations = []

    def add_rejected(self, title) -> str:
        """
        Appends the rejected TV-show to rejected_reccomendations array

        Args:
            title (str): the title of the TV-show
        """
        self.rejected_recommendations.append(title)

    def clear_filters(self):
        """
        Resets the TV_shows object to all TV-shows
        """
        self.TV_shows = self.all_TV_shows

    def get_tv_show_info(self, scraped_tv_shows) -> list:
        """
        Formatting the data that we got from the scraping

        Args:
            scraped_tv_shows (bs4.element.ResultSet): the content we get from scraping the TV-shows

        Returns:
            list: returns lists in which the title, year and TV-show URl is stored from all the TV-shows
        """
        tv_shows = []
        tv_shows_url_list = []
        years = []

        for tv_show in scraped_tv_shows:
            href = tv_show.find('a')['href']
            tv_shows_url = self.imdb_url + href
            tv_show = tv_show.get_text().replace('\n', '')
            tv_show = tv_show.strip(' ')
            tv_show = tv_show[5:]
            tv_show = tv_show.strip(' ')
            year = tv_show[-5:len(tv_show) - 1]
            tv_show = tv_show[:-6]

            tv_shows.append(tv_show)
            years.append(year)
            tv_shows_url_list.append(tv_shows_url)

        return tv_shows, years, tv_shows_url_list

    def get_ratings_info(self, scraped_ratings) -> list:
        """
        Formatting the data that we got from the scraping

        Args:
            scraped_ratings (bs4.element.ResultSet): the content we get from scraping the TV-shows

        Returns:
            list: returns lists in which the ratings and number of people rated is stored from all the TV-shows
        """
        ratings = []
        people_rated = []
        for rating in scraped_ratings:
            rated_number = rating.find('strong')
            rated_number = str(rated_number)
            rated_number = rated_number[28:]
            rated_number = rated_number[:rated_number.find(' ')]
            people_rated.append(rated_number)
            rating = rating.get_text().replace('\n', '')
            ratings.append(rating)
        return ratings, people_rated

    def get_tv_shows(self) -> pd.DataFrame:
        """
        Scraping IMDB top 250 TV-shows for title, year, TV-shows URL, ratings of the TV-shows and by how many people it was rated and then setting it in pandas data frame

        Returns:
            pd.DataFrame: information of all the TV-shows
        """
        # getting the content
        page = requests.get(self.imdb_top_250_tv_show_url)
        soup = bs(page.content, 'html.parser')

        # scrapped shows names
        scraped_shows = soup.find_all('td', class_='titleColumn')

        titles, years, tv_shows_url = self.get_tv_show_info(scraped_shows)

        # scrap raring for movies
        scraped_ratings = soup.find_all('td', class_='ratingColumn imdbRating')

        # parse ratings
        ratings, people_rated = self.get_ratings_info(scraped_ratings)

        # setting the dictionary
        dict_data = {'TV Show': titles, 'Year': years,
                     'Rating': ratings, 'Rated by': people_rated, 'TV Show Url': tv_shows_url}

        # appending the data and setting the index to start from 1
        data = pd.DataFrame(dict_data, index=pd.RangeIndex(
            start=1, stop=251, name='Index'))

        self.all_TV_shows = self.TV_shows = data
        return data

    def recommend(self):
        """
        Recommends a random TV-show to the user

        Returns:
            pandas.core.series.Series: The recomendation for a Tv-show
            or
            str: Empty string because no more recommendations are left
        """
        self.TV_shows = self.TV_shows.reset_index(drop=True)
        index = random.randint(0, len(self.TV_shows) - 1)
        choice = self.TV_shows.iloc[index]
        choice_title = str(self.TV_shows.iloc[index, 0])
        if choice_title not in self.rejected_recommendations:
            return choice
        elif len(self.rejected_recommendations) == len(self.TV_shows):
            print("No more reccomendations left.")
            return ""
        else:
            return self.recommend()

    def filter_by_year(self, year: str):
        """
        Filters TV_shows by year

        Args:
            year (str): Year that we want to filter by
        """
        self.TV_shows = self.TV_shows.query("Year == @year")

    def filter_by_period(self, start: str, end: str):
        """
        Filters TV-shows by period

        Args:
            start (str): start year
            end (str): end year
        """
        if start > end:
            start, end = end, start
        self.TV_shows = self.TV_shows.query(
            "(Year >= @start) and (Year <= @end)")

    def add_commas(self, rated_by_int):
        """
        Helper function to sort_by_rating(), adds commas to 'Rated by' column to increase readability
        """
        item = str(rated_by_int)
        if len(item) > 6:
            item = item[:1] + ',' + item[1:4] + ',' + item[4:]
            return item
        elif len(item) > 5:
            item = item[:3] + ',' + item[3:]
            return item
        elif len(item) > 4:
            item = item[:2] + ',' + item[2:]
            return item
        else:
            return item

    def sort_by_rating(self):
        """
        Sorts the TV-shows by ratings and how many people have rated it in descending order
        """
        # remove the commas from 'Rated by'
        self.TV_shows['Rated by'] = self.TV_shows['Rated by'].replace(
            ',', '', regex=True)
        # convert Rating and Rated by columns to float and int respectively
        self.TV_shows = self.TV_shows.astype(
            {"Rating": float, "Rated by": int})
        # perform the sorting
        self.TV_shows = self.TV_shows.sort_values(
            ['Rating', 'Rated by'], ascending=[False, False])
        # add back the commas to 'Rated by'
        self.TV_shows['Rated by'] = self.TV_shows['Rated by'].apply(
            lambda x: self.add_commas(x))

    def show_content(self):
        """
        Prints the TV-shows
        """
        print(self.TV_shows)

    def get_content(self) -> pd.DataFrame:
        """
        Gets the current TV-shows 

        Returns:
            pd.DataFrame: current TV-shows
        """
        return self.TV_shows

    def get_all_content(self) -> pd.DataFrame:
        """
        Gets all the TV-shows

        Returns:
            pd.DataFrame: all TV-shows
        """
        return self.all_TV_shows

    def empty_filter(self) -> bool:
        """
        Checks if we have preformed data manipulation on the TV-shows

        Returns:
            bool
        """
        if self.TV_shows.empty:
            return True
        else:
            return False


class Controller:
    """
    Composed of Movies and TV_shows objects and is responsible for facilitating the control-flow of the program 
    """
    __movies = Movies()
    __tv_shows = TV_shows()

    def handle_input(self):
        """
        Handles the user input and allows them to choose the type of entertainment they want to look at
        """
        print('Would you like to fetch movies or TV shows?')
        print('1. Movies', '\n2. TV shows')
        choice = str(input())
        match choice:
            case '1':
                self.__movies.get_movies()
                self.handle_data_manipulation(self.__movies)
                return
            case '2':
                self.__tv_shows.get_tv_shows()
                self.handle_data_manipulation(self.__tv_shows)
                return
            case _:
                print('Invalid input... enter 1 or 2')
                self.handle_input()
                return

    def save_data(self, filtered_df, output_name):
        """
        Saves the data to a CSV file under saved_content directory

        Args:
            filtered_df (pandas.core.series.Series): the pandas data frame
            output_name (str): name of the file
        """
        # remove special characters to be able to save file with no exceptions
        output_name = re.sub('[^A-Za-z0-9]+', '', output_name)
        filtered_df.to_csv(f'saved_content/{output_name}.csv')

    def handle_data_manipulation(self, content):
        """
        Allowas the user to perform data manipulation

        Args:
            content (object): Movies or TV-shows object
        """
        print('What data manipulation would you like to perform?')
        print('0. None', '\n1. Filter by year', '\n2. Filter by range of years',
              '\n3. Sort by rating and number of ratings (descending)', '\n4. Recommend random movie/TV show', '\n5. Clear filters')
        choice = str(input())
        match choice:
            case '0':
                content.show_content()
            case '1':
                year = str(input('Enter a year:'))
                content.filter_by_year(year)
                content.show_content()
                self.handle_data_manipulation(content)
                return
            case '2':
                start = str(input('Enter starting year:'))
                end = str(input('Enter ending year:'))
                content.filter_by_period(start, end)
                content.show_content()
                self.handle_data_manipulation(content)
                return
            case '3':
                content.sort_by_rating()
                content.show_content()
                self.handle_data_manipulation(content)
                return
            case '4':
                self.recommender_handler(content)
                self.handle_data_manipulation(content)
                return
            case '5':
                content.clear_filters()
                self.handle_data_manipulation(content)
                return
            case _:
                print('Invalid input... enter 0-5')
                self.handle_data_manipulation(content)
                return

        output_name = str(input('Enter an output file name:'))
        if content.empty_filter():
            self.save_data(content.get_all_content(), output_name)
        else:
            self.save_data(content.get_content(), output_name)

    def recommender_handler(self, content):
        """
        Handels the recommendations, gives new one if watched and adds it to a list of rejected recommenadations 

        Args:
            content (object): Movies or TV-shows object
        """
        recommendation = content.recommend()
        if not isinstance(recommendation, str):
            print(recommendation)
        else:
            return
        print('0. Exit',
              '\n1. I have seen this one, give me another recommendation')
        choice = str(input())
        match choice:
            case '0':
                return
            case '1':
                content.add_rejected(recommendation.iloc[0])
                self.recommender_handler(content)
                return
            case _:
                print('Invalid input... enter 0-1')
                self.recommender_handler(content)
                return
