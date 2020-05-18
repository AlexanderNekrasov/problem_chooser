import datetime
import re
from copy import deepcopy
import requests
from bs4 import BeautifulSoup

import cfg
from src.Parser import Parser
from src.Worker import Worker


ALLOWED_VERDICTS = ('NO', 'OK', 'RJ', 'PR', 'WA', 'PE', 'RT', 'TL', 'ML',
                    'SV', 'IG', 'DQ', 'CF', 'CE', 'WT', 'SM', 'SY', 'SK',
                    'SE', 'PD', 'PT')
OK_VERDICTS = ('OK', 'PR', 'PD')
WA_VERDICTS = ('RJ', 'WA', 'PE', 'RT', 'TL', 'ML', 'SM')
BAD_VERDICTS = ('DQ', 'CF', 'SE', 'SY')
TOSOLVE_VERDICTS = ('NO', 'RJ', 'WA', 'PE', 'RT', 'TL', 'ML', 'SV', 'IG',
                    'CF', 'CE', 'WT', 'SM', 'SY', 'SK', 'SE', 'PT')

_table_parser_reload_worker = Worker()


class Contest:

    def __init__(self, td, first_prob_id, tds_prob_names):
        title = td['title']
        self.id = int(re.match(r'#(\d+),.*', title).group(1))
        self.name = re.match(r'.*[^\d.](\d+\..*)', title).group(1)
        self.n_probs = int(td['colspan'])
        if first_prob_id is not None:
            self.set_probs_info(first_prob_id, tds_prob_names)

    def set_probs_info(self, first_prob_id, tds_prob_names):
        self.first_prob_id = first_prob_id
        self.prob_short_names = []
        self.prob_full_names = []
        for prob_id in range(self.first_prob_id,
                             self.first_prob_id + self.n_probs):
            self.prob_full_names.append(tds_prob_names[prob_id]['title'])
            self.prob_short_names.append(tds_prob_names[prob_id].text)

    def prob_short_name(self, prob_id):
        return self.prob_short_names[prob_id - self.first_prob_id]

    def prob_full_name(self, prob_id):
        return self.prob_full_names[prob_id - self.first_prob_id]


class Problem:

    def __init__(self, prob_id, contest):
        self.contest_id = contest.id
        self.id = prob_id
        self.short_name = contest.prob_short_name(prob_id)
        self.full_name = contest.prob_full_name(prob_id)
        self.attempts = 0
        self.verdicts = dict().fromkeys(ALLOWED_VERDICTS, 0)

    @property
    def score(self):
        ok = sum((self.verdicts[v] for v in OK_VERDICTS))
        wa = sum((self.verdicts[v] for v in WA_VERDICTS))
        bad = sum((self.verdicts[v] for v in BAD_VERDICTS))
        invisible_attempts = self.attempts - sum((ok, wa, bad))
        score = 2.0 * ok - 0.7 * wa - 1.0 * bad - 0.1 * invisible_attempts
        return round(score, 5)

    def __lt__(self, other):
        return (self.score, self.contest_id, self.id) < \
               (other.score, other.contest_id, self.id)

    def __iadd__(self, verdict):
        if isinstance(verdict, int):
            self.attempts += verdict
        elif verdict != 'NO':
            self.verdicts[verdict] += 1
            self.attempts += 1
        return self


class Participant:

    def __init__(self, tr):
        self.id = tr.find('td', {'class': 'rank'}).text
        self.all_name = tr.find('td', {'class': 'name'}).text
        self.name = re.match(r'\w+? (.*)', self.all_name).group(1)
        self.solved = float(tr.find('td', {'class': 'solved'}).text)
        self.err_attempts = int(tr.find('td', {'class': 'err_attempts'}).text)
        self.verdicts = []
        self.attempts = []
        for td in tr.find_all('td', {'class': 'verdict'}):
            ver = td['class'][1]
            if ver not in ALLOWED_VERDICTS:
                raise Exception(f'Oops! Unknown verdict "{ver}"')
            self.verdicts.append(ver)
            if ver in ('DQ', 'PR'):
                num = 1
            else:
                num = int('0' + re.match(r'[-+.](\d*)', td.text).group(1))
                if td.text[0] == '+':
                    num += 1
            self.attempts.append(num)

    @property
    def no_problems_id(self):
        res = []
        for prob_id, ver in enumerate(self.verdicts):
            if ver in TOSOLVE_VERDICTS:
                res.append(prob_id)
        return res


class TableParser(Parser):

    def __init__(self, first_contest=690, last_contest=5000):
        self.first_contest = first_contest
        self.last_contest = last_contest
        self.last_reload_time = None

    def set_from_server(self):
        try:
            time_now = datetime.datetime.now()
            html = TableParser.get_table_html(self.first_contest,
                                              self.last_contest)
            self.set_from_html(html)
            self.last_reload_time = time_now
        except Exception:
            raise Exception('There are some problems with server. Please '
                            'check the server is up or you Internet '
                            'connection.')
        self.save_cache()

    def set_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table')[0]
        rows = table.find_all("tr")

        tds_contests = rows[0].find_all('td', {'class': 'contest'})
        tds_problem_names = rows[1].find_all('td', {'class': 'problem'})

        problems = []
        for td_contest in tds_contests:
            last_contest = Contest(td_contest, len(problems),
                                   tds_problem_names)
            for i in range(last_contest.n_probs):
                problems.append(
                    Problem(len(problems), last_contest))

        participants = dict()
        for par_ind in range(2, len(rows)):
            par = Participant(rows[par_ind])
            participants[par.name] = par
            for prob_id in range(len(problems)):
                problems[prob_id] += par.verdicts[prob_id]
                problems[prob_id] += max(0, par.attempts[prob_id] - 1)

        self.problems = problems
        self.participants = participants

    def get_names(self):
        return list(self.participants.keys())

    def get_stat(self, name):
        no_problems = []
        for prob_id in self.participants[name].no_problems_id:
            no_problems.append(deepcopy(self.problems[prob_id]))
        no_problems.sort(reverse=True)
        return no_problems

    @staticmethod
    def get_table_html(first_contest=690, last_contest=5000):
        url = f'{cfg.TABLE_URL}?from={first_contest}&to={last_contest}'
        return requests.get(url).text

    def __getattr__(self, item):
        if item == 'reload_worker':
            return _table_parser_reload_worker
        else:
            raise AttributeError
