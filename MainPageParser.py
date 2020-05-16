import re
import requests
from bs4 import BeautifulSoup
from Worker import Worker
from Parser import Parser

MAIN_PAGE_URL = "https://server.179.ru/wiki/?page=Informatika/9B"

_main_page_parser_reload_worker = Worker()


class ContestUrls:
    def __init__(self, statements_url=None, contest_url=None,
                 results_url=None):
        self.statements_url = statements_url
        self.contest_url = contest_url
        self.results_url = results_url


class MainPageParser(Parser):
    def __init__(self):
        self.urls = None

    def set_from_server(self):
        html = requests.get(MAIN_PAGE_URL).text
        soup = BeautifulSoup(html, "html.parser")
        contest_rows = soup.find_all("tr", {"class": "userrow"})
        urls = dict()
        for row in contest_rows:
            links = list(map(lambda el: el.get("href"), row.find_all("a")))
            if len(links) == 3:
                urls[MainPageParser.get_contest_id(links[1])] = \
                    ContestUrls(*links)
        self.urls = urls
        self.save_cache()

    def get_statements_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.urls.get(contest_id, ContestUrls()).statements_url

    def get_contest_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.urls.get(contest_id, ContestUrls()).contest_url

    def get_results_url_by_id(self, contest_id):
        self.reload_worker.join()
        return self.urls.get(contest_id, ContestUrls()).results_url

    @staticmethod
    def get_contest_id(url):
        match = re.search(r"contest_id=(\d+)", url)
        return match.group(1)

    def __getattr__(self, item):
        if item == 'reload_worker':
            return _main_page_parser_reload_worker
        else:
            raise AttributeError
