"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""

import json

class BaselineNotFound(Exception):
    '''
    Baseline not found
    '''

class Baseline(object):
    '''
    Baseline
    '''

    def __init__(self, id, baseline):
        self.id = id
        self.baseline = baseline

    def print(self):
        print("""Baseline:
ID: %d,
Baseline: %s""" % (self.id, self.baseline))

class Baselines(object):
    '''
    Baselines management service
    '''

    def __init__(self, db):
        self._db = db

    def add_baseline(self, id, baseline):
        self._db.add_baseline(
            id, json.dumps(baseline))

    def add_baseline_from_object(self, baseline):
        self.add_baseline(
            baseline.id, baseline.baseline)

    def get_baseline(self, id):
        baseline_raw = self._db.get_baseline(id)
        if not baseline_raw:
            raise BaselineNotFound

        baseline = json.loads(baseline_raw[1])
        return Baseline(baseline_raw[0], baseline)
