from flask.cli import FlaskGroup

from project import create_app

app = create_app()
cli = FlaskGroup(app)


@cli.command()
def test():
    pass


if __name__ == '__main__':
    cli()
