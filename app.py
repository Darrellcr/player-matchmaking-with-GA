from flask import Flask, render_template
from core import object
app = Flask(__name__)


@app.route('/')
def hello_world():
    posts = {
        'title': 'Hello World',
        'player_pool': object.Player.generate_player_pool(100),
    }   
    return render_template('index.html', posts=posts)


if __name__ == '__main__':
    app.run(debug=True)