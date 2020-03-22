#! /usr/bin/python3
#bootstrap theme found at https://bootswatch.com/darkly/

from flask import Flask, render_template, session, request, redirect, send_from_directory
from flask_socketio import SocketIO
from flask_socketio import send, emit, join_room, leave_room
import pymysql
import os, string, random, hashlib
import creds
import logging
from time import strftime
from logging.handlers import RotatingFileHandler
from DBUtils.PersistentDB import PersistentDB

app = Flask(__name__)
app.secret_key = creds.secretKey
socketio = SocketIO(app)
SALT = creds.salt


#con = pymysql.connect(creds.DBHost, creds.DBUser, creds.DBPass, creds.DBName,cursorclass=pymysql.cursors.DictCursor,autocommit=True)

def connect_db():
    '''Establishes DB connection'''
    return PersistentDB(
        creator = pymysql, # the rest keyword arguments belong to pymysql
        user = creds.DBUser, password = creds.DBPass, database = creds.DBName, 
        autocommit = True, charset = 'utf8mb4', 
        cursorclass = pymysql.cursors.DictCursor)

def get_db():
    '''Opens a new database connection per app.'''
    if not hasattr(app, 'db'):
        app.db = connect_db()
    return app.db.connection() 

def apply_role(role,playerList):
    while True: #will loop until a role is assigned
        randomPlayer = random.randrange(0,len(playerList)) #real code
        # randomPlayer = random.randrange(0,3) #assigns first three players the roles
        if playerList[randomPlayer]["role"] == "villager":
            playerList[randomPlayer]["role"] = role
            print("ASSIGNMENT: {} will be a: {}".format(playerList[randomPlayer]["username"],playerList[randomPlayer]["role"]))
            cur = get_db().cursor()
            if role == "seer":
                cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET TimesSeer=TimesSeer+1 WHERE Username = %s",(playerList[randomPlayer]["username"]))
            elif role == "headWerewolf" or role == "werewolf":
                cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET TimesWerewolf=TimesWerewolf+1 WHERE Username = %s",(playerList[randomPlayer]["username"]))
            elif role == "healer":
                cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET TimesDoctor=TimesDoctor+1 WHERE Username = %s",(playerList[randomPlayer]["username"]))
            cur.close()
            break

def assign_roles(game):
    #logic to assign roles based on rules
    # print("Players and roles before assignments:",game["gameLogic"])
    # print("PLAYERS NEEDED:",int(game["playersNeeded"]))
    if 6<= int(game["playersNeeded"]) <=7: ##change back to 6-9
        apply_role("headWerewolf",game["gameLogic"])
        apply_role("seer",game["gameLogic"])
        apply_role("healer",game["gameLogic"])
    if 8<= int(game["playersNeeded"]) <=13: ##change back to 10-13
        apply_role("headWerewolf",game["gameLogic"])
        apply_role("werewolf",game["gameLogic"])
        apply_role("seer",game["gameLogic"])
        apply_role("healer",game["gameLogic"])
    if 14<= int(game["playersNeeded"]) <=16:
        apply_role("headWerewolf",game["gameLogic"])
        apply_role("werewolf",game["gameLogic"])
        apply_role("werewolf",game["gameLogic"])
        apply_role("seer",game["gameLogic"])
        apply_role("healer",game["gameLogic"])
    #print("Players and roles AFTER assignments:",game["gameLogic"])
    return

def create_active_game(game):
    cur = get_db().cursor()
    roomId = game["roomId"]
    decisionTimer = game["decisionTimer"]
    print("ADDING TO ActiveGames in DB!")
    for player in game["gameLogic"]:
        print("Creating entry for: {}".format(player["username"]))
        cur.execute("INSERT INTO ActiveGames (Username, RoomId, Role, DecisionTimer) VALUES (%s, %s, %s, %s)",(player["username"], roomId, player["role"], decisionTimer))
    cur.close()
    return

