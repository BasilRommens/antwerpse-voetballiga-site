from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from project import db
import enum


class Status(enum.Enum):
    POSTPONED = 'postponed'
    CANCELED = 'canceled'
    FORFAIT = 'forfait'


class User(db.Model):
    __tablename__ = 'users'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    clubID = db.Column(db.Integer, ForeignKey('Club.ID'), nullable=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def to_json(self):
        return {
            'ID': self.id,
            'username': self.username,
            'email': self.email,
            'clubID': self.clubID
        }


class Admin(db.Model):
    __tablename__ = 'admin'
    userID = db.Column(db.Integer, primary_key=True)
    isSuper = db.Column(db.Boolean, nullable=False)

    def __init__(self, userID, isSuper):
        self.userID = userID
        self.isSuper = isSuper

    def to_json(self):
        return {'userID': self.userID, 'isSuper': self.isSuper}


class Season(db.Model):
    __tablename__ = "season"
    season = db.Column(db.Integer, primary_key=True, autoincrement=True)

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
    dateOfBirth = db.Column(db.DateTime, nullable=False)

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
            'first_name': self.firstName,
            'last_name': self.lastName,
            'address': self.address,
            'zipCode': self.zipCode,
            'city': self.city,
            'phone_number': self.phoneNumber,
            'email': self.email,
            'dateOfBirth': self.dateOfBirth
        }


class Match(db.Model):
    __tablename__ = 'match'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goalsHome = db.Column(db.Integer, nullable=True)
    goalsAway = db.Column(db.Integer, nullable=True)
    matchStatus = db.Column(enum.Enum(Status))
    mDate = db.Column(db.Date, nullable=False)
    mTime = db.Column(db.Time, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    teamHomeID = db.Column(db.Integer, ForeignKey('Team.ID'), nullable=False)
    teamAwayID = db.Column(db.Integer, ForeignKey('Team.ID'), nullable=False)
    divisionID = db.Column(db.Integer,
                           ForeignKey('Division.ID'),
                           nullable=False)
    seasonID = db.Column(db.Integer, ForeignKey('Season.ID'), nullable=False)
    refID = db.Column(db.Integer, ForeignKey('Referee.ID'), nullable=False)

    def __init__(self, goalsHome, goalsAway, matchStatus, mDate, mTime, week,
                 teamHomeID, teamAwayID, divisionID, seasonID, refID):
        self.goalsHome = goalsHome
        self.goalsAway = goalsAway
        self.matchStatus = matchStatus
        self.mDate = mDate
        self.mTime = mTime
        self.teamHomeID = teamHomeID
        self.teamAwayID = teamAwayID
        self.divisionID = divisionID
        self.seasonID = seasonID
        self.refID = refID

    def to_json(self):
        return {
                'goals_home': self.goalsHome,
                'goals_away': self.goalsAway,
                'match_status': self.matchStatus,
                'date': self.mDate,
                'time': self.mTime,
                'team_home_ID': self.teamHomeID,
                'team_away_ID': self.teamAwayID,
                'division_ID': self.divisionID,
                'season_ID': self.seasonID,
                'ref_ID': self.refID
        }


class Team(db.Model):
    pass
