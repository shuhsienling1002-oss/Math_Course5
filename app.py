import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定 (乾淨、大字體、考試風)
# ==========================================
st.set_page_config(page_title="標準分數練習 (優化版)", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #212529; }
    
    /* 題目區 */
    .question-card {
        background: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 5px solid #3b82f6;
        margin-bottom: 30px;
    }
    
    /* 詳解區 */
    .solution-box {
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        margin-top: 20px;
        text-align: left;
        font-family: monospace;
        font-size: 1.1rem;
    }
    
    /* 錯誤區 */
    .error-box {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        margin-top: 20px;
        text-align: left;
    }

    /* 計分板 */
    .score-board {
        font-size: 1.2rem;
        font-weight: bold;
        color: #64748b;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (含步驟解析)
# ==========================================

def get_op_latex(op):
    return {'+': '+', '-': '-', '×': '\\times', '÷': '\\div'}[op]

def calculate_step(a, op, b):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '×': return a * b
    if op == '÷': return a / b if b != 0 else a
    return 0

def generate_question():
    """生成題目 + 詳解步驟"""
    dens = [2, 3, 4, 5, 6, 8]
    
    # 生成 3 個數
    nums = [Fraction(random.randint(1, 4), random.choice(dens)) for _ in range(3)]
    
    # 生成符號
    ops = [random.choice(['+', '-', '×', '÷']) for _ in range(2)]
    
    # 決定運算順序
    priority_ops = ['×', '÷']
    
    step1_val = 0
    final_ans = 0
    explanation = ""
    
    # A op1 B op2 C
    op1, op2 = ops[0], ops[1]
    n1, n2, n3 = nums[0], nums[1], nums[2]
    
    # 判斷先算哪邊
    if op2 in priority_ops and op1 not in priority_ops:
        # 先算後面 (B op2 C)
        step1_val = calculate_step(n2, op2, n3)
        final_ans = calculate_step(n1, op1, step1_val)
        explanation = f"""
        1. 先算乘除： {n2} {op2} {n3} = {step1_val}
        2. 再算加減： {n1} {op1} {step1_val} = {final_ans}
        """
    else:
        # 先算前面 (A op1 B)
        step1_val = calculate_step(n1, op1, n2)
        final_ans = calculate_step(step1_val, op2, n3)
        explanation = f"""
        1. 依照順序/先乘除： {n1} {op1} {n2} = {step1_val}
        2. 再算下一步： {step1_val} {op2} {n3} = {final_ans}
        """

    # LaTeX 題目字串
    tex = f"{n1.numerator}/{n1.denominator} {get_op_latex(op1)} {n2.numerator}/{n2.denominator} {get_op_latex(op2)} {n3.numerator}/{n3.denominator}"
    
    # 為了顯示漂亮，把假分數變成真分數的顯示也可以(這裡先維持分數)
    tex = tex.replace('/', '\\over ') # 簡單轉 LaTeX 分數
    
    return {
        "latex": tex,
        "answer": final_ans,
        "explanation": explanation
    }

# 初始化
if 'q' not in st.session_state:
    st.session_state.q = generate_question()
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = None # None, 'correct', 'wrong'

def submit():
    user_frac = Fraction(st.session_state.u_num, st.session_state.u_den)
    ans = st.session_state.q['answer']
    
    if user_frac == ans:
        st.session_state.feedback = 'correct'
        st.session_state.score += 1
    else:
        st.session_state.feedback = 'wrong'

def next_q():
    st.session_state.q = generate_question()
    st.session_state.feedback = None
    # 清空輸入框需要用 key reset，這裡簡單用 rerurn
    st.session_state.u_num = 0
    st.session_state.u_den = 1

# ==========================================
# 3. 介面渲染
# ==========================================

# 頂部
col_l, col_r = st.columns([1, 1])
with col_l:
    st.title("📝 分數運算練習")
with col_r:
    st.markdown(f'<div class="score-board">🏆 連對題數：{st.session_state.score}</div>', unsafe_allow_html=True)

# 題目區
q = st.session_state.q
st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
st.latex(f"\\huge {q['latex']} = ?")
st.markdown('</div>', unsafe_allow_html=True)

# 答題區 (使用 Form 讓 Enter 鍵生效)
if st.session_state.feedback is None:
    with st.form("ans_form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.number_input("分子", value=0, step=1, key="u_num")
        with c2:
            st.number_input("分母", value=1, step=1, key="u_den")
        with c3:
            st.write("") # Spacer
            st.write("")
            submitted = st.form_submit_button("提交答案", type="primary", use_container_width=True, on_click=submit)

# 結果回饋區
else:
    if st.session_state.feedback == 'correct':
        st.success(f"✅ 答對了！答案就是 {q['answer']}")
        st.balloons()
    else:
        st.error(f"❌ 答錯囉... 正確答案是 {q['answer']}")
        # 顯示詳解
        st.markdown(f"""
        <div class="solution-box">
            <b>💡 計算過程解析：</b><br>
            {q['explanation']}
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("➡️ 下一題 (Next)", type="primary", on_click=next_q):
        st.rerun()

st.markdown("---")
st.caption("提示：這就是最標準的練習模式。算完請直接按 Enter 提交。")
