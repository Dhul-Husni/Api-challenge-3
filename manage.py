from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from Iris import db, create_app


iris = create_app("development")
migrate = Migrate(iris, db)
manager = Manager(iris)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
