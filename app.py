import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定
# ==========================================
st.set_page_config(page_title="標準分數運算 (含提示)", page_icon="📐", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #000; }
    
    /* 題目顯示區 */
    .math-display {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #e9ecef;
    }
    
    /* 加大數學公式字體 */
    .katex { font-size: 2.5em !important; }
    
    /* 提示區樣式 */
    .hint-text {
        color: #666;
        font-size: 1.1rem;
        background: #fff3cd;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
    }

    /* 按鈕樣式 */
    div.stButton > button {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        padding: 10px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (含優先級判斷)
# ==========================================

def get_op_symbol(op):
    if op == '*': return '\\times'
    if op == '/': return '\\div'
    return op

def to_latex(f):
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def generate_question():
    """生成題目 + 智慧提示"""
    dens = [2, 3, 4, 5, 6, 8]
    
    # 生成 3 個分數
    nums = [Fraction(random.randint(1, 4), random.choice(dens)) for _ in range(3)]
    
    # 生成 2 個運算符
    ops = [random.choice(['+', '-', '*', '/']) for _ in range(2)]
    
    # 計算正確答案
    expr_str = f"nums[0] {ops[0]} nums[1] {ops[1]} nums[2]"
    ans = eval(expr_str, {"nums": nums, "Fraction": Fraction})
    
    # 建構完整題目的 LaTeX
    full_tex = f"{to_latex(nums[0])} {get_op_symbol(ops[0])} {to_latex(nums[1])} {get_op_symbol(ops[1])} {to_latex(nums[2])}"
    
    # --- 智慧提示邏輯 (找出第一步) ---
    # 判斷邏輯：如果後面是乘除(高優先)，且前面是加減(低優先)，則先算後面。否則都從前面算。
    is_op2_high = ops[1] in ['*', '/']
    is_op1_low = ops[0] in ['+', '-']
    
    hint_tex = ""
    if is_op2_high and is_op1_low:
        # 提示先算後面
        hint_tex = f"{to_latex(nums[1])} {get_op_symbol(ops[1])} {to_latex(nums[2])}"
        hint_msg = "後面這部分優先級較高，請先算："
    else:
        # 提示先算前面
        hint_tex = f"{to_latex(nums[0])} {get_op_symbol(ops[0])} {to_latex(nums[1])}"
        hint_msg = "請依照順序，先算前面這部分："

    return {
        "latex": full_tex,
        "answer": ans,
        "hint_tex": hint_tex,
        "hint_msg": hint_msg
    }

# 初始化
if 'q_data' not in st.session_state:
    st.session_state.q_data = generate_question()
if 'feedback' not in st.session_state:
    st.session_state.feedback = None 
if 'u_num' not in st.session_state: st.session_state.u_num = 0
if 'u_den' not in st.session_state: st.session_state.u_den = 1

def check_answer():
    try:
        user_val = Fraction(st.session_state.u_num, st.session_state.u_den)
        if user_val == st.session_state.q_data['answer']:
            st.session_state.feedback = 'correct'
        else:
            st.session_state.feedback = 'wrong'
    except:
        st.error("請輸入有效數字")

def next_question():
    st.session_state.q_data = generate_question()
    st.session_state.feedback = None
    st.session_state.u_num = 0
    st.session_state.u_den = 1

# ==========================================
# 3. 畫面渲染
# ==========================================

st.title("📐 分數運算 (附智慧提示)")

# 題目顯示
q = st.session_state.q_data
st.markdown('<div class="math-display">', unsafe_allow_html=True)
st.latex(q['latex'])
st.markdown('</div>', unsafe_allow_html=True)

# --- 💡 這裡就是你要的「不明顯提示」 ---
# 使用 expander 收合，學生不點就不會看到
with st.expander("💡 卡住了嗎？點我看第一步該算哪裡"):
    st.markdown(f"**{q['hint_msg']}**")
    # 只顯示第一步的局部算式
    st.latex(q['hint_tex'])
    st.caption("算出這一步後，再跟剩下的數字運算喔！")

st.divider()

# 答題區
if st.session_state.feedback is None:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
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
        st.error(f"❌ 算錯囉，正確答案是： {ans_str}")
        
    st.button("➡️ 下一題", type="primary", on_click=next_question)
