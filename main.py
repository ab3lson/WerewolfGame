#! /usr/bin/python3
#bootstrap theme found at https://bootswatch.com/darkly/

from flask import Flask, render_template, session, request, redirect, send_from_directory
import os, string, random

app = Flask(__name__)
app.secret_key = "WEareBYUstudents!"

def roomGenerator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


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

@app.route("/guestlogin")
def guestlogin():
#TODO: insert code to create guest in database and get id to append to name
    session["username"] = "Guest#1"
    session['loggedIn'] = 1
    return redirect("/game")

@app.route("/stats")
def stats():
    try:
        if session["loggedIn"]:
            return render_template("stats.html")
    except:
        return redirect("/")

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

@app.route("/signup")
def signup():
    try:
        if session["loggedIn"]:
            return redirect("/")
    except:
        return render_template("signup.html")

@app.route("/game")
def game():
    try:
        if session["loggedIn"]:
            return render_template("game.html")
    except:
        return redirect("/")

@app.route("/createGame",methods=['POST'])
def createGame():
    try:
        if session["loggedIn"]:
            decisionSeconds = int(request.form["decisionTimer"])*60
            session["roomId"] = roomGenerator()
            print("*****************\nROOM ID GENERATED: {}".format(session["roomId"]))
            print("Variables from form:\nDecision in seconds:",decisionSeconds,"\nPlayers needed:", request.form["playersNeeded"])
            print("*****************")
            ##TODO: get values and create lobby in database
            roomId = session["roomId"]
            return redirect("lobby")
    except Exception as e:
        print("**ERROR in create game:",e)
        return redirect("/")

@app.route("/joinGame", methods=['POST'])
def joinGame():
    try:
        if session["loggedIn"]:
            #TODO: add if statement to see if roomId is in the database. if it is then join it, if not redirect and display error on play.html
            session["roomId"] = request.form["roomId"]
            print("****************")
            print("The user {} is joining the lobby: {}\n***************".format(session["username"]),session["roomId"])
            roomId = session["roomId"]
            return redirect("lobby")
    except Exception as e:
        print("**ERROR in join game:",e)
        return redirect("/")

@app.route("/lobby")
def lobby():
    try:
        if session["loggedIn"]:
            #TODO: get people needed from database based on roomId
            return render_template("lobby.html",roomId=session["roomId"],peopleNeeded=12)
    except Exception as e:
        print("**ERROR in lobby route:",e)
        return redirect("/")

@app.route("/create")
def create():
    try:
        if session["loggedIn"]:
            return render_template("create.html")
    except:
        return redirect("/login")

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3088,debug=True)