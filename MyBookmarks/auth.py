import functools

from flask import (Blueprint, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from MyBookmarks.db import get_db, init_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    '''View decorator that redirects anonymous users to the login page.'''

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    '''If a user id is stored in the session, load the user object from
    the database into ``g.user``.'''
    user_id = session.get('user_id')
    db = get_db()
    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


@bp.route('/login', methods=('GET', 'POST'))
def login():
    '''Log in a user by adding the user id to the session.'''
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        rememberme = request.form.get('rememberme')
        db = get_db()
        error = None
        try:
            user = db.execute('SELECT * FROM user WHERE username = ?',
                              (username.lower(),)).fetchone()
        except:
            tables = db.execute('SELECT name FROM sqlite_master').fetchall()
            if tables == []:
                init_db()
                flash('Detected first time running. Initialized the database.')
            else:
                flash('Critical Error! Please contact your system administrator.')
            return render_template('auth/login.html')

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password) and user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['id']
            if rememberme == 'on':
                session.permanent = True
            else:
                session.permanent = False
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/setting', methods=('GET', 'POST'))
@login_required
def setting():
    '''Change current user's password.'''
    if request.method == 'POST':
        password = request.form.get('password')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        db = get_db()
        error = 0
        message = None
        user = db.execute('SELECT password FROM user WHERE id = ?',
                          (g.user['id'],)).fetchone()

        if not check_password_hash(user['password'], password) and user['password'] != password:
            message = 'Incorrect password.'
            error = 1
        elif password1 != password2:
            message = "Confirm password doesn't match new password."
            error = 2
        elif password1 == password:
            message = 'New password cannot be the same as your current password.'
            error = 2
        elif password1 is None or password1 == '':
            message = 'New password cannot be blank.'

        if not message:
            # Store new password in the database and go to
            # the login page
            db.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (generate_password_hash(password1), g.user['id']),
            )
            db.commit()
            session.clear()
            return jsonify({'status': 1})

        return jsonify({'status': 0, 'message': message, 'error': error})

    return render_template('auth/setting.html')


@bp.route('/logout')
@login_required
def logout():
    '''Clear the current session, including the stored user id.'''
    session.clear()
    return redirect(url_for('auth.login'))
