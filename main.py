#!/usr/bin/env python3

import sqlite3
from datetime import datetime
from email.message import EmailMessage
from io import StringIO
from smtplib import SMTP

import click

from MyBookmarks import create_app

app = create_app()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(run)


@cli.command(short_help='Add User')
@click.argument('username')
def add(username):
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        db.executescript(
            f"INSERT INTO user(username) VALUES ('{username.lower()}');")
        click.echo('Done.')
    except sqlite3.IntegrityError:
        click.echo(f'[ERROR]Username {username.lower()} already exists.')
    except:
        click.echo('Critical Error! Please contact your system administrator.')
    db.close()


@cli.command(short_help='Delete User')
@click.argument('username')
def delete(username):
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        cursor = db.execute(
            f"DELETE FROM user WHERE username='{username.lower()}';")
        if cursor.rowcount:
            click.echo('Done.')
        else:
            click.echo(f'[ERROR]User {username.lower()} does not exist.')
    except:
        click.echo('Critical Error! Please contact your system administrator.')
    db.commit()
    db.close()


@cli.command(short_help='Backup Database')
def backup():
    try:
        msg = EmailMessage()
        msg['Subject'] = f'My Bookmarks Backup-{datetime.now():%Y%m%d}'
        msg['From'] = app.config['BACKUP_MAIL']
        msg['To'] = app.config['BACKUP_DEST']
        mem = StringIO()
        db = sqlite3.connect(app.config['DATABASE'])
        mem.write('\n'.join(db.iterdump()))
        db.close()
        msg.add_attachment(mem.getvalue(), filename='database')
        mem.close()
        with SMTP(app.config['BACKUP_SMTP'], app.config['BACKUP_SMTP_PORT']) as s:
            s.starttls()
            s.login(app.config['BACKUP_MAIL'], app.config['BACKUP_MAIL_AUTH'])
            s.send_message(msg)
    except:
        click.echo('Failed. Please check mail setting.')


@cli.command(short_help='Run Server')
@click.option('--port', '-p', default=80, help='Listening Port')
@click.option('--debug', is_flag=True, hidden=True)
def run(port, debug):
    if debug:
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    cli()
