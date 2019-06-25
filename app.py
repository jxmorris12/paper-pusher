from flask import Flask
from paper import Paper
from flask import redirect, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    """ Display all papers. """
    papers = Paper.get_all()
    return render_template('index.html', papers=papers)

@app.route('/add')
def add():
    """ Add a new paper. """
    return render_template('add.html')

@app.route('/add_paper', methods=['POST'])
def add_paper():
    params = request.form
    print('params:',params)
    paper = Paper.from_params(params)
    paper.save()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
