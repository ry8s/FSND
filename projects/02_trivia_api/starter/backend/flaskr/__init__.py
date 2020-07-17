import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#----------------------------------------------------------------------------#
# App Setup
#----------------------------------------------------------------------------#


def create_app(test_config=None):
    '''create and configure the app'''
    app = Flask(__name__)
    setup_db(app)

    '''
  TODO DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  TODO DONE: Use the after_request decorator to set Access-Control-Allow
  '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

#----------------------------------------------------------------------------#
# Custom Functions
#----------------------------------------------------------------------------#

    def paginate_questions(request, selection):
        '''Paginate and format questions 

        Parameters:
          * <HTTP object> request, that may contain a "page" value
          * <database selection> selection of questions  queried from database

        Returns:
          * <list> of dictionaries of questions. max of 10

        '''
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    def getErrorMessage(error, default_text):
        '''Returns default error or custom error message

        Parameters:
          * <error> system generated error message containing a message
          * <string> default text to be used as error message if Error has no specific message

        Returns:
          * <string> specific error message or default text

        '''
        try:
            return error.description["message"]
        except TypeError:
            return default_text


#  API Endpoints
#  ----------------------------------------------------------------
#  NOTE:  For explanation of each endpoint, please look at the backend/README.md file.
#----------------------------------------------------------------------------#
# Endpoint /questions GET/POST/DELETE
#----------------------------------------------------------------------------#
    '''
  # TODO DONE Create an endpoint to handle GET requests for questions
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST DONE: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        '''Returns paginated questions

        Tested by:
          Success:
            - test_get_all_categories
          Error:
            - test_error_405_get_all_categories

        '''
        selection = Question.query.order_by(Question.id).all()
        questions_paginated = paginate_questions(request, selection)
        if len(questions_paginated) == 0:
            abort(404)

        categories = Category.query.all()
        categories_all = [category.format() for category in categories]

        categories_returned = []
        for cat in categories_all:
            categories_returned.append(cat['type'])
        return jsonify({
            'questions': questions_paginated,
            'total_questions': len(selection),
            'categories': categories_returned,
            'current_category': categories_returned,
            'success': True,
        })

    # TODO DONE: Create an endpoint to DELETE question using a question ID.
    '''
  TEST DONE: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        '''Delete a question
          Tested by:
            Success:
              - test_delete_question
            Error:
              - test_404_delete_question
        '''

        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if not question:
            abort(
                400, {'message': 'Question {} does not exist.'.format(question_id)})

        try:
            question.delete()
            return jsonify({
                'deleted': question_id,
                'success': True,
            })
        except:
            abort(422)
    '''
  # TODO DONE:  Create an endpoint to POST a new question,  
  which will require the question and answer text,  
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  ADDITIONALLY:

  # TODO DONE: Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 

  '''
    @app.route('/questions', methods=['POST'])
    def create_or_search_questions():
        '''Creates a question or searches for it with search term

          Tested by:
            Success:
              - test_create_question
              - test_search_question
            Error:
              - test_error_create_question
              - test_error_404_search_question

        '''
        body = request.get_json()

        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        search_term = body.get('searchTerm', None)

        if search_term:
            questions = Question.query.filter(
                Question.question.contains(search_term)).all()

            if not questions:
                abort(
                    404, {'message': 'no questions containing "{}" found.'.format(search_term)})

            questions_found = [question.format() for question in questions]
            selections = Question.query.order_by(Question.id).all()
            categories = Category.query.all()
            categories_all = [category.format() for category in categories]

            return jsonify({
                'questions': questions_found,
                'total_questions': len(selections),
                'current_category': categories_all,
                'success': True,
            })

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if not new_question:
            abort(400, {'message': 'Question is required'})

        if not new_answer:
            abort(400, {'message': 'Answer is required'})

        if not new_category:
            abort(400, {'message': 'Category is required'})

        if not new_difficulty:
            abort(400, {'message': 'Difficulty is required'})

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            selections = Question.query.order_by(Question.id).all()
            questions_paginated = paginate_questions(request, selections)

            return jsonify({
                'created': question.id,
                'questions': questions_paginated,
                'total_questions': len(selections),
                'success': True,
            })

        except:
            abort(422)

#----------------------------------------------------------------------------#
# Endpoint /quizzes POST
#----------------------------------------------------------------------------#
    '''
  TODO DONE: Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        '''Play quiz by returning a random question

          Tested by:
            Success:
              - test_play_quiz_with_category
              - test_play_quiz_without_category
            Error:
              - test_error_400_play_quiz
              - test_error_405_play_quiz

        '''
        body = request.get_json()

        if not body:
            abort(400, {
                  'message': 'Please provide a JSON body with previous question Ids and optional category.'})

        previous_questions = body.get('previous_questions', None)
        current_category = body.get('quiz_category', None)

        if not previous_questions:
            if current_category:
                questions_raw = (Question.query
                                 .filter(Question.category == str(current_category['id']))
                                 .all())
            else:
                questions_raw = (Question.query.all())
        else:
            if current_category:
                questions_raw = (Question.query
                                 .filter(Question.category == str(current_category['id']))
                                 .filter(Question.id.notin_(previous_questions))
                                 .all())
            else:
                questions_raw = (Question.query
                                 .filter(Question.id.notin_(previous_questions))
                                 .all())

        questions_formatted = [question.format() for question in questions_raw]
        random_question = questions_formatted[random.randint(
            0, len(questions_formatted))]

        return jsonify({
            'question': random_question,
            'success': True,

        })
#----------------------------------------------------------------------------#
# Endpoint /catogories GET
#----------------------------------------------------------------------------#

    # TODO DONE Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''Returns all categories as list
          Tested by:
            Success:
              - test_get_all_categories
            Error:
              - test_400_get_categories
        '''
        categories = Category.query.all()

        if not categories:
            abort(404)

        categories_all = [category.format() for category in categories]

        categories_returned = []
        for cat in categories_all:
            categories_returned.append(cat['type'])

        return jsonify({
            'categories': categories_returned,
            'success': True,
        })

    '''
  # TODO DONE: Create a GET endpoint to get questions based on category. 
  TEST DONE: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<string:category_id>/questions', methods=['GET'])
    def get_questions_from_categories(category_id):
        '''Returns paginated questions from specific category

            Tested by:
              Success:
                - test_get_questions_from_category
              Error:
                - test_400_get_questions_from_category
        '''

        selection = (Question.query
                     .filter(Question.category == str(category_id))
                     .order_by(Question.id)
                     .all())

        if not selection:
            abort(
                400, {'message': 'No questions with category {} found.'.format(category_id)})

        questions_paginated = paginate_questions(request, selection)

        if not questions_paginated:
            abort(404, {'message': 'No questions in selected page.'})

        return jsonify({
            'questions': questions_paginated,
            'total_questions': len(selection),
            'current_category': category_id,
            'success': True,
        })

#----------------------------------------------------------------------------#
# API error handler & formatter.
#----------------------------------------------------------------------------#

    # TODO DONE: Create error handlers for all expected errors

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": getErrorMessage(error, "bad request")
        }), 400

    @app.errorhandler(404)
    def ressource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": getErrorMessage(error, "resource not found")
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": getErrorMessage(error, "unprocessable")
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
