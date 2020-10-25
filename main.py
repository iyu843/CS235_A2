#!/usr/bin/env python3
from flask import Flask, request, jsonify
from jinja2 import Template
from datafilereaders.movie_file_csv_reader import MovieFileCSVReader
import os
import math

# CONSTANTS
DATA_PATH_ENV = "MOVIE_MODEL_VIEWER_DATA_PATH"
MIN_RESULTS_PER_PAGE = 5
MAX_RESULTS_PER_PAGE = 100

data_path = "./datafiles/Data1000Movies.csv"
if DATA_PATH_ENV in os.environ:
    data_path = os.environ[DATA_PATH_ENV]

data_reader = MovieFileCSVReader(data_path)
data_reader.read_csv_file()

movies_index = []
actors_index = {}
genres_index = {}
for i in range(len(data_reader.dataset_of_movies)):
    data = {
        "idx": i,
        "title": data_reader.dataset_of_movies[i].title,
        "year": data_reader.dataset_of_movies[i].year,
        "actors": ",\n".join(x.actor_full_name for x in data_reader.dataset_of_movies[i].actors),
        "genres": ",\n".join(x.genre_name for x in data_reader.dataset_of_movies[i].genres),
    }
    movies_index.append(data)
    for actor in data_reader.dataset_of_movies[i].actors:
        # actor_full_name is expected to identify an actor
        if actor.actor_full_name not in actors_index:
            actors_index[actor.actor_full_name] = []
        actors_index[actor.actor_full_name].append(data)

    for genre in data_reader.dataset_of_movies[i].genres:
        # genre_name is expected to identify a genre
        if genre.genre_name not in genres_index:
            genres_index[genre.genre_name] = []
        genres_index[genre.genre_name].append(data)


sortby_vals = ["title", "year", "actors", "genres"]
searchby_vals = ["title", "year", "actor", "genre"]

parameter_defaults = {
    "q": None,
    "page": 1,
    "num-results": 10,
    "sortby": "title",
    "searchby": None,
    "reverse": False,
}


class QueryFactory:
    _section_template = Template(open("templates/results_section.jinja", "r").read())

    def __init__(
        self,
        path,
        query_string=parameter_defaults["q"],
        page_num=parameter_defaults["page"],
        results_per_page=parameter_defaults["num-results"],
        sortby=parameter_defaults["sortby"],
        searchby=parameter_defaults["searchby"],
        reverse=parameter_defaults["reverse"],
    ):
        """generates results_list used for template creation
        NOTE: assumes some parameters are sanitised"""
        if searchby not in searchby_vals and searchby is not None:
            raise ValueError("bad searchby param")
        if sortby not in sortby_vals:
            raise ValueError("bad sortby param")
        # path important for anchor tags with different parameters
        self._path = path
        self._query_string = query_string
        self._results_per_page = results_per_page
        self._sortby = sortby
        self._searchby = searchby
        self._reverse = reverse

        results = self.get_title_results()
        if searchby == "year":
            results = self.get_year_results()
        elif searchby == "actor":
            results = self.get_actor_results()
        elif searchby == "genre":
            results = self.get_genre_results()
        self._max_page = int(math.ceil(len(results) / results_per_page))
        self._page_num = page_num
        if page_num > self._max_page:
            self._page_num = self._max_page
        self._results_list = self._filter(results)

    def get_title_results(self):
        query_results = movies_index
        return query_results

    def get_year_results(self):
        query_results = movies_index
        return query_results

    def get_actor_results(self):
        query_results = actors_index
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def get_genre_results(self):
        query_results = genres_index
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def _filter(self, results):
        tp = results[:]
        tp.sort(key=lambda x: x[self.sortby], reverse=self.reverse)
        rv = []
        for i in range((self.page_num - 1) * self.results_per_page, self.page_num * self.results_per_page):
            if i >= len(tp):
                break
            rv.append(tp[i])
        return rv

    @property
    def path(self):
        return self._path

    @property
    def query_string(self):
        return self._query_string

    @property
    def page_num(self):
        return self._page_num

    @property
    def results_per_page(self):
        return self._results_per_page

    @property
    def sortby(self):
        return self._sortby

    @property
    def searchby(self):
        return self._searchby

    @property
    def reverse(self):
        return self._reverse

    @property
    def max_page(self):
        return self._max_page

    @property
    def has_prev(self):
        return self._page_num > 1

    @property
    def section_template(self):
        return self._section_template

    @property
    def results_list(self):
        return self._results_list

    def render_section(self):
        parameters = {}
        if self.sortby != parameter_defaults["sortby"]:
            parameters["sortby"] = self.sortby
        if self.searchby != parameter_defaults["searchby"]:
            parameters["searchby"] = self.searchby
        if self.query_string != parameter_defaults["q"]:
            parameters["q"] = self.query_string
        if self.results_per_page != parameter_defaults["num-results"]:
            parameters["num-results"] = self.results_per_page
        if self.reverse != parameter_defaults["reverse"]:
            parameters["reverse"] = self.reverse
        page_hrefs = []
        for i in range(1, self.max_page + 1):
            parameters["page"] = i
            page_hrefs.append(self.path + "?" + "&".join("{}={}".format(x, parameters[x]) for x in parameters))

        return self.section_template.render(
            results_list=self.results_list, max_page=self.max_page, page_hrefs=page_hrefs, page_num=self.page_num
        )

    def serialize(self):
        return dict(
            results_list=self.results_list,
            max_page=self.max_page,
            has_prev=self.has_prev,
            page_num=self.page_num,
        )


