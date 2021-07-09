from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from project import db
import enum


class Status(db.Model):
    __tablename__ = 'state'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    matches = db.relationship("Match", back_populates="state",
                              cascade='all, delete', passive_deletes=True)

    def __init__(self, name):
        self.name = name

    def to_json(self):
        return {'name': self.name, 'ID': self.ID}


class Club(db.Model):
    __tablename__ = 'club'
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    zipCode = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(128), nullable=False)
    stamNumber = db.Column(db.Integer, primary_key=True, nullable=False)
    website = db.Column(db.String(128), nullable=False)
    teams = db.relationship("Team", back_populates="club",
                            cascade='all, delete', passive_deletes=True)

    def __init__(self, name, address, zipCode, city, stamNumber, website):
        self.name = name
        self.address = address
        self.zipCode = zipCode
        self.city = city
        self.stamNumber = stamNumber
        self.website = website

    def to_json(self):
        return {
            'name': self.name,
            'address': self.address,
            'zipCode': self.zipCode,
            'city': self.city,
            'stam_number': self.stamNumber,
            'website': self.website,
        }


class User(db.Model):
    __tablename__ = 'users'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    teamID = db.Column(db.Integer,
                       ForeignKey('team.ID', ondelete='CASCADE'),
                       nullable=True)
    admin = db.relationship('Admin', back_populates='user',
                            cascade='all, delete', passive_deletes=True)
    team = db.relationship('Team', back_populates='users')

    def __init__(self, username, email, password, teamID=None):
        self.username = username
        self.email = email
        self.password = password
        self.teamID = teamID

    def to_json(self):
        return {
            'ID': self.ID,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'teamID': self.teamID
        }


class Admin(db.Model):
    __tablename__ = 'admin'
    userID = db.Column(db.Integer, ForeignKey('users.ID', ondelete='CASCADE'),
                       primary_key=True)
    isSuper = db.Column(db.Boolean, nullable=False)
    user = db.relationship('User', back_populates='admin')

    def __init__(self, userID, isSuper):
        self.userID = userID
        self.isSuper = isSuper

    def to_json(self):
        return {'admin_id': self.userID, 'is_super': self.isSuper}


class Season(db.Model):
    __tablename__ = "season"
    season = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matches = db.relationship("Match", back_populates="season",
                              cascade='all, delete', passive_deletes=True)

    def __init__(self):
        pass

    def to_json(self):
        return {'season': self.season}


class Referee(db.Model):
    __tablename__ = 'referee'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(128), nullable=False)
    lastName = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    zipCode = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(128), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(128), nullable=False)
    dateOfBirth = db.Column(db.Date, nullable=False)
    matches = db.relationship("Match", back_populates="referee",
                              cascade='all, delete', passive_deletes=True)

    def __init__(self, firstName, lastName, address, zipCode, city,
                 phoneNumber, email, dateOfBirth):
        self.firstName = firstName
        self.lastName = lastName
        self.address = address
        self.zipCode = zipCode
        self.city = city
        self.phoneNumber = phoneNumber
        self.email = email
        self.dateOfBirth = dateOfBirth

    def to_json(self):
        return {
            'ID': self.ID,
            'first_name': self.firstName,
            'last_name': self.lastName,
            'address': self.address,
            'zip_code': self.zipCode,
            'city': self.city,
            'phone_number': self.phoneNumber,
            'email': self.email,
            'date_of_birth': self.dateOfBirth.strftime('%Y-%m-%d')
        }


class Match(db.Model):
    __tablename__ = 'match'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goalsHome = db.Column(db.Integer, nullable=True)
    goalsAway = db.Column(db.Integer, nullable=True)
    matchStatus = db.Column(db.Integer,
                            ForeignKey('state.ID', ondelete='SET NULL'),
                            nullable=True)
    mDate = db.Column(db.Date, nullable=False)
    mTime = db.Column(db.Time, nullable=False)
    week = db.Column(db.Integer, nullable=True)
    teamHomeID = db.Column(db.Integer,
                           ForeignKey('team.ID', ondelete='CASCADE'),
                           nullable=False)
    teamAwayID = db.Column(db.Integer,
                           ForeignKey('team.ID', ondelete='CASCADE'),
                           nullable=False)
    divisionID = db.Column(db.Integer,
                           ForeignKey('division.ID', ondelete='CASCADE'),
                           nullable=False)
    seasonID = db.Column(db.Integer,
                         ForeignKey('season.season', ondelete="CASCADE"),
                         nullable=False)
    refID = db.Column(db.Integer, ForeignKey('referee.ID', ondelete='SET NULL'),
                      nullable=True)
    division = db.relationship('Division', back_populates='matches')
    referee = db.relationship('Referee', back_populates='matches')
    season = db.relationship('Season', back_populates='matches')
    state = db.relationship('Status', back_populates='matches')
    home_team = db.relationship('Team', foreign_keys=[teamHomeID])
    away_team = db.relationship('Team', foreign_keys=[teamAwayID])

    def __init__(self, goalsHome, goalsAway, matchStatus, mDate, mTime, week,
                 teamHomeID, teamAwayID, divisionID, seasonID, refID):
        self.goalsHome = goalsHome
        self.goalsAway = goalsAway
        self.matchStatus = matchStatus
        self.mDate = mDate
        self.mTime = mTime
        self.week = week
        self.teamHomeID = teamHomeID
        self.teamAwayID = teamAwayID
        self.divisionID = divisionID
        self.seasonID = seasonID
        self.refID = refID

    def to_json(self):
        return {
            'ID': self.ID,
            'goals_home': self.goalsHome,
            'goals_away': self.goalsAway,
            'match_status': self.matchStatus,
            'date': str(self.mDate),
            'time': str(self.mTime),
            'week': str(self.week),
            'team_home_ID': self.teamHomeID,
            'team_away_ID': self.teamAwayID,
            'division_ID': self.divisionID,
            'season_ID': self.seasonID,
            'ref_ID': self.refID
        }


class Team(db.Model):
    __tablename__ = 'team'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    suffix = db.Column(db.String(128), nullable=False)
    colors = db.Column(db.String(128), nullable=False)
    stamNumber = db.Column(db.Integer,
                           ForeignKey('club.stamNumber', ondelete='CASCADE'),
                           nullable=False)
    users = db.relationship('User', back_populates='team',
                            cascade='all, delete', passive_deletes=True)
    club = db.relationship('Club', back_populates='teams')

    def __init__(self, suffix, colors, stamNumber):
        self.suffix = suffix
        self.colors = colors
        self.stamNumber = stamNumber

    def to_json(self):
        return {
            'ID': self.ID,
            'suffix': self.suffix,
            'colors': self.colors,
            'stamNumber': self.stamNumber
        }


class Division(db.Model):
    __tablename__ = 'division'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    matches = db.relationship("Match", back_populates="division",
                              cascade='all, delete', passive_deletes=True)

    def __init__(self, name):
        self.name = name

    def to_json(self):
        return {'ID': self.ID, 'name': self.name}
