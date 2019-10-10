import arxiv

""" Functions that make it easy to search Arxiv for papers. """

def query(query_text, max_results=20):
    """ Searches arxiv for a given query. """
    results = arxiv.query(query=query_text)
    del results[max_results:] # Remove extra results.
    return [Paper.from_arxiv(result) for result in results]
