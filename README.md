
# Setting up Werewolf

=======================
## Packages

--------
- Before running the server, you must have the following packages installed on your environment using `sudo apt-get install`:
```
- mysql-server
- phpmyadmin
- apache2
- python3
- git
```
  
## Getting the code

----------------

- Navigate to where you want the code to exist and run:

`git clone https://github.com/ab3lson/WerewolfGame/`

## Python modules

--------------
- Move inside WerewolfGame and run the following command to install all the python3 modules that are needed:
`pip3 install -r requirements.txt`
## Config file

-----------
- In the root project directory, create a credentials file using:
`touch creds.py`
- Inside the creds file insert the credentials for your project with the following format:
```
"""Database connection creds"""
DBUser = "username"
DBPass = "password"
DBHost = "127.0.0.1"
DBName = "werewolf"

"""Password Encryption Salt"""
salt = "RandomSalt"
secretKey = "RandomSalt"
```
  

## Set up database

---------------
- Navigate to localhost/phpmyadmin and log in with admin credentials.
- Navigate to the *Import* tab at the top.
- Import createWerewolfEmptyDB.sql from the project directory and select *Go* at the bottom.

  

## Run in test environment

-----------------------
- Make *main.py* executable with:
`chmod +x main.py`
- Run *main.py* with:
`./main.py`
- Navigate to the server in your browser (it is configured to run on port 3088 by default):
 `localhost:3088`