import streamlit as st
import gspread
import pandas as pd

# ==========================================
# 1. 建立 Google Sheets 連線
# ==========================================
@st.cache_resource
def init_connection():
    # 從 Streamlit Secrets 讀取憑證
    credentials = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(credentials)
    return gc

gc = init_connection()

# ==========================================
# 2. 開啟指定的試算表與工作表
# ==========================================
# 💡 請在此處替換成您的試算表網址或名稱
SHEET_INPUT = "https://docs.google.com/spreadsheets/d/1EnRG4xHSh8rxdUFidLWzgowkH_f0tooy-p062u4lsDU/edit?gid=0#gid=0"
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
    st.info("目前沒有資料。")
    df = pd.DataFrame()

st.divider()

# ==========================================
# 4. 新增資料 (Create)
# ==========================================
st.header("2️⃣ 新增資料")
with st.form("add_data_form", clear_on_submit=True):
    col1 = st.text_input("項目名稱 (第一欄)")
    col2 = st.text_input("內容描述 (第二欄)")
    submitted = st.form_submit_button("確認新增")

    if submitted:
        if col1.strip() == "":
            st.error("項目名稱不能為空！")
        else:
            worksheet.append_row([col1, col2])
            st.success("資料已成功新增！")
            st.rerun()

st.divider()

# ==========================================
# 5. 修改與刪除資料 (Update & Delete)
# ==========================================
if data:
    # 建立下拉選單，行數由 2 開始 (因為第 1 行是標題)
    row_options = {f"第 {idx+2} 行: {list(row.values())[0]}": idx + 2 for idx, row in enumerate(data)}
    
    col_update, col_delete = st.columns(2)

    # --- 修改資料 ---
    with col_update:
        st.header("3️⃣ 修改資料")
        selected_option_update = st.selectbox("選擇要修改的行", options=list(row_options.keys()), key="update_select")
        selected_row_update = row_options[selected_option_update]
        
        # 獲取該行目前的內容
        current_val = data[selected_row_update - 2]
        
        with st.form("update_data_form"):
            new_name = st.text_input("新項目名稱", value=list(current_val.values())[0])
            new_qty = st.text_input("新內容描述", value=list(current_val.values())[1] if len(current_val) > 1 else "")
            update_submitted = st.form_submit_button("確認修改")

            if update_submitted:
                if new_name.strip() == "":
                    st.error("名稱不能為空！")
                else:
                    worksheet.update_cell(selected_row_update, 1, new_name)
                    worksheet.update_cell(selected_row_update, 2, new_qty)
                    st.success("更新成功！")
                    st.rerun()

    # --- 刪除資料 ---
    with col_delete:
        st.header("4️⃣ 刪除資料")
        selected_option_del = st.selectbox("選擇要刪除的行", options=list(row_options.keys()), key="delete_select")
        selected_row_del = row_options[selected_option_del]
        
        st.warning(f"⚠️ 即將刪除：**{selected_option_del}**")
        
        if st.button("🗑️ 確認刪除這筆資料", type="primary"):
            worksheet.delete_rows(selected_row_del)
            st.success("資料已刪除！")
            st.rerun()
