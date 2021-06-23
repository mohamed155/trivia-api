import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_questions_request(self):
        # request response
        response = self.client().get('/questions')
        # data returned from the request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)

        # test response properties values
        self.assertEqual(data.success, True)
        self.assertTrue(data.totalQuestions)
        self.assertTrue(len(data.questions))
        self.assertTrue(len(data.categories))
        self.assertTrue(len(data.currentCategory))

    def test_questions_invalid_page_error(self):
        # request response
        response = self.client().get('/questions?page=8000')
        # data returned from the request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 404)

        # test response properties values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, 'not found')

    def test_categories_request(self):
        # request response
        response = self.client().get('/categories')
        # data returned from the request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)

        # test response properties
        self.assertEqual(data.success, True)
        self.assertTrue(len(data.categories))

    def test_categories_invalid_page_error(self):
        # request response
        response = self.client().get('/categories/8000')
        # data returned from the request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 404)

        # test response properties
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, 'not found')

    def test_question_deletion(self):
        # create a question and insert into the database
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        # response returned from request
        response = self.client().delete(f'/questions/{question_id}')
        # data returned in the response
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)
        # test response properties
        self.assertEqual(data.success, True)
        self.assertEqual(data.questionId, str(question_id))

        # try to get the deleted question
        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        # test if the question is not exist
        self.assertEqual(question, None)

    def test_question_deletion_error(self):
        # request response
        response = self.client().delete('/questions/8000')
        # data returned from request
        data = json.loads(response.data)

        # test response status
        self.assertEqual(response.status_code, 422)
        # test response properties values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, 'unprocessable data')

    def test_question_addition(self):
        # create a new question data
        new_question_data = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        # get questions number in database before addition
        questions_number_before_addition = len(Question.query.all())
        # send question addition request and get response
        response = self.client().post('/questions', json=new_question_data)
        # get data returned from request
        data = json.loads(response.data)
        # get questions number in database after addition
        questions_number_after_addition = len(Question.query.all())

        # test request status
        self.assertEqual(response.status_code, 200)
        # test request success
        self.assertEqual(data.success, True)
        # test the questions number if it grows by one
        self.assertEqual(questions_number_after_addition, questions_number_before_addition + 1)

    def test_question_addition_error(self):
        # create uncompleted question data
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 422)
        # test response properties values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, "unprocessable data")

    def test_questions_search_request(self):
        # make a search term to search with
        search_term = {'searchTerm': 'dummy question'}
        # send search request and get response
        response = self.client().post('/questions/search', json=search_term)
        # get the data returned from request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)
        # test request response values
        self.assertEqual(data.success, True)
        self.assertIsNotNone(data.questions)
        self.assertIsNotNone(data.totalQuestions)

    def test_search_request_error(self):
        # make an invalid search term to search with
        new_search = {'searchTerm': ''}

        # send search request and get response
        response = self.client().post('/questions/search', json=new_search)
        # get the data returned from request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 404)
        # test request response values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, "not found")

    def test_category_questions_request(self):
        # send search request and get response
        response = self.client().get('/categories/1/questions')
        # get the data returned from request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)

        # test request response values
        self.assertEqual(data.success, True)
        self.assertTrue(len(data.questions))
        self.assertTrue(data.totalQuestions)
        self.assertTrue(data.currentCategory)

    def test_category_questions_request_error(self):
        # send an invalid search request and get response
        response = self.client().get('/categories/a/questions')
        # get the data returned from request
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 404)
        # test request response values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, "not found")

    def test_quiz_request(self):
        # make a quiz object
        quiz_object = {'quizCategory': {'id': 10, 'type': 'Entertainment'},
                       'previousQuestions': []}

        # send request and get response
        response = self.client().post('/quizzes', json=quiz_object)
        # get data came from response
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 200)
        # test response values
        self.assertEqual(data.success, True)

    def test_quiz_request_error(self):
        # make a quiz object without category
        quiz_object = {'previousQuestions': []}
        # send request and get response
        response = self.client().post('/quizzes', json=quiz_object)
        # get data came from response
        data = json.loads(response.data)

        # test request status
        self.assertEqual(response.status_code, 422)
        # test response values
        self.assertEqual(data.success, False)
        self.assertEqual(data.message, "unprocessable data")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
