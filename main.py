from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Webhook aktif dan siap menerima POST dari Dialogflow!"


@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json()
    user_query = req.get("queryResult").get("queryText")  # misalnya: "2 + 4"

    try:
        result = eval(user_query)
        response_text = f"Hasilnya adalah {result}"
    except:
        response_text = "Maaf, saya tidak bisa menghitung soal itu."

    return jsonify({"fulfillmentText": response_text})


app.run(host='0.0.0.0', port=3000)
