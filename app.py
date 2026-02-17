import streamlit as st
import random
from fractions import Fraction

# ==========================================
# 1. 介面設定
# ==========================================
st.set_page_config(page_title="分數運算 (正負號版)", page_icon="±", layout="centered")

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

def to_latex(f, need_parens=False):
    """
    將分數轉為 LaTeX，並自動處理負號與括號
    f: 分數物件
    need_parens: 是否強制需要括號 (通常用於運算符後面的負數)
    """
    # 處理整數情況 (美觀)
    if f.denominator == 1:
        tex = str(f.numerator)
    else:
        # 處理負號位置：把負號放在分數前面，而不是分子上
        sign = "-" if f < 0 else ""
        tex = f"{sign}\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    
    # 如果是負數且需要括號 (例如在乘除號後面)，加上括號
    if f < 0 and need_parens:
        return f"\\left( {tex} \\right)"
    return tex

def generate_question():
    """生成包含正負號的題目"""
    dens = [2, 3, 4, 5, 6, 8]
    
    # [更新] 分子隨機範圍擴大到包含負數 (排除 0)
    # 範圍：-5 到 5，但排除 0
    nums = []
    for _ in range(3):
        n = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        d = random.choice(dens)
        nums.append(Fraction(n, d))
    
    ops = [random.choice(['+', '-', '*', '/']) for _ in range(2)]
    
    # 計算正確答案
    expr_str = f"nums[0] {ops[0]} nums[1] {ops[1]} nums[2]"
    ans = eval(expr_str, {"nums": nums, "Fraction": Fraction})
    
    # 建構漂亮的 LaTeX (加入括號邏輯)
    # 第一個數通常不用括號 (除非為了強調，但標準寫法不用)
    tex_1 = to_latex(nums[0], need_parens=False)
    # 第二個數：如果它是負數，加上括號會比較標準 (例如 1 + (-2))
    tex_2 = to_latex(nums[1], need_parens=True)
    # 第三個數：同理
    tex_3 = to_latex(nums[2], need_parens=True)
    
    full_tex = f"{tex_1} {get_op_symbol(ops[0])} {tex_2} {get_op_symbol(ops[1])} {tex_3}"
    
    # 智慧提示邏輯 (保持不變，但顯示時也要套用括號規則)
    is_op2_high = ops[1] in ['*', '/']
    is_op1_low = ops[0] in ['+', '-']
    
    hint_tex = ""
    if is_op2_high and is_op1_low:
        # 提示先算後面
        hint_tex = f"{to_latex(nums[1], False)} {get_op_symbol(ops[1])} {to_latex(nums[2], True)}"
        hint_msg = "後面這部分優先級較高，請先算："
    else:
        # 提示先算前面
        hint_tex = f"{to_latex(nums[0], False)} {get_op_symbol(ops[0])} {to_latex(nums[1], True)}"
        hint_msg = "請依照順序，先算前面這部分："

    return {
        "latex": full_tex,
        "answer": ans,
        "hint_tex": hint_tex,
        "hint_msg": hint_msg
    }

# ==========================================
# 3. 狀態管理
# ==========================================

# 自動修復機制：確保資料結構與新版相容
force_reset = False
if 'q_data' in st.session_state:
    # 如果舊資料沒有 hint_msg (V6以前) 或者題目裡沒有負數特徵(雖然很難判斷)，就重置
    if 'hint_msg' not in st.session_state.q_data:
        force_reset = True

if 'q_data' not in st.session_state or force_reset:
    st.session_state.q_data = generate_question()
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

st.title("📐 分數運算 (正負號挑戰)")
st.caption("注意：負數運算規則 (負負得正、正負得負)")

# 題目顯示
q = st.session_state.q_data
st.markdown('<div class="math-display">', unsafe_allow_html=True)
st.latex(q['latex'])
st.markdown('</div>', unsafe_allow_html=True)

# 提示區
with st.expander("💡 負數搞混了嗎？點我看第一步"):
    st.markdown(f"**{q.get('hint_msg', '請先算乘除')}**")
    st.latex(q.get('hint_tex', ''))
    st.caption("小撇步：看到括號前的減號，記得要把裡面的正負號反過來喔！")

st.divider()

# 答題區
if st.session_state.feedback is None:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        # [更新] 分子輸入框允許負數 (預設 step=1 即可支援負整數輸入)
        st.number_input("分子 (可輸入負號)", step=1, key="u_num")
    with c2:
        st.number_input("分母", step=1, key="u_den")
    with c3:
        st.write("") 
        st.write("") 
        st.button("送出答案", type="primary", on_click=check_answer)

# 結果回饋
else:
    ans = st.session_state.q_data['answer']
    # 顯示答案時也要處理一下負號的美觀
    if ans.denominator == 1:
        ans_str = str(ans.numerator)
    else:
        sign = "-" if ans < 0 else ""
        ans_str = f"{sign}{abs(ans.numerator)}/{ans.denominator}"
    
    if st.session_state.feedback == 'correct':
        st.success(f"✅ 答對了！答案是 {ans_str}")
        st.balloons()
    else:
        st.error(f"❌ 算錯囉，正確答案是： {ans_str}")
        
    st.button("➡️ 下一題", type="primary", on_click=next_question)
