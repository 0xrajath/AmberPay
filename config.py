import os

WTF_CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tod.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
