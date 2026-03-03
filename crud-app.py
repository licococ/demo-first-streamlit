import streamlit as st
import gspread
import pandas as pd

# ==========================================
# 1. 建立 Google Sheets 連線
# ==========================================
@st.cache_resource
def init_connection():
    # 這裡對應您在 .streamlit/secrets.toml 設定的內容
    credentials = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(credentials)
    return gc

gc = init_connection()

# ==========================================
# 2. 開啟指定的試算表與工作表
# ==========================================
# 請將這裡替換成您的試算表網址或名稱
SHEET_INPUT = "試算表網址" 
WORKSHEET_NAME = "工作表1"

try:
    if SHEET_INPUT.startswith("http://") or SHEET_INPUT.startswith("https://"):
        sh = gc.open_by_url(SHEET_INPUT)
    else:
        sh = gc.open(SHEET_INPUT)
    worksheet = sh.worksheet(WORKSHEET_NAME)
except Exception as e:
    st.error(
        f"無法開啟試算表，請確認名稱/網址是否正確，且服務帳號 ({gc.auth.signer_email}) "
        f"已被加入共用編輯者！\n錯誤訊息：{e}")
    st.stop()

st.title("📊 Google Sheet 讀寫測試儀表板")

# ==========================================
# 3. 讀取資料 (Read)
# ==========================================
st.header("1️⃣ 目前資料列表")
data = worksheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前工作表內沒有資料。")

st.divider()

# ==========================================
# 4. 新增資料 (Create)
# ==========================================
st.header("2️⃣ 新增資料")
with st.form("add_data_form", clear_on_submit=True):
    col1 = st.text_input("項目名稱")
    col2 = st.number_input("數量", min_value=0, step=1)
    submitted = st.form_submit_button("確認新增")

    if submitted:
        if col1.strip() == "":
            st.warning("項目名稱不能為空！")
        else:
            worksheet.append_row([col1, col2])
            st.success("資料已成功新增！")
            st.rerun()

st.divider()

# ==========================================
# 5. 修改與刪除資料 (Update & Delete)
# ==========================================
if data:
    # 建立選項清單（以便對應到正確的行數，Excel/Google Sheet 行數通常從 2 開始，因為 1 是標題）
    row_options = {f"{row['項目名稱']} (第{idx+2}行)": idx + 2 for idx, row in enumerate(data)}
    
    col_update, col_delete = st.columns(2)

    # --- 修改資料 ---
    with col_update:
        st.header("3️⃣ 修改資料")
        selected_option_update = st.selectbox("選擇要修改的項目", options=list(row_options.keys()), key="update_box")
        selected_row_update = row_options[selected_option
