from flask import Flask, g
from paper import Paper
from flask import redirect, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    """ Display all papers. """
    papers = Paper.get_all()
    print('papers:', papers)
    return render_template('index.html', papers=papers)

@app.route('/add')
def add():
    """ Add a new paper. """
    return render_template('add.html')

@app.route('/paper/<id>')
def view_paper(id):
    """ Add a new paper. """
    paper = Paper.get_paper_by_id(id)
    return render_template('paper.html', paper=paper)

@app.route('/add_paper', methods=['POST'])
def add_paper():
    params = request.form
    paper = Paper.from_params(params)
    paper.save()
    return redirect('/') # @TODO highlight paper in list after redirect.

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
