import streamlit as st
import random
import uuid
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Optional

# ==========================================
# 0. 系統配置與全局 CSS (System Config)
# ==========================================
st.set_page_config(
    page_title="Fraction Master: Zero-Entropy",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 融合 Code-CRF 推薦的暗色系與高對比視覺風格
st.markdown("""
<style>
    /* 全局背景：深空藍灰 (Zero-Entropy Base) */
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    
    /* 儀表板容器 */
    .dashboard-box {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* 數值顯示：高亮 */
    .metric-value {
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 1.8rem;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    
    /* 卡牌按鈕優化 */
    div.stButton > button {
        background: linear-gradient(180deg, #334155, #1e293b) !important;
        color: #f1f5f9 !important;
        border: 1px solid #64748b !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        transition: all 0.2s !important;
        height: auto !important;
        padding: 10px 0 !important;
    }
    div.stButton > button:hover {
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    }

    /* 圓餅圖 CSS (來自 app.py) */
    .fraction-visual-container {
        display: flex; gap: 4px; align-items: center; justify-content: center;
        margin-bottom: 4px; flex-wrap: wrap;
    }
    .pie-chart {
        width: 24px; height: 24px; border-radius: 50%;
        background: conic-gradient(#38bdf8 var(--p), #334155 0);
        border: 2px solid #94a3b8; flex-shrink: 0;
    }
    .pie-full { background: #38bdf8; border-color: #bae6fd; }
    .pie-negative { background: conic-gradient(#f472b6 var(--p), #334155 0); border-color: #f472b6; }
    .pie-full-negative { background: #f472b6; border-color: #fbcfe8; }

    /* 反應爐算式區 (來自 app (1).py) */
    .reactor-box {
        background: #020617;
        border: 1px dashed #64748b;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin: 10px 0;
        font-family: 'Times New Roman', serif;
    }
    
    /* 狀態標籤 */
    .status-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-size: 0.85rem; font-weight: bold; margin-bottom: 5px;
    }
    .badge-add { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
    .badge-mult { background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid #a855f7; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 統一數據模型 (Unified Domain Model)
# ==========================================

@dataclass
class MathCard:
    numerator: int
    denominator: int
    # 模式標記：True=除法卡(用於乘除模式), False=普通數值
    is_division: bool = False 
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def value(self) -> Fraction:
        """獲取數學值"""
        return Fraction(self.numerator, self.denominator)

    @property
    def display_text_add(self) -> str:
        """加減模式顯示"""
        n, d = self.numerator, self.denominator
        # 處理整數與帶分數顯示邏輯
        if d == 1: return f"{n}"
        if abs(n) > d:
            whole = int(n/d)
            rem = abs(n) % d
            if rem == 0: return f"{whole}"
            return f"{whole} {rem}/{d}"
        return f"{n}/{d}"

    @property
    def display_text_mult(self) -> str:
        """乘除模式顯示 (帶運算符)"""
        op = "➗" if self.is_division else "✖️"
        n_display = f"({self.numerator})" if self.numerator < 0 else f"{self.numerator}"
        return f"{op} {n_display}/{self.denominator}"

    def get_pie_chart_html(self) -> str:
        """生成圓餅圖 HTML (視覺化第一性原理)"""
        val = self.value
        abs_val = abs(val)
        integer_part = int(abs_val)
        fraction_part = abs_val - integer_part
        
        is_neg = val < 0
        pie_class = "pie-negative" if is_neg else "pie-chart"
        full_class = "pie-full-negative" if is_neg else "pie-full"
        
        html = ""
        # 限制顯示數量防止崩潰
        display_ints = min(integer_part, 3) 
        for _ in range(display_ints):
            html += f'<div class="{full_class} pie-chart" style="--p: 100%;"></div>'
        if integer_part > 3:
            html += '<span style="font-size:12px; color:#94a3b8;">+..</span>'
        if fraction_part > 0:
            percent = float(fraction_part) * 100
            html += f'<div class="{pie_class}" style="--p: {percent}%;"></div>'
            
        return f'<div class="fraction-visual-container">{html}</div>'

# ==========================================
# 2. 雙模引擎 (Dual Engines)
# ==========================================

class GameEngine:
    @staticmethod
    def generate_level(mode: str, level: int):
        """
        工廠模式：根據模式生成關卡數據
        Mode 'add': 加減法 (The Construct)
        Mode 'mult': 乘除法 (The Reactor)
        """
        if mode == 'add':
            return GameEngine._gen_add_level(level)
        else:
            return GameEngine._gen_mult_level(level)

    @staticmethod
    def _gen_add_level(level: int):
        # 配置參考自 app.py (分數拼湊)
        configs = {
            1: {'dens': [2, 4], 'count': 2, 'neg': False, 'title': "基礎堆疊 (同分母)"},
            2: {'dens': [2, 3, 6], 'count': 3, 'neg': False, 'title': "進階通分 (異分母)"},
            3: {'dens': [2, 4, 8], 'count': 3, 'neg': True, 'title': "正負抵銷 (整數目標)"},
            4: {'dens': [2, 5, 10], 'count': 4, 'neg': True, 'title': "歸零挑戰 (Target 0)"},
            5: {'dens': [3, 4, 6], 'count': 5, 'neg': True, 'title': "大師級混戰"}
        }
        cfg = configs.get(level, configs[5])
        
        # 動態目標生成
        target_pool = [Fraction(1,1), Fraction(0,1), Fraction(2,1)] if cfg['neg'] else [Fraction(1,1), Fraction(2,1)]
        target = random.choice(target_pool)
        
        hand = []
        current_sum = Fraction(0, 1)
        
        # 逆向生成保證有解
        for _ in range(cfg['count'] - 1):
            d = random.choice(cfg['dens'])
            n = random.choice([1, 2] if d < 5 else [1, 2, 3])
            if cfg['neg'] and random.random() < 0.4: n = -n
            card = MathCard(n, d)
            hand.append(card)
            current_sum += card.value
            
        needed = target - current_sum
        # 避免生成過於離譜的分數
        if needed.denominator > 12 or abs(needed.numerator) > 12:
            return GameEngine._gen_add_level(level) # 重試
            
        hand.append(MathCard(needed.numerator, needed.denominator))
        
        # 加入干擾項
        for _ in range(2):
            d = random.choice(cfg['dens'])
            n = random.choice([1, -1] if cfg['neg'] else [1])
            hand.append(MathCard(n, d))
            
        random.shuffle(hand)
        return {"target": target, "hand": hand, "start_val": Fraction(0,1), "title": cfg['title']}

    @staticmethod
    def _gen_mult_level(level: int):
        # 配置參考自 app (1).py (分數鍊金術)
        configs = {
            1: {'nums': [2, 3], 'steps': 2, 'div': False, 'neg': False, 'title': "基礎合成 (整數)"},
            2: {'nums': [2, 3, 4], 'steps': 2, 'div': False, 'neg': False, 'title': "等價交換 (約分)"},
            3: {'nums': [2, 3, 5], 'steps': 3, 'div': True, 'neg': False, 'title': "逆向煉成 (除法)"},
            4: {'nums': [2, 3, 5], 'steps': 3, 'div': True, 'neg': True, 'title': "極性反轉 (負數)"},
            5: {'nums': [2, 3, 4, 5, 6], 'steps': 4, 'div': True, 'neg': True, 'title': "賢者之石 (高階)"}
        }
        cfg = configs.get(level, configs[5])
        
        target = Fraction(1, 1)
        correct_cards = []
        
        for _ in range(cfg['steps']):
            n = random.choice(cfg['nums'])
            d = random.choice(cfg['nums'])
            while n == d: d = random.choice(cfg['nums'])
            if cfg['neg'] and random.random() < 0.5: n = -n
            is_div = cfg['div'] and random.random() < 0.3
            
            card = MathCard(n, d, is_division=is_div)
            correct_cards.append(card)
            
            # 乘除運算邏輯
            val = Fraction(d, n) if is_div else Fraction(n, d)
            target *= val

        # 干擾項
        distractors = []
        for _ in range(2):
            n = random.choice(cfg['nums'])
            d = random.choice(cfg['nums'])
            is_div = cfg['div'] and random.random() < 0.3
            distractors.append(MathCard(n, d, is_division=is_div))

        hand = correct_cards + distractors
        random.shuffle(hand)
        return {"target": target, "hand": hand, "start_val": Fraction(1,1), "title": cfg['title']}

    @staticmethod
    def generate_latex_visual(history: List[MathCard]) -> str:
        """生成乘除法的視覺化約分字串 (The Reactor Core)"""
        if not history: return "1"
        
        parts_tex = []
        nums, dens = [], []
        
        for card in history:
            n, d = card.numerator, card.denominator
            if card.is_division:
                parts_tex.append(f"\\div \\frac{{{n}}}{{{d}}}")
                nums.append(d) # 翻轉
                dens.append(n)
            else:
                parts_tex.append(f"\\times \\frac{{{n}}}{{{d}}}")
                nums.append(n)
                dens.append(d)

        # 簡單貪婪約分標記
        cancel_n = [False] * len(nums)
        cancel_d = [False] * len(dens)
        for i in range(len(nums)):
            for j in range(len(dens)):
                if not cancel_d[j] and not cancel_n[i] and abs(nums[i]) == abs(dens[j]):
                    cancel_n[i] = True
                    cancel_d[j] = True
                    break
        
        # 構建 LaTeX
        n_tex = " \\cdot ".join([f"\\cancel{{{x}}}" if c else f"{x}" for x, c in zip(nums, cancel_n)])
        d_tex = " \\cdot ".join([f"\\cancel{{{x}}}" if c else f"{x}" for x, c in zip(dens, cancel_d)])
        
        raw_eq = "".join(parts_tex)
        if raw_eq.startswith("\\times"): raw_eq = raw_eq[6:]
        
        return f"{raw_eq} = \\frac{{{n_tex}}}{{{d_tex}}}"

# ==========================================
# 3. 狀態管理 (Session State Manager)
# ==========================================

class StateManager:
    @staticmethod
    def init():
        defaults = {
            'mode': 'add', # add or mult
            'level': 1,
            'target': Fraction(1,1),
            'hand': [],
            'history': [],
            'current_val': Fraction(0,1),
            'game_status': 'setup', # setup, playing, won, lost
            'level_title': '',
            'msg': '歡迎來到零熵算術領域',
            'msg_type': 'info'
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    @staticmethod
    def switch_mode(new_mode):
        st.session_state.mode = new_mode
        st.session_state.level = 1
        st.session_state.game_status = 'setup'
        st.rerun()

    @staticmethod
    def start_level():
        data = GameEngine.generate_level(st.session_state.mode, st.session_state.level)
        st.session_state.target = data['target']
        st.session_state.hand = data['hand']
        st.session_state.current_val = data['start_val']
        st.session_state.level_title = data['title']
        st.session_state.history = []
        st.session_state.game_status = 'playing'
        st.session_state.msg = "請選擇卡牌達成目標"
        st.session_state.msg_type = 'info'

    @staticmethod
    def play_card(idx):
        hand = st.session_state.hand
        if 0 <= idx < len(hand):
            card = hand.pop(idx)
            st.session_state.history.append(card)
            
            # 更新數值
            if st.session_state.mode == 'add':
                st.session_state.current_val += card.value
            else:
                op_val = Fraction(card.denominator, card.numerator) if card.is_division else Fraction(card.numerator, card.denominator)
                st.session_state.current_val *= op_val
            
            StateManager.check_win()

    @staticmethod
    def undo():
        if st.session_state.history:
            card = st.session_state.history.pop()
            st.session_state.hand.append(card)
            
            # 逆向操作
            if st.session_state.mode == 'add':
                st.session_state.current_val -= card.value
            else:
                op_val = Fraction(card.denominator, card.numerator) if card.is_division else Fraction(card.numerator, card.denominator)
                st.session_state.current_val /= op_val
            
            st.session_state.game_status = 'playing'
            st.toast("已悔棋 (Entropy Reversal)", icon="↩️")

    @staticmethod
    def check_win():
        target = st.session_state.target
        current = st.session_state.current_val
        
        if current == target:
            st.session_state.game_status = 'won'
            st.session_state.msg = "✨ 運算完美收斂！(Zero Entropy Achieved)"
            st.session_state.msg_type = 'success'
            st.balloons()
        elif not st.session_state.hand:
            st.session_state.game_status = 'lost'
            st.session_state.msg = "🌑 手牌耗盡，路徑崩塌。"
            st.session_state.msg_type = 'error'

# ==========================================
# 4. UI 渲染組件 (Components)
# ==========================================

def render_dashboard():
    """統一的頂部儀表板"""
    mode = st.session_state.mode
    target = st.session_state.target
    current = st.session_state.current_val
    level = st.session_state.level
    
    # 模式標籤
    badge_cls = "badge-add" if mode == 'add' else "badge-mult"
    mode_name = "THE CONSTRUCT (加減法)" if mode == 'add' else "THE REACTOR (乘除法)"
    
    st.markdown(f'<div class="status-badge {badge_cls}">{mode_name} Lv.{level}</div>', unsafe_allow_html=True)
    st.markdown(f"**任務：{st.session_state.level_title}**")
    
    # 進度顯示
    cols = st.columns([1, 0.2, 1])
    with cols[0]:
        st.markdown(f"<div style='text-align:center;color:#94a3b8'>TARGET</div>", unsafe_allow_html=True)
        st.latex(f"\\huge {target.numerator}/{target.denominator}" if target.denominator!=1 else f"\\huge {target.numerator}")
    with cols[1]:
        icon = "⚖️" if st.session_state.game_status == 'playing' else ("✅" if st.session_state.game_status=='won' else "❌")
        st.markdown(f"<div style='text-align:center;font-size:2rem;padding-top:10px'>{icon}</div>", unsafe_allow_html=True)
    with cols[2]:
        color = "#38bdf8" if mode == 'add' else "#a855f7"
        if st.session_state.game_status == 'won': color = "#4ade80"
        
        st.markdown(f"<div style='text-align:center;color:#94a3b8'>CURRENT</div>", unsafe_allow_html=True)
        val_latex = f"\\huge \\color{{{color}}}{{{current.numerator}/{current.denominator}}}" if current.denominator!=1 else f"\\huge \\color{{{color}}}{{{current.numerator}}}"
        st.latex(val_latex)

    # 進度條 (僅加法模式適合線性進度，乘法模式顯示動態)
    if mode == 'add':
        try:
            # 安全的進度計算，避免除以零
            max_val = max(float(target) * 1.5, float(current) * 1.2, 1.0)
            cur_pct = min(max(float(current) / max_val, 0.0), 1.0)
            tgt_pct = min(max(float(target) / max_val, 0.0), 1.0)
            
            st.markdown(f"""
            <div style="background:#334155;height:8px;border-radius:4px;position:relative;margin-top:10px;">
                <div style="background:#38bdf8;width:{cur_pct*100}%;height:100%;border-radius:4px;transition:width 0.5s;"></div>
                <div style="background:#4ade80;width:4px;height:12px;position:absolute;top:-2px;left:{tgt_pct*100}%;"></div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

def render_play_area():
    """遊戲操作區"""
    mode = st.session_state.mode
    
    # 1. 顯示歷史/算式
    st.markdown("---")
    if mode == 'add':
        # 加法模式：顯示算式字串
        eq_parts = [f"{c.value}" for c in st.session_state.history]
        eq_str = " + ".join(eq_parts) if eq_parts else "0"
        st.caption(f"運算鏈： {eq_str} = {st.session_state.current_val}")
    else:
        # 乘法模式：顯示反應爐 LaTeX
        visual_latex = GameEngine.generate_latex_visual(st.session_state.history)
        st.markdown(f'<div class="reactor-box">', unsafe_allow_html=True)
        st.latex(f"\\Large {visual_latex} = {st.session_state.current_val}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. 手牌區
    if st.session_state.game_status == 'playing':
        hand = st.session_state.hand
        if hand:
            st.write("👇 點擊投入運算：")
            cols = st.columns(4)
            for i, card in enumerate(hand):
                with cols[i % 4]:
                    # 視覺輔助：加法顯示圓餅圖，乘法不顯示
                    if mode == 'add':
                        st.markdown(card.get_pie_chart_html(), unsafe_allow_html=True)
                        label = card.display_text_add
                    else:
                        label = card.display_text_mult
                    
                    if st.button(label, key=f"card_{card.id}", use_container_width=True):
                        StateManager.play_card(i)
                        st.rerun()
        
        # 3. 控制區
        col_undo, col_reset = st.columns([1, 4])
        with col_undo:
            if st.session_state.history:
                st.button("↩️ 撤銷", on_click=StateManager.undo)
    
    # 4. 結算區
    elif st.session_state.game_status == 'won':
        if st.button("🚀 前往下一層", type="primary", use_container_width=True):
            st.session_state.level += 1
            StateManager.start_level()
            st.rerun()
            
    elif st.session_state.game_status == 'lost':
        if st.button("💥 重置反應爐", type="primary", use_container_width=True):
            StateManager.start_level()
            st.rerun()

# ==========================================
# 5. 主程式 (Main Loop)
# ==========================================

def main():
    StateManager.init()

    # --- Sidebar: Mode Selection ---
    with st.sidebar:
        st.title("💠 零熵算術")
        st.markdown("---")
        
        mode_select = st.radio(
            "選擇運算模組：",
            ('add', 'mult'),
            format_func=lambda x: "➕ 拼湊 (加減)" if x=='add' else "✖️ 煉金 (乘除)",
            index=0 if st.session_state.mode=='add' else 1
        )
        
        if mode_select != st.session_state.mode:
            StateManager.switch_mode(mode_select)
        
        st.markdown("---")
        st.caption("Architecture v6.4 | Zero-Entropy Math")
        if st.button("🔄 完全重置"):
            st.session_state.clear()
            st.rerun()

    # --- Main Content ---
    
    # 檢查是否需要初始化關卡
    if st.session_state.game_status == 'setup':
        StateManager.start_level()
        st.rerun()

    # 渲染儀表板
    st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
    render_dashboard()
    st.markdown('</div>', unsafe_allow_html=True)

    # 渲染操作區
    render_play_area()

if __name__ == "__main__":
    main()
