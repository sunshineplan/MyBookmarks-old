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
        db.executescript(f"INSERT INTO user(username) VALUES ('{username}');")
        click.echo('Done.')
    except sqlite3.IntegrityError:
        click.echo(f'[ERROR]Username {username} already exists.')
    except sqlite3.OperationalError:
        click.echo('Critical Error! Please contact your system administrator.')
    db.close()


@cli.command(short_help='Backup Database')
def backup():
    mem = StringIO()
    db = sqlite3.connect(app.config['DATABASE'])
    mem.write('\n'.join(db.iterdump()))
    db.close()
    try:
        msg = EmailMessage()
        msg['Subject'] = f'My Bookmarks Backup-{datetime.now():%Y%m%d}'
        msg['From'] = app.config['BACKUP_MAIL']
        msg['To'] = app.config['BACKUP_MAIL']
        msg.add_attachment(mem.getvalue(), filename='database')
        with SMTP(app.config['BACKUP_SMTP']) as s:
            s.send_message(msg)
    except:
        click.echo('Failed. Please check mail setting.')


@cli.command(short_help='Run Server')
@click.option('--port', '-p', default=80, help='Listening Port')
@click.option('--debug', is_flag=False, hidden=True)
def run(port, debug):
    if debug:
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    cli()