def checkWinConditions(game):
    villagerCount = 0
    werewolfCount = 0
    winCond = False
    for player in game:
        if player["role"] != "werewolf" and player["role"] != "headWerewolf" and player["isAlive"] == "1":
            villagerCount += 1
        elif player["role"] == "werewolf" or player["role"] == "headWerewolf":
            if player["isAlive"] == "1":
                werewolfCount += 1
    if werewolfCount < 1:
        winCond = "Villagers"
        # print("Victory! Villagers win!")
    if villagerCount < 2:
        winCond = "Werewolves"
        # print("Victory! Werewolves win!")
    return winCond

GAMES = [] #holds all active games with "roomId" and "players" - list of players

def roomGenerator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

"""Handles the connection log after each request comes in (see last section of code)"""
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

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
    cur = get_db().cursor()
    cur.execute("SELECT Password FROM User WHERE Username = %s",(request.form['username']))
    result = cur.fetchall()
    cur.close()
    if len(result) == 0:
        return render_template("login.html",error="badUsername")
    elif hashedPass.hexdigest() != result[0]["Password"]:
        return render_template("login.html",error="badPassword")
    else:
        
        cur = get_db().cursor()
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
    cur = get_db().cursor()
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
            cur = get_db().cursor()
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

@app.route("/search", methods=["POST"])
def search():
    try:
        if session["loggedIn"]:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM `User` RIGHT JOIN `Stats` ON User.UserId=Stats.UserId where SOUNDEX(`username`) = SOUNDEX(%s)",(request.form['search_results']))
            result = cur.fetchall()
            cur.close()
            search = None
            search = result[0]
            # return render_template("stats.html",gamesPlayed=stats["GamesPlayed"],gamesWon=stats["gamesWon"],peopleEaten=stats["peopleEaten"])
            return render_template("search.html",search=search)
    except:
        return redirect("/")

@app.route("/signout")
def signout():
    cur = get_db().cursor()
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
        cur = get_db().cursor()
        cur.execute("SELECT * FROM User WHERE Username = %s",(request.form['username']))
        result = cur.fetchall()
        cur.close()
        if len(result) != 0: #the username already exists in the db
            return render_template("signup.html",error="badUsername")
        else:
            hashedPass = hashlib.md5((request.form["password"] + SALT).encode()).hexdigest()
            cur = get_db().cursor()
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
            cur = get_db().cursor()
            cur.execute("INSERT INTO Lobby (RoomId, PlayersNeeded, DecisionTimer) VALUES (%s, %s, %s)",(newRoomId,int(request.form["playersNeeded"]),int(decisionSeconds)))
            cur.close()
            newGame = {"roomId":session["roomId"],"players":[session["username"]],"playersNeeded":request.form["playersNeeded"],"decisionTimer":decisionSeconds}
            GAMES.append(newGame)
            print("Making new game: {}".format(newRoomId))
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
                    cur = get_db().cursor()
                    cur.execute("UPDATE Lobby SET CurrentPlayers = CurrentPlayers + 1 WHERE RoomId = %s",(session["roomId"]))
                    cur.close()
                    print("The user {} is joining the lobby: {}".format(session["username"],session["roomId"]))
                    roomId = session["roomId"]
                    return redirect("lobby")
            print("The user {} entered invalid roomId: {}".format(session["username"],request.form["roomId"]))
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
            if int(currentPlayers) == int(playersNeeded):
                for game in GAMES:
                    if game["roomId"] == session["roomId"]:
                        game["gameLogic"] = []
                        for player in game["players"]:
                            game["gameLogic"].append({"username":player, "role":"villager", "isAlive":"1", "isReady":"0", "chosenByHealer":"0", "specialUsed": "0", "killVotes":0})
                        assign_roles(game) #assigns roles to players
                        create_active_game(game) #adds players to ActiveGames table in DB
                print(f"Player count reached for {session['roomId']}... REDIRECTING!")
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
                            cur = get_db().cursor()
                            cur.execute("UPDATE Lobby SET CurrentPlayers = CurrentPlayers - 1 WHERE RoomId = %s",(session["roomId"]))
                            cur.close()
                            socketio.emit('reload users', userList,room=session["roomId"]) #tells view for all players in the lobby to refresh
                    # print("Players left in the lobby:",len(game["players"]))
                    if len(game["players"]) == 0:
                        print("Nobody is in the lobby: {}. Deleting the lobby.".format(session["roomId"]))
                        cur = get_db().cursor()
                        cur.execute("DELETE FROM Lobby WHERE RoomId = %s",(session["roomId"]))
                        cur.close()
                        GAMES.remove(game)
                        # print("Remaining lobbies:",GAMES)
            session.pop('roomId', None)
            return redirect("/game")
    except Exception as e:
        print("**ERROR in leaveLobby route:",e)
        return redirect("/")

