# tests/test_recipes.py

import unittest
import json
import uuid
import time

from api import db
from api.models import User, RecipeCategory, Recipe
from tests.base import BaseTestCase


class TestRecipeBlueprint(BaseTestCase):

    # helper function to register user
    def register_user(self, first_name, last_name, email, password):
        user = json.dumps({"first_name": first_name,
                                "last_name": last_name,
                                "email": email,
                                "password": password})
        return self.client.post('/auth/register', data=user, 
                                 content_type='application/json')
    
    def test_recipe_creation_in_category(self):
        """
        Test for recipe creation in category
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        rep_login = self.client.post(
            'auth/login', data=registered_user, 
            content_type='application/json'
        )
        self.assertEqual(rep_login.status_code, 200)
        self.assertIn('Successfully logged in', 
                        str(rep_login.data))
        self.assertIn('success', str(rep_login.data))
        # valid token
        headers=dict(
            Authorization='Bearer ' + json.loads(
                rep_login.data.decode()
            )['auth_token']
        )
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New recipe added to category', 
                       str(response.data))
        # create recipe with same name
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recipe already exists', 
                       str(response.data))
        # create recipe in category which doesnot exit
        response = self.client.post('/recipe_category/3/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found in database', 
                       str(response.data))
        # create recipe with empty fields
        recipe_data = json.dumps({"name": "", 
                                  "ingredients": "",
                                  "description": ""})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('field names not provided', 
                       str(response.data))
    
    def test_get_recipes_in_category(self):
        """
        Test for getting recipes in category
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        rep_login = self.client.post(
            'auth/login', data=registered_user, 
            content_type='application/json'
        )
        self.assertEqual(rep_login.status_code, 200)
        self.assertIn('Successfully logged in', 
                        str(rep_login.data))
        self.assertIn('success', str(rep_login.data))
        # valid token
        headers=dict(
            Authorization='Bearer ' + json.loads(
                rep_login.data.decode()
            )['auth_token']
        )
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        recipe = Recipe(
            name="Rolex for Lunch",
            cat_id=2,
            user_id=1,
            ingredients="oil, Onions, Tomatoes",
            description="How to make breakfast rolex"            
        )
        recipe.save()
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New recipe added to category', 
                       str(response.data))
        response = self.client.get('/recipe_category/2/recipes', 
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Rolex for Lunch', str(response.data))
        self.assertIn('Mix and boil', str(response.data))
        # get recipes in category with limit
        response = self.client.get('/recipe_category/2/recipes?limit=1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Rolex for Lunch', str(response.data))
        self.assertNotIn('Mix and boil', str(response.data))
        # get recipes in category which doesnot exit
        response = self.client.get('/recipe_category/3/recipes', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found in database', 
                       str(response.data))
    
    def test_get_single_recipe_in_category(self):
        """
        Test for getting single recipe in category
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        rep_login = self.client.post(
            'auth/login', data=registered_user, 
            content_type='application/json'
        )
        self.assertEqual(rep_login.status_code, 200)
        self.assertIn('Successfully logged in', 
                        str(rep_login.data))
        self.assertIn('success', str(rep_login.data))
        # valid token
        headers=dict(
            Authorization='Bearer ' + json.loads(
                rep_login.data.decode()
            )['auth_token']
        )
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        recipe = Recipe(
            name="Rolex for Lunch",
            cat_id=2,
            user_id=1,
            ingredients="oil, Onions, Tomatoes",
            description="How to make breakfast rolex"            
        )
        recipe.save()
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New recipe added to category', 
                       str(response.data))
        response = self.client.get('/recipe_category/2/recipes/1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Rolex for Lunch', str(response.data))
        self.assertNotIn('Mix and boil', str(response.data))
        # get recipe not yet in database
        response = self.client.get('/recipe_category/2/recipes/4', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))
        # get recipe in category not yet in database
        response = self.client.get('/recipe_category/3/recipes/1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found in database', 
                      str(response.data))
    
    def test_update_recipe_in_category(self):
        """
        Test for editing recipe in category
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        rep_login = self.client.post(
            'auth/login', data=registered_user, 
            content_type='application/json'
        )
        self.assertEqual(rep_login.status_code, 200)
        self.assertIn('Successfully logged in', 
                        str(rep_login.data))
        self.assertIn('success', str(rep_login.data))
        # valid token
        headers=dict(
            Authorization='Bearer ' + json.loads(
                rep_login.data.decode()
            )['auth_token']
        )
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        recipe = Recipe(
            name="Rolex for Lunch",
            cat_id=2,
            user_id=1,
            ingredients="oil, Onions, Tomatoes",
            description="How to make breakfast rolex"            
        )
        recipe.save()
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New recipe added to category', 
                       str(response.data))
        recipe_data = json.dumps({"name": "Chicken Lunch Buffes", 
                                  "ingredients": "oil, Onions",
                                  "description": "Mix and boil"})
        response = self.client.put('/recipe_category/2/recipes/1', 
                                    headers=headers,
                                    data=recipe_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recipe has been updated', str(response.data))
        response = self.client.get('/recipe_category/2/recipes/1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Chicken Lunch Buffes', str(response.data))
        self.assertNotIn('Tomatoes', str(response.data))
        # update recipe not yet in database
        response = self.client.put('/recipe_category/2/recipes/4', 
                                    headers=headers,
                                    data=recipe_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))
        # update recipe in category not yet in database
        response = self.client.put('/recipe_category/3/recipes/1', 
                                    headers=headers,
                                    data=recipe_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found in database', 
                      str(response.data))
    
    def test_delete_recipe_in_category(self):
        """
        Test for deleting recipe in category
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        rep_login = self.client.post(
            'auth/login', data=registered_user, 
            content_type='application/json'
        )
        self.assertEqual(rep_login.status_code, 200)
        self.assertIn('Successfully logged in', 
                        str(rep_login.data))
        self.assertIn('success', str(rep_login.data))
        # valid token
        headers=dict(
            Authorization='Bearer ' + json.loads(
                rep_login.data.decode()
            )['auth_token']
        )
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        recipe = Recipe(
            name="Rolex for Lunch",
            cat_id=2,
            user_id=1,
            ingredients="oil, Onions, Tomatoes",
            description="How to make breakfast rolex"            
        )
        recipe.save()
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New recipe added to category', 
                       str(response.data))
        response = self.client.delete('/recipe_category/2/recipes/2', 
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recipe item deleted', str(response.data))
        response = self.client.get('/recipe_category/2/recipes/2', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))
        # delete recipe not yet in database
        response = self.client.delete('/recipe_category/2/recipes/4', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))
        # delete recipe in category not yet in database
        response = self.client.delete('/recipe_category/3/recipes/1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found in database', 
                      str(response.data))
    
    def test_recipe_crud_when_not_logged_in(self):
        """
        Test for recipe crud when not logged in
        """
        response = self.register_user(
            "Patrick", "Walukagga", 
            "pwalukagga@gmail.com", "telnetcmd123"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully registered', str(response.data))
        self.assertIn('success', str(response.data))
        # registered user login
        registered_user = json.dumps({
            "email": "pwalukagga@gmail.com",
            "password": "telnetcmd123" 
        })
        headers=dict(Authorization='Bearer ')
        category = RecipeCategory(
            name="Breakfast",
            description="How to make breakfast",
            user_id=1
        )
        category.save()
        category_data = json.dumps({"name": "LunchBuffe", 
                                    "description": 
                                    "How to make lunch buffe"})
        response = self.client.post('/recipe_category', 
                                    headers=headers,
                                    data=category_data)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))
        recipe = Recipe(
            name="Rolex for breakfast",
            cat_id=1,
            user_id=1,
            ingredients="oil, Onions, Tomatoes",
            description="How to make breakfast rolex"            
        )
        recipe.save()
        recipe_data = json.dumps({"name": "Chicken Lunch Buffe", 
                                  "ingredients": "oil, Onions,\
                                  Tomatoes",
                                  "description": "Mix and boil"})
        response = self.client.post('/recipe_category/2/recipes', 
                                    headers=headers, 
                                    data=recipe_data)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))
        response = self.client.delete('/recipe_category/2/recipes/2', 
                                    headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))
        response = self.client.get('/recipe_category/2/recipes/2', 
                                    headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))
        # delete recipe not yet in database
        response = self.client.delete('/recipe_category/2/recipes/4', 
                                    headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))
        # delete recipe in category not yet in database
        response = self.client.delete('/recipe_category/3/recipes/1', 
                                    headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', str(response.data))