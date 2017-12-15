# tests/test_single_category_update.py

import unittest
import json
import uuid
import time

from api import db
from api.models import User, RecipeCategory
from tests.register_login import RegisterLogin


class TestUpdateSingleCategoriesBlueprint(RegisterLogin):

    def test_update_single_recipe_category(self):
        """
        Test for update single recipe category
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
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
    
    def test_update_single_recipe_category_id_not_number(self):
        """
        Test for update single recipe category id not number
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
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
            response = self.client.put('/recipe_category/a', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('Category ID must be an integer', 
                          str(response.data))
            self.assertIn('fail', str(response.data))
    
    def test_update_single_recipe_category_with_one_field(self):
        """
        Test for update single recipe category with one field
        """
        with self.client:
            response = self.register_user(
                "Patrick", "Walukagga", 
                "pwalukagga@gmail.com", "telnetcmd123"
            )
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
            category_data = json.dumps({"name": "Lunchfast"})
            response = self.client.put('/recipe_category/1', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Recipe Category updated', 
                          str(response.data))
            
            category_data = json.dumps({ "description": 
                                         "How to make lunchfast"})
            response = self.client.put('/recipe_category/1', 
                                        headers=headers,
                                        data=category_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Recipe Category updated', 
                          str(response.data))

if __name__ == '__main__':
    unittest.main()