@app.route("/pregame")
def pregame():
    try:
        if session["loggedIn"] and session["roomId"]:
            try:
                for game in GAMES:
                    if game["roomId"] == session["roomId"]:
                        for player in game["gameLogic"]:
                            if player["username"] == session["username"]:
                                session["role"] = player["role"]
                cur = get_db().cursor()
                cur.execute("SELECT RoleDescription FROM Roles WHERE Role = %s",(session["role"]))
                result = cur.fetchall()
                cur.close()
                if len(result) == 0:
                    return render_template("gameViews/pregame.html",roleDesc="ERROR: Role description not found!")
                else:
                    return render_template("gameViews/pregame.html" ,roleDesc=result[0]["RoleDescription"])
            except Exception as e:
                print("**ERROR in pregame route:",e)
                return redirect("/")
    except:
        return redirect("/login")

@app.route("/intro")
def intro():
    try:
        if session["loggedIn"] and session["roomId"]:
            session["isAlive"] = "1"
            return render_template("gameViews/intro.html")
    except:
        return redirect("/login")
    

@app.route("/daytime")
def daytime():
    try:
        if session["loggedIn"] and session["roomId"]:                     
            alivePlayers = []
            playersKilled = []
            winCheck = False
            werewolfAlive = True
            for game in GAMES:
                if session["roomId"] == game["roomId"]:
                    winCheck = checkWinConditions(game["gameLogic"])
                    if winCheck:                        
                        return redirect("results")
                    for player in game["gameLogic"]:
                        if player["username"] == session["username"] and player["isAlive"] == "0":
                            print(f"{session['username']} is dead. Removing from game.")
                            session.pop("roomId",None)
                            session.pop("role",None)
                            return redirect("/")
                        if player["isAlive"] == "0":
                            playersKilled.append({"username":player["username"], "role": player["role"]})
                        else:
                            alivePlayers.append(player["username"])
                        player["specialUsed"] = "0"
                        player["chosenByHealer"] = "0"
            return render_template("gameViews/daytime.html",alivePlayers=alivePlayers,playersKilled=playersKilled)
    except Exception as e:
        print("***ERROR: error in daytime route:",e)
        return redirect("/login")

@app.route("/nighttime")
def nighttime():
    try:
        if session["loggedIn"] and session["roomId"]:
            werewolfAlive = False
            healerAlive = False
            seerAlive = False
            alreadyGone = False
            for game in GAMES:
                if session["roomId"] == game["roomId"]:
                    for player in game["gameLogic"]:
                        if player["username"] == session["username"] and player["role"] == "headWerewolf" and player["specialUsed"] == "1":
                            socketio.emit('wake up', room=session["roomId"])
                            return redirect("/daytime")
                        if player["role"] == "healer" and player["isAlive"] == "1":
                            healerAlive = True
                        elif player["role"] == "headWerewolf" and player["isAlive"] == "1":
                            werewolfAlive = True
                        elif player["role"] == "seer" and player["isAlive"] == "1":
                            seerAlive = True
            #checks to see if healer has already made a decision
            for game in GAMES:
                if session["roomId"] == game["roomId"]:
                    for player in game["gameLogic"]:
                        if player["specialUsed"] == "1":
                            alreadyGone = True
                        if player["username"] == session["username"] and player["isAlive"] == "0":
                            print(f"{session['username']} is dead. Removing from game.")
                            session.pop("roomId",None)
                            session.pop("role",None)
                            return redirect("/")
            if not alreadyGone and session["role"]=="healer" and healerAlive:
                return redirect("specialRole")
            elif not alreadyGone and session["role"]=="seer" and not healerAlive and seerAlive:
                return redirect("specialRole")
            elif not alreadyGone and session["role"]=="headWerewolf" and not healerAlive and not seerAlive:
                return redirect("specialRole")
            else:
                return render_template("gameViews/nighttime.html")
        else:
            #redirect to home, because the player is dead
            return redirect("/")
    except:
        return redirect("/login")

