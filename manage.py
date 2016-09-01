# manage.py

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from project import app, db
from project.models import User

migrate = Migrate(app, db)
manager = Manager(app)
server = Server(host="0.0.0.0", port=5000)

# migrations
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", server)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(email='ad@min.com', password='admin', admin=True))
    db.session.commit()


@manager.command
def create_data():
    """Creates sample data."""
    pass


if __name__ == '__main__':
    manager.run()
