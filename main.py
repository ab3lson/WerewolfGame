#! /usr/bin/python3
#bootstrap theme found at https://bootswatch.com/darkly/

from flask import Flask, render_template, session, request, redirect, send_from_directory
from flask_socketio import SocketIO
from flask_socketio import send, emit, join_room, leave_room
import pymysql
import os, string, random, hashlib
import creds

app = Flask(__name__)
app.secret_key = creds.secretKey
socketio = SocketIO(app)
SALT = creds.salt

#Establishes DB connection
con = pymysql.connect(creds.DBHost, creds.DBUser, creds.DBPass, creds.DBName,cursorclass=pymysql.cursors.DictCursor,autocommit=True)

GAMES = [] #holds all active games with "roomId" and "players" - list of players

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
    hashedPass = hashlib.md5((request.form["password"] + SALT).encode())
    print("HASHED PASS:",hashedPass.hexdigest())
    cur = con.cursor()
    cur.execute("SELECT Password FROM User WHERE Username = %s",(request.form['username']))
    result = cur.fetchall()
    cur.close()
    if len(result) == 0:
        return render_template("login.html",error="badUsername")
    elif hashedPass.hexdigest() != result[0]["Password"]:
        return render_template("login.html",error="badPassword")
    else:
        cur = con.cursor()
        cur.execute("UPDATE User SET LoggedIn = 1 WHERE Username = %s",(request.form['username']))
        cur.execute("SELECT UserId FROM User WHERE Username = %s",(request.form['username']))
        result = cur.fetchone()
        cur.close()
        session["userId"] = result["UserId"]
        session["username"] = request.form['username']
        session['loggedIn'] = 1
        return redirect("/game")

@app.route("/guestlogin")
def guestlogin():
    cur = con.cursor()
    cur.execute("SELECT MAX(UserId) AS HighestID FROM User")
    highestId = cur.fetchone()
    guestId = int(highestId["HighestID"]) + 1
    cur.execute("INSERT INTO User (Username, Password, IsGuest, LoggedIn) VALUES (%s, %s, '0', '1')",('Guest#{}'.format(guestId),random.getrandbits(128)))
    cur.execute("SELECT UserId FROM User WHERE Username =%s",('Guest#{}'.format(guestId)))
    UserId = cur.fetchone()
    cur.close()
    session["userId"] = UserId["UserId"]
    session["username"] = 'Guest#{}'.format(guestId)
    session['loggedIn'] = 1
    # print("SESSION VARS:",session)
    return redirect("game")

@app.route("/stats")
def stats():
    try:
        if session["loggedIn"]:
            cur = con.cursor()
            cur.execute("SELECT * FROM Stats WHERE UserId = %s",(session['userId']))
            result = cur.fetchall()
            cur.close()
            error = None
            stats = None
            if len(result) == 0:
                error = "isGuest"
            else:
                stats = result[0]
            if error == "isGuest":
                return render_template("game.html",error=error)
            # return render_template("stats.html",gamesPlayed=stats["GamesPlayed"],gamesWon=stats["gamesWon"],peopleEaten=stats["peopleEaten"])
            return render_template("stats.html",stats=stats)
    except:
        return redirect("/")

@app.route("/signout")
def signout():
    cur = con.cursor()
    if "Guest#" in session["username"]:
        print(f"{session['username']} signed out. Deleting from DB.")
        cur.execute("DELETE FROM User WHERE UserId = %s",(session['userId']))
    cur.execute("UPDATE User SET LoggedIn = 0 WHERE Username = %s",(session['username']))
    cur.close()
    session.clear()
    return redirect("/")

@app.route("/signup")
def signup():
    try:
        if session["loggedIn"]:
            return redirect("/")
    except:
        return render_template("signup.html")

