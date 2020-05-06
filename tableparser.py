import requests
import re
from bs4 import BeautifulSoup
from copy import deepcopy
import cachepath


TABLE_URL = 'https://server.179.ru/shashkov/stand_b22.php'
CACHE_LOCATION = 'problem_chooser_saved_table'

ALLOWED_VERDICTS = ('NO', 'OK', 'RJ', 'PR', 'WA', 'PE', 'RT', 'TL', 'ML',
                    'SV', 'IG', 'DQ', 'CF', 'CE', 'WT', 'SM', 'SY', 'SK',
                    'SE', 'PD', 'PT')
OK_VERDICTS = ('OK', 'PR', 'PD')
WA_VERDICTS = ('RJ', 'WA', 'PE', 'RT', 'TL', 'ML', 'SM')
BAD_VERDICTS = ('DQ', 'CF', 'SE', 'SY')
TOSOLVE_VERDICTS = ('NO', 'RJ', 'WA', 'PE', 'RT', 'TL', 'ML', 'SV', 'IG',
                    'CF', 'CE', 'WT', 'SM', 'SY', 'SK', 'SE', 'PT')


class Contest:

    def __init__(self, td, first_prob_id=None, tds_prob_names=None):
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
        for prob_id in range(self.first_prob_id, self.first_prob_id +
                             self.n_probs):
            self.prob_full_names.append(tds_prob_names[prob_id]['title'])
            self.prob_short_names.append(tds_prob_names[prob_id].text)

    def prob_short_name(self, prob_id):
        return self.prob_short_names[prob_id - self.first_prob_id]

    def prob_full_name(self, prob_id):
        return self.prob_full_names[prob_id - self.first_prob_id]

    def __str__(self):
        return f'#{self.id}, {self.name}'

    def __repr__(self):
        return self.__str__()


class Problem:

    def __init__(self, contest, prob_id):
        self.contest = contest
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
        return (self.score, self.contest.id, self.id) < \
               (other.score, other.contest.id, self.id)

    def __le__(self, other):
        return (self.score, self.contest.id, self.id) <= \
               (other.score, other.contest.id, self.id)

    def __gt__(self, other):
        return (self.score, self.contest.id, self.id) > \
               (other.score, other.contest.id, self.id)

    def __ge__(self, other):
        return (self.score, self.contest.id, self.id) >= \
               (other.score, other.contest.id, self.id)

    def __iadd__(self, verdict):
        if isinstance(verdict, int):
            self.attempts += verdict
        elif verdict != 'NO':
            self.verdicts[verdict] += 1
            self.attempts += 1
        return self

    def __str__(self):
        return f'{self.score} ---  {self.short_name}  ---  {self.contest}'

    def __repr__(self):
        return self.__str__()


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


class Parser:

    def __init__(self, first_contest, last_contest):
        self.first_contest = first_contest
        self.last_contest = last_contest

    @staticmethod
    def from_cache(location=CACHE_LOCATION):
        f = cachepath.CachePath(location)
        if not f.exists():
            raise Exception('Cache file is not exists')
        try:
            text = f.read_text(encoding='utf-8')
            mtch = re.match(r'(\d+) (\d+)\n', text, re.UNICODE)
            p = Parser(mtch.group(1), mtch.group(2))
            html = text[len(mtch.group(0)):]
            p.set_from_html(html)
            return p
        except Exception as ex:
            raise Exception('There are some problems with cache. Please '
                            'update the cache by get table from server.')

    def save_cache(self, location=CACHE_LOCATION):
        f = cachepath.CachePath(location)
        f.write_text(str(self.first_contest) + ' ' + str(self.last_contest) +
                     '\n' + self.html)

    @staticmethod
    def is_cache_exists(location=CACHE_LOCATION):
        return cachepath.CachePath(location).exists()

    @staticmethod
    def delete_cache(location=CACHE_LOCATION):
        return cachepath.CachePath(location).rm()

    @staticmethod
    def from_server(first_contest=690, last_contest=5000):
        try:
            html = Parser.get_table_html(first_contest, last_contest)
            p = Parser(first_contest, last_contest)
            p.set_from_html(html)
        except Exception as ex:
            raise Exception('There are some problems with server. Please '
                            'check the server is up or you Internet '
                            'connection.')
        return p

    def set_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table')[0]
        rows = table.find_all("tr")

        tds_contests = rows[0].find_all('td', {'class': 'contest'})
        tds_problem_names = rows[1].find_all('td', {'class': 'problem'})

        contests = []
        problems = []
        for td_contest in tds_contests:
            contests.append(Contest(td_contest, len(problems),
                                    tds_problem_names))
            for i in range(contests[-1].n_probs):
                problems.append(Problem(contests[-1],
                                        len(problems)))

        participants = dict()
        for par_ind in range(2, len(rows)):
            par = Participant(rows[par_ind])
            participants[par.name] = par
            for prob_id in range(len(problems)):
                problems[prob_id] += par.verdicts[prob_id]
                problems[prob_id] += max(0, par.attempts[prob_id] - 1)

        self.html = html
        self.contests = contests
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
        url = f'{TABLE_URL}?from={first_contest}&to={last_contest}'
        return requests.get(url).text
