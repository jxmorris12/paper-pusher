from flask import Flask, g
from paper import Paper
from flask import redirect, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/papers')
def papers():
    """ Display all papers. """
    papers_read = Paper.get_papers_read()
    papers_in_queue = Paper.get_papers_in_queue()
    print(
        'papers read:', len(papers_read),
        'papers_in_queue:', len(papers_in_queue)
    )
    return render_template('papers.html',
        papers_read=papers_read,
        papers_in_queue=papers_in_queue
    )

@app.route('/add')
def add():
    """ Add a new ~read~ paper. """
    return render_template('add.html')

@app.route('/add_paper', methods=['POST'])
def add_paper():
    # Stores a read paper in the database.
    params = request.form.to_dict()
    print('params:', params)
    # Deal with checkbox.
    if 'inQueue' in params:
        params['inQueue'] = 1
    else:
        params['inQueue'] = 0
    paper = Paper(**params)
    paper.save()
    return redirect('/') # @TODO highlight paper in list after redirect.

@app.route('/edit/<id>')
def edit(id):
    """ Add a new ~read~ paper. """
    paper = Paper.get_paper_by_id(id)
    print('editing paper:', paper)
    return render_template('edit.html', paper=paper)

@app.route('/edit_paper', methods=['POST'])
def edit_paper():
    # Stores a read paper in the database.
    params = request.form.to_dict()
    print('params:', params)
    # Deal with checkbox.
    if 'inQueue' in params:
        params['inQueue'] = 1
    else:
        params['inQueue'] = 0
    paper = Paper(**params)
    paper.update()
    return redirect('/') # @TODO highlight paper in list after redirect.

@app.route('/paper/<id>')
def view_paper(id):
    """ Add a new paper. """
    paper = Paper.get_paper_by_id(id)
    print('got paper:', paper)
    return render_template('paper.html', paper=paper)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
