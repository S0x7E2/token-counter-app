import streamlit as st
import json

# ============================
# إعداد السعر (ريال سعودي)
# ============================
PRICE_PER_TOKEN = 0.0000005  # سعر التوكين

# ============================
# دالة حساب التوكينات (بديل tiktoken)
# ============================
def count_tokens(text):
    if not text:
        return 0
    return int(len(text.split()) * 1.3)

# ============================
# واجهة Streamlit
# ============================
st.set_page_config(page_title="Token Counter", layout="wide")

st.title("حاسبة التوكينات والتكلفة لمحادثات ChatGPT")
st.write("ارفع ملف JSON المصدّر من شات جي بي تي لحساب عدد التوكينات والتكلفة.")

uploaded_file = st.file_uploader("ارفع ملف JSON", type=["json"])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        st.stop()

    # ملف تصدير شات جي بي تي يكون عبارة عن قائمة
    conversation = data[0] if isinstance(data, list) else data
    mapping = conversation.get("mapping", {})

    total_tokens = 0
    total_cost = 0
    messages_list = []

    for msg_id, msg in mapping.items():

        message = msg.get("message")
        if not isinstance(message, dict):
            continue

        role = message.get("author", {}).get("role", "")

        content = message.get("content", {})
        parts = content.get("parts", [])

        if not isinstance(parts, list):
            continue

        for part in parts:
            if isinstance(part, str) and part.strip():

                tokens = count_tokens(part)
                cost = tokens * PRICE_PER_TOKEN

                total_tokens += tokens
                total_cost += cost

                messages_list.append({
                    "role": role,
                    "text": part,
                    "tokens": tokens,
                    "cost": cost
                })

    st.subheader("الإجمالي")
    st.write(f"إجمالي التوكينات: {total_tokens}")
    st.write(f"التكلفة: {total_cost:.6f} ريال")

    st.markdown("---")

    st.subheader("تفاصيل الرسائل")

    for m in messages_list:
        with st.expander(f"{m['role']} — {m['tokens']} tokens"):
            st.write(m["text"])
            st.write(f"التكلفة: {m['cost']:.6f} ريال")
