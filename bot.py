# ============================================================
#  استراحة البديعة — WhatsApp Bot
#  Meta Cloud API | Python Flask
# ============================================================

from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# ============================================================
#  ⚙️  الإعدادات — عدّل هذه القيم فقط
# ============================================================

ACCESS_TOKEN    = "EAAMgygHsVm8BR5Vv7GHIeZCSsRlHxKvvZAEOuiiuR4efkUSCzKIZC76yahHEoDbmO7igwc3ZB92rSmyZAjuVZCDASt2GJqZCiJxm9PkZCQ1SNq6jxwmpg2SDmWZCVDZCUhMHNmCAgZAHfYSf7EpZAjJhEFIypVt1IU5QjUO9OWi3fjm2ZB0eLDZCe69SwwZAfccW28NmAjOwWOZAeZCSHEGUGKZAdEkxkk4GRdOwdkXEmhceSdh0Mbi6oirZAey73G4Opn156Hj5KosuFVxjt5oa0XS4Hlo8UwtMsd8"
PHONE_NUMBER_ID = "1249901378202203"
VERIFY_TOKEN    = "albudayia_verify_2024"
MANAGER_PHONE   = "966554803840"

# ============================================================
#  💬  نصوص الردود
# ============================================================

MSG_WELCOME = """\
مرحباً بك في *استراحة البديعة* 🌿
المدينة المنورة - حي السكب

يمكنني الإجابة على:
• 💰 الأسعار
• 🏠 القسمين وتفاصيلهم
• 🏊 المسبح وعمقه
• 📍 الموقع
• 📋 التأمين
• 🚭 سياسة التدخين

فقط اكتب سؤالك 😊"""

MSG_PRICES = """\
💰 *أسعار استراحة البديعة*

🔹 *القسم الأول:*  1,000 ريال / الليلة
🔹 *القسم الثاني:* 1,200 ريال / الليلة

⚠️ الأسعار *غير شاملة* مبلغ التأمين والمناسبات الخاصة.

للحجز أو الاستفسار عن التواريخ المتاحة تواصل مع المسؤول مباشرةً."""

MSG_SECTIONS = """\
🏠 *أقسام استراحة البديعة*

━━━━━━━━━━━━━━━━━━
*🔹 القسم الأول — 1,000 ريال*
• صالون داخلي كبير + غرفة جلوس إضافية
• مطبخ مجهز
• جلسة خارجية
• مسبح (عمق 1 متر)
• دورتا مياه + مغاسل خارجية

━━━━━━━━━━━━━━━━━━
*🔹 القسم الثاني — 1,200 ريال*
• صالون داخلي كبير
• مطبخ مجهز
• مسبح كبير منفصل (عمق 120 – 190 سم)
• ألعاب مائية للأطفال 🎠
• غرفة جلوس مطلة على الألعاب المائية
• غرفة جلوس مطلة على الحوش
• جلسة خارجية
• دورتا مياه + مغاسل + مروش خارجي"""

MSG_POOL = """\
🏊 *تفاصيل المسابح*

🔹 *القسم الأول:*
مسبح عمقه *1 متر* — مناسب للأطفال والعائلات

🔹 *القسم الثاني:*
مسبح كبير منفصل عمقه *من 120 سم إلى 190 سم*
+ ألعاب مائية مخصصة للأطفال 🎠"""

MSG_FACILITIES = """\
🛎️ *مرافق استراحة البديعة*

*القسم الأول:*
✅ صالون داخلي كبير + غرفة جلوس إضافية
✅ مطبخ
✅ جلسة خارجية
✅ مسبح (عمق 1م)
✅ دورتا مياه + مغاسل خارجية

*القسم الثاني:*
✅ صالون داخلي كبير
✅ مطبخ
✅ مسبح كبير (عمق 120-190سم) + ألعاب مائية
✅ غرفتا جلوس (إطلالة على الألعاب والحوش)
✅ جلسة خارجية
✅ دورتا مياه + مغاسل + مروش خارجي"""

MSG_LOCATION = """\
📍 *موقع استراحة البديعة*

المدينة المنورة - حي السكب

🗺️ اضغط للخريطة:
https://maps.app.goo.gl/6rW195zy2kLWsAgc9?g_st=ic"""

MSG_INSURANCE = """\
📋 *مبلغ التأمين*

💵 المبلغ: *500 ريال*
يُدفع عند تأكيد الحجز أو عند الدخول، ويُسترد كاملاً عند الخروج.

⚠️ *يُخصم التأمين في حالة:*
• اتساخ الكنب والمفروشات
• رمي مخلفات أو أطعمة في المسبح
• حدوث كسور أو تلفيات في الممتلكات"""

