from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# 🔟 Daftar 10 soal
soal_list = [
    {"soal": "Berapakah hasil dari 2 + 3?", "opsi": {"A": "4", "B": "5", "C": "6"}, "jawaban": "B"},
    {"soal": "Berapakah hasil dari 7 - 4?", "opsi": {"A": "3", "B": "2", "C": "5"}, "jawaban": "A"},
    {"soal": "Berapakah hasil dari 6 x 2?", "opsi": {"A": "10", "B": "12", "C": "14"}, "jawaban": "B"},
    {"soal": "Berapakah hasil dari 15 ÷ 3?", "opsi": {"A": "5", "B": "3", "C": "6"}, "jawaban": "A"},
    {"soal": "Berapakah hasil dari 9 + 6?", "opsi": {"A": "15", "B": "16", "C": "14"}, "jawaban": "A"},
    {"soal": "Berapakah hasil dari 8 - 5?", "opsi": {"A": "2", "B": "3", "C": "4"}, "jawaban": "B"},
    {"soal": "Berapakah hasil dari 3 x 4?", "opsi": {"A": "12", "B": "10", "C": "14"}, "jawaban": "A"},
    {"soal": "Berapakah hasil dari 18 ÷ 6?", "opsi": {"A": "2", "B": "3", "C": "4"}, "jawaban": "B"},
    {"soal": "Berapakah hasil dari 11 + 7?", "opsi": {"A": "18", "B": "17", "C": "19"}, "jawaban": "A"},
    {"soal": "Berapakah hasil dari 10 - 8?", "opsi": {"A": "1", "B": "2", "C": "3"}, "jawaban": "B"},
]

session_data = {}
webhook_url = "https://script.google.com/macros/s/AKfycbzzbAEZHPZr3jhCEdXAG2JdraO-kUsq7FIrkUcsO2M/dev"

@app.route("/", methods=["GET"])
def index():
    return "Webhook kuis aktif!"

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json()
    session = req.get("session", "unknown_session")
    user_input = req.get("queryResult", {}).get("queryText", "").strip()

    if session not in session_data:
        session_data[session] = {"index": 0, "skor": 0}
        soal = soal_list[0]
        text = format_soal(soal)
        return jsonify({"fulfillmentText": f"Selamat datang! Mari mulai kuis.\n{text}"})

    data = session_data[session]
    idx = data["index"]

    if idx >= len(soal_list):
        return jsonify({"fulfillmentText": "Kuis sudah selesai. Ketik 'mulai' untuk mengulang."})

    jawaban_user = user_input.upper().replace("SAYA PILIH ", "").strip()
    soal = soal_list[idx]
    jawaban_benar = soal["jawaban"]

    if jawaban_user in ["A", "B", "C"]:
        if jawaban_user == jawaban_benar:
            data["skor"] += 1
            response = "Benar!"
        else:
            response = f"Salah. Jawaban yang benar adalah {jawaban_benar}."

        data["index"] += 1

        if data["index"] < len(soal_list):
            soal_selanjutnya = soal_list[data["index"]]
            response += "\n\n" + format_soal(soal_selanjutnya)
        else:
            # Hitung skor dan nilai akhir
            skor = data["skor"]
            total = len(soal_list)
            nilai = round((skor / total) * 100)

            if nilai == 100:
                feedback = "Luar biasa! Semua jawaban benar 🎉"
            elif nilai >= 75:
                feedback = "Bagus sekali! 👍"
            elif nilai >= 50:
                feedback = "Lumayan! Tetap semangat 💪"
            else:
                feedback = "Perlu belajar lebih giat lagi 📘"

            # Kirim data ke Google Sheet
            payload = {
                "nama": "Anonim",
                "session": session,
                "skor": skor,
                "nilai": nilai,
                "feedback": feedback
            }

            try:
                res = requests.post(webhook_url, json=payload)
                print("✅ Data terkirim ke Google Sheets:", res.status_code)
            except Exception as e:
                print("❌ Gagal kirim ke Google Sheets:", e)

            # Tambahkan hasil akhir ke response
            response += f"\n\nKuis selesai! Skor akhir Anda: {nilai} dari 100\n{feedback}"

            # Bersihkan session
            del session_data[session]

        return jsonify({"fulfillmentText": response})
    else:
        return jsonify({"fulfillmentText": "Silakan jawab dengan A, B, atau C (misalnya: Saya pilih A)."})

def format_soal(soal):
    return f"{soal['soal']}\nA. {soal['opsi']['A']}\nB. {soal['opsi']['B']}\nC. {soal['opsi']['C']}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server berjalan di port {port}")
    app.run(host="0.0.0.0", port=port)
