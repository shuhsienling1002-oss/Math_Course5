import streamlit as st
import random
from fractions import Fraction
import uuid

# ==========================================
# 1. 設定與樣式 (積木風格)
# ==========================================
st.set_page_config(page_title="Math Collapse: 運算消消樂", page_icon="🧱", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #2b2d42; color: white; }
    
    /* 算式容器 */
    .equation-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        padding: 40px 20px;
        background: #8d99ae;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
        min-height: 150px;
        flex-wrap: wrap;
    }

    /* 數字積木 (靜態) */
    .num-block {
        background: #edf2f4;
        color: #2b2d42;
        padding: 15px 20px;
        border-radius: 12px;
        font-family: 'Courier New', monospace;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 5px 0 #adb5bd;
        min-width: 80px;
        text-align: center;
    }

    /* 運算符按鈕 (互動熱點) */
    div.stButton > button {
        width: 60px !important;
        height: 60px !important;
        border-radius: 15px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        background-color: #ef233c !important; /* 紅色 */
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 0 #d90429 !important;
        transition: all 0.1s;
    }
    div.stButton > button:hover {
        transform: translateY(2px);
        box-shadow: 0 3px 0 #d90429 !important;
    }
    div.stButton > button:active {
        transform: translateY(5px);
        box-shadow: none !important;
    }

    /* 步驟紀錄 */
    .step-log {
        background: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 8px;
        margin-top: 20px;
        font-family: monospace;
        color: #89f7fe;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 邏輯核心
# ==========================================

def format_fraction(val):
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"

def generate_level(difficulty=1):
    """生成算式鏈"""
    dens = [2, 3, 4, 5]
    ops = ['+', '-', '×', '÷']
    
    # 難度決定長度
    length = 3 if difficulty == 1 else 5 # 3個數 or 5個數
    
    expr = []
    # 數
    expr.append(Fraction(random.choice([1,2,3]), random.choice(dens)))
    
    for _ in range(length - 1):
        # 符
        expr.append(random.choice(ops))
        # 數
        expr.append(Fraction(random.choice([1,2,3]), random.choice(dens)))
        
    return expr

# 初始化
if 'blocks' not in st.session_state:
    st.session_state.blocks = generate_level(1) # Level 1
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message' not in st.session_state:
    st.session_state.message = "點擊運算符號來消除積木！(記得先乘除後加減)"

# ==========================================
# 3. 互動處理
# ==========================================

def handle_click(index):
    current_blocks = st.session_state.blocks
    clicked_op = current_blocks[index]
    
    # 1. 檢查優先級 (先乘除後加減)
    has_high = any(x in ['×', '÷'] for x in current_blocks if isinstance(x, str))
    is_high = clicked_op in ['×', '÷']
    
    if has_high and not is_high:
        st.toast("🚫 順序錯誤！還有乘除號 (× ÷) 沒算喔！", icon="⚠️")
        return

    # 2. 執行計算 (消消樂)
    left = current_blocks[index-1]
    right = current_blocks[index+1]
    
    res = 0
    if clicked_op == '+': res = left + right
    elif clicked_op == '-': res = left - right
    elif clicked_op == '×': res = left * right
    elif clicked_op == '÷': res = left / right if right != 0 else left
    
    # 3. 記錄步驟 (讓學生看懂發生了什麼)
    log_text = f"{format_fraction(left)} {clicked_op} {format_fraction(right)} = {format_fraction(res)}"
    st.session_state.logs.append(log_text)
    
    # 4. 更新積木鏈
    new_blocks = current_blocks[:index-1] + [res] + current_blocks[index+2:]
    st.session_state.blocks = new_blocks
    
    if len(new_blocks) == 1:
        st.balloons()
        st.session_state.message = f"🎉 消除完成！最終答案：{format_fraction(res)}"
    else:
        st.session_state.message = "✅ 計算正確！積木合併了，繼續下一步..."

def restart(difficulty):
    st.session_state.blocks = generate_level(difficulty)
    st.session_state.logs = []
    st.session_state.message = "新局開始！"

# ==========================================
# 4. 畫面渲染
# ==========================================

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🧱 運算消消樂")
    st.caption(st.session_state.message)
with col2:
    diff = st.selectbox("難度", [1, 2], format_func=lambda x: "簡單 (3數)" if x==1 else "困難 (5數)")
    if st.button("🔄 重來"):
        restart(diff)
        st.rerun()

# --- 核心遊戲區 ---
blocks = st.session_state.blocks

if len(blocks) == 1:
    # 勝利畫面
    st.success(f"🏆 最終結果：{format_fraction(blocks[0])}")
    st.markdown("### 📝 計算回顧：")
    for log in st.session_state.logs:
        st.code(log)
    
    if st.button("挑戰下一關 ➡️", type="primary"):
        restart(diff)
        st.rerun()
else:
    # 遊戲畫面：動態排列
    st.markdown('<div class="equation-container">', unsafe_allow_html=True)
    
    # 使用 columns 排版
    cols = st.columns(len(blocks))
    
    for i, item in enumerate(blocks):
        with cols[i]:
            if isinstance(item, Fraction):
                # 數字積木 (白色)
                st.markdown(f'<div class="num-block">{format_fraction(item)}</div>', unsafe_allow_html=True)
            else:
                # 符號按鈕 (紅色)
                # key 必須唯一，所以加上 uuid
                if st.button(item, key=f"btn_{i}_{uuid.uuid4()}"):
                    handle_click(i)
                    st.rerun()
                    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 顯示步驟紀錄 (即時回饋)
    if st.session_state.logs:
        st.markdown("**📜 已完成步驟：**")
        for log in st.session_state.logs:
            st.markdown(f'<div style="color:#aaa; font-family:monospace;">✔️ {log}</div>', unsafe_allow_html=True)
