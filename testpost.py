from flask import Flask, request, render_template


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=["GET", "POST"])
def login():
    print(request.form)
    print(request.data)
    print(request.method)
    print(request.values)
    print(request.headers)
    print(request.args)
    print(request.json)
    return render_template("login.html")


if __name__ == '__main__':
    app.run()
