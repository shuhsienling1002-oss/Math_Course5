import streamlit as st
import random
import time
from fractions import Fraction
import uuid

# ==========================================
# 1. 介面設計與 CSS (UI/UX)
# ==========================================
st.set_page_config(page_title="Math Fusion", page_icon="🧩", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #fff; }
    
    /* 遊戲主舞台 */
    .game-stage {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 10px;
        padding: 40px 20px;
        background: #2b2d42;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin: 20px 0;
        flex-wrap: wrap; /* 防止手機版破版 */
    }

    /* 數字卡片 */
    .num-card {
        background: linear-gradient(135deg, #89f7fe, #66a6ff);
        color: #000;
        padding: 15px 25px;
        border-radius: 12px;
        font-family: 'Courier New', monospace;
        font-size: 1.8rem;
        font-weight: 900;
        box-shadow: 0 4px 0 #0056b3; /* 立體感 */
        min-width: 80px;
        text-align: center;
        border: 2px solid #fff;
    }

    /* 運算符按鈕 (Streamlit Button 改裝) */
    div.stButton > button {
        background-color: #ff0055 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border: 3px solid white !important;
        box-shadow: 0 0 15px #ff0055 !important;
        transition: transform 0.1s !important;
        margin: 0 !important;
    }
    div.stButton > button:hover {
        transform: scale(1.1);
        background-color: #ff3377 !important;
    }
    div.stButton > button:active {
        transform: scale(0.95);
    }
    
    /* 提示訊息 */
    .hint-box {
        text-align: center;
        font-size: 1.2rem;
        color: #ffd700;
        margin-bottom: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 邏輯核心
# ==========================================

def format_fraction(val):
    """美化分數顯示"""
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"

def generate_puzzle(level=1):
    """生成保證合法的算式"""
    denominators = [2, 3, 4, 5]
    ops = ['+', '-', '×', '÷']
    
    # 強制生成：數字 - 符號 - 數字 - 符號 - 數字
    # 例如： 1/2 + 2/3 × 4/5
    length = 3 # 3個數字，2個符號
    
    expression = []
    # 1. 生成數字
    for _ in range(length):
        d = random.choice(denominators)
        n = random.choice([1, 2, 3])
        expression.append(Fraction(n, d))
    
    # 2. 插入符號 (這一步是為了修復你截圖中的空白 Bug)
    final_expr = []
    for i in range(length - 1):
        final_expr.append(expression[i])
        # 隨機選一個符號，並確保它是字串
        op = random.choice(ops)
        final_expr.append(op)
    final_expr.append(expression[-1])
    
    return final_expr

# 初始化狀態
if 'expr' not in st.session_state:
    st.session_state.expr = generate_puzzle()
if 'msg' not in st.session_state:
    st.session_state.msg = "請依照「先乘除、後加減」點擊符號來消除卡片！"

# ==========================================
# 3. 互動處理
# ==========================================

def check_logic(index):
    """檢查是否符合運算順序"""
    expr = st.session_state.expr
    clicked_op = expr[index]
    
    # 檢查算式中是否還有 × 或 ÷
    has_high_priority = any(op in ['×', '÷'] for op in expr if isinstance(op, str))
    is_current_high = clicked_op in ['×', '÷']
    
    if has_high_priority and not is_current_high:
        st.toast("🚫 順序錯誤！還有乘除法沒算，不能先算加減。", icon="⚠️")
        return False
    return True

def execute_merge(index):
    """執行合併動畫效果"""
    if not check_logic(index):
        return

    expr = st.session_state.expr
    left = expr[index-1]
    op = expr[index]
    right = expr[index+1]
    
    # 計算結果
    res = 0
    if op == '+': res = left + right
    elif op == '-': res = left - right
    elif op == '×': res = left * right
    elif op == '÷': res = left / right if right != 0 else left
    
    # 更新狀態：把 [左, 符號, 右] 替換成 [結果]
    new_expr = expr[:index-1] + [res] + expr[index+2:]
    st.session_state.expr = new_expr
    
    if len(new_expr) == 1:
        st.balloons()
        st.session_state.msg = f"🎉 成功融合！答案是 {format_fraction(res)}"
        time.sleep(0.5) # 稍微停頓讓使用者看到
    else:
        st.session_state.msg = "✅ 融合成功，繼續下一步..."

def restart():
    st.session_state.expr = generate_puzzle()
    st.session_state.msg = "新題目：請消除所有符號！"

# ==========================================
# 4. 畫面渲染
# ==========================================

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🧩 卡片融合 (Math Fusion)")
with col_h2:
    if st.button("🔄 換一題"):
        restart()
        st.rerun()

st.markdown(f'<div class="hint-box">{st.session_state.msg}</div>', unsafe_allow_html=True)

# --- 核心遊戲區 ---
# 使用 container 包裹，模擬「舞台」
st.markdown('<div class="game-stage">', unsafe_allow_html=True)

# 為了讓按鈕和卡片能水平排列，我們使用多個 column
# 這是 Streamlit 唯一能模擬「並排」的方法
expr = st.session_state.expr
cols = st.columns(len(expr))

for i, item in enumerate(expr):
    with cols[i]:
        if isinstance(item, Fraction):
            # 渲染數字卡片
            st.markdown(
                f'<div class="num-card">{format_fraction(item)}</div>', 
                unsafe_allow_html=True
            )
        else:
            # 渲染運算符按鈕
            # 只有符號是可以點擊的，這樣更直覺
            if st.button(item, key=f"btn_{i}_{uuid.uuid4()}"):
                execute_merge(i)
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 勝利畫面 ---
if len(expr) == 1:
    st.success(f"最終結果：{format_fraction(expr[0])}")
    if st.button("🚀 下一關", type="primary", use_container_width=True):
        restart()
        st.rerun()
