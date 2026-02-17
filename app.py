import streamlit as st
import random
import time
from fractions import Fraction
import uuid

# ==========================================
# 1. 設定與樣式 (保證按鈕大且清楚)
# ==========================================
st.set_page_config(page_title="Math Fusion V3", page_icon="🔥", layout="centered")

st.markdown("""
<style>
    /* 全局字體加大 */
    .stApp { background-color: #1e1e2e; color: #fff; }
    
    /* 數字卡片：藍色方形 */
    .num-card {
        background: #3b82f6;
        color: white;
        padding: 20px 10px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        border: 2px solid #60a5fa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin: 5px;
    }

    /* 符號按鈕區：確保按鈕置中且顯眼 */
    div.stButton > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        background-color: #ef4444 !important; /* 紅色按鈕 */
        color: white !important;
        border-radius: 50px !important; /* 圓角 */
        border: 2px solid white !important;
    }
    div.stButton > button:hover {
        background-color: #dc2626 !important;
        transform: scale(1.05);
    }
    
    /* 提示訊息 */
    .instruction {
        text-align: center;
        font-size: 1.2rem;
        color: #fbbf24;
        margin-bottom: 20px;
        background: #374151;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (保證不會生成壞題目)
# ==========================================

def format_fraction(val):
    """將分數轉為字串"""
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"

def generate_puzzle():
    """生成題目：數字 - 符號 - 數字 - 符號 - 數字"""
    denominators = [2, 3, 4, 5]
    ops_pool = ['+', '-', '×', '÷']
    
    # 強制結構：[數, 符, 數, 符, 數]
    expr = []
    
    # 第1個數
    expr.append(Fraction(random.choice([1,2,3]), random.choice(denominators)))
    # 第1個符號
    expr.append(random.choice(ops_pool))
    # 第2個數
    expr.append(Fraction(random.choice([1,2,3]), random.choice(denominators)))
    # 第2個符號
    expr.append(random.choice(ops_pool))
    # 第3個數
    expr.append(Fraction(random.choice([1,2,3]), random.choice(denominators)))
    
    return expr

# 初始化
if 'puzzle' not in st.session_state:
    st.session_state.puzzle = generate_puzzle()
if 'message' not in st.session_state:
    st.session_state.message = "👉 請點擊「紅色運算符」來計算！"

# ==========================================
# 3. 動作處理 (點擊後發生什麼)
# ==========================================

def handle_click(index):
    current_expr = st.session_state.puzzle
    clicked_op = current_expr[index]
    
    # 1. 檢查規則：先乘除，後加減
    # 檢查算式裡有沒有乘除號
    has_mul_div = any(x in ['×', '÷'] for x in current_expr if isinstance(x, str))
    is_clicking_mul_div = clicked_op in ['×', '÷']
    
    # 如果有乘除號，但你卻點了加減號 -> 報錯
    if has_mul_div and not is_clicking_mul_div:
        st.toast("🚫 順序錯誤！請先算乘除法 (× 或 ÷)", icon="⚠️")
        return

    # 2. 執行計算
    left_num = current_expr[index-1]
    right_num = current_expr[index+1]
    
    result = 0
    if clicked_op == '+': result = left_num + right_num
    elif clicked_op == '-': result = left_num - right_num
    elif clicked_op == '×': result = left_num * right_num
    elif clicked_op == '÷': result = left_num / right_num if right_num != 0 else left_num
    
    # 3. 更新算式：把 [左, 符, 右] 變成 [結果]
    # 例如：[1/2, +, 1/3] -> [5/6]
    new_expr = current_expr[:index-1] + [result] + current_expr[index+2:]
    st.session_state.puzzle = new_expr
    
    if len(new_expr) == 1:
        st.balloons()
        st.session_state.message = f"🎉 成功！答案是 {format_fraction(result)}"
    else:
        st.session_state.message = "✅ 計算成功！請繼續..."

def reset_game():
    st.session_state.puzzle = generate_puzzle()
    st.session_state.message = "新題目開始！請點擊紅色符號"

# ==========================================
# 4. 畫面顯示 (UI)
# ==========================================

st.title("🔥 Math Fusion: 運算順序挑戰")

col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f'<div class="instruction">{st.session_state.message}</div>', unsafe_allow_html=True)
with col_top2:
    if st.button("🔄 換一題"):
        reset_game()
        st.rerun()

st.markdown("---")

# 這裡是最重要的顯示邏輯
# 我們用 columns 把算式橫向排開
puzzle = st.session_state.puzzle

# 勝利畫面
if len(puzzle) == 1:
    st.success(f"🏆 最終結果：{format_fraction(puzzle[0])}")
    if st.button("挑戰下一關 ➡️", type="primary"):
        reset_game()
        st.rerun()

else:
    # 遊戲畫面
    cols = st.columns(len(puzzle))
    
    for i, item in enumerate(puzzle):
        with cols[i]:
            if isinstance(item, Fraction):
                # 如果是數字，顯示藍色卡片 (不能點)
                st.markdown(f'<div class="num-card">{format_fraction(item)}</div>', unsafe_allow_html=True)
            else:
                # 如果是符號，顯示紅色按鈕 (可以點)
                # 使用 uuid 確保每個按鈕 ID 唯一，防止報錯
                if st.button(item, key=f"btn_{i}_{uuid.uuid4()}"):
                    handle_click(i)
                    st.rerun()

st.markdown("---")
st.info("💡 **玩法說明：** 數學規則是「先乘除、後加減」。請觀察算式，如果看到 × 或 ÷，**必須先點擊它們**！")
