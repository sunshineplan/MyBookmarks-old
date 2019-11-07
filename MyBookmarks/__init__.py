import os
import sys

from flask import Flask


def create_app():
    '''Create and configure an instance of the Flask application.'''
    app = Flask(__name__, instance_relative_config=True)
    # store the database in the instance folder
    app.config['DATABASE'] = os.path.join(app.instance_path, 'mybookmarks.db')
    app.config['SECRET_KEY'] = os.urandom(16)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from MyBookmarks import db

    db.init_app(app)

    # apply the blueprints to the app
    from MyBookmarks import auth, bookmark

    app.register_blueprint(auth.bp)
    app.register_blueprint(bookmark.bp)

    app.add_url_rule('/', endpoint='index')

    return app
