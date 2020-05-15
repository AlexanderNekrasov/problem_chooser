import re
import requests
from bs4 import BeautifulSoup
from Worker import Worker
from Parser import Parser

MAIN_PAGE_URL = "https://server.179.ru/wiki/?page=Informatika/9B"

_main_page_parser_reload_worker = Worker()


class MainPageParser(Parser):
    def __init__(self):
        pass

    def set_from_server(self):
        html = requests.get(MAIN_PAGE_URL).text
        soup = BeautifulSoup(html, "html.parser")
        contest_rows = soup.find_all("tr", {"class": "userrow"})
        arr = []  # [[statements, contest, results]]
        for row in contest_rows:
            links = row.find_all("a")
            if len(links) == 3:
                arr.append([links[0], links[1], links[2]])
        statements_url = dict()
        contest_url = dict()
        results_url = dict()
        for row in arr:
            contest_id = MainPageParser.get_contest_id(row[1].get("href"))
            statements_url[contest_id] = row[0].get("href")
            contest_url[contest_id] = row[1].get("href")
            results_url[contest_id] = row[2].get("href")
        self.statements_url = statements_url
        self.contest_url = contest_url
        self.results_url = results_url
        self.save_cache()

    def get_statements_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.statements_url.get(contest_id, None)

    def get_contest_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.contest_url.get(contest_id, None)

    def get_results_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.results_url.get(contest_id, None)

    @staticmethod
    def get_contest_id(s):
        match = re.search(r"contest_id=(\d+)", s)
        return match.group(1)

    def __getattr__(self, item):
        if item == 'reload_worker':
            return _main_page_parser_reload_worker
        else:
            raise AttributeError
