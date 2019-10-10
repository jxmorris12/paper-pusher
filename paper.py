import config
import dateutil.parser
import json
import sqlite3

from flask import g # global flask variables
from tinydb import TinyDB, where, Query

DATABASE = './database.db'

# Helper function for getting the database.
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Helper function for creating new table.
def create_paper_table():
    db = get_db()
    create_table_sql = '''CREATE TABLE IF NOT EXISTS papers (
        id integer PRIMARY KEY,
        title text NOT NULL,
        source text NOT NULL,
        datePublished text NOT NULL,
        dateRead text NOT NULL,
        summary text NOT NULL,
        futureWork text NOT NULL,
        otherThoughts text NOT NULL
    );'''
    try:
        c = db.cursor()
        c.execute(create_table_sql)
        db.commit()
    except Error as e:
        print('Error inserting new table:', e)

# The string that identifies this type within the database.
PAPER_DB_TYPE = 'papers'

class Paper:
    """ Metadata for an academic paper I've read, including my notes.

    Also interfaces directly with database. """

    columns = ['title', 'source', 'datePublished', 'dateRead', 'summary', 'futureWork', 'otherThoughts']

    def __init__(self, **kwargs):
        """ A constructor that automatically stores all keyword arguments.

        (Because I'm lazy.) """

        print('kwargs:', kwargs)
        # Validate entry.
        for param in Paper.columns:
            if param not in kwargs:
                raise ValueError('Cannot instantiate paper without {}.'.format(param))
        # Store.
        self.__dict__.update(kwargs)

    def save(self):
        """ Save an object to the database and get its ID. """
        db = get_db()
        col_sql = '({})'.format(','.join(Paper.columns)) # '(title,source,...,otherThoughts)'
        col_sql_vals = tuple(self.__dict__[x] for x in Paper.columns)
        col_sql_q = '({})'.format(','.join(['?' for _ in Paper.columns]))
        sql = ''' INSERT INTO {}{} VALUES{} '''.format(PAPER_DB_TYPE, col_sql, col_sql_q)
        print('sql:', sql)
        print('col_sql_vals:', col_sql_vals)
        cur = db.cursor()
        cur.execute(sql, col_sql_vals)
        db.commit()
        self.id = cur.lastrowid
        print('set id:', self.id)

    def to_json(self):
        self_as_dict = vars(self)
        self_as_dict['type'] = PAPER_DB_TYPE
        return self_as_dict

    @staticmethod
    def from_sql_row(row):
        obj_dict = dict(zip(['id'] + Paper.columns, row))
        return Paper(**obj_dict)

    @staticmethod
    def get_paper_by_id(paper_id):
        # Get papers from database 'papers' table by ID.
        db = get_db()
        db.row_factory = sqlite3.Row # This enables column access by name: row['column_name']
        conn = db.cursor()
        rows = conn.execute('SELECT * from {} WHERE id={}'.format(
            PAPER_DB_TYPE, paper_id)
        ).fetchall()
        conn.close()
        #@TODO: Throw error for multiple rows, and for 0 rows?
        return Paper.from_sql_row(rows[0])

    @staticmethod
    def get_all(retry=False):
        try:
            # Get papers from database 'papers' table.
            db = get_db()
            db.row_factory = sqlite3.Row # This enables column access by name: row['column_name']

            conn = db.cursor()
            rows = conn.execute('SELECT * from {}'.format(PAPER_DB_TYPE)).fetchall()
            conn.close()
            # If no papers, return None instead of '[]'. :)
            if rows == '[]':
                return None
            else:
                return [Paper.from_sql_row(row) for row in rows]
        except sqlite3.OperationalError as e:
            if not retry:
                # First error-- try inserting table.
                create_paper_table()
                return Paper.get_all(retry=True)
            else:
                raise e

    @classmethod
    def from_params(_class, params):
        """ Creates a Paper from POST request params.

        For now, do not convert times to datetime objects; keep them as ISO
            strings. """
        print('params:', params)
        return _class(
            title=params.get('title'),
            source=params.get('source'),
            datePublished=params.get('datePublished'),
            dateRead=params.get('dateRead'),
            summary=params.get('summary'),
            futureWork=params.get('futureWork'),
            otherThoughts=params.get('otherThoughts'),
        )

    @classmethod
    def from_arxiv(_class, object):
        """ Creates a Paper from an arxiv search result. """
        title = object.title
        source = None
        datePublished = date_to_iso(object.published)
        dateRead = None
        comments = None
        return _class(
            title=title,
            source=source,
            datePublished=datePublished,
            dateRead=dateRead,
            comments=comments
        )


def date_to_iso(date_text):
    """ Parses pretty much any date format and returns an ISO string. """
    date_time = dateutil.parser.parse(date_text)
    return date_time.isoformat()
