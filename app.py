import streamlit as st
import random
from fractions import Fraction
from dataclasses import dataclass
import time

# ==========================================
# 0. 系統配置 & CSS
# ==========================================
st.set_page_config(
    page_title="Fraction Fusion: Order of Operations",
    page_icon="⚛️",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    
    /* 算式顯示區 */
    .equation-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 12px;
        padding: 30px;
        background: #1e293b;
        border-radius: 16px;
        border: 2px solid #475569;
        margin-bottom: 20px;
        min-height: 120px;
    }

    /* 數字卡片 (靜態) */
    .num-card {
        background: #334155;
        color: #f8fafc;
        padding: 10px 18px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* 運算符按鈕 (互動核心) */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        transition: transform 0.1s, box-shadow 0.2s !important;
    }
    div.stButton > button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
    }
    div.stButton > button:active {
        transform: scale(0.9);
    }

    /* 高優先級運算符提示 (乘除) */
    .priority-high {
        border: 2px solid #f472b6 !important; /* Pink border */
    }

    /* 狀態訊息 */
    .status-msg {
        text-align: center;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    .msg-error { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid #f43f5e; }
    .msg-success { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
    .msg-info { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #60a5fa; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心邏輯引擎
# ==========================================

class MixedOpEngine:
    @staticmethod
    def generate_expression(level: int):
        """生成混合運算式 (由數字和運算符組成的列表)"""
        # 難度控制：分母範圍與算式長度
        if level == 1:
            dens = [2, 3, 4, 5]
            ops_pool = ['+', '-', '×'] # 只有一個乘法
            length = 3 # A op B op C
        elif level == 2:
            dens = [2, 3, 4, 6, 8]
            ops_pool = ['+', '-', '×', '÷']
            length = 3
        else:
            dens = [2, 3, 4, 5, 6, 8, 10]
            ops_pool = ['+', '-', '×', '÷', '+']
            length = 5 # A op B op C op D op E

        # 生成數字與運算符
        nums = []
        for _ in range(length):
            d = random.choice(dens)
            n = random.choice([1, 2, 3])
            if random.random() < 0.3: n = -n # 偶爾出現負數
            nums.append(Fraction(n, d))
            
        ops = []
        for _ in range(length - 1):
            ops.append(random.choice(ops_pool))
            
        # 構建結構：[Num, Op, Num, Op, Num...]
        expression = []
        for i in range(len(ops)):
            expression.append(nums[i])
            expression.append(ops[i])
        expression.append(nums[-1])
        
        return expression

    @staticmethod
    def check_priority(expression, clicked_idx):
        """
        核心物理法則：檢查運算順序是否正確
        clicked_idx: 被點擊的運算符在 expression 列表中的索引
        """
        clicked_op = expression[clicked_idx]
        
        # 掃描整個式子，看是否有更高優先級的運算符存在
        has_high_priority = False
        for item in expression:
            if isinstance(item, str) and item in ['×', '÷']:
                has_high_priority = True
                break
        
        # 規則判定
        is_high = clicked_op in ['×', '÷']
        
        if has_high_priority and not is_high:
            return False, "⚠️ 能量不足！必須先處理「強作用力」(乘除法)。"
        
        return True, "✅ 順序正確，反應進行中..."

    @staticmethod
    def calculate_step(expression, op_idx):
        """執行一步運算 (坍縮)"""
        left = expression[op_idx - 1]
        op = expression[op_idx]
        right = expression[op_idx + 1]
        
        res = Fraction(0, 1)
        if op == '+': res = left + right
        elif op == '-': res = left - right
        elif op == '×': res = left * right
        elif op == '÷': res = left / right if right != 0 else left # 防呆
        
        # 重組列表：將 [left, op, right] 替換為 [res]
        new_expr = expression[:op_idx-1] + [res] + expression[op_idx+2:]
        return new_expr, res

def format_fraction(val):
    """格式化分數顯示"""
    if isinstance(val, str): return val
    if val.denominator == 1: return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"

# ==========================================
# 2. 狀態管理
# ==========================================

if 'level' not in st.session_state:
    st.session_state.level = 1
if 'expression' not in st.session_state:
    st.session_state.expression = MixedOpEngine.generate_expression(1)
if 'msg' not in st.session_state:
    st.session_state.msg = "請依照運算順序點擊運算符"
if 'msg_type' not in st.session_state:
    st.session_state.msg_type = "info"
if 'game_status' not in st.session_state:
    st.session_state.game_status = "playing"

def reset_game():
    st.session_state.expression = MixedOpEngine.generate_expression(st.session_state.level)
    st.session_state.game_status = "playing"
    st.session_state.msg = "新的反應序列已生成"
    st.session_state.msg_type = "info"

def handle_click(op_idx):
    expr = st.session_state.expression
    
    # 1. 檢查順序 (PEMDAS Check)
    valid, msg = MixedOpEngine.check_priority(expr, op_idx)
    
    if not valid:
        st.session_state.msg = msg
        st.session_state.msg_type = "error"
        # 懲罰：不改變狀態，只顯示錯誤
    else:
        # 2. 執行運算
        new_expr, result = MixedOpEngine.calculate_step(expr, op_idx)
        st.session_state.expression = new_expr
        
        # 3. 檢查是否完成
        if len(new_expr) == 1:
            st.session_state.game_status = "won"
            st.session_state.msg = f"✨ 坍縮完成！最終結果：{format_fraction(new_expr[0])}"
            st.session_state.msg_type = "success"
            st.balloons()
        else:
            st.session_state.msg = f"✅ 運算成功 (={format_fraction(result)})，請繼續..."
            st.session_state.msg_type = "success"

# ==========================================
# 3. UI 呈現
# ==========================================

st.title("⚛️ Fraction Fusion: 秩序之環")
st.caption("任務：依照「先乘除後加減」的物理法則，將算式坍縮為單一數值。")

# --- 頂部控制欄 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(st.session_state.level / 5)
with col2:
    if st.button("🔄 重置題目"):
        reset_game()
        st.rerun()

# --- 訊息提示 ---
msg_cls = f"msg-{st.session_state.msg_type}"
st.markdown(f'<div class="status-msg {msg_cls}">{st.session_state.msg}</div>', unsafe_allow_html=True)

# --- 核心算式區 (動態生成) ---
st.markdown('<div class="equation-container">', unsafe_allow_html=True)

# 這裡我們需要一個極為巧妙的 Layout 來混合顯示「靜態數字」與「互動按鈕」
# Streamlit 的 columns 可以做到
expr = st.session_state.expression
cols = st.columns(len(expr))

for i, item in enumerate(expr):
    with cols[i]:
        if isinstance(item, Fraction):
            # 顯示數字卡片
            txt = format_fraction(item)
            st.markdown(f'<div class="num-card">{txt}</div>', unsafe_allow_html=True)
        else:
            # 顯示運算符按鈕
            # 只有在遊戲進行中才顯示按鈕，贏了就只顯示文字
            if st.session_state.game_status == "playing":
                st.button(
                    item, 
                    key=f"op_{i}_{time.time()}", # 防止 Key 重複
                    on_click=handle_click,
                    args=(i,)
                )
            else:
                st.markdown(f"<div style='text-align:center;font-size:2rem;color:#64748b'>{item}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 遊戲勝利處理 ---
if st.session_state.game_status == "won":
    col_next, _ = st.columns([1, 2])
    with col_next:
        if st.button("🚀 挑戰下一關 (Level Up)", type="primary"):
            st.session_state.level = min(st.session_state.level + 1, 5)
            reset_game()
            st.rerun()

# --- 教學區 ---
with st.expander("📖 物理法則說明 (Rules)"):
    st.markdown("""
    1.  **強作用力 (× ÷)**：優先級最高，必須先被消除。
    2.  **弱作用力 (+ -)**：只有當算式中沒有乘除號時，才能進行加減。
    3.  **算式坍縮**：每次點擊正確的運算符，兩側的數字會結合成一個新數字，直到只剩下一個最終結果。
    """)
