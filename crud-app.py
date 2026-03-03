import streamlit as st
import gspread
import pandas as pd

# ==========================================
# 1. 建立 Google Sheets 連線
# ==========================================
@st.cache_resource
def init_connection():
credentials = dict(st.secrets[&quot;gcp_service_account&quot;])
gc = gspread.service_account_from_dict(credentials)
return gc
gc = init_connection()
# ==========================================
# 2. 開啟指定的試算表與工作表
# ==========================================
SHEET_INPUT = &quot;試算表網址&quot;
WORKSHEET_NAME = &quot;工作表1&quot;
try:
if SHEET_INPUT.startswith(&quot;http://&quot;) or SHEET_INPUT.startswith(&quot;https://&quot;):
sh = gc.open_by_url(SHEET_INPUT)
else:
sh = gc.open(SHEET_INPUT)
worksheet = sh.worksheet(WORKSHEET_NAME)
except Exception as e:
st.error(
f&quot;無法開啟試算表，請確認名稱/網址是否正確，且服務帳號 ({gc.auth.signer_email})
已被加入共用編輯者！\n錯誤訊息：{e}&quot;)
st.stop()
st.title(&quot;�� Google Sheet 讀寫測試儀表板&quot;)
# ==========================================
# 3. 讀取資料 (Read)
# ==========================================
st.header(&quot;1️⃣ 目前資料列表&quot;)
data = worksheet.get_all_records()
if data:
df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)
else:

st.divider()
# ==========================================
# ==========================================
st.header(&quot;2️⃣ 新增資料&quot;)
with st.form(&quot;add_data_form&quot;, clear_on_submit=True):

if submitted:
if col1.strip() == &quot;&quot;:
else:
worksheet.append_row([col1, col2])
st.rerun()
st.divider()

if data:

col_update, col_delete = st.columns(2)
# ==========================================
# ==========================================
with col_update:
st.header(&quot;3️⃣ 修改資料&quot;)
selected_row_update = row_options[selected_option_update]

current_data = data[selected_row_update - 2]
with st.form(&quot;update_data_form&quot;):

if update_submitted:
if new_name.strip() == &quot;&quot;:
else:

worksheet.update_cell(selected_row_update, 1, new_name)
worksheet.update_cell(selected_row_update, 2, new_qty)
st.rerun()
# ==========================================
# ==========================================
with col_delete:
st.header(&quot;4️⃣ 刪除資料&quot;)

selected_row_del = row_options[selected_option_del]
st.write(f&quot;⚠️ 即將刪除：**{selected_option_del}**&quot;)

if st.button(&quot;��️ 確認刪除這筆資料&quot;, type=&quot;primary&quot;):
worksheet.delete_rows(selected_row_del)
st.rerun()
