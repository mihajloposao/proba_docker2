import os
from flask import Flask, jsonify, request
from qr_obrada_smestanje import web_scraping,csv_u_bazu,proba
from datetime import datetime
from rutine_kupovina import lista_preporucenih

app = Flask(__name__)

@app.route("/qr",methods=["POST"])
def qr():
    povratna = request.json
    qr = povratna.get("qr")
    web_scraping(qr)
    return {'rezultat': "USPEH"}

@app.route("/datum",methods=["GET"])
def datum():
    now = datetime.now()
    now = now.strftime("%d/%m/%Y")
    return{'datum':now}

@app.route("/lista_preporuka",methods=["GET"])
def preporuke():
    return{'lista':lista_preporucenih()}

@app.route("/",methods=["GET"])
def home():
    return "RADI"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
