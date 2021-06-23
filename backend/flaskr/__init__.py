import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''

    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
            )
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories')
    def get_categories():
        category_list = Category.query.all()

        if len(category_list) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': [category.format() for category in category_list]
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions')
    def get_questions():
        try:
            questions_list = Question.query.all()
            categories_list = Category.query.all()

            page = request.args.get('page', 1)
            list_size_min = min(int(page) * QUESTIONS_PER_PAGE * 2,
                                len(questions_list))
            print([question.format() for question in questions_list])
            print((int(page)-1) * QUESTIONS_PER_PAGE)
            print(list_size_min)
            print(int(page))
            paginated_question_list = questions_list[(int(page)-1) * QUESTIONS_PER_PAGE:
                                                     list_size_min]
            paginated_questions_categories = []
            for question in paginated_question_list:
                paginated_questions_categories\
                    .append(category for category in
                            categories_list if category.type == question.category)

            return jsonify({
                'success': True,
                'questions': [question.format() for question in paginated_question_list],
                'totalQuestions': len(questions_list),
                'categories':  [category.format() for category in categories_list],
                'currentCategory': [category.format() for category in paginated_questions_categories]
            })
        except:
            abort(404)

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return ({
                'success': True,
                'questionId': question_id
            })
        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route('/posts', methods=['POST'])
    def add_new_question():
        question_data = request.get_json()

        if not ('question' in question_data and 'answer' in question_data and
                'category' in question_data):
            abort(422)

        try:
            question = Question(
                question=question_data.get('question'),
                answer=question_data.get('answer'),
                difficulty=question_data.get('difficulty'),
                category=question_data.get('category')
            )
            question.insert()

            return ({
                'success': True
            })
        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route('/questions/search', methods=['POST'])
    def questions_search():
        search_term = request.body.get('searchTerm')

        if search_term:
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return ({
                'success': True,
                'questions': [question.format() for question in questions],
                'totalQuestions': len(questions),
                'currentCategory': None
            })
        else:
            abort(404)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            return ({
                'success': True,
                'questions': [question.format() for question in questions],
                'totalQuestions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        try:
            quiz_data = request.get_json()

            if not ('quizCategory' in quiz_data and
                    'previousQuestions' in quiz_data):
                abort(422)

            if quiz_data.get('quiz_category')['type'] == 'click':
                questions = Question.query \
                    .filter(Question.id.notin_(quiz_data.get(
                        quiz_data.get('previousQuestions')))).all()
            else:
                questions = Question.query.filter_by(
                    category=quiz_data.get('quizCategory')[id]) \
                    .filter(Question.id.notin_(quiz_data.get(
                        quiz_data.get('previousQuestions'))))

            question = questions[random.randrange(0, len(questions))].format()\
                if len(questions) > 0 else None

            return ({
                'success': True,
                'question': question
            })
        except:
            abort(422)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def not_found(error):
        return ({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable data'
        }), 422

    @app.errorhandler(500)
    def serverside_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'server-side error'
        }), 500

    return app
