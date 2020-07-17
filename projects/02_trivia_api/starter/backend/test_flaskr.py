import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

    def setUp(self):
        '''Define test variables and initialize app.'''
        user = 'postgres'
        pwd = 'testpass123'
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            user, pwd, 'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        ''' binds the app to the current context'''
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        '''Executed after reach test'''
        pass

    '''
    TODO DONE
    Write at least one test for each test for successful operation and for expected errors.
    '''

#----------------------------------------------------------------------------#
# General Test
#----------------------------------------------------------------------------#

    def test_endpoint_not_available(self):
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

#----------------------------------------------------------------------------#
# Tests for /questions POST
#----------------------------------------------------------------------------#

    def test_create_question(self):
        json_create_question = {
            'question': 'What is the meaning of life?',
            'answer': '42',
            'category': '2',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_create_question(self):
        json_create_question_error = {
            'question': 'What is the meaning of life?',
            'answer': '24',
            'category': 1
        }

        res = self.client().post('/questions', json=json_create_question_error)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Difficulty is required')

    def test_search_question(self):

        json_search_question = {
            'searchTerm': 'cat',
        }

        res = self.client().post('/questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_404_search_question(self):

        json_search_question = {
            'searchTerm': 'tacocat',
        }

        res = self.client().post('/questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'no questions containing "tacocat" found.')


#----------------------------------------------------------------------------#
# Tests for /questions GET
#----------------------------------------------------------------------------#

    def test_get_all_questions_paginated(self):
        res = self.client().get('/questions?page=1',
                                json={'category:': 'science'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_404_get_all_questions_paginated(self):
        res = self.client().get('/questions?page=12452512')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

#----------------------------------------------------------------------------#
# Tests for /questions DELETE
#----------------------------------------------------------------------------#

    def test_delete_question(self):

        json_create_question = {
            'question': 'Am I sorry?',
            'answer': 'Yes!',
            'category': '1',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question)
        data = json.loads(res.data)
        question_id = data['created']

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], question_id)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/{}'.format(8675309))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(
            data['message'], 'Question {} does not exist.'.format(8675309))

#----------------------------------------------------------------------------#
# Tests for /categories GET
#----------------------------------------------------------------------------#
    def test_get_all_categories(self):
        json_create_category = {
            'type': 'Sports'
        }

        res = self.client().post('/categories', json=json_create_category)
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']) > 0)


#----------------------------------------------------------------------------#
# Tests for /categories/<string:category_id>/questions GET
#----------------------------------------------------------------------------#

    def test_get_questions_from_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], '1')

    def test_400_get_questions_from_category(self):
        res = self.client().get('/categories/999999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(
            data['message'], 'No questions with category 999999 found.')


#----------------------------------------------------------------------------#
# Tests for /quizzes POST
#----------------------------------------------------------------------------#

    def test_play_quiz_with_category(self):
        json_play_quizz = {
            'previous_questions': [1, 2, 5],
            'quiz_category': {
                'type': 'History',
                'id': '4'
            }
        }
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id']
                        not in json_play_quizz['previous_questions'])

    def test_play_quiz_without_category(self):
        json_play_quizz = {
            'previous_questions': [3, 4, 6],
        }
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id']
                        not in json_play_quizz['previous_questions'])

    def test_error_400_play_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(
            data['message'], 'Please provide a JSON body with previous question Ids and optional category.')


if __name__ == "__main__":
    unittest.main()
