#! /usr/bin/python3
#bootstrap theme found at https://bootswatch.com/darkly/

from flask import Flask, render_template, session, request, redirect, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "WEareBYUstudents!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/verify",methods=['POST'])
def verify():
#TODO: insert code to check database for valid login
    session["username"] = request.form['username']
    session['loggedIn'] = 1
    return redirect("/game")

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/game")
def game():
    try:
        if session["loggedIn"]:
            return render_template("game.html")
    except:
        pass
    return redirect("/login")

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3088,debug=True)