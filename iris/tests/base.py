"""
Base test case for all tests
"""
import unittest
from iris import create_app, db
import json
from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
)


def db_DropEverything(db):
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything

    conn = db.engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(db.engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((), (), name=fk['name'])
                )
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()


class BaseApiTestCase(unittest.TestCase):
    """
    Setup
    """
    def setUp(self):
        self.iris = create_app('testing')
        self.client = self.iris.test_client
        self.user_data = {
            'First Name': 'Kali',
            'Last Name': 'Siren',
            'email': 'user1234@example.com',
            'password': 'test_password',
            'Secret word':'Kali2018'
        }
        with self.iris.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def tearDown(self):
        """Tear down all initialized variables"""
        with self.iris.app_context():
            db.session.remove()
            db_DropEverything(db)

    def register_user(self, first_name='Kali', last_name='siren',
                      email='user1234@gmail.com', password='testpassword', secret='Kali2018'):
        """Implied registration . A helper method"""
        user_data = {
                    'email': email,
                    'password': password,
                    'First Name': first_name,
                    'Last Name': last_name,
                    "Secret word": secret
                    }
        return self.client().post('/v2/auth/register', data=user_data)

    def login_user(self, email='user1234@gmail.com', password='testpassword'):
        """Implied login. A helper method"""
        user_data = {
                    'email': email,
                    'password': password,
                    }
        return self.client().post('/v2/auth/login', data=user_data)

