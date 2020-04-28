from sfml import sf

class Problem:
    def __init__(self, ):
        '''
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
        self.verdicts_cnt = dict.from_keys(('OK', 'RJ', 'PR', 'WA', 'PE', 'RT', 'TL', 'ML', 'SV', 'IG', 'DQ'))




class Parser:
    def __init__(self):
        pass

    def get_names(self):
        # TODO: remove this stuff
        return ['Abichev', 'Andrianov', 'Nekrasov']

    def get_stat(self, name):
        t'''
        Returns all not solved problems sorted by count of people solved this problem
        '''
        pass
