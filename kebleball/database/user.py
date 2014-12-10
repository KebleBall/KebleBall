# coding: utf-8
"""
user.py

Contains User class
"""

from kebleball.database import db
from kebleball.database.battels import Battels
from kebleball.database.college import College
from kebleball.database.affiliation import Affiliation
from kebleball.app import app
from flask.ext.bcrypt import Bcrypt
from kebleball.helpers import generate_key

from datetime import datetime
from passlib.hash import bcrypt as passlib_bcrypt
import re

bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )
    newemail = db.Column(
        db.String(120),
        unique=True,
        nullable=True
    )
    passhash = db.Column(
        db.BINARY(60),
        nullable=False
    )
    firstname = db.Column(
        db.String(120),
        nullable=False
    )
    surname = db.Column(
        db.String(120),
        nullable=False
    )
    fullname = db.column_property(firstname + " " + surname)
    phone = db.Column(
        db.String(20),
        nullable=False
    )
    secretkey = db.Column(
        db.String(64),
        nullable=True
    )
    secretkeyexpiry = db.Column(
        db.DateTime(),
        nullable=True
    )
    verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )
    deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )
    note = db.Column(
        db.Text,
        nullable=True
    )
    role = db.Column(
        db.Enum(
            'User',
            'Admin'
        ),
        nullable=False
    )

    college_id = db.Column(
        db.Integer,
        db.ForeignKey('college.id'),
        nullable=False
    )
    college = db.relationship(
        'College',
        backref=db.backref(
            'users',
            lazy='dynamic'
        )
    )

    affiliation_id = db.Column(
        db.Integer,
        db.ForeignKey('affiliation.id'),
        nullable=False
    )
    affiliation = db.relationship(
        'Affiliation',
        backref=db.backref(
            'users',
            lazy='dynamic'
        )
    )

    battels_id = db.Column(
        db.Integer,
        db.ForeignKey('battels.id'),
        nullable=True
    )
    battels = db.relationship(
        'Battels',
        backref=db.backref(
            'user',
            uselist=False
        )
    )

    def __init__(self, email, password, firstname,
                 surname, phone, college, affiliation):
        self.email = email
        self.passhash = bcrypt.generate_password_hash(password)
        self.firstname = firstname
        self.surname = surname
        self.phone = phone
        self.secretkey = generate_key(64)
        self.verified = False
        self.deleted = False
        self.role = 'User'

        if hasattr(college, 'id'):
            self.college_id = college.id
        else:
            self.college_id = college

        if hasattr(affiliation, 'id'):
            self.affiliation_id = affiliation.id
        else:
            self.affiliation_id = affiliation

        battels = Battels.query.filter(Battels.email == email).first()

        if battels is not None:
            self.battels = battels
        elif re.match('(.*?)@keble\.ox\.ac\.uk$', email) is not None:
            self.battels = Battels(None, None, None, None, None, True)
            db.session.add(self.battels)
        else:
            self.battels = None

    def __repr__(self):
        return "<User {0}: {1} {2}>".format(
            self.id, self.firstname, self.surname)

    def check_password(self, candidate):
        try:
            return bcrypt.check_password_hash(self.passhash, candidate)
        except ValueError:
            if passlib_bcrypt.verify(candidate, self.passhash):
                self.passhash = bcrypt.generate_password_hash(candidate)
                db.session.commit()
                return True
            else:
                return False

        return False

    def set_password(self, password):
        self.passhash = bcrypt.generate_password_hash(password)

    def has_tickets(self):
        return len([x for x in self.tickets
                    if not x.cancelled]) > 0

    def has_uncollected_tickets(self):
        return len([x for x in self.tickets
                    if not x.cancelled and not x.collected]) > 0

    def has_collected_tickets(self):
        return len([x for x in self.tickets
                    if not x.cancelled and x.collected]) > 0

    def has_unresold_tickets(self):
        return len([x for x in self.tickets
                    if not x.cancelled and x.resalekey is None]) > 0

    def is_reselling_tickets(self):
        return len([x for x in self.tickets
                    if x.resalekey is not None]) > 0

    def has_unpaid_tickets(self, method=None):
        if method is None:
            return len(
                [
                    x for x in self.tickets if (
                        not x.paid and
                        not x.cancelled
                    )
                ]
            ) > 0
        else:
            return len(
                [
                    x for x in self.tickets if (
                        x.paymentmethod == method and
                        not x.paid and
                        not x.cancelled
                    )
                ]
            ) > 0

    def has_paid_tickets(self, method=None):
        if method is None:
            return len(
                [
                    x for x in self.tickets if (
                        x.paid and
                        not x.cancelled
                    )
                ]
            ) > 0
        else:
            return len(
                [
                    x for x in self.tickets if (
                        x.paymentmethod == method and
                        x.paid and
                        not x.cancelled
                    )
                ]
            ) > 0

    def promote(self):
        self.role = 'Admin'

    def demote(self):
        self.role = 'User'

    def is_admin(self):
        return self.role == 'Admin'

    def is_waiting(self):
        return self.waiting.count() > 0

    def waiting_for(self):
        return sum([x.waitingfor for x in self.waiting])

    def can_pay_by_battels(self):
        return (
            self.battels is not None and
            app.config['CURRENT_TERM'] != 'TT'
        )

    def gets_discount(self):
        return (
            self.college.name == 'Keble' and
            self.affiliation.name == 'Student' and
            app.config['KEBLE_DISCOUNT'] > 0 and
            self.tickets.count() == 0
        )

    def is_verified(self):
        return self.verified

    def is_deleted(self):
        return self.deleted

    def is_active(self):
        return self.is_verified() and not self.is_deleted()

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def get_by_id(id):
        user = User.query.filter(User.id == int(id)).first()

        if not user:
            return None

        return user

    @staticmethod
    def get_by_email(email):
        user = User.query.filter(User.email == email).first()

        if not user:
            return None

        return user
