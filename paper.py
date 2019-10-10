import config
import dateutil.parser

from tinydb import TinyDB, where

db = TinyDB(config.db_path)

# The string that identifies this type within the database.
PAPER_DB_TYPE = 'paper'

class Paper:
    """ Metadata for an academic paper I've read, including my notes.

    Also interfaces directly with database. """
    def __init__(self, **kwargs):
        """ A constructor that automatically stores all keyword arguments.

        (Because I'm lazy.) """
        self.__dict__.update(kwargs)

        for param in ['title', 'source', 'datePublished', 'dateRead', 'comments']:
            if param not in kwargs:
                raise ValueError('Cannot instantiate paper without {}.'.format(param))

    def save(self):
        """ Saves an object to the database. """
        db.insert(self.to_json())

    def to_json(self):
        self_as_dict = vars(self)
        self_as_dict['type'] = PAPER_DB_TYPE
        return self_as_dict

    @staticmethod
    def get_all():
        return db.search(where('type') == PAPER_DB_TYPE)

    @classmethod
    def from_params(_class, params):
        """ Creates a Paper from POST request params.

        For now, do not convert times to datetime objects; keep them as ISO
            strings. """
        return _class(
            title=params.get('title'),
            source=params.get('source'),
            datePublished=params.get('datePublished'),
            dateRead=params.get('dateRead'),
            comments=params.get('comments'),
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
