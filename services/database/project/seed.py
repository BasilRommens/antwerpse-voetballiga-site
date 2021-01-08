from project.api.models import Club, Division, Match, Referee, Status, Team, Season
import csv


def seed_club(db):
    with open('project/data/clubs.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip on the first iteration
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            db.session.add(Club(name=row[1], address=row[2], zipCode=int(
                row[3]), city=row[4], stamNumber=int(row[0]), website=row[5]))
    db.session.commit()


def seed_division(db):
    with open('project/data/divisions.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip on the first iteration
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            db.session.add(Division(name=row[1]))
    db.session.commit()


def add_seasons(db):
    for i in range(3):
        db.session.add(Season())
    db.session.commit()


def seed_matches(db):
    add_seasons(db)
    current_season = 0
    for file_name in ['matches_2018_2019.csv', 'matches_2019_2020.csv', 'matches_2020_2021.csv']:
        current_season += 1
        with open(f'project/data/{file_name}', 'r') as csv_file:
            reader = csv.reader(csv_file)
            # Skip on the first iteration
            skip = True
            for row in reader:
                if skip:
                    skip = False
                    continue
                no_eight = row[8]
                no_one = row[1]
                no_six = row[6]
                no_seven = row[7]
                if row[8] == 'NULL':
                    no_eight = None
                if row[1] == 'NULL':
                    no_one = None
                if row[6] == 'NULL':
                    no_six = None
                if row[7] == 'NULL':
                    no_seven = None

                db.session.add(Match(goalsHome=no_six, goalsAway=no_seven, matchStatus=no_eight, mDate=row[2], mTime=row[3],
                                     week=no_one, teamHomeID=row[4], teamAwayID=row[5], divisionID=row[0], seasonID=current_season, refID=None))
    db.session.commit()


def seed_referees(db):
    with open('project/data/referees.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip on the first iteration
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            db.session.add(Referee(firstName=row[0], lastName=row[1], address=row[2], zipCode=int(
                row[3]), city=row[4], phoneNumber=int(row[5]), email=row[6], dateOfBirth=row[7]))
    db.session.commit()


def seed_status(db):
    with open('project/data/status.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip on the first iteration
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            db.session.add(Status(name=row[1]))
    db.session.commit()


def seed_team(db):
    with open('project/data/teams.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip on the first iteration
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            db.session.add(
                Team(suffix=row[2], colors=row[3], stamNumber=row[1]))
    db.session.commit()