@app.route("/createAccount",methods=['POST'])
def createAccount():
    try:
        if session["loggedIn"]:
            return redirect("/")
    except:
        # print(request.form)
        if request.form["password"] != request.form["confirmPassword"]:
            return render_template("signup.html",error="badPassword")
        cur = con.cursor()
        cur.execute("SELECT * FROM User WHERE Username = %s",(request.form['username']))
        result = cur.fetchall()
        cur.close()
        if len(result) != 0: #the username already exists in the db
            return render_template("signup.html",error="badUsername")
        else:
            hashedPass = hashlib.md5((request.form["password"] + SALT).encode()).hexdigest()
            cur = con.cursor()
            try: #with email
                cur.execute("INSERT INTO User (Username, Password, Email, IsGuest, LoggedIn) VALUES (%s, %s, %s, '0', '1')",(request.form['username'],hashedPass,request.form['email']))
            except: #without email
                cur.execute("INSERT INTO User (Username, Password, IsGuest, LoggedIn) VALUES (%s, %s, '0', '1')",(request.form['username'],hashedPass))
            cur.execute("SELECT UserId FROM User WHERE Username = %s",(request.form['username']))
            result = cur.fetchall()
            cur.execute("INSERT INTO Stats (UserId) VALUES (%s)",(result[0]["UserId"]))
            session["userId"] = result[0]["UserId"]
            session["username"] = request.form["username"]
            session['loggedIn'] = 1
            cur.close()
            return redirect("game")

@app.route("/game")
def game():
    try:
        if session["loggedIn"]:
            return render_template("game.html")
    except:
        return redirect("/")

@app.route("/create")
def create():
    try:
        if session["loggedIn"]:
            return render_template("create.html")
    except:
        return redirect("/login")

@app.route("/createGame",methods=['POST'])
def createGame():
    try:
        if session["loggedIn"]:
            try:
                if session["roomId"]:
                    print("The user {} tried to make a new room, but they are already in room {}!".format(session["username"],session["roomId"]))
                    print("Removing old roomId to create a new room.")
                    session.pop('roomId', None)
            except:
                pass #the user is not already in a room
            decisionSeconds = int(request.form["decisionTimer"])*60
            newRoomId = roomGenerator()
            session["roomId"] = newRoomId
            # print("*****************\nROOM ID GENERATED: {}".format(session["roomId"]))
            # print("Variables from form:\nDecision in seconds:",decisionSeconds,"\nPlayers needed:", request.form["playersNeeded"])
            # print("*****************")
            playersInt = int(request.form["playersNeeded"])
            cur = con.cursor()
            cur.execute("INSERT INTO Lobby (RoomId, PlayersNeeded, DecisionTimer) VALUES (%s, %s, %s)",(newRoomId,int(request.form["playersNeeded"]),int(decisionSeconds)))
            cur.close()
            newGame = {"roomId":session["roomId"],"players":[session["username"]],"playersNeeded":request.form["playersNeeded"],"decisionTimer":decisionSeconds}
            GAMES.append(newGame)
            print("Making new game:",newGame)
            print("All active games:",GAMES)
            return redirect("lobby")
    except Exception as e:
        print("**ERROR in create game:",e)
        return redirect("/")

@app.route("/joinGame", methods=['POST'])
def joinGame():
    try:
        try:
            if session["roomId"]:
                print("The user {} tried to join room {}, but they are already in room {}!".format(session["username"],request.form["roomId"],session["roomId"]))
                print("Removing old roomId to join a new room.")
                session.pop('roomId', None)
        except:
            pass #the user is not already in a room
        if session["loggedIn"]:
            for game in GAMES:
                if request.form["roomId"] == game["roomId"]:
                    session["roomId"] = request.form["roomId"]
                    game["players"].append(session["username"])
                    cur = con.cursor()
                    cur.execute("UPDATE Lobby SET CurrentPlayers = CurrentPlayers + 1 WHERE RoomId = %s",(session["roomId"]))
                    cur.close()
                    print("The user {} is joining the lobby: {}".format(session["username"],session["roomId"]))
                    roomId = session["roomId"]
                    return redirect("lobby")
            print("The user {} is entered invalid roomId: {}".format(session["username"],request.form["roomId"]))
            return redirect("/game")          
    except Exception as e:
        print("**ERROR in join game:",e)
        return redirect("/")

