import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定 (乾淨、大字體)
# ==========================================
st.set_page_config(page_title="標準分數運算練習", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; color: #000; }
    
    /* 題目顯示區 */
    .question-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #3b82f6;
    }
    
    /* 結果顯示區 */
    .result-box {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 20px;
    }
    .correct { background-color: #dcfce7; color: #166534; border: 1px solid #166534; }
    .wrong { background-color: #fee2e2; color: #991b1b; border: 1px solid #991b1b; }
    
    /* 按鈕樣式 */
    div.stButton > button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 出題邏輯 (加減乘除混合)
# ==========================================

def generate_question():
    """生成一道分數四則運算題"""
    # 數字範圍 (避免分母太大太難算)
    denominators = [2, 3, 4, 5, 6, 8, 10]
    
    # 生成 3 個分數 (A op1 B op2 C)
    nums = []
    for _ in range(3):
        d = random.choice(denominators)
        n = random.choice([1, 2, 3, 4, 5])
        # 確保真分數或簡單假分數
        if n >= d: n = d - 1 if d > 1 else 1
        nums.append(Fraction(n, d))
        
    # 隨機運算符 (包含加減乘除)
    ops_pool = ['+', '-', '×', '÷']
    op1 = random.choice(ops_pool)
    op2 = random.choice(ops_pool)
    
    # 構建顯示字串 (用於 LaTeX)
    def frac_latex(f):
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
    
    question_latex = f"{frac_latex(nums[0])} {op1} {frac_latex(nums[1])} {op2} {frac_latex(nums[2])}"
    
    # 計算正確答案 (處理 Python 運算邏輯)
    # 將顯示符號轉為程式運算符
    real_op1 = '*' if op1 == '×' else ('/' if op1 == '÷' else op1)
    real_op2 = '*' if op2 == '×' else ('/' if op2 == '÷' else op2)
    
    # 這裡要注意：Python 的 fraction 運算順序是正確的 (先乘除後加減)
    # 我們直接構造一個 Python 表達式來算答案
    # 為了安全，我們手動計算
    
    # 邏輯：A op1 B op2 C
    # 如果 op1 是 +,- 且 op2 是 *,/ -> 先算 B op2 C
    # 否則 -> 先算 A op1 B
    
    val_a, val_b, val_c = nums[0], nums[1], nums[2]
    
    # 輔助計算函數
    def calc(a, op, b):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '×': return a * b
        if op == '÷': return a / b if b != 0 else a
        return 0

    priority_ops = ['×', '÷']
    
    ans = Fraction(0,1)
    
    # 情況 1: 後面優先 (A + B × C)
    if op2 in priority_ops and op1 not in priority_ops:
        step1 = calc(val_b, op2, val_c)
        ans = calc(val_a, op1, step1)
    # 情況 2: 前面優先或同級 (A × B + C 或 A × B × C)
    else:
        step1 = calc(val_a, op1, val_b)
        ans = calc(step1, op2, val_c)

    return {
        "latex": question_latex,
        "answer": ans,
        "raw_str": f"{nums[0]} {op1} {nums[1]} {op2} {nums[2]}"
    }

# 初始化
if 'q_data' not in st.session_state:
    st.session_state.q_data = generate_question()
if 'user_result' not in st.session_state:
    st.session_state.user_result = None # None, 'correct', 'wrong'

# ==========================================
# 3. 介面互動
# ==========================================

st.title("📝 標準分數運算 (先乘除後加減)")

# 1. 顯示題目
q = st.session_state.q_data
st.markdown('<div class="question-box">', unsafe_allow_html=True)
st.latex(f"\\Large {q['latex']} = ?")
st.markdown('</div>', unsafe_allow_html=True)

# 2. 輸入答案區域
st.write("請輸入你的答案（最簡分數）：")
col1, col2 = st.columns(2)
with col1:
    user_num = st.number_input("分子", value=0, step=1)
with col2:
    user_den = st.number_input("分母", value=1, step=1)

# 3. 提交按鈕
if st.button("提交答案"):
    if user_den == 0:
        st.error("分母不能為 0")
    else:
        user_frac = Fraction(user_num, user_den)
        correct_frac = q['answer']
        
        if user_frac == correct_frac:
            st.session_state.user_result = 'correct'
        else:
            st.session_state.user_result = 'wrong'

# 4. 顯示結果與下一題
if st.session_state.user_result == 'correct':
    st.markdown(f'<div class="result-box correct">✅ 答對了！答案是 {q["answer"]}</div>', unsafe_allow_html=True)
    if st.button("下一題 ➡️", type="primary"):
        st.session_state.q_data = generate_question()
        st.session_state.user_result = None
        st.rerun()

elif st.session_state.user_result == 'wrong':
    st.markdown(f'<div class="result-box wrong">❌ 答錯了... 正確答案是 {q["answer"]}</div>', unsafe_allow_html=True)
    st.write("再試一次，或者直接跳過：")
    if st.button("換一題 (跳過)"):
        st.session_state.q_data = generate_question()
        st.session_state.user_result = None
        st.rerun()

st.markdown("---")
st.caption("提示：記得先乘除後加減。如果有負數，請將負號填在分子。")
