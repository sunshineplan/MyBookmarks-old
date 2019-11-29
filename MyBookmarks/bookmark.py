from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, url_for)

from MyBookmarks.auth import login_required
from MyBookmarks.db import get_db

bp = Blueprint('bookmark', __name__)


@bp.route('/')
@login_required
def index():
    '''Show the bookmarks belong the current user.'''
    category_id = request.args.get('category')
    db = get_db()
    if category_id is None:
        category = {'id': -1, 'name': 'All Bookmarks'}
        bookmarks = db.execute('SELECT bookmark.id, bookmark, url, category FROM bookmark'
                               ' LEFT JOIN category ON category_id = category.id'
                               ' WHERE bookmark.user_id = ? ORDER BY seq',
                               (g.user['id'],)).fetchall()
        for i in bookmarks:
            if not i['category']:
                i['category'] = ''
    elif category_id == '0':
        category = {'id': 0, 'name': 'Uncategorized'}
        bookmarks = db.execute('SELECT id, bookmark, url FROM bookmark'
                               ' WHERE category_id = 0 AND user_id = ?'
                               ' ORDER BY seq', (g.user['id'],)).fetchall()
    else:
        category = {'id': int(category_id)}
        category['name'] = db.execute('SELECT category FROM category WHERE id = ? AND user_id = ?',
                                      (category_id, g.user['id'])).fetchone()['category']
        bookmarks = db.execute('SELECT id, bookmark, url FROM bookmark'
                               ' WHERE category_id = ? AND user_id = ?'
                               ' ORDER BY seq', (category_id, g.user['id'])).fetchall()
        for i in bookmarks:
            i['category'] = category['name']
    return render_template('bookmark/index.html', category=category, bookmarks=bookmarks)


@bp.route('/category/get', methods=('GET',))
@login_required
def get_category():
    '''Get current user's categories.'''
    db = get_db()
    total = db.execute('SELECT count(bookmark) num FROM bookmark WHERE user_id = ?',
                       (g.user['id'],)).fetchone()['num']
    uncategorized = db.execute('SELECT count(bookmark) num FROM bookmark WHERE category_id = 0 AND user_id = ?',
                               (g.user['id'],)).fetchone()['num']
    categories = db.execute('SELECT category.id, category, count(bookmark) num'
                            ' FROM category LEFT JOIN bookmark ON category.id = category_id'
                            ' WHERE category.user_id = ? GROUP BY category_id ORDER BY category', (g.user['id'],)).fetchall()
    return jsonify({'total': total, 'uncategorized': uncategorized, 'categories': categories})


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
    last_visit = request.cookies.get('LastVisit')
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
            if last_visit:
                return redirect(last_visit)
            else:
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


@bp.route('/bookmark/add', methods=('GET', 'POST'))
@login_required
def add_bookmark():
    '''Create a new bookmark for the current user.'''
    category_id = request.args.get('category_id')
    last_visit = request.cookies.get('LastVisit')
    db = get_db()
    if category_id:
        category = db.execute('SELECT category FROM category WHERE id = ? AND user_id = ?',
                              (category_id, g.user['id'])).fetchone()['category']
    else:
        category = ''
    if request.method == 'POST':
        category = request.form.get('category')
        bookmark = request.form.get('bookmark')
        url = request.form.get('url')
        if db.execute('SELECT id FROM bookmark WHERE url = ? AND user_id = ?', (url, g.user['id'])).fetchone() is not None:
            flash(f'Bookmark url {url} is already existed.')
        elif db.execute('SELECT id FROM bookmark WHERE bookmark = ? AND user_id = ?', (bookmark, g.user['id'])).fetchone() is not None:
            flash(f'Bookmark name {bookmark} is already existed.')
        else:
            if category:
                if category_id := db.execute('SELECT id FROM category WHERE category = ? AND user_id = ?', (category, g.user['id'])).fetchone():
                    category_id = category_id['id']
                else:
                    db.execute(
                        'INSERT INTO category (category, user_id) VALUES (?, ?)', (category, g.user['id']))
                    category_id = db.execute(
                        'SELECT last_insert_rowid() id').fetchone()['id']
            else:
                category_id = 0
            db.execute('INSERT INTO bookmark (bookmark, url, user_id, category_id)'
                       ' VALUES (?, ?, ?, ?)', (bookmark, url, g.user['id'], category_id))
            db.commit()
            if last_visit:
                return redirect(last_visit)
            else:
                return redirect(url_for('index'))
    return render_template('bookmark/bookmark.html', id=0, bookmark={}, category=category)


@bp.route('/bookmark/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_bookmark(id):
    '''Edit a bookmark for the current user.'''
    db = get_db()
    last_visit = request.cookies.get('LastVisit')
    bookmark = db.execute('SELECT bookmark, url, category FROM bookmark'
                          ' LEFT JOIN category ON category_id = category.id'
                          ' WHERE bookmark.id = ? AND bookmark.user_id = ?',
                          (id, g.user['id'])).fetchone()
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
            if category:
                if category_id := db.execute('SELECT id FROM category WHERE category = ? AND user_id = ?', (category, g.user['id'])).fetchone():
                    category_id = category_id['id']
                else:
                    db.execute(
                        'INSERT INTO category (category, user_id) VALUES (?, ?)', (category, g.user['id']))
                    category_id = db.execute(
                        'SELECT last_insert_rowid() id').fetchone()['id']
            else:
                category_id = 0
            db.execute('UPDATE bookmark SET bookmark = ?, url = ?, category_id = ?'
                       ' WHERE id = ? AND user_id = ?', (bookmark, url, category_id, id, g.user['id']))
            db.commit()
            if last_visit:
                return redirect(last_visit)
            else:
                return redirect(url_for('index'))
    return render_template('bookmark/bookmark.html', id=id, bookmark=bookmark)


@bp.route('/bookmark/delete/<int:id>', methods=('POST',))
@login_required
def delete_bookmark(id):
    '''Edit a bookmark for the current user.'''
    db = get_db()
    last_visit = request.cookies.get('LastVisit')
    db.execute('DELETE FROM bookmark WHERE id = ? and user_id = ?',
               (id, g.user['id']))
    db.commit()
    if last_visit:
        return redirect(last_visit)
    else:
        return redirect(url_for('index'))


@bp.route('/reorder', methods=('POST',))
def reorder():
    orig = request.form.get('orig')
    dest = request.form.get('dest')
    db = get_db()
    orig_seq = db.execute(
        'SELECT seq FROM bookmark WHERE bookmark = ? AND user_id = ?', (orig, g.user['id'])).fetchone()['seq']
    if dest != '#TOP_POSITION#':
        dest_seq = db.execute(
            'SELECT seq FROM bookmark WHERE bookmark = ? AND user_id = ?', (dest, g.user['id'])).fetchone()['seq']
    else:
        dest_seq = 0
    if orig_seq > dest_seq:
        dest_seq += 1
        db.execute('UPDATE bookmark SET seq = seq+1 WHERE seq >= ? AND user_id = ? AND seq < ?',
                   (dest_seq, g.user['id'], orig_seq))
    else:
        db.execute('UPDATE bookmark SET seq = seq-1 WHERE seq <= ? AND user_id = ? AND seq > ?',
                   (dest_seq, g.user['id'], orig_seq))
    db.execute('UPDATE bookmark SET seq = ? WHERE bookmark = ? AND user_id = ?',
               (dest_seq, orig, g.user['id']))
    db.commit()
    return '1'
