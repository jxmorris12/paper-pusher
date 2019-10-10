import config
import dateutil.parser
import json
import sqlite3

from flask import g # global flask variables

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
        inQueue integer,
        title text NOT NULL,
        author text NOT NULL,
        source text,
        datePublished text NOT NULL,
        dateRead text,
        summary text,
        futureWork text,
        otherThoughts text
    );'''
    try:
        c = db.cursor()
        c.execute(create_table_sql)
        db.commit()
    except Error as e:
        print('Error inserting new table:', e)

def query_db_papers(query_where='', retry=False):
    try:
        # Get papers from database 'papers' table.
        db = get_db()
        db.row_factory = sqlite3.Row # This enables column access by name: row['column_name']
        query = 'SELECT * from {} {}'.format(PAPER_DB_TYPE, query_where)
        conn = db.cursor()
        rows = conn.execute(query).fetchall()
        conn.close()
        print('executed query:', query)
        print('\t got rows:', rows)
        # If no papers, return [] instead of '[]'. :)
        if rows == '[]':
            return []
        else:
            return [Paper.from_sql_row(row) for row in rows]
    except sqlite3.OperationalError as e:
        if not retry:
            # First error-- try inserting table.
            create_paper_table()
            return Paper.get_all(query_where=query_where, retry=True)
        else:
            raise e

# The string that identifies this type within the database.
PAPER_DB_TYPE = 'papers'

class Paper:
    """ Metadata for an academic paper I've read, including my notes.

    Also interfaces directly with database. """

    # The order of these column names MUST match the order in SQL.
    columns = ['inQueue', 'title', 'author', 'source', 'datePublished',
                'dateRead', 'summary', 'futureWork', 'otherThoughts']

    optional_columns = ['source', 'dateRead', 'summary', 'futureWork',
        'otherThoughts']

    def __init__(self, **kwargs):
        """ A constructor that automatically stores all keyword arguments.

        (Because I'm lazy.) """

        # Validate entry.
        for param in Paper.columns:
            if param not in kwargs and param not in Paper.optional_columns:
                raise ValueError('Cannot instantiate paper without {}.'.format(param))
        # Store.
        self.__dict__.update(kwargs)

    def update(self):
        """ Update an object by its ID. """

        if not self.id:
            raise Exception('Cannot update an object without an ID.')

        db = get_db()

        sql_cmd = 'UPDATE {} SET'.format(PAPER_DB_TYPE)
        sql_vars = []
        set_vars = []
        for col in Paper.columns:
            if col in self.__dict__:
                set_vars.append(' {} = ?'.format(col))
                sql_vars.append(self.__dict__[col])
        sql_cmd += ', '.join(set_vars)
        sql_cmd += ' WHERE id = {}'.format(self.id)
        print('sql:', sql_cmd)
        print('\tsql_vars:',sql_vars)
        cur = db.cursor()
        cur.execute(sql_cmd, sql_vars)
        db.commit()
        print('updated obj with id:', self.id)

    def save(self):
        """ Save an object to the database and get its ID. """
        db = get_db()
        columns = Paper.columns
        col_sql = '({})'.format(','.join(columns)) # '(title,source,...,otherThoughts)'
        col_sql_vals = []
        for col in columns:
            if col in self.__dict__:
                val = self.__dict__[col]
                if isinstance(val, str):
                    val = val.strip() # Trim whitespace
                col_sql_vals.append(val)
            else:
                col_sql_vals.append(None)
        col_sql_q = '({})'.format(','.join(['?' for _ in columns]))
        sql = ''' INSERT INTO {}{} VALUES{} '''.format(PAPER_DB_TYPE, col_sql, col_sql_q)
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
        row = list(row)
        for i in range(len(row)):
            if isinstance(row[i], str):
                row[i] = row[i].strip()
        obj_dict = dict(zip(['id'] + Paper.columns, row))
        return Paper(**obj_dict)

    @staticmethod
    def get_paper_by_id(paper_id):
        papers = query_db_papers('WHERE id={}'.format(paper_id))
        #@TODO: Throw error for multiple rows, and for 0 rows?
        return papers[0]

    @staticmethod
    def get_papers_read(retry=False):
        return query_db_papers('WHERE inQueue = 0')

    @staticmethod
    def get_papers_in_queue(retry=False):
        return query_db_papers('WHERE inQueue = 1')

    @staticmethod
    def get_all(retry=False):
        return query_db_papers()

    @classmethod
    def from_arxiv(_class, object):
        """ Creates a Paper from an arxiv search result.

            @TODO update this function for Sqlite3.
         """
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
