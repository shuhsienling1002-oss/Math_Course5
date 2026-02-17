import streamlit as st
import random
import time
from fractions import Fraction
from dataclasses import dataclass, field
import uuid

# ==========================================
# 1. 基礎設定與樣式 (Setup)
# ==========================================
st.set_page_config(
    page_title="分數運算大師",
    page_icon="🧮",
    layout="centered"
)

st.markdown("""
<style>
    /* 全局樣式：乾淨的深色模式 */
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    
    /* 頂部儀表板 */
    .dashboard {
        background: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* 數字顯示 */
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        font-family: monospace;
        color: #4da6ff;
    }
    
    /* 卡片按鈕 */
    div.stButton > button {
        font-size: 1.2rem !important;
        padding: 10px !important;
        border-radius: 8px !important;
        background-color: #333 !important;
        color: white !important;
        border: 1px solid #555 !important;
        width: 100%;
    }
    div.stButton > button:hover {
        border-color: #4da6ff !important;
        color: #4da6ff !important;
    }

    /* 四則運算模式的運算符按鈕 */
    .op-btn-container { text-align: center; }
    
    /* 錯誤與成功訊息 */
    .msg-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .msg-success { background: rgba(0, 255, 0, 0.1); color: #4ade80; border: 1px solid #4ade80; }
    .msg-error { background: rgba(255, 0, 0, 0.1); color: #f87171; border: 1px solid #f87171; }
    .msg-info { background: rgba(0, 100, 255, 0.1); color: #60a5fa; border: 1px solid #60a5fa; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (Logic)
# ==========================================

def format_fraction(val: Fraction) -> str:
    """將分數轉為易讀文字 (例如 3/2 顯示為 1 1/2 或 3/2)"""
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"

class MathGenerator:
    """題目生成器"""
    
    @staticmethod
    def generate_add_sub(level):
        """生成加減法題目：湊出目標數"""
        # 難度設定
        denominators = [2, 3, 4, 5, 6, 8]
        if level > 2: denominators += [7, 9, 10, 12]
        
        target = Fraction(1, 1) # 目標通常是湊出 1
        if level > 3: target = random.choice([Fraction(1,1), Fraction(2,1), Fraction(0,1)])
        
        current_sum = Fraction(0, 1)
        hand = []
        
        # 隨機生成前幾張牌
        count = 2 if level <= 2 else 3
        for _ in range(count):
            d = random.choice(denominators)
            n = random.choice([1, 2, 3])
            if level > 2 and random.random() < 0.4: n = -n # 加入負數
            
            f = Fraction(n, d)
            hand.append(f)
            current_sum += f
            
        # 計算最後一張牌，確保總和等於 Target
        needed = target - current_sum
        hand.append(needed)
        
        # 加入干擾牌
        for _ in range(2):
            d = random.choice(denominators)
            n = random.choice([1, 2])
            hand.append(Fraction(n, d))
            
        random.shuffle(hand)
        return {"target": target, "hand": hand, "type": "add_sub"}

    @staticmethod
    def generate_mul_div(level):
        """生成乘除法題目：約分消除"""
        nums = [2, 3, 4, 5]
        if level > 2: nums += [6, 7, 8, 9]
        
        target = Fraction(1, 1) # 乘除法的目標通常是約分到剩下 1
        hand = []
        
        steps = 2 if level <= 2 else 3
        
        # 生成成對的分子分母以便約分
        for _ in range(steps):
            n = random.choice(nums)
            d = random.choice(nums)
            while n == d: d = random.choice(nums)
            
            # 決定是乘法還是除法卡
            is_div = (level > 1 and random.random() < 0.3)
            
            # 記錄卡片
            hand.append({"val": Fraction(n, d), "is_div": is_div})
            
            # 計算邏輯：如果是除法，數值效果是翻轉的
            effect = Fraction(d, n) if is_div else Fraction(n, d)
            target *= effect # 這裡為了讓最終結果回推為1，我們先算總積，其實遊戲中是從1開始乘
            
        # 其實乘除法遊戲通常是：給定一堆牌，讓當前數值變成 1
        # 這裡簡化邏輯：我們生成一組可以互消的牌
        # 重新生成簡單版：
        hand = []
        base = Fraction(1, 1)
        for _ in range(steps):
            a = random.choice(nums)
            b = random.choice(nums)
            # 放入一張分數
            hand.append({"val": Fraction(a, b), "is_div": False})
            # 放入一張它的倒數 (或者除法卡)
            if random.random() < 0.5 and level > 1:
                # 放入除法卡 (除以 a/b 等於 乘以 b/a)
                hand.append({"val": Fraction(a, b), "is_div": True})
            else:
                # 放入乘法卡 (乘以 b/a)
                hand.append({"val": Fraction(b, a), "is_div": False})
                
        random.shuffle(hand)
        return {"target": Fraction(1, 1), "hand": hand, "type": "mul_div"}

    @staticmethod
    def generate_mixed_ops(level):
        """生成四則運算題目：先乘除後加減"""
        # 結構： 數字 符號 數字 符號 數字...
        # 例如： 1/2 + 1/3 * 1/4
        
        denominators = [2, 3, 4, 5]
        ops_pool = ['+', '-', '×', '÷']
        
        length = 3 if level == 1 else 5 # 數字的數量
        
        expression = []
        
        # 生成數字
        for _ in range(length):
            d = random.choice(denominators)
            n = random.choice([1, 2, 3])
            expression.append(Fraction(n, d))
            
        # 插入符號
        final_expr = []
        for i in range(length - 1):
            final_expr.append(expression[i])
            op = random.choice(ops_pool)
            # 第一關只給加減乘，簡單點
            if level == 1: op = random.choice(['+', '-', '×'])
            final_expr.append(op)
        final_expr.append(expression[-1])
        
        return {"expression": final_expr, "type": "mixed"}

# ==========================================
# 3. 狀態管理 (Session State)
# ==========================================

if 'mode' not in st.session_state:
    st.session_state.mode = 'add_sub' # add_sub, mul_div, mixed
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'game_data' not in st.session_state:
    st.session_state.game_data = None
if 'current_val' not in st.session_state:
    st.session_state.current_val = Fraction(0, 1)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'message' not in st.session_state:
    st.session_state.message = "歡迎！請選擇左側模式開始。"
if 'msg_type' not in st.session_state:
    st.session_state.msg_type = "info"

def start_game():
    """開始新的一局"""
    mode = st.session_state.mode
    level = st.session_state.level
    
    if mode == 'add_sub':
        data = MathGenerator.generate_add_sub(level)
        st.session_state.current_val = Fraction(0, 1)
        st.session_state.message = f"請湊出目標：{format_fraction(data['target'])}"
    elif mode == 'mul_div':
        data = MathGenerator.generate_mul_div(level)
        st.session_state.current_val = Fraction(1, 1) # 乘法從 1 開始
        st.session_state.message = f"請透過乘除，讓數值變回 1"
    else:
        data = MathGenerator.generate_mixed_ops(level)
        st.session_state.message = "請依照「先乘除、後加減」的順序點擊符號"
        
    st.session_state.game_data = data
    st.session_state.history = []
    st.session_state.msg_type = "info"

def check_mixed_op_logic(index):
    """檢查四則運算順序邏輯"""
    expr = st.session_state.game_data['expression']
    clicked_op = expr[index]
    
    # 檢查是否還有乘除號
    has_mul_div = any(op in ['×', '÷'] for op in expr if isinstance(op, str))
    is_current_mul_div = clicked_op in ['×', '÷']
    
    if has_mul_div and not is_current_mul_div:
        return False, "❌順序錯誤！還有乘除法沒算，不能先算加減。"
    return True, "✅計算中..."

def execute_mixed_op(index):
    """執行四則運算的一步"""
    valid, msg = check_mixed_op_logic(index)
    if not valid:
        st.session_state.message = msg
        st.session_state.msg_type = "error"
        return

    expr = st.session_state.game_data['expression']
    left = expr[index-1]
    op = expr[index]
    right = expr[index+1]
    
    res = 0
    if op == '+': res = left + right
    elif op == '-': res = left - right
    elif op == '×': res = left * right
    elif op == '÷': res = left / right if right != 0 else left
    
    # 更新算式列表
    new_expr = expr[:index-1] + [res] + expr[index+2:]
    st.session_state.game_data['expression'] = new_expr
    
    if len(new_expr) == 1:
        st.session_state.message = f"🎉 完成！答案是 {format_fraction(new_expr[0])}"
        st.session_state.msg_type = "success"
        st.balloons()
    else:
        st.session_state.message = f"✅ 算出 {format_fraction(res)}，繼續下一步..."
        st.session_state.msg_type = "success"

# ==========================================
# 4. 介面顯示 (UI)
# ==========================================

# --- 側邊欄 ---
with st.sidebar:
    st.title("🧮 分數運算大師")
    mode = st.radio(
        "選擇練習模式：",
        ('add_sub', 'mul_div', 'mixed'),
        format_func=lambda x: {
            'add_sub': "➕ 加減法 (湊數)",
            'mul_div': "✖️ 乘除法 (約分)",
            'mixed': "⚛️ 四則混合 (順序)"
        }[x]
    )
    
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.level = 1
        st.session_state.game_data = None
        st.rerun()
        
    st.divider()
    st.write(f"當前等級：Lv. {st.session_state.level}")
    if st.button("🔄 下一題 / 重置"):
        start_game()
        st.rerun()

# --- 主畫面 ---

if st.session_state.game_data is None:
    start_game()
    st.rerun()

# 顯示訊息框
msg_class = f"msg-{st.session_state.msg_type}"
st.markdown(f'<div class="msg-box {msg_class}">{st.session_state.message}</div>', unsafe_allow_html=True)

# 根據模式渲染不同介面
data = st.session_state.game_data

# === 模式 1 & 2: 加減 與 乘除 ===
if st.session_state.mode in ['add_sub', 'mul_div']:
    
    # 頂部資訊
    target = data['target']
    current = st.session_state.current_val
    
    col1, col2, col3 = st.columns([1, 0.2, 1])
    with col1:
        st.markdown("<div style='text-align:center'>目標數字</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-number' style='text-align:center'>{format_fraction(target)}</div>", unsafe_allow_html=True)
    with col2:
        eq_symbol = "=" if current == target else "≠"
        st.markdown(f"<div style='text-align:center;font-size:2rem;padding-top:10px'>{eq_symbol}</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='text-align:center'>目前數值</div>", unsafe_allow_html=True)
        color = "#4ade80" if current == target else "#facc15"
        st.markdown(f"<div class='big-number' style='text-align:center;color:{color}'>{format_fraction(current)}</div>", unsafe_allow_html=True)
        
    st.divider()
    
    # 算式歷程
    if st.session_state.history:
        history_str = ""
        for item in st.session_state.history:
            val_str = format_fraction(item['val'])
            if st.session_state.mode == 'add_sub':
                op = "+" if item['val'] >= 0 else "" # 負號自帶
                history_str += f" {op} {val_str}"
            else:
                op = "÷" if item['is_div'] else "×"
                history_str += f" {op} {val_str}"
        st.caption(f"計算過程： {history_str}")

    # 手牌區
    st.write("點擊卡片進行運算：")
    cols = st.columns(4)
    for i, card in enumerate(data['hand']):
        with cols[i % 4]:
            # 顯示邏輯
            if st.session_state.mode == 'add_sub':
                val = card
                label = format_fraction(val)
                if val > 0: label = f"+ {label}"
            else:
                val = card['val']
                is_div = card['is_div']
                op = "÷" if is_div else "×"
                label = f"{op} {format_fraction(val)}"
            
            if st.button(label, key=f"card_{i}"):
                # 執行運算
                if st.session_state.mode == 'add_sub':
                    st.session_state.current_val += val
                    st.session_state.history.append({'val': val})
                else:
                    effect = Fraction(val.denominator, val.numerator) if is_div else val
                    st.session_state.current_val *= effect
                    st.session_state.history.append(card)
                
                # 移除手牌
                del data['hand'][i]
                
                # 檢查勝利
                if st.session_state.current_val == target:
                    st.session_state.message = "🎉 恭喜達成目標！"
                    st.session_state.msg_type = "success"
                    st.balloons()
                st.rerun()

    # 重置按鈕
    if st.button("↩️ 復原上一步", key="undo"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            # 數值回退
            if st.session_state.mode == 'add_sub':
                st.session_state.current_val -= last['val']
                data['hand'].append(last['val'])
            else:
                val = last['val']
                is_div = last['is_div']
                effect = Fraction(val.denominator, val.numerator) if is_div else val
                st.session_state.current_val /= effect
                data['hand'].append(last)
            st.rerun()

# === 模式 3: 四則混合 ===
elif st.session_state.mode == 'mixed':
    
    st.write("請依照運算順序（先乘除、後加減）點擊中間的符號：")
    
    expr = data['expression']
    
    # 動態顯示算式
    # 使用 columns 來排版： 數字 | 按鈕 | 數字 | 按鈕 ...
    col_widths = [1] * len(expr)
    cols = st.columns(len(expr))
    
    for i, item in enumerate(expr):
        with cols[i]:
            if isinstance(item, Fraction):
                # 顯示數字卡片
                st.markdown(
                    f"""<div style="
                        background:#333;
                        padding:10px;
                        border-radius:5px;
                        text-align:center;
                        font-family:monospace;
                        border:1px solid #555;">
                        {format_fraction(item)}
                    </div>""", 
                    unsafe_allow_html=True
                )
            else:
                # 顯示運算符號按鈕
                # 只有符號是按鈕
                if st.button(item, key=f"op_{i}_{uuid.uuid4()}"):
                    execute_mixed_op(i)
                    st.rerun()

    if len(expr) == 1:
        if st.button("下一題 ->"):
            st.session_state.level += 1
            start_game()
            st.rerun()
