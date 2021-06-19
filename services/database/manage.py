import unittest
import csv

from flask.cli import FlaskGroup

from project import create_app, db
from project import seed

app = create_app()
cli = FlaskGroup(app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def seed_db():
    """Seeds the database."""
    seed.seed_referees(db)
    seed.seed_status(db)
    seed.seed_division(db)
    seed.seed_club(db)
    seed.seed_team(db)
    seed.seed_matches(db)
    seed.seed_users(db)


if __name__ == '__main__':
    cli()
