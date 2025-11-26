import streamlit as st
import json
import tiktoken

# ============================
# الإعدادات
# ============================
MODEL_NAME = "gpt-4o-mini"
PRICE_PER_TOKEN = 0.0000005  # سعر التوكين بالريال

enc = tiktoken.encoding_for_model(MODEL_NAME)

# حساب التوكينات
def count_tokens(text):
    try:
        return len(enc.encode(text))
    except:
        return len(text.split())


# ============================
# واجهة Streamlit
# ============================
st.set_page_config(page_title="صفحة سليمان لحساب التطبيقات  ", layout="wide")

st.title(" حاسبة التوكينات والتكلفة لمحادثات شات جي بي تي ")
st.write("ارفع ملف JSON المصدّر من شات جي بي تي، وسيتم حساب عدد التوكينات والتكلفة.")

uploaded_file = st.file_uploader(" ارفع ملف المحادثة (JSON)", type=["json"])

if uploaded_file is not None:

    try:
        data = json.load(uploaded_file)
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        st.stop()

    # ملف محادثة شات جي بي تي يكون قائمة -> نأخذ أول عنصر
    conversation = data[0] if isinstance(data, list) else data

    mapping = conversation.get("mapping", {})

    total_tokens = 0
    total_cost = 0
    message_list = []

    # ============================
    # قراءة كل الرسائل بأمان
    # ============================
    for msg_id, msg in mapping.items():

        # في بعض السجلات، message = None → نتجاوزها
        message = msg.get("message")
        if not isinstance(message, dict):
            continue

        author = message.get("author", {}).get("role", "")

        content = message.get("content", {})
        parts = content.get("parts", [])

        if not isinstance(parts, list):
            continue

        # قراءة كل جزء من الرسالة
        for part in parts:

            if isinstance(part, str) and part.strip():

                tokens = count_tokens(part)
                cost = tokens * PRICE_PER_TOKEN

                total_tokens += tokens
                total_cost += cost

                message_list.append({
                    "role": author,
                    "text": part,
                    "tokens": tokens,
                    "cost": cost
                })

    st.success("✔ تم تحليل المحادثة بنجاح")

    # ============================
    # عرض الإجمالي
    # ============================
    st.subheader("📌 الإجمالي")
    st.write(f"**إجمالي التوكينات:** {total_tokens}")
    st.write(f"**إجمالي التكلفة:** {total_cost:.6f} ريال")

    st.markdown("---")

    # ============================
    # عرض التفاصيل
    # ============================
    st.subheader("📄 تفاصيل كل رسالة")

    for m in message_list:
        with st.expander(f"{m['role']} — {m['tokens']} tokens"):
            st.write(m["text"])
            st.write(f"**التكلفة:** {m['cost']:.6f} ريال")