@app.route("/lobby")
def lobby():
    try:
        if session["loggedIn"] and session["roomId"]:
            playersNeeded = 0
            currentPlayers = 0
            gameDict = None
            for game in GAMES:
                if game["roomId"] == session["roomId"]:
                    currentPlayers=len(game["players"])
                    playersNeeded=game["playersNeeded"]
                    gameDict = game
            if int(currentPlayers) == int(playersNeeded):#TODO: add all players from players list in GAMES to ActiveGames in the DB
                print(f"Player count reached for {session['roomId']}!\nREDIRECTING and starting game!")
                socketio.emit('start game', room=session["roomId"])
                return redirect("pregame")
            else:
                return render_template("lobby.html",roomId=session["roomId"],currentPlayers=currentPlayers,playersNeeded=playersNeeded,playerNames=gameDict["players"])
    except Exception as e:
        print("**ERROR in lobby route:",e)
        return redirect("/")

@app.route("/leaveLobby")
def leaveLobby():
    try:
        if session["loggedIn"] and session["roomId"]:
            for game in GAMES:
                if game["roomId"] == session["roomId"]:
                    userList =  game["players"]
                    for user in game["players"]:
                        if user == session["username"]:
                            game["players"].remove(user)
                            print("The user {} left the lobby: {}".format(session["username"],session["roomId"]))
                            cur = con.cursor()
                            cur.execute("UPDATE Lobby SET CurrentPlayers = CurrentPlayers - 1 WHERE RoomId = %s",(session["roomId"]))
                            cur.close()
                            socketio.emit('reload users', userList,room=session["roomId"]) #tells view for all players in the lobby to refresh
                    # print("Players left in the lobby:",len(game["players"]))
                    if len(game["players"]) == 0:
                        print("Nobody is in the lobby: {}. Deleting the lobby.".format(session["roomId"]))
                        cur = con.cursor()
                        cur.execute("DELETE FROM Lobby WHERE RoomId = %s",(session["roomId"]))
                        cur.close()
                        GAMES.remove(game)
                        print("Remaining lobbies:",GAMES)
            session.pop('roomId', None)
            return redirect("/game")
    except Exception as e:
        print("**ERROR in leaveLobby route:",e)
        return redirect("/")

@app.route("/pregame")
def pregame():
    # try:
    #     if session["loggedIn"]:
    #         return render_template("create.html")
    # except:
    #     return redirect("/login")
    return render_template("gameViews/pregame.html")

@app.route("/intro")
def intro():
    # try:
    #     if session["loggedIn"]:
    #         return render_template("create.html")
    # except:
    #     return redirect("/login")
    return render_template("gameViews/intro.html")

@app.route("/daytime")
def daytime():
    # try:
    #     if session["loggedIn"]:
    #         return render_template("create.html")
    # except:
    #     return redirect("/login")
    return render_template("gameViews/daytime.html")

@app.route("/nighttime")
def nighttime():
    # try:
    #     if session["loggedIn"]:
    #         return render_template("create.html")
    # except:
    #     return redirect("/login")
    return render_template("gameViews/nighttime.html")

@app.route("/vote")
def vote():
    # try:
    #     if session["loggedIn"]:
    #         return render_template("create.html")
    # except:
    #     return redirect("/login")
    return render_template("gameViews/vote.html")

@app.route("/sessionDestroy")
def sessionDestroy():
	session.clear()
	return redirect("/")

@app.route("/sessionView")
def sessionView():
    print("*************")
    print(session)
    print("*************")
    return redirect("/")

""" SOCKET ROUTES BELOW """

@socketio.on('lobby entered')
def lobbyNotify(roomId):
    print(f"\nA player joined the room {roomId}\n")
    join_room(roomId)
    userList = None
    for game in GAMES:
        if roomId == game["roomId"]:
            userList=game["players"]
    # print(f"Sending: reload users in lobby to the lobby...\n This is the user list:{userList}")
    emit('reload users', userList, room=roomId)

# @socketio.on('refresh lobby list')
# def refreshLobby(roomId):
#     print("The room is be refreshed is:",roomId)
#     userList = None
#     for game in GAMES:
#         if roomId == game["roomId"]:
#             userList=game["players"]
#     print(f"A user left the lobby {roomId}.\n This is the new user list:{userList}")
#     emit('reload users', userList, room=roomId)




@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html'), 404

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0',port=3088,debug=True)
