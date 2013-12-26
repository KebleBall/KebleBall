"""
affiliation.py

Contains Affiliation class
Used to denote users' affiliations with their colleges
"""

from kebleball.database import db

class Affiliation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Affiliation {id}: {name}>".format_map(vars(self))