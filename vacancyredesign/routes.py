from flask import render_template, url_for, redirect

# package related imports
from vacancyredesign import app
from vacancyredesign.modules.readability import check_readability


# Routing logic

@app.route("/")
def hello_world():
    #myInp = checkReadability()
    #name = "something extraordinary"
    
    return render_template("base.html", name="InitialConfig")
