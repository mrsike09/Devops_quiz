import unittest
import os
import shutil
import tempfile
from database import FallbackDatabase
from app import app

class QuizAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a temporary database file for testing the fallback mechanism
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_db.json')
        self.fallback_db = FallbackDatabase(self.db_path)
        
        # Set up Flask test client
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def tearDown(self):
        # Clean up the temporary database file and folder
        shutil.rmtree(self.test_dir)

    def test_database_insert_and_find(self):
        collection = self.fallback_db.test_collection
        
        # Test insert_one
        doc = {'name': 'Trivia Test', 'score': 95}
        result = collection.insert_one(doc)
        self.assertIsNotNone(result.inserted_id)
        
        # Test find_one
        found = collection.find_one({'name': 'Trivia Test'})
        self.assertIsNotNone(found)
        self.assertEqual(found['score'], 95)
        
        # Test find all
        all_docs = collection.find()
        self.assertEqual(len(all_docs), 1)

    def test_database_update(self):
        collection = self.fallback_db.test_collection
        doc = {'_id': 'test-id-123', 'name': 'Update Tester', 'items': [1, 2]}
        collection.insert_one(doc)
        
        # Test update_one with $set
        collection.update_one({'_id': 'test-id-123'}, {'$set': {'name': 'Updated Name'}})
        updated_doc = collection.find_one({'_id': 'test-id-123'})
        self.assertEqual(updated_doc['name'], 'Updated Name')
        
        # Test update_one with $push
        collection.update_one({'_id': 'test-id-123'}, {'$push': {'items': 3}})
        updated_doc = collection.find_one({'_id': 'test-id-123'})
        self.assertEqual(updated_doc['items'], [1, 2, 3])

    def test_database_delete(self):
        collection = self.fallback_db.test_collection
        doc = {'name': 'Delete Me'}
        collection.insert_one(doc)
        
        # Test delete
        collection.delete_one({'name': 'Delete Me'})
        found = collection.find_one({'name': 'Delete Me'})
        self.assertIsNone(found)

    def test_flask_routes_guest(self):
        # Verify guest can access dashboard
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Verify guest can access login page
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        
        # Verify guest can access register page
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        
        # Verify guest can access leaderboard page
        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        
        # Verify protected routes redirect to login
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])
        
        response = self.client.get('/quiz/create')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])

if __name__ == '__main__':
    unittest.main()
