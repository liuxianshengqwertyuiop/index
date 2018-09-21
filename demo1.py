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



    username = request.values.get('username')
    password = request.values.get("password")
    if username == "root" and password =="root":
        return render_template("zz.html")
    else:
        content = {
            "msg":"请登录"
        }
        return render_template("index.html",**content)

if __name__ == '__main__':
    app.run(debug=True)
    else:
    content = {
        "msg": "请登录"
    }
    return render_template("index.html", **content)

if __name__ == '__main__':
    app.run(debug=True)    else:
        content = {
            "msg":"请登录"
        }
        return render_template("index.html",**content)

if __name__ == '__main__':
    app.run(debug=True)    else:
        content = {
            "msg":"请登录"
        }
        return render_template("index.html",**content)

if __name__ == '__main__':
    app.run(debug=True)    else:
        content = {
            "msg":"请登录"
        }
        return render_template("index.html",**content)

if __name__ == '__main__':
    app.run(debug=True)    else:
        content = {
            "msg":"请登录"
        }
        return render_template("index.html",**content)

if __name__ == '__main__':
    app.run(debug=True)






