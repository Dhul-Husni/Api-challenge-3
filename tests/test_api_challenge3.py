import unittest
import json
from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
        )
from app import create_app, db


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


class ApiTestCase(unittest.TestCase):
    """This test represents the api challenge 3 test case"""
    def setUp(self):
        """Initializes app and sets test variables"""
        self.app = create_app("testing")
        self.client = self.app.test_client
        self.user = {"email": "sir3n.sn@gmail.com",
                     "first_name": "Dhulkifli",
                     "last_name": "Hussein",
                     "password": "Kali2017",
                     "Secret word": "Kali2018"}

        # bind the app to the current context
        with self.app.app_context():
            db.create_all()

    def register_user(self, first_name='Kali', last_name='sir3n',
                      email='user1234@gmail.com', password='testpassword', secret='Kali2018'):
        """Implied registration . A helper method"""
        user_data = {
                    'email': email,
                    'password': password,
                    'First Name': first_name,
                    'Last Name': last_name,
                    "Secret word": secret
                    }
        return self.client().post('/api-1.0/auth/register', data=user_data)

    def login_user(self, email='user1234@gmail.com', password='testpassword'):
        """Implied login. A helper method"""
        user_data = {
                    'email': email,
                    'password': password,
                    }
        return self.client().post('/api-1.0/auth/login', data=user_data)

    def test_no_access_token_provided_in_category(self):
        """Tests if a user does not provide an access token to the endpoints"""
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },)
        self.assertEqual(res.status_code, 300)
        self.assertIn('Please Provide an access token', str(res.data))

    def test_no_access_token_provided_in_category_id(self):
        """Tests if a user does not provide an access token to the endpoints"""
        res = self.client().get('/api-1.0/categories/1', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },)
        self.assertEqual(res.status_code, 300)
        self.assertIn('please provide an access token', str(res.data).lower())

    def test_invalid_keys_set_for_category(self):
        """Test for when user does a post request with invalid keys"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
            "invalid_category": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 203)
        self.assertIn('please use keys name and detail', str(res.data))

    def test_invalid_keys_for_category_id_put(self):
        """Test for when user does a put request with invalid keys on category id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        res = self.client().put('/api-1.0/categories/1', data={
            "invalid name": "Bitter pie",
            "detail": "Made by me"
        },
                                headers=dict(Authorization=access_token)
                                )
        self.assertEqual(res.status_code, 203)
        self.assertIn('please use the keys name and detail', str(res.data).lower())

    def test_invalid_or_expired_token_in_get_and_post_category(self):
        """Test expired or invalid token in get and post category"""
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization='invalid.token')
                                 )
        self.assertEqual(res.status_code, 401)
        self.assertIn('invalid' or 'expired', str(res.data).lower())

    def test_invalid_or_expired_token_in_get_and_put_delete_category(self):
        """Test expired or invalid token in edit and delete category by id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/api-1.0/categories/{}'.format(result_in_json['id']),
                                   headers=dict(Authorization='Invalid.token')
                                   )
        self.assertEqual(result.status_code, 401)
        self.assertIn('invalid' or 'expired', str(result.data).lower())

    def test_token_based_authentication(self):
        """Tests if the user is given a token after login"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())
        self.assertIn('Access token', access_token)

    def test_users_can_create_categories(self):
        """Test if users can create a recipe category(POST)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                     "name": "Sweet pie",
                                                                     "detail": "Made by mama"
                                                                     },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Sweet pie'.title(), str(res.data))

    def test_get_categories_when_empty(self):
        """Tests when a get all request is made and all categories are empty"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        result = self.client().get('/api-1.0/categories',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn("Nothing here yet", str(result.data))

    def test_users_can_get_all_categories(self):
        """Test if Api can get All categories"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        result = self.client().get('/api-1.0/categories',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn("Made by mama".title(), str(result.data))

    def test_user_cannot_post_duplicate_entries(self):
        """When user creates two similar categories"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Sweet pie'.title(), str(res.data))
        # create duplicate entries
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 409)
        self.assertIn('Category already exists', str(res.data))

    def test_users_can_get_category_by_id(self):
        """Test if Api can get category by id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/api-1.0/categories/{}'.format(result_in_json['id']),
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn('Sweet pie'.title(), str(result.data))

    def test_users_categories_can_be_edited(self):
        """Test if Api can edit user categories(Put)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        res = self.client().put('/api-1.0/categories/1', data={
                                                                       "name": "Bitter pie",
                                                                       "detail": "Made by me"
                                                                       },
                                headers=dict(Authorization=access_token)
                                )
        self.assertEqual(res.status_code, 200)
        result = self.client().get('/api-1.0/categories/1',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Bitter pie'.title(), str(result.data))

    def test_users_categories_can_be_deleted(self):
        """Tests if Api can delete user categories"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        result = self.client().delete('/api-1.0/categories/1',
                                      headers=dict(Authorization=access_token),
                                      )
        self.assertEqual(result.status_code, 200)
        res = self.client().get('/api-1.0/categories/1',
                                headers=dict(Authorization=access_token)
                                )
        self.assertEqual(res.status_code, 404)

    def test_user_category_recipe_can_be_created(self):
        """Tests if api can create recipes (post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                                   "name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tea spoon'.title(), str(result.data))

    def test_user_category_recipe_with_invalid_token(self):
        """api should not create recipe with invalid email"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        res = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization='Invalid.token')
                                 )
        self.assertEqual(res.status_code, 401)
        self.assertIn("invalid" or 'expired', str(res.data).lower())

    def test_user_category_recipe_can_be_created_with_invalid_keys(self):
        """Tests if api can create recipes with invalid keys(post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                                   "Invalid name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(result.status_code, 203)
        self.assertIn('Please use keys name and recipe', str(result.data))

    def test_user_category_recipe_can_get_recipes(self):
        """Tests if api can get recipes (get)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                                   "name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tea spoon'.title(), str(result.data))
        result = self.client().get('/api-1.0/categories/1/recipes',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn('tea spoon'.title(), str(result.data))

    def test_user_category_recipe_can_get_recipes_when_empty(self):
        """Tests if api can get recipes (get)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )

        self.assertEqual(res.status_code, 201)
        self.assertIn('Sweet pie'.title(), str(res.data))
        result = self.client().get('/api-1.0/categories/1/recipes',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn('Nothing here yet', str(result.data))

    def test_user_category_recipe_can_be_edited(self):
        """Tests if api can edit recipes"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        result = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                                    "name": "Grandma's home made",
                                                                                    "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(result.status_code, 201)
        result = self.client().put('/api-1.0/categories/1/recipes/1', data={
                                                                                    "name": "Uncle's homemade",
                                                                                    "recipe": "1 bowl of onions"
                                                                                    },
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 201)
        final = self.client().get('/api-1.0/categories/1/recipes/1',
                                  headers=dict(Authorization=access_token)
                                  )
        self.assertEqual(final.status_code, 200)
        self.assertIn('bowl of'.title(), str(final.data))

    def test_user_can_search_through_categories_using_get_parameter_q(self):
        """Tests if a user queries a parameter it returns the closest matching category"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/api-1.0/categories', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/api-1.0/categories', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/search?q=chicken',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Made by brother".title(), str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_user_can_search_through_categories_with_no_token(self):
        """Tests if a user queries a parameter with no token"""
        search_result = self.client().get('/api-1.0/categories/search?q=chicken',)
        self.assertIn("Please provide an access token".lower(), str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 300)

    def test_user_can_search_through_categories_with_invalid_token(self):
        """Tests if a user queries a parameter with invalid token"""
        search_result = self.client().get('/api-1.0/categories/search?q=chicken',
                                          headers=dict(Authorization='Invalid.token'))
        self.assertIn("invalid" or "expired", str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 401)

    def test_user_can_search_through_categories_q_not_found(self):
        """Tests if a user queries a parameter WITH NONE EXISTING DATA"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/search?q=NONE_EXISTING',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Sorry we could not find what you are looking for", str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_user_can_search_through_categories_with_q_not_found(self):
        """Tests if a user does not provide q"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/search',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Please provide a search query", str(search_result.data))
        self.assertEqual(search_result.status_code, 404)

    def test_user_category_recipe_can_be_created_with_no_token(self):
        """Tests if api can create recipes with no token(post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/api-1.0/categories/1/recipes', data={
                                                                                   "name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    )
        self.assertEqual(result.status_code, 300)
        self.assertIn('Please provide an access token', str(result.data))

    def test_user_can_search_through_recipes_using_get_parameter_q(self):
        """Tests if a user queries a parameter it returns the closest matching recipe"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/1/recipes/search?q=chicken',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Made by brother".title(), str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_user_can_search_through_recipes_using_get_parameter_q_but_no_token(self):
        """Tests if a user queries a parameter with no access token"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/1/recipes/search?q=chicken',
                                          )
        self.assertIn("Please provide an access token", str(search_result.data))
        self.assertEqual(search_result.status_code, 300)

    def test_user_can_search_through_recipes_using_get_parameter_q_which_is_none_existen(self):
        """Tests if a user queries a parameter that does not exist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/1/recipes/search?q=NONE_EXISTENT',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Sorry we could not find what you are looking for", str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_user_can_search_through_recipes_with_invalid_category(self):
        """Tests if a user queries a parameter and does not provide a valid category"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        search_result = self.client().get('/api-1.0/categories/1/recipes/search',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Category does not exist", str(search_result.data))
        self.assertEqual(search_result.status_code, 405)

    def test_user_can_search_through_recipes_using_get_parameter_q_with_invalid_token(self):
        """Tests if a user queries a recipe with invalid token """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/api-1.0/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/api-1.0/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/api-1.0/categories/1/recipes/search?q=chicken',
                                          headers=dict(Authorization='Invalid.token')
                                          )
        self.assertIn("invalid" or 'expired', str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 401)

    def test_user_can_get_recipes_by_id_with_non_exist_category(self):
        """Tests if a user can get recipe by id if the category does not exist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']

        result = self.client().get('/api-1.0/categories/1/recipes/1', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertIn("The category does not exist", str(result.data))
        self.assertEqual(result.status_code, 405)

    def test_user_can_get_recipes_by_id_with_invalid_token(self):
        """Tests if a user can get recipe by id if the category does not exist"""
        result = self.client().get('/api-1.0/categories/1/recipes/1', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                                   headers=dict(Authorization='Invalid.token')
                                   )
        self.assertIn("invalid" or 'expired', str(result.data).lower())
        self.assertEqual(result.status_code, 401)

    def tearDown(self):
        """Tear down all initialized variables"""
        with self.app.app_context():
            db.session.remove()
            db_DropEverything(db)

