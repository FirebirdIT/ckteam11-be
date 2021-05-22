from flask import Flask
from flask import jsonify
from flask import request

from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import sqlite3

from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, support_credentials=True)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

DATABASE_PATH = "database.sqlite"

## Database
def insert_data(sql, value = None):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        if(value == None):
            cur.execute(sql)
        else:
            cur.execute(sql, value)
        conn.commit()
        conn.close()
        return {"msg": "Data Inserted Successfully", "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Inserted Failed", "success": False, "error_msg": str(e)}

def select_all_data(sql, value = None):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        if(value == None):
            cur.execute(sql)
        else:
            cur.execute(sql, value)
        rows = cur.fetchall()
        conn.close()
        return {"data": rows, "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Retrieve Failed", "success": False, "error_msg": str(e)}

def select_one_data(sql, value = None):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        if(value == None):
            cur.execute(sql)
        else:
            cur.execute(sql, value)
        row = cur.fetchone()
        conn.close()
        return {"data": row, "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Retrieve Failed", "success": False, "error_msg": str(e)}

def update_data(sql, value):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute(sql, value)
        conn.commit()
        conn.close()
        return {"msg": "Data Updated Successfully", "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Update Failed", "success": False, "error_msg": str(e)}

def delete_data(sql):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()
        return {"msg": "Data Deleted Successfully", "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Delete Failed", "success": False, "error_msg": str(e)}

@app.route("/donation", methods=["POST"])
def donation():
    try:
        customer_name = request.json.get("customer_name")
        if (customer_name == None):
            return jsonify({"msg": "customer_name Missing", "success": False})
    except:
        return jsonify({"msg": "customer_name Missing", "success": False})

    try:
        amount = request.json.get("amount")
        if (amount == None):
            return jsonify({"msg": "amount Missing", "success": False})
    except:
        return jsonify({"msg": "amount Missing", "success": False})

    try:
        description = request.json.get("description")
        if (description == None):
            return jsonify({"msg": "description Missing", "success": False})
    except:
        return jsonify({"msg": "description Missing", "success": False})

    try:
        username = request.json.get("username")
        if (username == None):
            return jsonify({"msg": "username Missing", "success": False})
    except:
        return jsonify({"msg": "username Missing", "success": False})

    donation_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    response = insert_data('''
            INSERT INTO report(datetime,customer_name,amount,description,username)VALUES(?,?,?,?,?)
        ''', (donation_date, customer_name, amount, description, username))

    if(response["success"]):
        return jsonify({"msg": "Record Successfully", "success": response["success"]})
    else:
        return jsonify({"msg": "Record Failed", "success": response["success"]})

@app.route("/volunteer/register", methods=["POST"])
def volunteer_register():
    try:
        username = request.json.get("username")
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.json.get("password")
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        display_name = request.json.get("display_name")
        if (display_name == None):
            return jsonify({"msg": "display_name Missing", "success": False})
    except:
        return jsonify({"msg": "display_name Missing", "success": False})

    try:
        address = request.json.get("address")
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.json.get("phone_no")
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    try:
        ic = request.json.get("ic")
        if (ic == None):
            return jsonify({"msg": "ic Missing", "success": False})
    except:
        return jsonify({"msg": "ic Missing", "success": False})

    try:
        team = request.json.get("team")
        if (team == None):
            return jsonify({"msg": "team Missing", "success": False})
    except:
        return jsonify({"msg": "team Missing", "success": False})

    ## Check Team Valid Anot
    response = select_all_data("SELECT * FROM team")
    validTeam = False
    if (response["success"]):
        for row in response["data"]:
            if (team == row[1]):
                validTeam = True
        if(validTeam == False):
            return jsonify({"msg": "Invalid Team. Please Submit Team Username", "success": False})
    else:
        print(response["error_msg"])
        return jsonify({"msg": "Team Checking Failed", "success": False})

    ## Check Username
    response = select_all_data("SELECT username FROM team UNION ALL SELECT username FROM volunteer")
    if(response["success"]):
        for row in response["data"]:
            if(username == row[0]):
                return jsonify({"msg": "Username Taken.", "success": False})
    else:
        print(response["error_msg"])
        return jsonify({"msg": "Username Checking Failed", "success": False})

    response = insert_data('''
        INSERT INTO volunteer(username,password,display_name, address, phone_no, ic, team)VALUES(?,?,?,?,?,?,?)
    ''', (username, password, display_name, address, phone_no, ic, team))

    if(response["success"]):
        return jsonify({"msg": "{} registered successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})

@app.route("/team/register", methods=["POST"])
def team_register():
    try:
        username = request.json.get("username")
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.json.get("password")
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        display_name = request.json.get("display_name")
        if (display_name == None):
            return jsonify({"msg": "display_name Missing", "success": False})
    except:
        return jsonify({"msg": "display_name Missing", "success": False})

    try:
        address = request.json.get("address")
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.json.get("phone_no")
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    ## Check Username
    response = select_all_data("SELECT username FROM team UNION ALL SELECT username FROM volunteer")
    if(response["success"]):
        for row in response["data"]:
            if(username == row[0]):
                return jsonify({"msg": "Username Taken.", "success": False})
    else:
        print(response["error_msg"])
        return jsonify({"msg": "Username Checking Failed", "success": False})

    response = insert_data('''
        INSERT INTO team(username,password,display_name, address, phone_no)VALUES(?,?,?,?,?)
    ''', (username, password, display_name, address, phone_no))

    if(response["success"]):
        return jsonify({"msg": "{} registered successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if(username == None):
        return jsonify({"msg": "Username Missing", "success": False})

    if (password == None):
        return jsonify({"msg": "Password Missing", "success": False})

    if(username == "admin" and password == "admin"):
        access_token = create_access_token(identity=username)
        return jsonify({"msg": "Login Successfully", "role": "admin", "access_token": access_token})

    response = select_all_data("select * from team")
    for row in response["data"]:
        if username == row[1] and password == row[2]:
            access_token = create_access_token(identity=username)
            return jsonify({"msg": "Login Successfully", "role": "team", "access_token": access_token})

    response = select_all_data("select * from volunteer")
    for row in response["data"]:
        if username == row[1] and password == row[2]:
            access_token = create_access_token(identity=username)
            return jsonify({"msg": "Login Successfully", "role": "volunteer", "access_token": access_token})

    return jsonify({"msg": "Invalid username or password"}), 401

@app.route("/test", methods=["GET"])
#@jwt_required()
def test():
    return "HELLO WORLD"

if __name__ == "__main__":
    app.run(debug=True)