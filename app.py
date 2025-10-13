import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Split name ASUS", layout="wide")
st.title("🧩 Split name ASUS")

st.markdown("""
Input **tên hóa đơn ASUS** (1 product each row),    
""")

input_text = st.text_area("Dán danh sách tên hóa đơn tại đây:", height=200, placeholder="Mỗi dòng là 1 tên hóa đơn...")

# --- HÀM XỬ LÝ CHÍNH
def extract_short_name(name: str) -> str:
    # Bỏ phần trước ASUS
    name = re.split(r'\bASUS\b', name, flags=re.IGNORECASE)
    if len(name) < 2:
        return ""
    part = name[1].strip()

    # Tách thành các cụm theo "/"
    segments = re.split(r'/', part)
    result = []
    last_storage_index = -1

    # Xác định vị trí cuối cùng có SSD/HDD
    for i, seg in enumerate(segments):
        if re.search(r'(SSD|HDD)', seg, re.IGNORECASE):
            last_storage_index = i

    if last_storage_index != -1:
        # Lấy đến cụm chứa SSD/HDD cuối cùng
        result = segments[:last_storage_index + 1]
    else:
        # Không có SSD/HDD -> lấy đến RAM
        for i, seg in enumerate(segments):
            result.append(seg)
            if re.search(r'\d{1,2}\s?(GB|GD)', seg, re.IGNORECASE):
                break

    short_name = " ".join(result)
    short_name = short_name.replace("/", " ").replace("  ", " ").strip()
    return short_name

def extract_long_name(name: str) -> str:
    match = re.search(r'\(.*\)', name)
    if match:
        return match.group(0)
    return ""

# --- NÚT XỬ LÝ
if st.button("🚀 START"):
    rows = [x.strip() for x in input_text.splitlines() if x.strip()]
    if not rows:
        st.warning("⚠️ Vui lòng nhập ít nhất 1 dòng dữ liệu.")
    else:
        data = []
        for row in rows:
            short = extract_short_name(row)
            long = extract_long_name(row)
            data.append({
                "Tên hóa đơn": row,
                "Tên ngắn": short,
                "Tên dài": long,
                "Short >40": len(short) > 40,
                "Long >127": len(long) > 127
            })

        df = pd.DataFrame(data)[["Tên hóa đơn", "Tên ngắn", "Tên dài"]]

        # --- Highlight ô vượt giới hạn (vàng + chữ đen)
        def highlight_over(val, limit):
            if len(str(val)) > limit:
                return "background-color: #fff176; color: black;"
            return ""

        styled = df.style.applymap(lambda v: highlight_over(v, 40), subset=["Tên ngắn"]) \
                         .applymap(lambda v: highlight_over(v, 127), subset=["Tên dài"])

        st.subheader("📊 Result")
        st.dataframe(styled, use_container_width=True)
