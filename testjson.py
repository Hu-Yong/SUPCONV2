from flask import Flask
app = Flask(__name__)


@app.route("/")
def getdata():

    return "hello world"


@app.route("/me")
def me_api():
    datas = getdata()
    return str(datas)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
