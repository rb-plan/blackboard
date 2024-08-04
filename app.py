# app.py

from flask import Flask, render_template, Response
import data_plotter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot.png')
def plot_png():
    img = data_plotter.plot_data()
    return Response(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5001)