MSG_SMOKING = """\
🚭 *سياسة التدخين*

❌ ممنوع التدخين والشيشة داخل الصالونات والأماكن المغلقة.
✅ مسموح في الجلسات الخارجية فقط."""

MSG_TRANSFER = """\
شكراً لتواصلك مع *استراحة البديعة* 🌿

سؤالك خارج نطاق الردود التلقائية، سيتواصل معك المسؤول قريباً إن شاء الله. 🙏"""

MSG_BOOKING = """\
📅 *الحجز*

للحجز أو الاستفسار عن التواريخ المتاحة، سيتواصل معك المسؤول قريباً إن شاء الله 🙏"""

# ============================================================
#  🧠  منطق الردود — كشف الكلمات المفتاحية
# ============================================================

def get_response(text: str) -> tuple[str, bool]:
    """
    يُعيد (نص_الرد, تحويل_للمسؤول)
    """
    t = text.strip()

    # تحية
    if re.search(r'مرحب|هلا|السلام|أهلا|هله|كيف|صباح|مساء|وش عندكم|ايش عندكم', t):
        return MSG_WELCOME, False

    # سعر / تكلفة
    if re.search(r'سعر|أسعار|بكم|كم.*ريال|ريال|تعرفة|كلفة|ثمن|ايش.*سعر|وش.*سعر|قديش|كم.*تكلف|غالي|رخيص', t):
        return MSG_PRICES, False

    # عدد الأقسام
    if re.search(r'كم.*قسم|قسم.*كم|كم أقسام|عدد.*قسم|قسمين|القسمين|كم.*قسم', t):
        return MSG_SECTIONS, False

    # مسبح / عمق
    if re.search(r'مسبح|عمق|عميق|سباحة|حمام.*سباح|pool', t):
        return MSG_POOL, False

    # ما فيها / مرافق
    if re.search(r'فيها|فيه|إيش فيه|ايش فيه|وش فيه|مرافق|محتويات|مميزات|تجهيز|شامل|يشمل|ما يوجد|ما في', t):
        return MSG_FACILITIES, False

    # موقع / عنوان
    if re.search(r'موقع|مكان|وين|أين|عنوان|خريطة|كيف.*أجي|طريق|location', t):
        return MSG_LOCATION, False

    # تأمين
    if re.search(r'تأمين|ضمان|وديعة|مبلغ.*ضمان', t):
        return MSG_INSURANCE, False

    # تدخين / شيشة
    if re.search(r'تدخين|شيشة|دخان|سيجارة|نرجيلة|تبغ', t):
        return MSG_SMOKING, False

    # حجز
    if re.search(r'حجز|أحجز|احجز|متاح|خالي|توافر|تأجير|أجار|استئجار|booking', t):
        return MSG_BOOKING, True

    # سؤال غير معروف
    return MSG_TRANSFER, True


# ============================================================
#  📤  إرسال رسالة واتساب
# ============================================================

def send_message(to: str, body: str) -> dict:
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    return r.json()


# ============================================================
#  🌐  Webhook
# ============================================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """تحقق الـ Webhook مع Meta."""
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified")
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    """استقبال الرسائل الواردة والرد عليها."""
    data = request.get_json(silent=True) or {}

    try:
        changes = data["entry"][0]["changes"][0]["value"]

        # تجاهل أحداث الحالة (status updates)
        if "messages" not in changes:
            return jsonify({"status": "ok"}), 200

        msg    = changes["messages"][0]
        sender = msg["from"]

        # تجاهل المسؤول (حتى لا يلف البوت على نفسه)
        if sender == MANAGER_PHONE:
            return jsonify({"status": "ok"}), 200

        if msg["type"] == "text":
            text = msg["text"]["body"]
        else:
            send_message(sender, "أرسل رسالة نصية وسأجيبك فوراً 😊")
            return jsonify({"status": "ok"}), 200

        # الرد التلقائي
        reply, transfer = get_response(text)
        send_message(sender, reply)

        # إشعار المسؤول إذا لزم
        if transfer:
            notif = (
                f"📩 *رسالة تحتاج ردك*\n"
                f"من: +{sender}\n"
                f"السؤال: {text}"
            )
            send_message(MANAGER_PHONE, notif)

    except (KeyError, IndexError, TypeError) as e:
        print(f"⚠️ خطأ في معالجة الرسالة: {e}")

    return jsonify({"status": "ok"}), 200


# ============================================================
#  🚀  تشغيل التطبيق
# ============================================================

if __name__ == "__main__":
    print("🤖 بوت استراحة البديعة يعمل...")
    app.run(host="0.0.0.0", port=5000, debug=False)
