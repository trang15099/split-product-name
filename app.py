import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Tool tách tên ngắn & dài ASUS", layout="wide")
st.title("🧩 Tool tách Tên ngắn & Tên dài từ Tên hóa đơn ASUS")

st.markdown("""
Nhập nhiều dòng **tên hóa đơn ASUS** (mỗi dòng 1 sản phẩm),  
sau đó bấm **“Xử lý dữ liệu”** để tạo *Tên ngắn* (≤40 ký tự) và *Tên dài* (≤127 ký tự).  
""")

# --- Nhập dữ liệu
input_text = st.text_area("Dán danh sách tên hóa đơn tại đây:", height=200, placeholder="Mỗi dòng là 1 tên hóa đơn...")

# --- HÀM XỬ LÝ CHÍNH
def extract_short_name(name: str) -> str:
    # Bỏ phần trước ASUS
    name = re.split(r'\bASUS\b', name, flags=re.IGNORECASE)
    if len(name) < 2:
        return ""
    part = name[1].strip()

    # Lấy model (cụm đầu tiên sau ASUS)
    tokens = re.split(r'[/\s]+', part)
    model = tokens[0]

    # Lấy cụm từ model đến hết tất cả cụm có SSD/HDD
    segments = re.split(r'/', part)
    take_segments = []
    found_ssd = False
    for seg in segments:
        take_segments.append(seg)
        if re.search(r'SSD|HDD', seg, re.IGNORECASE):
            found_ssd = True
    if not found_ssd:
        # Nếu không có SSD/HDD → dừng sau CPU + RAM
        temp = []
        for seg in segments:
            temp.append(seg)
            if re.search(r'\d{1,2}GB', seg, re.IGNORECASE):
                break
        take_segments = temp

    short_name = " ".join(take_segments)
    short_name = short_name.replace("/", " ").replace("  ", " ").strip()
    return short_name

def extract_long_name(name: str) -> str:
    match = re.search(r'\(.*\)', name)
    if match:
        return match.group(0)
    return ""

# --- NÚT XỬ LÝ
if st.button("🚀 Xử lý dữ liệu"):
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

        # --- tô màu vàng khi vượt giới hạn
        def highlight_exceed(val, limit):
            return "background-color: #fff2b3" if len(str(val)) > limit else ""

        styled = df.style.applymap(lambda v: highlight_exceed(v, 40), subset=["Tên ngắn"]) \
                         .applymap(lambda v: highlight_exceed(v, 127), subset=["Tên dài"])

        st.subheader("📊 Kết quả")
        st.dataframe(styled, use_container_width=True)

        # --- Chuẩn bị text copy cho từng cột
        short_text = "\n".join(df["Tên ngắn"].astype(str).tolist())
        long_text = "\n".join(df["Tên dài"].astype(str).tolist())

        st.markdown("### 📋 Copy nhanh cột 'Tên ngắn'")
        st.text_area("Tên ngắn", short_text, height=150)

        st.markdown("### 📋 Copy nhanh cột 'Tên dài'")
        st.text_area("Tên dài", long_text, height=150)
