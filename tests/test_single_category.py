# tests/test_categories.py

import unittest
import json
import uuid
import time

from api import db
from api.models import User, RecipeCategory
from tests.register_login import RegisterLogin


class TestSingleCategoriesBlueprint(RegisterLogin):
    
    
    def test_user_retrieve_single_recipe_category(self):
        """
        Test for user retrieves single recipe category
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn('Successfully registered', str(response.data))
            self.assertIn('success', str(response.data))
            rep_login = self.login_user("pwalukagga@gmail.com", "telnetcmd123")
            # valid token
            headers=dict(
                Authorization='Bearer ' + json.loads(
                    rep_login.data.decode()
                )['auth_token']
            )
            response = self.create_category("Breakfast", 
                                            "How to make breakfast", 
                                            headers)
            
            response = self.create_category("Lunchfast", 
                                            "How to make lunchfast", 
                                            headers)
            response = self.client.get('/recipe_category/2', 
                                        headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn('How to make lunchfast', 
                        str(response.data))
            self.assertNotIn('How to make breakfast', 
                        str(response.data))
    
    def test_user_retrieves_single_recipe_category_not_in_database(self):
        """
        Test for user retrieves single recipe category which does not exist
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn('Successfully registered', str(response.data))
            self.assertIn('success', str(response.data))
            # registered user login
            rep_login = self.login_user("pwalukagga@gmail.com", "telnetcmd123")
            # valid token
            headers=dict(
                Authorization='Bearer ' + json.loads(
                    rep_login.data.decode()
                )['auth_token']
            )
            response = self.create_category("Breakfast", 
                                            "How to make breakfast", 
                                            headers)
            
            response = self.create_category("Lunchfast", 
                                            "How to make lunchfast", 
                                            headers)
            response = self.client.get('/recipe_category/5', 
                                        headers=headers)
            self.assertEqual(response.status_code, 404)
            self.assertIn('No category found', str(response.data))
            self.assertNotIn('How to make breakfast', 
                             str(response.data))
    
    def test_update_single_recipe_category(self):
        """
        Test for update single recipe category
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn('Successfully registered', str(response.data))
            self.assertIn('success', str(response.data))
            # registered user login
            rep_login = self.login_user("pwalukagga@gmail.com", "telnetcmd123")
            # valid token
            headers=dict(
                Authorization='Bearer ' + json.loads(
                    rep_login.data.decode()
                )['auth_token']
            )
            response = self.create_category("Breakfast", 
                                            "How to make breakfast", 
                                            headers)
            category_data = json.dumps({"name": "Lunchfast", 
                                     "description": 
                                     "How to make lunchfast"})
            response = self.client.put('/recipe_category/1', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Recipe Category updated', 
                          str(response.data))
            self.assertNotIn('How to make breakfast', 
                             str(response.data))
            # update recipe category not in database
            response = self.client.put('/recipe_category/3', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 404)
            self.assertIn('No category found', 
                          str(response.data))
            self.assertNotIn('How to make lunchfast', 
                             str(response.data))
    
    def test_delete_single_recipe_category(self):
        """
        Test for delete single recipe category
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn('Successfully registered', str(response.data))
            self.assertIn('success', str(response.data))
            # registered user login
            rep_login = self.login_user("pwalukagga@gmail.com", "telnetcmd123")
            # valid token
            headers=dict(
                Authorization='Bearer ' + json.loads(
                    rep_login.data.decode()
                )['auth_token']
            )
            cresponse = self.create_category("Breakfast", 
                                            "How to make breakfast", 
                                            headers)
            
            response = self.create_category("Lunchfast", 
                                            "How to make lunchfast", 
                                            headers)
            response = self.client.delete('/recipe_category/1', 
                                        headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Recipe category deleted', 
                        str(response.data))
            # delete recipe category not in database
            response = self.client.delete('/recipe_category/3', 
                                        headers=headers, )
            self.assertEqual(response.status_code, 404)
            self.assertIn('No category found', 
                          str(response.data))

    def test_crud_category_when_not_logged_in(self):
        """
        Test for crud recipe category when not logged in
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn('Successfully registered', str(response.data))
            self.assertIn('success', str(response.data))
            # invalid token
            headers=dict(Authorization='Bearer ')
            response = self.create_category("Breakfast", 
                                            "How to make breakfast", 
                                            headers)
            self.assertEqual(response.status_code, 401)
            self.assertIn('Token is missing', str(response.data))
            category_data = json.dumps({"name": "Lunchfast", 
                                     "description": 
                                     "How to make lunchfast"})
            response = self.client.put('/recipe_category/1', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 401)
            self.assertIn('Token is missing', str(response.data))
            response = self.client.delete('/recipe_category/1', 
                                        headers=headers, 
                                        data=category_data)
            self.assertEqual(response.status_code, 401)
            self.assertIn('Token is missing', str(response.data))
            # delete recipe category not in database
            response = self.client.delete('/recipe_category/3', 
                                        headers=headers, 
                                        data=category_data)
            self.assertEqual(response.status_code, 401)
            self.assertIn('Token is missing', str(response.data))