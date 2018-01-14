from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from Iris import db, create_app


app = create_app("development")
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