@app.route("/specialRole")
def specialRole():
    try:
        if session["role"] == "healer":
            #play noise for healer to open their eyes since they get directed to this screen right away
            pass
        userList = None
        for game in GAMES:
            if session["roomId"] == game["roomId"]:
                decisionTimer = game["decisionTimer"]
                userList=game["gameLogic"]
                for player in game["gameLogic"]:
                    if session["username"] == player["username"]:
                        player["specialUsed"]="1"
        return render_template("gameViews/specialRole.html",playerNames=userList,role=session["role"], decisionTimer=decisionTimer)
        
    except Exception as e:
        print("**ERROR in specialRole route:",e)
        return redirect("/nighttime")

@app.route("/voteResults")
def vote():
    try:
        isDead = False
        winCheck = False
        if session["loggedIn"] and session["roomId"]:
            playersKilled = []
            for game in GAMES:
                if session["roomId"] == game["roomId"]:
                    winCheck = checkWinConditions(game["gameLogic"])
                    if winCheck:
                        return redirect("/results")
                    for player in game["gameLogic"]:
                        if player["isAlive"] == "0":
                            playersKilled.append({"username":player["username"], "role": player["role"]})
                        if player["username"] == session["username"] and player["isAlive"] == "0":
                            isDead = True
            return render_template("gameViews/voteResults.html",playersKilled=playersKilled,isDead=isDead)
    except Exception as e:
        print("**ERROR in voteResults route:",e)
        return redirect("/daytime")

@app.route("/results")
def results():
    try:
        if session["loggedIn"] and session["roomId"]:
            winType = False
            for game in GAMES:
                if session["roomId"] == game["roomId"]:
                    winType = checkWinConditions(game["gameLogic"])
                    if session["role"] == "headWerewolf": #only updates the stats once (ghetto but it works)
                        for player in game["gameLogic"]: #increments games played
                            if "Guest#" not in player["username"]:
                                cur = get_db().cursor()
                                cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET GamesPlayed=GamesPlayed+1 WHERE Username = %s",(player["username"]))
                                cur.close()
                        if winType == "Villagers": #increments games won if villagers won
                            for player in game["gameLogic"]:
                                if "Guest#" not in player["username"]:
                                    if (player["role"] is not "werewolf" or player["role"] is not "headWerewolf")  and player["isAlive"] == "1":
                                        cur = get_db().cursor()
                                        cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET GamesWon=GamesWon+1 WHERE Username = %s",(player["username"]))
                                        cur.close()
                        elif winType == "Werewolves": #increments games won if werewolves won
                            for player in game["gameLogic"]:
                                if "Guest#" not in player["username"]:
                                    if (player["role"] == "headWerewolf" or player["role"] == "werewolf") and player["isAlive"] == "1":
                                        cur = get_db().cursor()
                                        cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET GamesWon=GamesWon+1 WHERE Username = %s",(player["username"]))
                                        cur.close()
            return render_template("gameViews/results.html",winType = winType)
    except Exception as e:
        print("***ERROR: error in results route:",e)
        return redirect("/login")

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
    # print(f"A player joined the room {roomId}")
    join_room(roomId)
    userList = None
    for game in GAMES:
        if roomId == game["roomId"]:
            userList=game["players"]
    # print(f"Sending: reload users in lobby to the lobby...\n This is the user list:{userList}")
    emit('reload users', userList, room=roomId)

@socketio.on('im ready')
def readyUp():
    print(f"{session['username']} is ready to move on!")
    allReady = True
    join_room(session["roomId"])
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["isAlive"] == "0": #dead players are always ready
                    player["isReady"] = "1"
                if player["username"] == session["username"]:
                    player["isReady"] = "1"  
            for player in game["gameLogic"]:
                if player["isReady"] != "1":
                    allReady = False
    if allReady == True:
        #changes all players to not ready again
        for game in GAMES:
            if session["roomId"] == game["roomId"]:
                for player in game["gameLogic"]:
                        if player["isAlive"] == "0": #dead players are always ready
                            player["isReady"] = "1"
                        else:
                            player["isReady"] = "0"
        print("All players are ready! Changing screens...")
        print("Sending 'next screen' to {}".format(session["roomId"]))
        emit("next screen", room=session["roomId"])
    else:
        print("Not all players are ready yet...")

