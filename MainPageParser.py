from bs4 import BeautifulSoup
import threading
import requests
import re

URL = "https://server.179.ru/wiki/?page=Informatika/9B"


def get_contest_id(s):
    match = re.search(r"contest_id=(\d+)", s)
    return match.group(1)


class MainPageParser:
    def __init__(self):
        self.loaded = False
        self.load_url()
        self.load_thread = threading.Thread(target=self.load_url, daemon=True)
        self.load_thread.start()

    def load_url(self):
        self.html_code = requests.get(URL).text
        soup = BeautifulSoup(self.html_code, "html.parser")
        contest_rows = soup.find_all("tr", {"class": "userrow"})
        arr = []  # [[problems, contest]]
        for row in contest_rows:
            links = row.find_all("a")
            if len(links) == 3:
                arr.append([links[0], links[1]])
        self.problem_url = dict()
        self.contest_url = dict()
        for row in arr:
            contest_id = get_contest_id(row[1].get("href"))
            self.problem_url[contest_id] = row[0].get("href")
            self.contest_url[contest_id] = row[1].get("href")

    def get_problems_url_by_id(self, contest_id):
        self.load_thread.join()
        return self.problem_url[contest_id]

    def get_contest_url_by_id(self, contest_id):
        self.load_thread.join()
        return self.contest_url[contest_id]


if __name__ == "__main__":
    parser = MainPageParser()
    print(parser.get_problems_url_by_id("872"))
    print(parser.get_contest_url_by_id("872"))
