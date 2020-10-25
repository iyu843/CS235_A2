#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
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
title_index = {}
year_index = {}
actor_index = {}
genre_index = {}
for i in range(len(data_reader.dataset_of_movies)):
    data = {
        "idx": i,
        "title": data_reader.dataset_of_movies[i].title,
        "year": data_reader.dataset_of_movies[i].year,
        "actors": "\n".join(x.actor_full_name for x in data_reader.dataset_of_movies[i].actors),
        "genres": "\n".join(x.genre_name for x in data_reader.dataset_of_movies[i].genres),
    }
    movies_index.append(data)
    title_str = data["title"].lower()
    if title_str not in title_index:
        title_index[title_str] = []
    title_index[title_str].append(data)
    year_str = str(data["year"])
    if year_str not in year_index:
        year_index[year_str] = []
    year_index[year_str].append(data)
    for actor in data_reader.dataset_of_movies[i].actors:
        # actor_full_name is expected to identify an actor
        name = actor.actor_full_name.lower()
        if name not in actor_index:
            actor_index[name] = []
        actor_index[name].append(data)

    for genre in data_reader.dataset_of_movies[i].genres:
        # genre_name is expected to identify a genre
        name = genre.genre_name.lower()
        if name not in genre_index:
            genre_index[name] = []
        genre_index[name].append(data)


title_trie = {"*": [{}, False]}
for key in title_index:
    node = title_trie["*"]
    for i in range(len(key)):
        if key[i] in node[0]:
            node = node[0][key[i]]
        else:
            new_node = [{}, False]
            node[0][key[i]] = new_node
            node = new_node
    node[1] = True

year_trie = {"*": [{}, False]}
for key in year_index:
    node = year_trie["*"]
    for i in range(len(key)):
        if key[i] in node[0]:
            node = node[0][key[i]]
        else:
            new_node = [{}, False]
            node[0][key[i]] = new_node
            node = new_node
    node[1] = True

actor_trie = {"*": [{}, False]}
for key in actor_index:
    node = actor_trie["*"]
    for i in range(len(key)):
        if key[i] in node[0]:
            node = node[0][key[i]]
        else:
            new_node = [{}, False]
            node[0][key[i]] = new_node
            node = new_node
    node[1] = True

genre_trie = {"*": [{}, False]}
for key in genre_index:
    node = genre_trie["*"]
    for i in range(len(key)):
        if key[i] in node[0]:
            node = node[0][key[i]]
        else:
            new_node = [{}, False]
            node[0][key[i]] = new_node
            node = new_node
    node[1] = True


def get_trie_strings(trienode, prefix, rv):
    if trienode[1]:
        rv.append(prefix)
    for c in trienode[0]:
        get_trie_strings(trienode[0][c], prefix + c, rv)


def query_trie(trie, prefix):
    node = trie["*"]
    for i in range(len(prefix)):
        if prefix[i] not in node[0]:
            return []
        node = node[0][prefix[i]]
    rv = []
    get_trie_strings(node, prefix, rv)
    return rv


sortby_vals = ["title", "year", "actors", "genres"]
searchby_vals = ["title", "year", "actor", "genre"]

parameter_defaults = {
    "q": "",
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
        self._query_string = query_string.lower()
        self._results_per_page = results_per_page
        self._sortby = sortby
        self._searchby = searchby
        self._reverse = reverse

        results = None
        if searchby == "year":
            results = self.get_year_results()
        if searchby == "title":
            results = self.get_title_results()
        elif searchby == "actor":
            results = self.get_actor_results()
        elif searchby == "genre":
            results = self.get_genre_results()
        else:
            results = self.get_all_results()
        self._max_page = max(1, int(math.ceil(len(results) / results_per_page)))
        self._page_num = page_num
        if page_num > self._max_page:
            self._page_num = self._max_page
        self._results_list = self._filter(results)

    def get_all_results(self):
        title_keys = query_trie(title_trie, self.query_string)
        query_results = {x: title_index[x] for x in title_keys}
        year_keys = query_trie(year_trie, self.query_string)
        query_results.update({x: year_index[x] for x in year_keys})
        actor_keys = query_trie(actor_trie, self.query_string)
        query_results.update({x: actor_index[x] for x in actor_keys})
        genre_keys = query_trie(genre_trie, self.query_string)
        query_results.update({x: genre_index[x] for x in genre_keys})
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def get_title_results(self):
        query_keys = query_trie(title_trie, self.query_string)
        query_results = {x: title_index[x] for x in query_keys}
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def get_year_results(self):
        query_keys = query_trie(year_trie, self.query_string)
        query_results = {x: year_index[x] for x in query_keys}
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def get_actor_results(self):
        query_keys = query_trie(actor_trie, self.query_string)
        query_results = {x: actor_index[x] for x in query_keys}
        rv = {}
        for key in query_results:
            for entry in query_results[key]:
                rv[entry["idx"]] = entry
        return list(rv.values())

    def get_genre_results(self):
        query_keys = query_trie(genre_trie, self.query_string)
        query_results = {x: genre_index[x] for x in query_keys}
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
    if query_string is not None:
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
    ret = open("templates/index.html").read()
    return app.response_class(response=ret, status=200)


@app.route("/query")
def query():
    query_factory = get_query_factory_from_params()
    return jsonify(query_factory.serialize())


@app.route("/search")
def search():
    # sanitise parameters
    query_string = request.args.get("q")
    if query_string is None:
        query_string = ""
    focus_search = request.args.get("focus-search")
    if focus_search != "true":
        focus_search = False
    search_template = Template(open("templates/search_section.jinja", "r").read())
    search_section = search_template.render(query_string=query_string, focus_search=focus_search)
    query_factory = get_query_factory_from_params()
    results_section = query_factory.render_section()
    results_template = Template(open("templates/results_page.jinja", "r").read())
    return results_template.render(results_section=results_section, search_section=search_section)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("templates/css", path)


if __name__ == "__main__":
    app.run(debug=True)