@socketio.on('player to heal')
def healPlayer(username, roomId):
    print(f"The healer chose to save: {username}!")
    join_room(roomId)
    userList = None
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["username"] == username:
                    player["chosenByHealer"] = "1"

@socketio.on('player to kill')
def killPlayer(username, roomId, werewolfName):
    print(f"The werewolf chose to kill: {username}!")
    join_room(roomId)
    userList = None
    healerName = ""
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["role"] == "healer":
                    healerName = player["username"]
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["username"] == username:
                    if player["chosenByHealer"] != "1":
                        player["isAlive"] = "0"
                        print(f"{username} was killed by the werewolf!")
                        cur = get_db().cursor()
                        cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET PeopleEaten=PeopleEaten+1 WHERE Username = %s",(werewolfName))
                        cur.close()
                    else:
                        print(f"{username} was saved by the healer!")
                        cur = get_db().cursor()
                        cur.execute("UPDATE User RIGHT JOIN Stats ON User.UserId=Stats.UserId SET PeopleSaved=PeopleSaved+1 WHERE Username = %s",(healerName))
                        cur.close()

@socketio.on('cast vote')
def castVote(username, roomId):
    print(f"Vote cast against: {username}!")
    join_room(roomId)
    userList = None
    allReady = True
    voteToKill = None
    tempHighest = 0
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["isAlive"] == "0": #dead players are always ready
                    player["isReady"] = "1"
                if player["username"] == username:
                    player["killVotes"] += 1
                if player["username"] == session["username"]:
                    player["isReady"] = "1"
                if player["isReady"] != "1":
                    allReady = False
    if allReady == True:
        #finds the player with the most votes
        for game in GAMES:
            if session["roomId"] == game["roomId"]:
                for player in game["gameLogic"]:
                    if player["killVotes"] > tempHighest:
                        voteToKill = player["username"]
                        tempHighest = player["killVotes"]
        #resets votes and not ready status
        for game in GAMES:
            if session["roomId"] == game["roomId"]:
                for player in game["gameLogic"]:
                        player["isReady"] = "0"
                        player["killVotes"] = 0
                        if player["username"] == voteToKill:
                            player["isAlive"] = "0"
                            if player["role"] == "headWerewolf": #checks if there is a werewolf to promote to head werewolf
                                for player in game["gameLogic"]:
                                    if player["role"] == "werewolf":
                                        player["role"] == "headWerewolf"
                                        break #exits loop once first werewolf is promoted
        print(f"{voteToKill} has been killed by the vote!")
        print("All players are have cast their vote! Changing screens...")
        emit("next screen", room=session["roomId"])

@socketio.on('join room')
def joinRoom():
    join_room(session["roomId"])    

@socketio.on('start seer event')
def seerStart():
    print("Starting seer event!")
    join_room(session["roomId"])
    for game in GAMES:
        if session["roomId"] == game["roomId"]:
            for player in game["gameLogic"]:
                if player["role"] == "seer" and player["isAlive"] == "0": #skips over seer if they are dead
                    print("Skipping seer, because they are dead.")
                    emit("werewolf event", room=session["roomId"])
                else:
                    emit("seer event", room=session["roomId"])
    
@socketio.on('start werewolf event')
def werewolfStart():
    print("Starting werewolf event!")
    join_room(session["roomId"])
    emit("werewolf event", room=session["roomId"])

@socketio.on('wake up')
def wakeUp():
    try:
        print(f"waking everybody up in room {session['roomId']}")
        join_room(session["roomId"])
        emit("wake up", room=session["roomId"])
    except Exception as e:
        print("ERROR:",e)

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html'), 404

if __name__ == "__main__":
    handler = RotatingFileHandler("../backups/werewolfConnection.log", maxBytes=100000, backupCount=3)
    logger = logging.getLogger("tdm")
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    socketio.run(app, host="0.0.0.0",port=3088, log_output=False, debug=True)
