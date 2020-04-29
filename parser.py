import urllib.request
from bs4 import BeautifulSoup


def get_html(url):
    return urllib.request.urlopen(url).read()


def get_table_html(first_contest=690, last_contest=5000):
    serverURL = f'https://server.179.ru/shashkov/stand_b22.php?from={first_contest}&to={last_contest}'
    return get_html(serverURL).decode('utf-8')



class ProblemVerdicts:

    def __init__(self):
        '''
        Keep verdicts of a problem
        OK - OK
        RJ - Rejected
        PR - Pending review
        WA - Wrong answer
        PE - Presentation error
        RT - Runtime error
        TL - Time limit
        ML - Memory limit
        SV - Style violation
        IG - Ignored
        DQ - Disqualified
        '''
        self.allowed_verdicts = ('OK', 'RJ', 'PR', 'WA', 'PE', 'RT', 'TL', 'ML', 'SV', 'IG', 'DQ')
        self.attempts = 0
        self.verdicts_cnt = dict().fromkeys(self.allowed_verdicts, 0)

    def add(self, verdict, cnt):
        if verdict not in self.allowed_verdicts:
            raise Exception(f'Unknown verdict "{verdict}"')
        self.verdicts_cnt[verdict] += cnt



class Parser:

    def __init__(self):
        pass

    def get_names(self):
        # TODO: remove this stuff
        return ['Abichev', 'Andrianov', 'Nekrasov']

    def get_stat(self, name):
        '''
        Returns all not solved problems sorted by count of people solved this problem
        '''
        pass
