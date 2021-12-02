from flask import render_template, request

from vacancyredesign import app


@app.route("/", methods=["POST", "GET"])
def hello_world():

    #formstring = request.args['job_text']
    name = "Ninja"
    return render_template("base.html", name=name)
