from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def index():
    content = {
        'username':'zhangsan',
        'password':'password',
        'age':12
    }
    return render_template("index.html",**content)

@app.route("/sub/")
def sub():
    return render_template("sub.html")

if __name__ == '__main__':
    app.run()






