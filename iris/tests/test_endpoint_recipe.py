"""
TestCase for enpoint /recipes
"""
import json

from iris.tests import base


class RecipeTestCase(base.BaseApiTestCase):
    """
    Test Enpoint /recipes
    """
    
    def test_post_recipe_no_token_provided_should_return_exception(self):
        """Tests if api can create recipes when no token in headers(post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        result = self.client().post('/v2/categories/1/recipes', data={
            "name": "Grandma home made",
            "recipe": "1 tea spoon sugar"
        },
                                    )
        self.assertEqual(result.status_code, 499)
        self.assertIn('Please provide an access token', str(result.data))

    def test_post_recipe_should_create_recipe(self):
        """Tests if api can create recipes inside a category(post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        result = self.client().post('/v2/categories/1/recipes', data={
                                                                                   "name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tea spoon'.title(), str(result.data))

    def test_post_recipe_invalid_token_should_return_exception(self):
        """Recipes should not be created without a valid Token"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
            "name": "Sweet pie",
            "detail": "Made by mama"
        },
                                 headers=dict(Authorization=access_token)
                                 )
        res = self.client().post('/v2/categories/1/recipes', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization='Invalid.token')
                                 )
        self.assertEqual(res.status_code, 498)
        self.assertIn("invalid" or 'expired', str(res.data).lower())

    def test_post_recipe_bad_item_names_should_return_exception(self):
        """Tests if api can create recipes with incorrect item names(post)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/v2/categories/1/recipes', data={
                                                                                   "Invalid name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(result.status_code, 400)
        self.assertIn('please use keys name and recipe', str(result.data))

    def test_get_recipe_get_recipe_should_return_recipe(self):
        """Tests if api can get recipes (get)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']
        res = self.client().post('/v2/categories', data={
                                                                "name": "Sweet pie",
                                                                "detail": "Made by mama"
                                                                },
                                 headers=dict(Authorization=access_token)
                                 )
        self.assertIn("Sweet pie".title(), str(res.data))
        result = self.client().post('/v2/categories/1/recipes', data={
                                                                                   "name": "Grandma home made",
                                                                                   "recipe": "1 tea spoon sugar"
                                                                                    },
                                    headers=dict(Authorization=access_token)
                                    )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tea spoon'.title(), str(result.data))
        result = self.client().get('/v2/categories/1/recipes',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertEqual(result.status_code, 200)
        self.assertIn('tea spoon'.title(), str(result.data))

    def test_get_recipe_no_recipes_available_should_notify_user(self):
        """Test for a get request to an empty category.
         Should return a message notification Nothing here yet
        (get)"""
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
        result = self.client().get('/v2/categories/1/recipes',
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertIn('Nothing Here yet', str(result.data))

    def test_put_recipe_edit_recipe_should_edit_recipe(self):
        """Tests if api can edit a recipe"""
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
                                                            "name": "Grandma's home made",
                                                            "recipe": "1 tea spoon sugar"
                                                            },
                           headers=dict(Authorization=access_token)
                           )
        result = self.client().put('/v2/categories/1/recipes/1', data={
                                                                                    "name": "Uncle's homemade",
                                                                                    "recipe": "1 bowl of onions"
                                                                                    },
                                   headers=dict(Authorization=access_token)
                                   )
        final = self.client().get('/v2/categories/1/recipes/1',
                                  headers=dict(Authorization=access_token)
                                  )
        self.assertIn('bowl of'.title(), str(final.data))

    def test_search_recipes_invalid_token_should_return_exception(self):
        """Tests if a user queries a recipe with invalid token """
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
                                          headers=dict(Authorization='Invalid.token')
                                          )
        self.assertIn("invalid" or 'expired', str(search_result.data).lower())
        self.assertEqual(search_result.status_code, 498)

    def test_get_recipes_none_exitent_category_should_return_exception(self):
        """Tests if a user can get recipe by id from the category that does not exist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['Access token']

        result = self.client().get('/v2/categories/1/recipes/1', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                                   headers=dict(Authorization=access_token)
                                   )
        self.assertIn("This page does not exist on iris", str(result.data))
        self.assertEqual(result.status_code, 404)

    def test_get_recipe_by_id_invalid_token_should_return_exception(self):
        """Tests if a user can get recipe by id with an invalid token"""
        result = self.client().get('/v2/categories/1/recipes/1', data={
                                                        "name": "Sour pie",
                                                        "recipe": "Made by brother"
                                                        },
                                   headers=dict(Authorization='Invalid.token')
                                   )
        self.assertIn("invalid", str(result.data).lower())
        self.assertEqual(result.status_code, 498)