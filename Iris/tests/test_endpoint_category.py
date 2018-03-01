"""
TestCase for endpoint /categories
"""
import json

from Iris.tests import base


class CategoryTestCase(base.BaseApiTestCase):
    """
    Class TesCase for Categories Enpoint
    """
    def test_post_category_no_access_token_should_refuse(self):
        """Tests if a user does not provide an access token to post to a category"""
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },)
        self.assertEqual(res.status_code, 499)
        self.assertIn('Please provide an access token', str(res.data))

    def test_get_category_by_id_no_access_token_should_refuse(self):
        """Tests if a user gets a category by id with no access token provided"""
        res = self.client().get('/v2/categories/1', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },)
        self.assertEqual(res.status_code, 499)
        self.assertIn('please provide an access token', str(res.data).lower())

    def test_postcategory_bad_item_names_should_return_exception(self):
        """Test for when user does a post a category with incorrect item names"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
            "invalid_category": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 400)
        self.assertIn('please use keys name and detail', str(res.data))

    def test_edit_category_bad_item_names_should_return_exception(self):
        """Test for when user edits a category with incorrect item names"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        edit = self.client().put('/v2/categories/1', data={
            "invalid name": "Bitter pie",
            "detail": "Made by me"
        },
                                headers=dict(Authorization=access_token)
                                )
        self.assertEqual(edit.status_code, 400)
        self.assertIn('please use keys name and detail', str(edit.data).lower())

    def test_post_category_invalid_token_should_return_exception(self):
        """Test posting a category with an invalid token"""
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization='invalid.token')
                                 )
        self.assertEqual(res.status_code, 498)
        self.assertIn('invalid', str(res.data).lower())

    def test_edit_category_invalid_token_should_return_exception(self):
        """Test editing a category with an invalid token"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/v2/categories/{}'.format(result_in_json['Category Id']),
                                   headers=dict(Authorization='Invalid.token')
                                   )
        self.assertEqual(result.status_code, 498)
        self.assertIn('invalid' or 'expired', str(result.data).lower())
        
    def test_users_can_create_categories(self):
        """Test if users can create a recipe category(POST)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
                                                                     "name": "Sweet pie",
                                                                     "detail": "Made by mama"
                                                                     },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Sweet pie'.title(), str(res.data))

    def test_get_categories_when_no_categories_should_notify_user(self):
        """Tests when a get all categories request is made and no categories exist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        result = self.client().get('/v2/categories',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn("Nothing here yet", str(result.data))

    def test_users_can_get_all_categories(self):
        """Test if Api can get All categories"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                           headers=dict(Authorization=access_token)
                           )
        result = self.client().get('/v2/categories',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn("Made by mama".title(), str(result.data))

    def test_user_cannot_post_duplicate_entries(self):
        """When user creates two similar categories"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                  "name": "Sweet pie",
                                                  "detail": "Made by mama"
                                                  },
                           headers=dict(Authorization=access_token)
                           )
        # create duplicate entries
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn('Category already exists', str(res.data))

    def test_users_can_get_category_by_id(self):
        """Test if Api can get category by id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/v2/categories/{}'.format(result_in_json['Category Id']),
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn('Sweet pie'.title(), str(result.data))

    def test_editing_a_category(self):
        """Test if Api can edit user categories(Put)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                        "name": "Sweet pie",
                                                        "detail": "Made by mama"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        res = self.client().put('/v2/categories/1', data={
                                                                       "name": "Bitter pie",
                                                                       "detail": "Made by me"
                                                                       },
                                headers=dict(Authorization=access_token)
                                )
        result = self.client().get('/v2/categories/1',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Bitter pie'.title(), str(result.data))

    def test_delete_category(self):
        """Tests if Api accepts a users request to delete a category"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                        "name": "Sweet pie",
                                                        "detail": "Made by mama"
                                                       },
                           headers=dict(Authorization=access_token)
                           )
        self.client().delete('/v2/categories/1',
                             headers=dict(Authorization=access_token),
                             )
        res = self.client().get('/v2/categories/1',
                                headers=dict(Authorization=access_token)
                                )
        self.assertEqual(res.status_code, 404)
    
    def test_user_can_search_through_categories_using_get_parameter_q(self):
        """Tests if a user queries a parameter it returns the closest matching category"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/v2/categories', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/v2/categories', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/search?q=chicken',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Made by brother".title(), str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_if_user_can_search_through_categories_with_no_token(self):
        """Tests if a user queries a parameter with no token"""
        search_result = self.client().get('/v2/categories/search?q=chicken',)
        self.assertIn("Please provide an access token".lower(), str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 499)

    def test_if_user_can_search_through_categories_with_invalid_token(self):
        """Tests if a user queries a parameter with invalid token"""
        search_result = self.client().get('/v2/categories/search?q=chicken',
                                          headers=dict(Authorization='Invalid.token'))
        self.assertIn("invalid", str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 498)

    def test_Search_none_existing_data_should_return_not_found(self):
        """Tests if a user queries a parameter WITH NONE EXISTING DATA"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/search?q=NONE_EXISTING',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Sorry we could not find what you are looking for", str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_search_param_q_not_provided_should_return_exception(self):
        """Tests if a user does not provide the parameter Q
        Used for searching.
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/search',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Cannot search for nothing", str(search_result.data))
        self.assertEqual(search_result.status_code, 400)

    def test_search_all_valid_data_provided_should_return_items(self):
        """Tests if a user queries a parameter it returns the closest matching recipe"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "recipe": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/1/recipes/search?q=chicken',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Made by brother".title(), str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_search_no_token_provided_should_return_exception(self):
        """Tests if a user queries a parameter with no access token"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/1/recipes/search?q=chicken',
                                          )
        self.assertIn("Please provide an access token", str(search_result.data))
        self.assertEqual(search_result.status_code, 499)

    def test_search_data_not_in_api_should_return_not_found(self):
        """Tests if a user queries a parameter that does not exist in api
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                               },
                           headers=dict(Authorization=access_token)
                           )

        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "Sour pie",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )
        self.client().post('/v2/categories/1/recipes', data={
                                                        "name": "chicken",
                                                        "detail": "Made by brother"
                                                        },
                           headers=dict(Authorization=access_token)
                           )

        search_result = self.client().get('/v2/categories/1/recipes/search?q=NONE_EXISTENT',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("Sorry we could not find what you are looking for", str(search_result.data))
        self.assertEqual(search_result.status_code, 200)

    def test_search_un_existing_category_should_return_exception(self):
        """Tests searching a None existent Category
         :returns: Category does not exist
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        search_result = self.client().get('/v2/categories/1/recipes/search?q=stuff',
                                          headers=dict(Authorization=access_token)
                                          )
        self.assertIn("This page does not exist on Iris", str(search_result.data))
        self.assertEqual(search_result.status_code, 404)