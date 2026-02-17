import streamlit as st
import random
from fractions import Fraction
import uuid

# ==========================================
# 1. 遊戲設定與 CSS (暗黑地牢風)
# ==========================================
st.set_page_config(page_title="Math Dungeon", page_icon="⚔️", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1a0b0b; color: #e5e5e5; }
    
    /* 怪物區 */
    .monster-box {
        background: #2d1b1b;
        border: 4px solid #8B0000;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(139, 0, 0, 0.5);
    }
    .monster-hp-bar {
        background: #444;
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
        margin-top: 10px;
        border: 2px solid #fff;
    }
    .hp-fill {
        background: linear-gradient(90deg, #ff4d4d, #cc0000);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* 玩家手牌區 */
    .hand-area {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    
    /* 卡牌按鈕 (武器) */
    div.stButton > button {
        background: linear-gradient(180deg, #2c3e50, #000);
        color: #f1c40f !important;
        border: 2px solid #f1c40f !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace;
        font-size: 1.5rem !important;
        padding: 15px 20px !important;
        width: 100%;
        transition: transform 0.1s;
    }
    div.stButton > button:hover {
        transform: translateY(-5px);
        background: #34495e;
        box-shadow: 0 0 15px #f1c40f;
    }
    
    /* 傷害數字 */
    .dmg-text { color: #ff4d4d; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 遊戲核心邏輯
# ==========================================

def init_game():
    """初始化一場戰鬥"""
    # 怪物總血量 (目標) 固定為 1，方便理解分數
    target = Fraction(1, 1)
    
    # 生成一組剛好能湊成 1 的手牌
    # 邏輯：隨機切分
    parts = []
    current = Fraction(0, 1)
    
    # 隨機切 3-4 刀
    options = [Fraction(1,2), Fraction(1,3), Fraction(1,4), Fraction(1,6), Fraction(1,8)]
    
    # 這裡用簡單的湊數邏輯：保證有解
    # 方案 A: 1/2 + 1/2
    # 方案 B: 1/2 + 1/4 + 1/4
    # 方案 C: 1/3 + 1/3 + 1/3
    # 方案 D: 1/2 + 1/3 + 1/6
    
    scenarios = [
        [Fraction(1,2), Fraction(1,2)],
        [Fraction(1,2), Fraction(1,4), Fraction(1,4)],
        [Fraction(1,3), Fraction(1,3), Fraction(1,3)],
        [Fraction(1,2), Fraction(1,3), Fraction(1,6)],
        [Fraction(1,4), Fraction(1,4), Fraction(1,4), Fraction(1,4)],
        [Fraction(1,2), Fraction(1,4), Fraction(1,8), Fraction(1,8)]
    ]
    
    winning_hand = random.choice(scenarios)
    
    # 加入 1-2 張干擾牌 (垃圾武器)
    decoys = [random.choice(options) for _ in range(2)]
    
    full_hand = winning_hand + decoys
    random.shuffle(full_hand)
    
    st.session_state.target_hp = target
    st.session_state.current_damage = Fraction(0, 1)
    st.session_state.hand = full_hand
    st.session_state.game_over = False
    st.session_state.msg = "戰鬥開始！選擇卡牌湊出剛好 1 的傷害！"

if 'target_hp' not in st.session_state:
    init_game()

def attack(card_idx):
    if st.session_state.game_over:
        return

    card_val = st.session_state.hand.pop(card_idx)
    st.session_state.current_damage += card_val
    
    damage_pct = float(st.session_state.current_damage / st.session_state.target_hp) * 100
    
    # 判定結果
    if st.session_state.current_damage == st.session_state.target_hp:
        st.session_state.game_over = True
        st.balloons()
        st.session_state.msg = f"⚔️ 致命一擊！怪物倒下了！ (傷害: {st.session_state.current_damage})"
    elif st.session_state.current_damage > st.session_state.target_hp:
        st.session_state.game_over = True
        st.session_state.msg = f"💥 傷害溢出！怪物狂暴了！ (當前: {st.session_state.current_damage} > 1)"
    else:
        st.session_state.msg = f"🗡️ 造成傷害！怪物還剩 {st.session_state.target_hp - st.session_state.current_damage} 血量"

def restart():
    init_game()

# ==========================================
# 3. 畫面顯示
# ==========================================

st.title("⚔️ Math Dungeon: 分數獵人")

# 頂部控制
col1, col2 = st.columns([3, 1])
with col1:
    st.info(st.session_state.msg)
with col2:
    if st.button("🔄 下一隻怪物"):
        restart()
        st.rerun()

# --- 怪物區 (血條) ---
target = st.session_state.target_hp
current = st.session_state.current_damage
# 計算血條百分比 (最高 100%)
hp_percent = max(0, min(100, float((target - current) / target) * 100))
dmg_percent = min(100, float(current / target) * 100)

st.markdown(f"""
<div class="monster-box">
    <h2>👹 混沌史萊姆</h2>
    <div style="font-size: 1.2rem; margin-bottom: 5px;">
        目標傷害：<span style="color:#f1c40f">{target}</span> | 
        已造成傷害：<span style="color:#ff4d4d">{current}</span>
    </div>
    <div class="monster-hp-bar">
        <div class="hp-fill" style="width: {dmg_percent}%;"></div>
    </div>
    <div style="margin-top:5px; font-size:0.9rem; color:#aaa;">怪物血量剩餘 {hp_percent:.1f}%</div>
</div>
""", unsafe_allow_html=True)

# --- 戰鬥區 (出牌) ---
if not st.session_state.game_over:
    st.write("👇 點擊卡牌進行攻擊：")
    
    # 卡牌排列
    cols = st.columns(4)
    hand = st.session_state.hand
    
    for i, card in enumerate(hand):
        with cols[i % 4]:
            # 顯示分數
            label = f"{card.numerator}/{card.denominator}"
            if st.button(f"⚔️ {label}", key=f"card_{i}_{uuid.uuid4()}"):
                attack(i)
                st.rerun()
else:
    # 遊戲結束狀態
    if current == target:
        st.success("🏆 討伐成功！")
        if st.button("繼續冒險 ->", type="primary"):
            restart()
            st.rerun()
    else:
        st.error("💀 討伐失敗...")
        if st.button("重新挑戰", type="primary"):
            # 重置當前局
            st.session_state.current_damage = Fraction(0, 1)
            st.session_state.hand = st.session_state.hand # 這裡簡化，不恢復手牌，直接重開比較快
            init_game() 
            st.rerun()
