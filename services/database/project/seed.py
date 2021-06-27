from project.api.models import Club, Division, Match, Referee, Status, Team, \
    Season, User, Admin
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
    for file_name in ['matches_2018_2019.csv', 'matches_2019_2020.csv',
                      'matches_2020_2021.csv']:
        current_season += 1
        with open(f'project/data/{file_name}', 'r') as csv_file:
            reader = csv.reader(csv_file)
            # Skip on the first iteration
            skip = True
            for row in reader:
                if skip:
                    skip = False
                    continue
                goals_home = row[6] if row[6] != 'NULL' else None
                goals_away = row[7] if row[7] != 'NULL' else None
                match_status = row[8] if row[8] != 'NULL' else None
                db.session.add(Match(goalsHome=goals_home, goalsAway=goals_away,
                                     matchStatus=match_status, mDate=row[2],
                                     mTime=row[3],
                                     week=row[1], teamHomeID=row[4],
                                     teamAwayID=row[5], divisionID=row[0],
                                     seasonID=current_season, refID=None))
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
            db.session.add(
                Referee(firstName=row[0], lastName=row[1], address=row[2],
                        zipCode=int(
                            row[3]), city=row[4], phoneNumber=int(row[5]),
                        email=row[6], dateOfBirth=row[7]))
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


def seed_users(db):
    # Club user
    db.session.add(User(username='a', email='a', password='a', teamID=13))
    # Super admin user
    db.session.add(User(username='b', email='b', password='b'))
    db.session.add(Admin(userID=2, isSuper=True))
    # Admin user
    db.session.add(User(username='c', email='c', password='c'))
    db.session.add(Admin(userID=3, isSuper=False))
    # Normal user
    db.session.add(User(username='d', email='d', password='d'))
    db.session.commit()
