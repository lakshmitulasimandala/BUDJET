from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/add', methods = ["POST"])
def add_transaction():
    return redirect("/")

@app.route('/history')
def history():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)
