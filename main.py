import os
from flask import Flask, send_from_directory
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from random import randint
import smtplib
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fpdf import FPDF
import subprocess

from datetime import date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

# DATABASE_PATH = "/home/ubuntu/ckteam-backend/database.sqlite"
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
# LOGO_ROOT = "/home/ubuntu/ckteam-backend/logo"
# FONT_PATH = '/home/ubuntu/ckteam-backend/font/unifont/'
# PDF_PATH = "/home/ubuntu/ckteam-backend/pdf"
# ASSEST_PATH = "/home/ubuntu/ckteam-backend/assest"

DATABASE_PATH = "database.sqlite"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
LOGO_ROOT = "logo"
FONT_PATH = 'font/unifont/'
PDF_PATH = "pdf"
ASSEST_PATH = "assest"

## Email
def send_smail(data, pdf_output_path):
    msg = MIMEMultipart()
    msg['Subject'] = 'Donation Receipt'
    msg['From'] = str("CKTEAM")
    msg['To'] = str(data["email"])

    body = "<p>Here's the receipt. Thanks for your donation.</p>"
    msgText = MIMEText('<b>%s</b>' % (body), 'html')
    msg.attach(msgText)

    filename = pdf_output_path
    with open(filename, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
    attach.add_header('Content-Disposition', 'attachment', filename=str(filename))
    msg.attach(attach)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("chrisliang183@gmail.com", "Hansheng0512#")
    try:
        server.send_message(msg)
        server.quit()
    except:
        return False
    return True

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


def delete_data(sql, value):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute(sql, value)
        conn.commit()
        conn.close()
        return {"msg": "Data Deleted Successfully", "success": True, "error_msg": ""}
    except Exception as e:
        print(e)
        return {"msg": "Data Delete Failed", "success": False, "error_msg": str(e)}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_pdf(data):
    response = select_one_data("SELECT * FROM pdf")
    if(not response["success"]):
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})

    subprocess.call(["php", "tfpdf.php"], shell=True)

    pdf = FPDF('P', 'in', 'A4');
    pdf.add_page()

    # Chinese font
    pdf.add_font('Simsun', '', os.path.join(FONT_PATH, "SIMSUN.ttf"), uni=True)

    pdf.set_margins(0, 0, 0)
    pdf.ln(3.75)
    pdf.rect(0.25, 3.75, 7.75, 4)
    pdf.image(os.path.join(LOGO_ROOT, 'main.png'), 0.75, 4, 1)
    pdf.set_font('Times', 'B', 4)
    pdf.ln(0.85)
    pdf.cell(0.925)
    pdf.cell(0, 0, f"", 0)

    # Header
    pdf.ln(-0.775)
    pdf.set_font('Simsun', '', 15)
    pdf.cell(1.875)
    pdf.cell(0, 0, response["data"][8], 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.ln(0.225)
    pdf.cell(1.875)
    pdf.cell(0, 0, f"XIAO XIN SERDANG OLD FOLKS HOME", 0)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.ln(0.175)
    pdf.cell(1.875)
    pdf.cell(0, 0, f"PERTUBUHAN KEBAJIKAN ORANG TUA XIAO XIN", 0)

    pdf.set_font('Times', '', 7)
    pdf.ln(0.15)
    pdf.cell(1.875)
    pdf.cell(0, 0, f"NO 1687, JALAN 18/46 TAMAN SRI SEDANG, 43300 SERI KEMBANGAN, SELANGOR", 0)
    pdf.set_font('Helvetica', '', 7)
    pdf.ln(0.15)
    pdf.cell(1.875)
    pdf.cell(0, 0, f"Contact: +6016-4738115 (LK)/+6016-8851687 (YT)", 0)

    pdf.ln(0.10)
    pdf.cell(1.875)
    pdf.cell(0, 0, f"Volunteer: {data['username']}", 0)

    pdf.set_font('Simsun', '', 11)
    pdf.ln(-0.7)
    pdf.cell(6.275)
    pdf.cell(0, 0, response["data"][0], 0)
    pdf.set_font('Times', '', 10)
    pdf.ln(0.115)
    pdf.cell(6)
    pdf.cell(0, 0, "OFFICIAL RECEIPT", 0)
    pdf.line(6, 4.5, 7.25, 4.5)
    pdf.set_font('Times', '', 14)
    pdf.ln(0.275)
    pdf.cell(6)
    pdf.cell(0, 0, f"No {data['recipe_no']}", 0)

    # Name and Contact
    pdf.set_font('Simsun', '', 11)
    pdf.ln(0.6)
    pdf.cell(1)
    pdf.cell(0, 0, response["data"][1], 0)
    pdf.set_font('Times', '', 10)
    pdf.ln(0.135)
    pdf.cell(1)
    pdf.cell(0, 0, f"NAME : {data['customer_name']}", 0)
    pdf.line(1.575, 5.5, 7.25, 5.5)

    pdf.set_font('Simsun', '', 10)
    pdf.ln(0.225)
    pdf.cell(1)
    pdf.cell(0, 0, response["data"][1], 0)
    pdf.set_font('Times', '', 10)
    pdf.ln(0.175)
    pdf.cell(1)
    pdf.cell(0, 0, f"CONTACT : {data['cust_phone_no']}", 0)
    pdf.line(1.825, 5.9, 7.25, 5.9)

    # Checkbox
    pdf.ln(0.225)
    pdf.cell(1)
    pdf.cell(0.25, 0.25, " X" if (data["cash_donation"]) else "", 1)
    pdf.set_font('Simsun', '', 9)
    pdf.ln(0.05)
    pdf.cell(1.25)
    pdf.cell(0, 0, response["data"][3], 0)
    pdf.set_font('Times', '', 9)
    pdf.ln(0.175)
    pdf.cell(1.25)
    pdf.cell(0, 0, "DONATION (CASH)", 0)

    pdf.ln(-0.225)
    pdf.cell(2.575)
    pdf.cell(0.25, 0.25, " X" if (data["medicine"]) else "", 1)
    pdf.set_font('Simsun', '', 9)
    pdf.ln(0.05)
    pdf.cell(2.825)
    pdf.cell(0, 0, response["data"][4], 0)
    pdf.set_font('Times', '', 9)
    pdf.ln(0.175)
    pdf.cell(2.825)
    pdf.cell(0, 0, "MEDICINE", 0)

    pdf.ln(-0.225)
    pdf.cell(3.625)
    pdf.cell(0.25, 0.25, " X" if (data["coffin"]) else "", 1)
    pdf.set_font('Simsun', '', 9)
    pdf.ln(0.05)
    pdf.cell(3.875)
    pdf.cell(0, 0, response["data"][5], 0)
    pdf.set_font('Times', '', 9)
    pdf.ln(0.175)
    pdf.cell(3.875)
    pdf.cell(0, 0, "COFFIN", 0)

    # Bank Account
    pdf.ln(-0.225)
    pdf.cell(5)
    pdf.image(os.path.join(ASSEST_PATH, "round_rect.png"), 4.5, 6.05, 2.75, 0.7)
    # pdf.cell(2.25, 0.675, "", 1) #square rectangle
    pdf.ln(0.175)
    pdf.cell(4.575)
    pdf.set_font('Times', 'BI', 10)
    pdf.cell(0, 0, "Bank Account", 0)
    pdf.ln(0.15)
    pdf.cell(4.575)
    pdf.cell(0, 0, f"Pertubuhan Kebajikan Orang Tua Xiao Xin ", 0)
    pdf.ln(0.15)
    pdf.cell(4.575)
    pdf.cell(0, 0, f"Ambank - 8881034592429", 0)

    # Amount
    pdf.ln(-0.02)
    pdf.cell(1)
    pdf.cell(3, 0.325, "", 1)
    pdf.ln(0.16)
    pdf.cell(1.05)
    pdf.set_font('Times', '', 13)
    pdf.cell(0, 0, f"RM {data['amount']}", 0)
    pdf.ln(0.35)
    pdf.cell(0.95)
    pdf.set_font('Times', '', 10)
    pdf.cell(0, 0, f"Cash/Cheque No : {data['cheque_no']}", 0)

    # Received By
    pdf.ln(0.095)
    pdf.cell(4.125)
    pdf.set_font('Simsun', '', 10)
    pdf.cell(0, 0, response["data"][6], 0)
    pdf.ln(0.175)
    pdf.cell(4.125)
    pdf.set_font('Times', '', 12)
    pdf.cell(0, 0, "Received By : YT Ong", 0)
    pdf.line(5.125, 7.4, 7.25, 7.4)

    # Date
    pdf.ln(-2.325)
    pdf.cell(5.6)
    pdf.set_font('Simsun', '', 8)
    pdf.cell(0, 0, response["data"][7], 0)
    pdf.ln(0.125)
    pdf.cell(5.6)
    pdf.set_font('Times', '', 8)
    pdf.cell(0, 0, f"DATE : {data['donation_date']}", 0)
    pdf.line(6, 5.175, 7.25, 5.175)

    # Output PDF
    pdf_name = f"{data['username']}_{randint(1, 999999)}.pdf"
    full_output_path = os.path.join(PDF_PATH, pdf_name)

    pdf.output(full_output_path, 'F')

    return full_output_path, pdf_name

@app.route("/donation/volunteer", methods=["POST"])
@cross_origin()
def donation_volunteer():
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
        cash_donation = request.json.get("cash_donation")
        if (cash_donation == None):
            return jsonify({"msg": "cash_donation Missing", "success": False})
    except:
        return jsonify({"msg": "cash_donation Missing", "success": False})

    try:
        medicine = request.json.get("medicine")
        if (medicine == None):
            return jsonify({"msg": "medicine Missing", "success": False})
    except:
        return jsonify({"msg": "medicine Missing", "success": False})

    try:
        coffin = request.json.get("coffin")
        if (coffin == None):
            return jsonify({"msg": "coffin Missing", "success": False})
    except:
        return jsonify({"msg": "coffin Missing", "success": False})

    try:
        username = request.json.get("username")
        if (username == None):
            return jsonify({"msg": "username Missing", "success": False})
    except:
        return jsonify({"msg": "username Missing", "success": False})

    try:
        email = request.json.get("email")
        if (email == None):
            return jsonify({"msg": "email Missing", "success": False})
    except:
        return jsonify({"msg": "email Missing", "success": False})

    try:
        donation_type = request.json.get("donation_type")
        if (donation_type == None):
            return jsonify({"msg": "donation_type Missing", "success": False})
        if(donation_type == 2):
            try:
                cheque_no = request.json.get("cheque_no")
                if (cheque_no == None):
                    return jsonify({"msg": "cheque_no Missing", "success": False})
            except:
                return jsonify({"msg": "cheque_no Missing", "success": False})
        else:
            cheque_no = "-"
    except:
        return jsonify({"msg": "donation_type Missing", "success": False})

    try:
        donation_date = request.json.get("donation_datetime")
        if (donation_date == None):
            return jsonify({"msg": "donation_datetime Missing", "success": False})
    except:
        return jsonify({"msg": "donation_datetime Missing", "success": False})

    try:
        cust_phone_no = request.json.get("cust_phone_no")
        if (cust_phone_no == None):
            return jsonify({"msg": "cust_phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "cust_phone_no Missing", "success": False})

    for _ in range(10):
        recipe_no = randint(100000, 199999)

    response = insert_data('''
            INSERT INTO report(datetime,customer_name,amount,username, email, role, donation_type, cheque_no, recipe_no, cash_donation, coffin, medicine,cust_phone_no, team)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (donation_date, customer_name, amount, username, email, "volunteer", donation_type, cheque_no, recipe_no, cash_donation, coffin, medicine,cust_phone_no,""))

    if(response["success"]):
        res = select_one_data("SELECT * FROM volunteer WHERE username=?", (username,))
        if(res["success"]):
            if res["data"] != None:
                selected_team = res["data"][7]
            else:
                return jsonify({"msg": "invalid volunteer username", "success": False})
        else:
            return jsonify({"msg": "database error", "error_msg": res["error_msg"],"success": False})

        res = select_one_data("SELECT * FROM team WHERE username=?", (selected_team,))
        if (res["success"]):
            if res["data"] != None:
                team_english_name = res["data"][3]
                team_address = res["data"][4]
                team_phone_no = res["data"][5]
                logo_relative_path = res["data"][6]
                team_chinese_name = res["data"][7]
                team_malay_name = res["data"][8]
                team_ssv_id = res["data"][9]
                bank_name = res["data"][10]
                bank_owner_name = res["data"][11]
                bank_account_number = res["data"][12]
            else:
                return jsonify({"msg": "invalid username", "success": False})
        else:
            return jsonify({"msg": "database error", "error_msg": res["error_msg"], "success": False})

        js = {
            "username": username,
            "team_english_name": team_english_name,
            "team_address": team_address,
            "team_phone_no": team_phone_no,
            "logo_relative_path": logo_relative_path,
            "team_chinese_name": team_chinese_name,
            "team_malay_name": team_malay_name,
            "team_ssv_id": team_ssv_id,
            "bank_name": bank_name,
            "bank_owner_name": bank_owner_name,
            "bank_account_number": bank_account_number,
            "donation_date": donation_date,
            "customer_name": customer_name,
            "amount": amount,
            "email": email,
            "cheque_no": cheque_no,
            "recipe_no": recipe_no,
            "cash_donation": cash_donation,
            "coffin": coffin,
            "medicine": medicine,
            "cust_phone_no": cust_phone_no
        }
        pdf_output_path, pdf_name = generate_pdf(js)
        send_smail(js, pdf_output_path)

        res = update_data("UPDATE report SET pdf_path=?, team=? WHERE datetime=? AND customer_name=? AND amount=?", (pdf_name,selected_team,donation_date, customer_name, amount,))
        if(res["success"]):
            return jsonify({"msg": "Record Successfully & Email Sent", "success": response["success"]})
        else:
            return jsonify({"msg": "PDF save Failed", "success": response["success"]})
    else:
        return jsonify({"msg": "Record Failed", "success": response["success"]})

@app.route("/donation/team", methods=["POST"])
@cross_origin()
def donation_team():
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
        cash_donation = request.json.get("cash_donation")
        if (cash_donation == None):
            return jsonify({"msg": "cash_donation Missing", "success": False})
    except:
        return jsonify({"msg": "cash_donation Missing", "success": False})

    try:
        medicine = request.json.get("medicine")
        if (medicine == None):
            return jsonify({"msg": "medicine Missing", "success": False})
    except:
        return jsonify({"msg": "medicine Missing", "success": False})

    try:
        coffin = request.json.get("coffin")
        if (coffin == None):
            return jsonify({"msg": "coffin Missing", "success": False})
    except:
        return jsonify({"msg": "coffin Missing", "success": False})

    try:
        username = request.json.get("username")
        if (username == None):
            return jsonify({"msg": "username Missing", "success": False})
    except:
        return jsonify({"msg": "username Missing", "success": False})

    try:
        email = request.json.get("email")
        if (email == None):
            return jsonify({"msg": "email Missing", "success": False})
    except:
        return jsonify({"msg": "email Missing", "success": False})

    try:
        donation_type = request.json.get("donation_type")
        if (donation_type == None):
            return jsonify({"msg": "donation_type Missing", "success": False})
        if(donation_type == 2):
            try:
                cheque_no = request.json.get("cheque_no")
                if (cheque_no == None):
                    return jsonify({"msg": "cheque_no Missing", "success": False})
            except:
                return jsonify({"msg": "cheque_no Missing", "success": False})
        else:
            cheque_no = "-"
    except:
        return jsonify({"msg": "donation_type Missing", "success": False})

    try:
        donation_date = request.json.get("donation_datetime")
        if (donation_date == None):
            return jsonify({"msg": "donation_datetime Missing", "success": False})
    except:
        return jsonify({"msg": "donation_datetime Missing", "success": False})

    try:
        cust_phone_no = request.json.get("cust_phone_no")
        if (cust_phone_no == None):
            return jsonify({"msg": "cust_phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "cust_phone_no Missing", "success": False})

    for _ in range(10):
        recipe_no = randint(100000, 199999)

    response = insert_data('''
            INSERT INTO report(datetime,customer_name,amount,username, email, role, donation_type, cheque_no, recipe_no, cash_donation, coffin, medicine,cust_phone_no,team)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (donation_date, customer_name, amount, username, email, "team", donation_type, cheque_no, recipe_no, cash_donation, coffin, medicine,cust_phone_no, username))

    if(response["success"]):
        res = select_one_data("SELECT * FROM team WHERE username=?", (username,))
        if (res["success"]):
            if res["data"] != None:
                team_english_name = res["data"][3]
                team_address = res["data"][4]
                team_phone_no = res["data"][5]
                logo_relative_path = res["data"][6]
                team_chinese_name = res["data"][7]
                team_malay_name = res["data"][8]
                team_ssv_id = res["data"][9]
                bank_name = res["data"][10]
                bank_owner_name = res["data"][11]
                bank_account_number = res["data"][12]
            else:
                return jsonify({"msg": "invalid username", "success": False})
        else:
            return jsonify({"msg": "database error", "error_msg": res["error_msg"], "success": False})

        js = {
            "username": username,
            "team_english_name": team_english_name,
            "team_address": team_address,
            "team_phone_no": team_phone_no,
            "logo_relative_path": logo_relative_path,
            "team_chinese_name": team_chinese_name,
            "team_malay_name": team_malay_name,
            "team_ssv_id": team_ssv_id,
            "bank_name": "Ambank",
            "bank_owner_name": "Pertubuhan Kebajikan Orang Tua Xiao Xin ",
            "bank_account_number": "8881034592429 ",
            "donation_date": donation_date,
            "customer_name": customer_name,
            "amount": amount,
            "email": email,
            "cheque_no": cheque_no,
            "recipe_no": recipe_no,
            "cash_donation": cash_donation,
            "coffin": coffin,
            "medicine": medicine,
            "cust_phone_no": cust_phone_no
        }
        pdf_output_path, pdf_name = generate_pdf(js)
        send_smail(js, pdf_output_path)

        res = update_data("UPDATE report SET pdf_path=? WHERE datetime=? AND customer_name=? AND amount=?", (pdf_name,donation_date, customer_name, amount,))
        if(res["success"]):
            return jsonify({"msg": "Record Successfully & Email Sent", "success": response["success"]})
        else:
            return jsonify({"msg": "PDF save Failed", "success": response["success"]})
    else:
        return jsonify({"msg": "Record Failed", "success": response["success"]})


@app.route('/pdf/<string:id>', methods=["GET"])
def download_file(id):
    res = select_one_data("SELECT * FROM report WHERE id=?", (id,))
    if(res["success"]):
        if(res["data"] != None):
            filename = res["data"][14]
        else:
            return jsonify({"msg": "invalid id", "success": False})
    return send_from_directory(PDF_PATH, filename, as_attachment=False)

@app.route("/volunteer/register", methods=["POST"])
def volunteer_register():
    try:
        username = request.form["username"]
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.form["password"]
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        english_name = request.form["english_name"]
        if (english_name == None):
            return jsonify({"msg": "english_name Missing", "success": False})
    except:
        return jsonify({"msg": "english_name Missing", "success": False})

    try:
        address = request.form["address"]
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.form["phone_no"]
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    try:
        ic = request.form["ic"]
        if (ic == None):
            return jsonify({"msg": "ic Missing", "success": False})
    except:
        return jsonify({"msg": "ic Missing", "success": False})

    try:
        team = request.form["team"]
        if (team == None):
            return jsonify({"msg": "team Missing", "success": False})
    except:
        return jsonify({"msg": "team Missing", "success": False})

    try:
        logo_file = request.files.get('logo_file')
        if (logo_file == None):
            return jsonify({"msg": "logo_file Missing", "success": False})
    except:
        return jsonify({"msg": "logo_file Missing", "success": False})

    ## Check Team Valid Anot
    response = select_all_data("SELECT * FROM team")
    validTeam = False
    if (response["success"]):
        for row in response["data"]:
            if (team == row[1]):
                validTeam = True
        if(validTeam == False):
            return jsonify({"msg": "Invalid Team. Please Check Team Username", "success": False})
    else:
        return jsonify({"msg": "Team Checking Failed", "error_msg": response["error_msg"],"success": False})

    ## Check Username
    response = select_all_data("SELECT username FROM team UNION ALL SELECT username FROM volunteer")
    if(response["success"]):
        for row in response["data"]:
            if(username == row[0]):
                return jsonify({"msg": "Username Taken.", "success": False})
    else:
        return jsonify({"msg": "Username Checking Failed", "error_msg": response["error_msg"], "success": False})

    ## Save Image
    filename = secure_filename(logo_file.filename)
    modified_filename = f"{randint(1, 999999)}_{filename}"
    logo_file.save(os.path.join(LOGO_ROOT, modified_filename))

    response = insert_data('''
        INSERT INTO volunteer(username,password,english_name, address, phone_no, ic, team, logo_path)VALUES(?,?,?,?,?,?,?,?)
    ''', (username, password, english_name, address, phone_no, ic, team, modified_filename,))

    if(response["success"]):
        return jsonify({"msg": "{} registered successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})

@app.route("/volunteer/edit", methods=["POST"])
def volunteer_edit():
    try:
        username = request.form["username"]
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.form["password"]
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        english_name = request.form["english_name"]
        if (english_name == None):
            return jsonify({"msg": "english_name Missing", "success": False})
    except:
        return jsonify({"msg": "english_name Missing", "success": False})

    try:
        address = request.form["address"]
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.form["phone_no"]
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    try:
        ic = request.form["ic"]
        if (ic == None):
            return jsonify({"msg": "ic Missing", "success": False})
    except:
        return jsonify({"msg": "ic Missing", "success": False})

    try:
        team = request.form["team"]
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
        return jsonify({"msg": "Team Checking Failed", "success": False})

    logo_file = request.files.get('logo_file')
    isLogoEmpty = True;

    if logo_file == None or logo_file.filename == '':
        isLogoEmpty = True
    else:
        isLogoEmpty = False
        if not allowed_file(logo_file.filename):
            return jsonify({"msg": "only support jpg, jpeg, png format", "success": False})

        ## Save Image
        filename = secure_filename(logo_file.filename)
        modified_filename = f"{randint(1, 999999)}_{filename}"
        logo_path = os.path.join(LOGO_ROOT, modified_filename)
        logo_file.save(logo_path)

    if (isLogoEmpty):
        response = update_data('''
                UPDATE volunteer SET password=?, english_name=?, address=?, phone_no=?, ic=?, team=? WHERE username=?
            ''', (password, english_name, address, phone_no, ic, team, username, ))
    else:
        response = update_data('''
                        UPDATE volunteer SET password=?, english_name=?, address=?, phone_no=?, ic=?, team=?, logo_path=? WHERE username=?
                    ''', (password, english_name, address, phone_no, ic, team, modified_filename, username,))

    if (response["success"]):
        return jsonify({"msg": "{} updated successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})

@app.route("/team/register", methods=["POST"])
def team_register():
    try:
        username = request.form['username']
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.form['password']
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        english_name = request.form['english_name']
        if (english_name == None):
            return jsonify({"msg": "english_name Missing", "success": False})
    except:
        return jsonify({"msg": "english_name Missing", "success": False})

    try:
        address = request.form['address']
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.form['phone_no']
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    try:
        chinese_name = request.form['chinese_name']
        if (chinese_name == None):
            return jsonify({"msg": "chinese_name Missing", "success": False})
    except:
        return jsonify({"msg": "chinese_name Missing", "success": False})

    try:
        malay_name = request.form['malay_name']
        if (malay_name == None):
            return jsonify({"msg": "malay_name Missing", "success": False})
    except:
        return jsonify({"msg": "malay_name Missing", "success": False})

    try:
        team_ssm_id = request.form['team_ssm_id']
        if (team_ssm_id == None):
            return jsonify({"msg": "team_ssm_id Missing", "success": False})
    except:
        return jsonify({"msg": "team_ssm_id Missing", "success": False})

    try:
        bank_name = request.form['bank_name']
        if (bank_name == None):
            return jsonify({"msg": "bank_name Missing", "success": False})
    except:
        return jsonify({"msg": "bank_name Missing", "success": False})

    try:
        bank_owner_name = request.form['bank_owner_name']
        if (bank_owner_name == None):
            return jsonify({"msg": "bank_owner_name Missing", "success": False})
    except:
        return jsonify({"msg": "bank_owner_name Missing", "success": False})

    try:
        bank_account_number = request.form['bank_account_number']
        if (bank_account_number == None):
            return jsonify({"msg": "bank_account_number Missing", "success": False})
    except:
        return jsonify({"msg": "bank_account_number Missing", "success": False})

    try:
        logo_file = request.files.get('logo_file')
        if (logo_file == None):
            return jsonify({"msg": "logo_file Missing", "success": False})
    except:
        return jsonify({"msg": "logo_file Missing", "success": False})

    try:
        pic = request.form['pic']
        if (pic == None):
            return jsonify({"msg": "pic Missing", "success": False})
    except:
        return jsonify({"msg": "pic Missing", "success": False})

    if logo_file.filename == '':
        return jsonify({"msg": "no selected file", "success": False})

    if not allowed_file(logo_file.filename):
        return jsonify({"msg": "only support jpg, jpeg, png format", "success": False})

    ## Save Image
    filename = secure_filename(logo_file.filename)
    modified_filename = f"{randint(1, 999999)}_{filename}"
    logo_file.save(os.path.join(LOGO_ROOT, modified_filename))

    ## Check Username
    response = select_all_data("SELECT username FROM team UNION ALL SELECT username FROM volunteer")
    if(response["success"]):
        for row in response["data"]:
            if(username == row[0]):
                return jsonify({"msg": "Username Taken.", "success": False})
    else:
        return jsonify({"msg": "Username Checking Failed", "error_msg": response["error_msg"],  "success": False})

    response = insert_data('''
        INSERT INTO team(username,password,english_name, address, phone_no, logo_path, chinese_name, malay_name, team_ssm_id, bank_name, bank_owner_name, bank_account_number,pic)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (username, password, english_name, address, phone_no, modified_filename, chinese_name, malay_name, team_ssm_id,bank_name, bank_owner_name, bank_account_number,pic,))

    if(response["success"]):
        return jsonify({"msg": "{} registered successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})

@app.route("/team/edit", methods=["POST"])
def team_edit():
    try:
        username = request.form['username']
        if (username == None):
            return jsonify({"msg": "Username Missing", "success": False})
    except:
        return jsonify({"msg": "Username Missing", "success": False})

    try:
        password = request.form['password']
        if (password == None):
            return jsonify({"msg": "Password Missing", "success": False})
    except:
        return jsonify({"msg": "password Missing", "success": False})

    try:
        english_name = request.form['english_name']
        if (english_name == None):
            return jsonify({"msg": "english_name Missing", "success": False})
    except:
        return jsonify({"msg": "english_name Missing", "success": False})

    try:
        address = request.form['address']
        if (address == None):
            return jsonify({"msg": "address Missing", "success": False})
    except:
        return jsonify({"msg": "address Missing", "success": False})

    try:
        phone_no = request.form['phone_no']
        if (phone_no == None):
            return jsonify({"msg": "phone_no Missing", "success": False})
    except:
        return jsonify({"msg": "phone_no Missing", "success": False})

    try:
        chinese_name = request.form['chinese_name']
        if (chinese_name == None):
            return jsonify({"msg": "chinese_name Missing", "success": False})
    except:
        return jsonify({"msg": "chinese_name Missing", "success": False})

    try:
        malay_name = request.form['malay_name']
        if (malay_name == None):
            return jsonify({"msg": "malay_name Missing", "success": False})
    except:
        return jsonify({"msg": "malay_name Missing", "success": False})

    try:
        team_ssm_id = request.form['team_ssm_id']
        if (team_ssm_id == None):
            return jsonify({"msg": "team_ssm_id Missing", "success": False})
    except:
        return jsonify({"msg": "team_ssm_id Missing", "success": False})

    try:
        bank_name = request.form['bank_name']
        if (bank_name == None):
            return jsonify({"msg": "bank_name Missing", "success": False})
    except:
        return jsonify({"msg": "bank_name Missing", "success": False})

    try:
        bank_owner_name = request.form['bank_owner_name']
        if (bank_owner_name == None):
            return jsonify({"msg": "bank_owner_name Missing", "success": False})
    except:
        return jsonify({"msg": "bank_owner_name Missing", "success": False})

    try:
        bank_account_number = request.form['bank_account_number']
        if (bank_account_number == None):
            return jsonify({"msg": "bank_account_number Missing", "success": False})
    except:
        return jsonify({"msg": "bank_account_number Missing", "success": False})

    try:
        pic = request.form['pic']
        if (pic == None):
            return jsonify({"msg": "pic Missing", "success": False})
    except:
        return jsonify({"msg": "pic Missing", "success": False})

    logo_file = request.files.get('logo_file')
    isLogoEmpty = True;

    if logo_file == None or logo_file.filename == '':
        isLogoEmpty = True
    else:
        isLogoEmpty = False
        if not allowed_file(logo_file.filename):
            return jsonify({"msg": "only support jpg, jpeg, png format", "success": False})

        ## Save Image
        filename = secure_filename(logo_file.filename)
        modified_filename = f"{randint(1, 999999)}_{filename}"
        logo_path = os.path.join(LOGO_ROOT, modified_filename)
        logo_file.save(logo_path)

    if(isLogoEmpty):
        response = update_data('''
            UPDATE team SET password=?, english_name=?, address=?, phone_no=?, chinese_name=?, malay_name=?, bank_name=?, 
            bank_owner_name=?, bank_account_number=?, pic=? WHERE username=?
        ''', (password, english_name, address, phone_no, chinese_name, malay_name, bank_name, bank_owner_name, bank_account_number,
              pic, username,))
    else:
        response = update_data('''
                    UPDATE team SET password=?, english_name=?, address=?, phone_no=?, chinese_name=?, malay_name=?, bank_name=?, 
                    bank_owner_name=?, bank_account_number=?, pic=?, logo_path=? WHERE username=?
                ''', (password, english_name, address, phone_no, chinese_name, malay_name, bank_name, bank_owner_name,
                      bank_account_number,
                      pic, modified_filename, username, ))

    if(response["success"]):
        return jsonify({"msg": "{} updated successfully".format(username), "success": response["success"]})
    else:
        return jsonify({"msg": response["msg"], "success": response["success"]})


@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username", None)
        if (username == None):
            return jsonify({"msg": "username missing", "success": False})
    except:
        return jsonify({"msg": "username missing", "success": False})

    try:
        password = request.json.get("password", None)
        if (password == None):
            return jsonify({"msg": "password missing", "success": False})
    except:
        return jsonify({"msg": "password missing", "success": False})

    if(username == "admin" and password == "admin"):
        access_token = create_access_token(identity=username)
        return jsonify({"msg": "Login Successfully", "role": "admin", "access_token": access_token})

    response = select_all_data("select * from team")
    if(not response["success"]):
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})
    for row in response["data"]:
        if username == row[1] and password == row[2]:
            access_token = create_access_token(identity=username)
            return jsonify({"msg": "Login Successfully", "role": "team", "access_token": access_token})

    response = select_all_data("select * from volunteer")
    if (not response["success"]):
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})
    for row in response["data"]:
        if username == row[1] and password == row[2]:
            access_token = create_access_token(identity=username)
            return jsonify({"msg": "Login Successfully", "role": "volunteer", "access_token": access_token})

    return jsonify({"msg": "Invalid username or password"}), 401


@app.route("/team/<username>", methods=["GET"])
#@jwt_required()
def team_retrieve_info(username):
    response = select_one_data("SELECT * FROM team WHERE username=?", (username,))
    if(response["success"]):
        if(response["data"] == None):
            return jsonify({"msg": "Team Not Exist", "success": False})
        js = {
            "username": username,
            "english_name": response["data"][3],
            "address": response["data"][4],
            "phone_no": response["data"][5],
            "chinese_name": response["data"][7],
            "malay_name": response["data"][8],
            "team_ssm_id": response["data"][9],
            "bank_name": response["data"][10],
            "bank_owner_name": response["data"][11],
            "bank_account_number": response["data"][12],
            "pic": response["data"][13],
            "password": response["data"][2],
        }
        return jsonify({"data": js, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/volunteer/<username>", methods=["GET"])
#@jwt_required()
def volunteer_retrieve_info(username):
    response = select_one_data("SELECT * FROM volunteer WHERE username=?", (username,))
    if(response["success"]):
        if(response["data"] == None):
            return jsonify({"msg": "Volunteer Not Exist", "success": False})
        js = {
            "username": username,
            "english_name": response["data"][3],
            "address": response["data"][4],
            "phone_no": response["data"][5],
            "ic": response["data"][6],
            "team": response["data"][7],
            "password": response["data"][2]
        }
        return jsonify({"data": js, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/user-list", methods=["GET"])
#@jwt_required()
def user_lst():
    main_list=[]
    response_team = select_all_data("SELECT * FROM team")
    if(response_team["success"]):
        if(response_team["data"] != None):
            for team in response_team["data"]:
                response_volunteer = select_all_data("SELECT * FROM volunteer WHERE team=?", (team[1],))
                print("LOG", response_volunteer)
                if(response_volunteer["success"]):
                    json = {
                        "username": team[1],
                        "password": team[2],
                        "english_name": team[3],
                        "address": team[4],
                        "phone_no": team[5],
                        "volunteer": []
                    }
                    if (response_volunteer["data"] != None):
                        for volunteer in response_volunteer["data"]:
                            js = {
                                "username": volunteer[1],
                                "password": volunteer[2],
                                "english_name": volunteer[3],
                                "address": volunteer[4],
                                "phone_no": volunteer[5],
                                "ic": volunteer[6]
                            }
                            json["volunteer"].append(js)
                        main_list.append(json)
                    else:
                        main_list.append(json)
                else:
                    return jsonify({"msg": "Database Error", "error_msg": response_volunteer["error_msg"], "success": False})
            return jsonify({"msg": "Data Retrieve Successfully", "data": main_list, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response_team["error_msg"], "success": False})


@app.route("/donation-list/volunteer", methods=["GET"])
#@jwt_required()
def volunteer_donation_list():
    main_list = []
    response = select_all_data("SELECT * FROM volunteer")
    if(response["success"]):
        if(response["data"] != None):
            volunteer_list = []
            for volunteer in response["data"]:
                volunteer_list.append(volunteer[1])

            sql = ""
            for vol in volunteer_list:
                sql += f" username='{vol}' OR "
            response = select_all_data(
                f"SELECT * FROM report WHERE {sql[1:-3]}")

            if(response["success"]):
                if(response["data"] != None):
                    for details in response["data"]:
                        js = {
                            "id": details[0],
                            "datetime": details[1],
                            "customer_name": details[2],
                            "amount": details[3],
                            "description": f"{'Cash, ' if details[10] == 1 else ''}{'Medicine, ' if details[11] == 1 else ''}{'Coffin' if details[12] == 1 else ''}",
                            "username": details[4]
                        }
                        main_list.append(js)
                    return jsonify({"msg": "Data Retrieve Successfully", "data": main_list, "success": True})
                else:
                    return jsonify({"msg": "Data Retrieve Successfully", "data": [], "success": True})
            else:
                return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/donation-list/team", methods=["GET"])
#@jwt_required()
def team_donation_list():
    main_list = []
    response = select_all_data("SELECT * FROM team")
    if(response["success"]):
        if(response["data"] != None):
            team_list = []
            for team in response["data"]:
                team_list.append(team[1])

            sql = ""
            for vol in team_list:
                sql += f" username='{vol}' OR team='{vol}' OR "
            response = select_all_data(
                f"SELECT * FROM report WHERE {sql[1:-3]}")

            if(response["success"]):
                if(response["data"] != None):
                    for details in response["data"]:
                        js = {
                            "id": details[0],
                            "datetime": details[1],
                            "customer_name": details[2],
                            "amount": details[3],
                            "description": f"{'Cash, ' if details[10] == 1 else ''}{'Medicine, ' if details[11] == 1 else ''}{'Coffin' if details[12] == 1 else ''}",
                            "username": details[4],
                            "team": details[15]
                        }
                        main_list.append(js)
                    return jsonify({"msg": "Data Retrieve Successfully", "data": main_list, "success": True})
                else:
                    return jsonify({"msg": "Data Retrieve Successfully", "data": [], "success": True})
            else:
                return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})

@app.route("/donation-list", methods=["GET"])
#@jwt_required()
def donation_list():
    main_list = []
    response = select_all_data("SELECT * FROM report")
    print(response)
    if(response["success"]):
        if(response["data"] == None):
            return jsonify({"data": [], "success": True})
        for details in response["data"]:
            js = {
                "id": details[0],
                "datetime": details[1],
                "customer_name": details[2],
                "amount": details[3],
                "description": f"{'Cash, ' if details[10] == 1 else ''}{'Medicine, ' if details[11] == 1 else ''}{'Coffin' if details[12] == 1 else ''}",
                "username": details[4],
                "team": details[15]
            }
            main_list.append(js)
        return jsonify({"data": main_list, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})

@app.route('/certificate/<string:username>', methods=["GET"])
def get_certificate_details(username):
    res = select_one_data("SELECT * FROM team JOIN volunteer ON volunteer.team=team.username WHERE volunteer.username=?", (username,))
    if(res["success"]):
        if(res["data"] is not None):
            start_date = date.today() + relativedelta(months=-2)
            end_date = date.today() + relativedelta(months=+2)
            js = {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "team_username": res["data"][1],
                "team_pic": res["data"][13],
                "team_chinese_name": res["data"][7],
                "team_english_name": res["data"][3],
                "team_malay_name": res["data"][8],
                "team_contact_number": res["data"][5],
                "team_address": res["data"][4],
                "volunteer_username": res["data"][15],
                "volunteer_english_name": res["data"][17],
                "volunteer_ic": res["data"][20],
            }
            return jsonify({"data": js, "success": True })
        else:
            return jsonify({"msg": "Invalid Volunteeer Username", "success": False})

@app.route('/icon/team/<string:username>', methods=["GET"])
def download_team_icon(username):
    res = select_one_data("SELECT * FROM team WHERE username=?", (username,))
    if(res["success"]):
        if(res["data"] != None):
            filename = res["data"][6]
        else:
            return jsonify({"msg": "invalid username", "success": False})
    return send_from_directory(LOGO_ROOT, filename, as_attachment=False)

@app.route('/icon/team/main', methods=["GET"])
def download_team_icon_main():
    return send_from_directory(LOGO_ROOT, 'main_white.png', as_attachment=False)

@app.route('/icon/volunteer/<string:username>', methods=["GET"])
def download_volunteer_icon(username):
    res = select_one_data("SELECT * FROM volunteer WHERE username=?", (username,))
    if(res["success"]):
        if(res["data"] != None):
            filename = res["data"][8]
        else:
            return jsonify({"msg": "invalid username", "success": False})
    return send_from_directory(LOGO_ROOT, filename, as_attachment=False)

@app.route("/health", methods=["GET"])
#@jwt_required()
def test():
    return "Connection Established!"


@app.route("/volunteer/delete", methods=["POST"])
def delete_volunteer():
    username = request.json.get("username", None)
    res = delete_data("DELETE FROM volunteer WHERE username=?", (username,))
    if (res["success"]):
        return jsonify({"msg": "Volunteer Deleted", "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": res["error_msg"], "success": False})


@app.route("/team/delete", methods=["POST"])
def delete_team():
    username = request.json.get("username", None)
    res = delete_data("DELETE FROM team WHERE username=?", (username,))
    if (res["success"]):
        return jsonify({"msg": "Team Deleted", "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": res["error_msg"], "success": False})


@app.route("/report/volunteer", methods=["POST"])
def report_volunteer():
    username = request.json.get("username", None)
    before_date = request.json.get("before_date", None)
    after_date = request.json.get("after_date", None)
    response = select_all_data("SELECT * FROM report WHERE username=? AND datetime BETWEEN ? AND ?", (username,after_date,before_date))
    if (response["success"]):
        data_to_return = {}
        data_to_return["id"] = 1
        data_to_return["username"] = username
        data_to_return["amount"] = 0
        data_to_return["start"] = after_date
        data_to_return["end"] = before_date
        if (response["data"] == None):
            return jsonify({"data": data_to_return, "success": True})
        for details in response["data"]:
            data_to_return["amount"] += float(details[3])
        return jsonify({"data": data_to_return, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/report/team", methods=["POST"])
def report_team():
    username = request.json.get("username", None)
    before_date = request.json.get("before_date", None)
    after_date = request.json.get("after_date", None)
    response = select_all_data("SELECT * FROM report WHERE username=? AND datetime BETWEEN ? AND ?", (username,after_date,before_date))
    if (response["success"]):
        data_to_return = {}
        data_to_return["username"] = username
        data_to_return["start"] = after_date
        data_to_return["end"] = before_date
        data_to_return["amount"] = 0
        if (response["data"] == None):
            return jsonify({"data": data_to_return, "success": True})
        for details in response["data"]:
            data_to_return["amount"] += float(details[3])
        return jsonify({"data": data_to_return, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/user/list", methods=["GET"])
#@jwt_required()
def list_user():
    data_to_return = []
    response = select_all_data("SELECT * FROM volunteer")
    if (response["success"]):
        if (response["data"] != None):
            for details in response["data"]:
                data_to_return.append({
                    "username": details[1],
                })
            return jsonify({"data": data_to_return, "success": True})
        else:
            return jsonify({"data": data_to_return, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


@app.route("/team/list", methods=["GET"])
#@jwt_required()
def list_team():
    data_to_return = []
    response = select_all_data("SELECT * FROM team")
    if (response["success"]):
        if (response["data"] != None):
            for details in response["data"]:
                data_to_return.append({
                    "username": details[1],
                })
            return jsonify({"data": data_to_return, "success": True})
        else:
            return jsonify({"data": data_to_return, "success": True})
    else:
        return jsonify({"msg": "Database Error", "error_msg": response["error_msg"], "success": False})


if __name__ == "__main__":
    app.run(debug=True)