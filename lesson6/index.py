from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.jinja2")

@app.route("/index")
def index2():
    return render_template("index.html")

@app.route("/classes")
def classes():
    title = "Tom"
    items = ["蘋果", "香蕉", "橘子"]
    days_of_week = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]
    return render_template("classes.html.jinja2", title=title, items=items, days=days_of_week)

@app.route("/news")
def news():
    return render_template("news.html.jinja2")

@app.route("/traffic")
def traffic():
    return render_template("traffic.html.jinja2")

@app.route("/contact")
def contact():
    return render_template("contact.html.jinja2")

@app.route("/test")
def test():
    return render_template("testindex.html.jinja2")
