from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Webhook aktif dan siap menerima POST dari Dialogflow!"

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json()
    user_query = req.get("queryResult", {}).get("queryText", "")

    # Normalisasi simbol matematika
    user_query = user_query.lower()  # ubah jadi huruf kecil (biar aman kalau ketik 'X')
    user_query = user_query.replace("×", "*").replace("x", "*")  # Perkalian
    user_query = user_query.replace("÷", "/").replace(":", "/")  # Pembagian
    user_query = user_query.replace("^", "**")  # Pangkat

    # Tambahan: hapus spasi di antara angka dan operator agar lebih aman
    user_query = re.sub(r'\s+', '', user_query)

    try:
        result = eval(user_query)
        response_text = f"Hasilnya adalah {round(result, 2)}"
    except ZeroDivisionError:
        response_text = "Maaf, tidak bisa membagi dengan nol."
    except:
        response_text = "Maaf, saya tidak bisa menghitung soal itu."

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