def get_query_factory_from_params():
    factory_kwargs = {}
    query_string = request.args.get("q")
    factory_kwargs["query_string"] = query_string
    page_num = request.args.get("page")
    # sanitise page_num
    try:
        page_num = int(page_num)
        page_num = max(1, page_num)
        factory_kwargs["page_num"] = page_num
    except (TypeError, ValueError):
        page_num = None
    sortby = request.args.get("sortby")
    # sanitise sortby
    try:
        if sortby.lower() not in sortby_vals:
            raise ValueError()
        sortby = sortby.lower()
        factory_kwargs["sortby"] = sortby
    except (AttributeError, ValueError):
        sortby = None
    reverse = request.args.get("reverse")
    try:
        if reverse.lower() not in ["true", "false"]:
            raise ValueError()
        reverse = True if reverse.lower() == "true" else False
        factory_kwargs["reverse"] = reverse
    except (AttributeError, ValueError):
        reverse = None
    results_per_page = request.args.get("num-results")
    # sanitise results_per_page
    try:
        results_per_page = int(results_per_page)
        # clamp results_per_page to range
        results_per_page = max(MIN_RESULTS_PER_PAGE, min(MAX_RESULTS_PER_PAGE, results_per_page))
        factory_kwargs["results_per_page"] = results_per_page
    except (TypeError, ValueError):
        results_per_page = None
    searchby = request.args.get("searchby")
    try:
        if searchby.lower() not in searchby_vals:
            raise ValueError()
        searchby = searchby.lower()
        factory_kwargs["searchby"] = searchby
    except (AttributeError, ValueError):
        searchby = None
    return QueryFactory(request.path, **factory_kwargs)


app = Flask("Movie_Model_Viewer")


@app.route("/")
def root():
    ret = open("index.html").read()
    return app.response_class(response=ret, status=200)


@app.route("/query")
def query():
    query_factory = get_query_factory_from_params()
    return jsonify(query_factory.serialize())


@app.route("/search")
def search():
    print(request.path)
    query_factory = get_query_factory_from_params()
    results_section = query_factory.render_section()
    results_template = Template(open("templates/results_page.jinja", "r").read())
    return results_template.render(results_section=results_section)


if __name__ == "__main__":
    app.run(debug=True)
