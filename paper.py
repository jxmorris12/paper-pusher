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
            name=params.get('name'),
            source=params.get('source'),
            datePublished=params.get('datePublished'),
            dateRead=params.get('dateRead'),
            comments=params.get('comments'),
        )
