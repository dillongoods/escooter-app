from app import app, redirect, url_for,Flask,render_template

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)