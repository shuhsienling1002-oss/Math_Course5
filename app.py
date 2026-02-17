import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定
# ==========================================
st.set_page_config(page_title="標準分數運算 (修復版)", page_icon="📐", layout="centered")

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
# 2. 核心邏輯
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
    
    nums = [Fraction(random.randint(1, 4), random.choice(dens)) for _ in range(3)]
    ops = [random.choice(['+', '-', '*', '/']) for _ in range(2)]
    
    # 計算答案
    expr_str = f"nums[0] {ops[0]} nums[1] {ops[1]} nums[2]"
    ans = eval(expr_str, {"nums": nums, "Fraction": Fraction})
    
    # 建構 LaTeX
    full_tex = f"{to_latex(nums[0])} {get_op_symbol(ops[0])} {to_latex(nums[1])} {get_op_symbol(ops[1])} {to_latex(nums[2])}"
    
    # 智慧提示邏輯
    is_op2_high = ops[1] in ['*', '/']
    is_op1_low = ops[0] in ['+', '-']
    
    hint_tex = ""
    if is_op2_high and is_op1_low:
        hint_tex = f"{to_latex(nums[1])} {get_op_symbol(ops[1])} {to_latex(nums[2])}"
        hint_msg = "後面這部分優先級較高，請先算："
    else:
        hint_tex = f"{to_latex(nums[0])} {get_op_symbol(ops[0])} {to_latex(nums[1])}"
        hint_msg = "請依照順序，先算前面這部分："

    return {
        "latex": full_tex,
        "answer": ans,
        "hint_tex": hint_tex,
        "hint_msg": hint_msg
    }

# ==========================================
# 3. 狀態管理 (自動修復區)
# ==========================================

# [關鍵修復]：檢查資料是否完整，如果不完整(KeyError來源)，強制重置
force_reset = False
if 'q_data' in st.session_state:
    # 檢查舊資料裡有沒有 hint_msg，如果沒有，代表是舊版資料
    if 'hint_msg' not in st.session_state.q_data:
        force_reset = True

if 'q_data' not in st.session_state or force_reset:
    st.session_state.q_data = generate_question()
    # 重置所有相關狀態
    st.session_state.feedback = None 
    st.session_state.u_num = 0
    st.session_state.u_den = 1

# ==========================================
# 4. 畫面渲染
# ==========================================

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

st.title("📐 分數運算 (附智慧提示)")

# 題目顯示
q = st.session_state.q_data
st.markdown('<div class="math-display">', unsafe_allow_html=True)
st.latex(q['latex'])
st.markdown('</div>', unsafe_allow_html=True)

# 💡 提示區 (使用 .get 雙重防呆)
with st.expander("💡 卡住了嗎？點我看第一步該算哪裡"):
    st.markdown(f"**{q.get('hint_msg', '請先算乘除')}**")
    st.latex(q.get('hint_tex', ''))
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
