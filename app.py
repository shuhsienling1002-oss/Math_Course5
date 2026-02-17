import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定
# ==========================================
st.set_page_config(page_title="標準分數運算", page_icon="📐", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #000; }
    
    /* 題目顯示區 */
    .math-display {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 30px;
        border: 2px solid #e9ecef;
    }
    
    /* 加大數學公式字體 */
    .katex { font-size: 2.8em !important; }
    
    /* 按鈕樣式 */
    div.stButton > button {
        font-size: 1.3rem !important;
        font-weight: bold !important;
        padding: 12px !important;
        border-radius: 10px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯
# ==========================================

def get_op_symbol(op):
    if op == '*': return '\\times'
    if op == '/': return '\\div'
    return op

def generate_question():
    """生成題目"""
    dens = [2, 3, 4, 5, 6, 8]
    
    # 生成 3 個分數
    nums = [Fraction(random.randint(1, 4), random.choice(dens)) for _ in range(3)]
    
    # 生成 2 個運算符
    ops = [random.choice(['+', '-', '*', '/']) for _ in range(2)]
    
    # 計算正確答案
    # 這裡直接用 Python 的 eval 計算，確保先乘除後加減邏輯正確
    expr_str = f"nums[0] {ops[0]} nums[1] {ops[1]} nums[2]"
    ans = eval(expr_str, {"nums": nums, "Fraction": Fraction})
    
    # 建構 LaTeX 顯示字串
    def to_latex(f):
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
    
    tex = f"{to_latex(nums[0])} {get_op_symbol(ops[0])} {to_latex(nums[1])} {get_op_symbol(ops[1])} {to_latex(nums[2])}"
    
    return {
        "latex": tex,
        "answer": ans
    }

# 初始化 Session State
if 'q_data' not in st.session_state:
    st.session_state.q_data = generate_question()
if 'feedback' not in st.session_state:
    st.session_state.feedback = None # None, 'correct', 'wrong'

# [修正重點]：初始化輸入框的值，避免黃色警告
if 'u_num' not in st.session_state:
    st.session_state.u_num = 0
if 'u_den' not in st.session_state:
    st.session_state.u_den = 1

def check_answer():
    try:
        # 讀取使用者輸入
        user_val = Fraction(st.session_state.u_num, st.session_state.u_den)
        if user_val == st.session_state.q_data['answer']:
            st.session_state.feedback = 'correct'
        else:
            st.session_state.feedback = 'wrong'
    except:
        st.error("請輸入有效的數字")

def next_question():
    # 生成新題目
    st.session_state.q_data = generate_question()
    st.session_state.feedback = None
    # [修正重點]：重置輸入框，這裡直接修改 state 即可，不要在 widget 設定 default value
    st.session_state.u_num = 0
    st.session_state.u_den = 1

# ==========================================
# 3. 畫面渲染
# ==========================================

st.title("📐 分數四則運算 (先乘除後加減)")

# 顯示題目
q = st.session_state.q_data
st.markdown('<div class="math-display">', unsafe_allow_html=True)
st.latex(q['latex'])
st.markdown('</div>', unsafe_allow_html=True)

# 答題區
if st.session_state.feedback is None:
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            # [修正重點]：移除了 value=0，直接綁定 key，這樣就不會報錯
            st.number_input("分子", step=1, key="u_num")
        with c2:
            st.number_input("分母", step=1, key="u_den")
        with c3:
            st.write("") 
            st.write("") 
            st.button("送出答案", type="primary", on_click=check_answer)

# 結果回饋
else:
    ans = st.session_state.q_data['answer']
    ans_str = f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else f"{ans.numerator}"
    
    if st.session_state.feedback == 'correct':
        st.success(f"✅ 答對了！答案是 {ans_str}")
        st.balloons()
    else:
        st.error(f"❌ 答錯囉，正確答案是： {ans_str}")
        
    st.button("➡️ 下一題", type="primary", on_click=next_question)
