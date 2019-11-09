from json import loads

from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, url_for)

from MyBookmarks.auth import login_required
from MyBookmarks.db import get_db

bp = Blueprint('bookmark', __name__)


@bp.route('/')
@login_required
def index():
    '''Show all the bookmarks belong the current user.'''
    db = get_db()
    categories = db.execute(
        'SELECT * FROM category WHERE user_id = ?', (g.user['id'],)).fetchall()
    return render_template('bookmark/index.html', categories=categories)


@bp.route('/category/get', methods=('GET',))
@login_required
def get_category():
    '''Get current user's categories.'''
    db = get_db()
    categories = db.execute(
        'SELECT id, category FROM category WHERE user_id = ?', (g.user['id'],)).fetchall()
    return jsonify(categories)


@bp.route('/category/add', methods=('GET', 'POST'))
@login_required
def add_category():
    '''Create a new category for the current user.'''
    if request.method == 'POST':
        db = get_db()
        category = request.form.get('category')
        if db.execute('SELECT id FROM category WHERE category = ? AND user_id = ?', (category, g.user['id'])).fetchone() is not None:
            flash(f'Category {category} is already existed.')
        else:
            db.execute(
                'INSERT INTO category (category, user_id) VALUES (?, ?)', (category, g.user['id']))
            db.commit()
            return redirect(url_for('index'))
    return render_template('bookmark/category.html', id=0, category={})


@bp.route('/category/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_category(id):
    '''Edit a category for the current user.'''
    db = get_db()
    category = db.execute(
        'SELECT * FROM category WHERE id = ? AND user_id = ?', (id, g.user['id'])).fetchone()
    if request.method == 'POST':
        old = category['category']
        new = request.form.get('category')
        error = None
        if old == new:
            error = 'New category is same as old category.'
        elif db.execute('SELECT id FROM category WHERE category = ? AND user_id = ?', (new, g.user['id'])).fetchone() is not None:
            error = f'Category {new} is already existed.'

        if error:
            flash(error)
        else:
            db.execute(
                'UPDATE category SET category = ? WHERE id = ? AND user_id = ?', (new, id, g.user['id']))
            db.commit()
            return redirect(url_for('index'))
    return render_template('bookmark/category.html', id=id, category=category)


@bp.route('/category/delete/<int:id>', methods=('POST',))
@login_required
def delete_category(id):
    '''Edit a category for the current user.'''
    db = get_db()
    db.execute('DELETE FROM category WHERE id = ? and user_id = ?',
               (id, g.user['id']))
    db.execute('UPDATE bookmark SET category_id = 0 WHERE category_id = ? and user_id = ?',
               (id, g.user['id']))
    db.commit()
    return redirect(url_for('index'))


@bp.route('/bookmark/get', defaults={'category_id': -1})
@bp.route('/bookmark/get/<int:category_id>', methods=('GET',))
@login_required
def get_bookmark(category_id):
    '''Get current user's bookmark of specified category.'''
    db = get_db()
    if category_id == -1:
        category = 'All Bookmarks'
        bookmarks = db.execute('SELECT bookmark, url, category FROM bookmark'
                               ' LEFT JOIN category ON category_id = category.id'
                               ' WHERE bookmark.user_id = ?',
                               (g.user['id'],)).fetchall()
    else:
        category = db.execute('SELECT category FROM category WHERE id = ? AND user_id = ?',
                              (category_id, g.user['id'])).fetchone()['category']
        bookmarks = db.execute('SELECT bookmark, url FROM bookmark WHERE category_id = ? AND user_id = ?',
                               (category_id, g.user['id'])).fetchall()
        for i in bookmarks:
            i['category'] = category
    return jsonify({'category': category, 'bookmarks': bookmarks})


@bp.route('/bookmark/add', methods=('GET', 'POST'))
@login_required
def add_bookmark():
    '''Create a new bookmark for the current user.'''
    if request.method == 'POST':
        db = get_db()
        category = request.form.get('category')
        bookmark = request.form.get('bookmark')
        url = request.form.get('url')
        if db.execute('SELECT id FROM bookmark WHERE url = ? AND user_id = ?', (url, g.user['id'])).fetchone() is not None:
            flash(f'Bookmark {url} is already existed.')
        else:
            db.execute('INSERT INTO bookmark (bookmark, url, user_id, category_id)'
                       ' VALUES (?, ?, ?, ?)', (bookmark, url, g.user['id'], category))
            db.commit()
            return redirect(url_for('index'))
    return render_template('bookmark/bookmark.html', id=0, bookmark={})


@bp.route('/bookmark/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_bookmark(id):
    '''Edit a bookmark for the current user.'''
    db = get_db()
    bookmark = db.execute(
        'SELECT * FROM bookmark WHERE id = ? AND user_id = ?', (id, g.user['id'])).fetchone()
    if request.method == 'POST':
        old = (bookmark['bookmark'], bookmark['url'], bookmark['category'])
        bookmark = request.form.get('bookmark')
        url = request.form.get('url')
        category = request.form.get('category')
        error = None
        if old == (bookmark, url, category):
            error = 'New bookmark is same as old bookmark.'
        elif db.execute('SELECT id FROM bookmark WHERE bookmark = ? AND id != ? AND user_id = ?', (bookmark, id, g.user['id'])).fetchone() is not None:
            error = f'Bookmark name {bookmark} is already existed.'
        elif db.execute('SELECT id FROM bookmark WHERE url = ? AND id != ? AND user_id = ?', (url, id, g.user['id'])).fetchone() is not None:
            error = f'Bookmark url {url} is already existed.'

        if error:
            flash(error)
        else:
            db.execute('UPDATE bookmark SET bookmark = ?, url = ?, category = ?'
                       ' WHERE id = ? AND user_id = ?', (bookmark, url, category, id, g.user['id']))
            db.commit()
            return redirect(url_for('index'))
    return render_template('bookmark/bookmark.html', id=id, bookmark=bookmark)


@bp.route('/bookmark/delete/<int:id>', methods=('POST',))
@login_required
def delete_bookmark(id):
    '''Edit a bookmark for the current user.'''
    db = get_db()
    db.execute('DELETE FROM bookmark WHERE id = ? and user_id = ?',
               (id, g.user['id']))
    db.commit()
    return redirect(url_for('index'))


@bp.route('/reorder', methods=('POST',))
def reorder():
    orig = loads(request.form.get('orig'))
    dest = loads(request.form.get('dest'))
    db = get_db()
    orig_seq = db.execute(
        'SELECT seq FROM bookmark WHERE bookmark = ? AND url = ? AND user_id = ?', (orig[0], orig[1], g.user['id'])).fetchone()['seq']
    if dest != 'top':
        dest_seq = db.execute(
            'SELECT seq FROM bookmark WHERE bookmark = ? AND url = ? AND user_id = ?', (dest[0], dest[1], g.user['id'])).fetchone()['seq']
    else:
        dest_seq = 0
    if orig_seq > dest_seq:
        dest_seq += 1
        db.execute('UPDATE bookmark SET seq = seq+1 WHERE seq >= ? AND user_id = ? AND seq < ?',
                   (dest_seq, g.user['id'], orig_seq))
    else:
        db.execute('UPDATE bookmark SET seq = seq-1 WHERE seq <= ? AND user_id = ? AND seq > ?',
                   (dest_seq, g.user['id'], orig_seq))
    db.execute('UPDATE bookmark SET seq = ? WHERE bookmark = ? AND url = ? AND user_id = ?',
               (dest_seq, orig[0], orig[1], g.user['id']))
    db.commit()
    return '1'
