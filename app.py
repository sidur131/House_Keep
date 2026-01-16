"""
Household Management App - אפליקציית ניהול משק בית
A mobile-first app for Talor and Romi to manage their shared household.
"""

import streamlit as st
from datetime import datetime, timedelta
import database as db
import streamlit.components.v1 as components

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="🏠 ניהול משק בית",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize database
db.init_database()
db.auto_cleanup_old_items()

# --- CSS VARIABLES (Safe handling to avoid SyntaxErrors) ---
APP_STYLE = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;900&display=swap');

        /* Global Reset */
        .stApp {
            direction: rtl;
            font-family: 'Heebo', sans-serif;
            background-color: #eef2f5;
        }

        /* Hide Streamlit Elements */
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 6rem;}

        /* THE CARD DESIGN */
        .custom-card {
            background: white;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 5px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border-right: 5px solid #ff4b4b; /* Default accent */
            transition: transform 0.2s;
        }
        .custom-card:hover {
            transform: translateY(-3px);
        }

        /* Typography */
        .card-title { font-size: 18px; font-weight: 900; color: #333; margin: 0; line-height: 1.2;}
        .card-sub { font-size: 14px; color: #888; margin-top: 5px; font-weight: 400;}
        .card-price { font-size: 20px; font-weight: 800; color: #2ecc71; direction: ltr; display: inline-block; margin-right: 25px !important;}
        
        /* Specific Accents */
        .border-green { border-right-color: #2ecc71 !important; }
        .border-blue { border-right-color: #3498db !important; }
        .border-orange { border-right-color: #f39c12 !important; }
        .border-gray { border-right-color: #95a5a6 !important; }

        /* Input Styling Override */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox, .stTimeInput input, div[data-baseweb="select"] {
            background-color: #fff !important;
            border: 2px solid #eef2f5 !important;
            border-radius: 12px !important;
            padding: 10px !important;
            box-shadow: none !important;
            direction: rtl; 
            text-align: right;
        }
        
        /* Button Styling */
        .stButton>button {
            border-radius: 12px !important;
            height: 50px !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        
        /* Notifications */
        .notification-banner {
            background: #333;
            color: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        /* Balance Card */
        .balance-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 25px;
            text-align: center;
            box-shadow: 0 15px 30px rgba(118, 75, 162, 0.4);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        .balance-card::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            transform: rotate(45deg);
        }
        .balance-amount { font-size: 3.5rem; font-weight: 900; }
        
        .row-widget.stButton { margin: 0 !important; }
        .stRadio label { direction: rtl; text-align: right; }

        /* ===== NUCLEAR OPTION: Hide Header, Resurrect Button ===== */
        
        /* 1. Hide the standard Streamlit Header Container entirely */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            border-bottom: none !important;
            visibility: hidden !important; /* Hides everything including decorations */
        }

        /* 2. Bring back ONLY the Sidebar Toggle Button */
        [data-testid="stSidebarCollapsedControl"] {
            visibility: visible !important; /* Override parent hiding */
            display: block !important;
            
            /* Position it cleanly */
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            left: auto !important;
            z-index: 999999 !important; /* Top of the world */
            
            /* Button Styling */
            background-color: white !important;
            width: 50px !important;
            height: 50px !important;
            border-radius: 50% !important; /* Perfect Circle */
            box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
            border: 1px solid #f0f0f0 !important;
            
            /* Flex to center the icon */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s ease !important;
        }

        /* Hover Effect */
        [data-testid="stSidebarCollapsedControl"]:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.2) !important;
        }

        /* 3. Hide the default chevron icon inside the button */
        [data-testid="stSidebarCollapsedControl"] svg, 
        [data-testid="stSidebarCollapsedControl"] img {
            display: none !important;
        }

        /* 4. Inject the Clean Hamburger Icon */
        [data-testid="stSidebarCollapsedControl"]::after {
            content: "☰" !important;
            font-size: 24px !important;
            color: #333 !important;
            font-weight: bold !important;
            margin-top: -2px !important;
        }

        /* 5. Ensure the Sidebar content itself (when open) is RTL */
        section[data-testid="stSidebar"] > div {
            direction: rtl;
        }

        /* ===== Sidebar Panel Styling ===== */
        [data-testid="stSidebar"] {
            right: 0 !important;
            left: auto !important;
            border-left: 1px solid #ddd !important;
            border-right: none !important;
            background: #fafafa !important;
        }

        /* Sidebar close button (X icon) */
        [data-testid="stSidebar"] button[kind="header"] {
            position: absolute !important;
            left: 10px !important;
            right: auto !important;
            top: 10px !important;
            background: white !important;
            border: 1px solid #eee !important;
            color: transparent !important;
            width: 36px !important;
            height: 36px !important;
            border-radius: 50% !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }

        [data-testid="stSidebar"] button[kind="header"] svg {
            display: none !important;
        }

        [data-testid="stSidebar"] button[kind="header"]::before {
            content: "✕" !important;
            font-size: 18px !important;
            color: #666 !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
        }

        [data-testid="stSidebar"] button[kind="header"]:hover::before {
            color: #e74c3c !important;
        }
    </style>
"""

# Apply CSS
st.markdown(APP_STYLE, unsafe_allow_html=True)


def set_auth_cookie():
    """Set authentication cookie via JavaScript (30 days)."""
    js_code = """
    <script>
        document.cookie = "household_auth=authenticated; max-age=2592000; path=/; SameSite=Lax";
    </script>
    """
    components.html(js_code, height=0)

def check_auth_cookie():
    """Check for authentication cookie via query params workaround."""
    # Since we can't read cookies directly in Streamlit, we use localStorage + query params
    pass  # We'll handle this differently

# PIN Pad CSS Styles
PIN_PAD_STYLE = """
<style>
    .pin-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        margin-top: 20px;
    }
    .pin-title {
        font-size: 2rem;
        font-weight: 900;
        color: #333;
        margin-bottom: 10px;
        text-align: center;
    }
    .pin-subtitle {
        font-size: 1rem;
        color: #888;
        margin-bottom: 30px;
        text-align: center;
    }
    .pin-dots {
        display: flex;
        gap: 15px;
        margin-bottom: 40px;
        direction: ltr;
    }
    .pin-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid #667eea;
        background: transparent;
        transition: all 0.2s ease;
    }
    .pin-dot.filled {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #764ba2;
    }
    .pin-error {
        color: #e74c3c;
        font-size: 0.9rem;
        margin-top: -20px;
        margin-bottom: 20px;
        animation: shake 0.5s ease;
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* FORCE horizontal columns on mobile for PIN pad */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        direction: ltr !important;
    }
    
    /* PIN pad button styling */
    div[data-testid="stHorizontalBlock"] [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
        min-width: 0 !important;
        padding: 5px !important;
    }
    
    /* iPhone-style circular buttons */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        height: 70px !important;
        border-radius: 50% !important;
        font-size: 28px !important;
        font-weight: 300 !important;
        background-color: #f0f0f0 !important;
        border: none !important;
        box-shadow: none !important;
        color: #333 !important;
        padding: 0 !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background-color: #e0e0e0 !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:active {
        background-color: #d0d0d0 !important;
    }
</style>
"""

def login_screen():
    """Simple PIN Login Screen."""
    
    # Custom styling for login
    st.markdown("""
    <style>
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            text-align: center;
        }
        .login-title {
            font-size: 2rem;
            font-weight: 900;
            color: #333;
            margin-bottom: 10px;
        }
        .login-subtitle {
            font-size: 1rem;
            color: #888;
            margin-bottom: 30px;
        }
        /* Style the password input */
        .stTextInput > div > div > input {
            text-align: center !important;
            font-size: 24px !important;
            letter-spacing: 8px !important;
            padding: 15px !important;
            border-radius: 12px !important;
        }
    </style>
    <div class="login-container">
        <div class="login-title">🔐 הכנס קוד</div>
        <div class="login-subtitle">הקש את קוד הגישה בן 6 הספרות</div>
    </div>
    """, unsafe_allow_html=True)
    
    CORRECT_PIN = "151215"
    
    # Password input
    pin_input = st.text_input(
        "קוד גישה",
        type="password",
        max_chars=6,
        placeholder="••••••",
        label_visibility="collapsed"
    )
    
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔓 כניסה", use_container_width=True, type="primary"):
            if pin_input == CORRECT_PIN:
                st.session_state['authenticated'] = True
                st.session_state['set_cookie'] = True
                st.toast("התחברת בהצלחה! 🔓", icon="✅")
                st.rerun()
            else:
                st.error("❌ קוד שגוי, נסה שוב")


def handle_pin_press(digit: str, correct_pin: str):
    """Handle PIN digit press with auto-submit on 6 digits."""
    st.session_state.pin_error = False
    
    if len(st.session_state.pin_input) < 6:
        st.session_state.pin_input += digit
        
        # Check if PIN is complete (6 digits)
        if len(st.session_state.pin_input) == 6:
            if st.session_state.pin_input == correct_pin:
                # Correct PIN - Login success!
                st.session_state['authenticated'] = True
                st.session_state['set_cookie'] = True  # Flag to set cookie
                st.session_state.pin_input = ""
                st.toast("התחברת בהצלחה! 🔓", icon="✅")
            else:
                # Wrong PIN
                st.session_state.pin_error = True
                st.session_state.pin_input = ""
        
        st.rerun()


def main_app():
    """The Main Application Logic."""
    # Initialize session state
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = {}
    
    # --- APP HEADER WITH STYLED LOGO ---
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    ">
        <div style="font-size: 50px; margin-bottom: 5px;">🏠</div>
        <div style="color: white; font-size: 1.5rem; font-weight: 900;">משק הבית שלנו</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">טלאור ורומי ❤️</div>
    </div>
    """, unsafe_allow_html=True)

    # --- EDIT MODE TOGGLE (Top Right Button) ---
    edit_col1, edit_col2 = st.columns([0.85, 0.15])
    with edit_col2:
        edit_mode = st.session_state.get('edit_mode', False)
        if st.button("✏️ עריכה" if not edit_mode else "✅ סיום", key="edit_mode_toggle", use_container_width=True):
            st.session_state['edit_mode'] = not edit_mode
            st.rerun()
    
    if st.session_state.get('edit_mode', False):
        st.info("מצב עריכה פעיל - ניתן למחוק ולערוך פריטים")

    # --- GLOBAL ALERTS ---
    overdue_cat_tasks = db.get_overdue_cat_tasks()
    if overdue_cat_tasks:
        for task in overdue_cat_tasks:
            st.markdown(f"""<div class="notification-banner">🔔 {task['task_name']} דורש טיפול!</div>""", unsafe_allow_html=True)

    st.divider()

    # --- GLOBAL DAILY ALERTS (EVENTS & CHORES) ---
    today_alerts = []
    now = datetime.now()
    today_str = now.date().isoformat()
    current_time_str = now.strftime("%H:%M")

    event_count = 0
    chore_count = 0

    # 1. Events Today (Future Only)
    all_events_alert = db.get_all_events()
    for ev in all_events_alert:
        try:
            if ev['date'] == today_str:
                # Check time conditions
                is_future_event = False
                if not ev['time']: is_future_event = True # All day
                elif ev['time'] > current_time_str: is_future_event = True
                
                if is_future_event:
                    time_part = f" ב-{ev['time']}" if ev['time'] else ""
                    today_alerts.append(f"🎉 אירוע היום: **{ev['title']}**{time_part}")
                    event_count += 1
        except: pass

    # 2. Chores Due Today (Active Only)
    all_chores_alert = db.get_all_chores()
    for ch in all_chores_alert:
        try:
            if not ch['done'] and ch['due_date'] == today_str:
                 today_alerts.append(f"✅ משימה להיום: **{ch['name']}**")
                 chore_count += 1
        except: pass

    if today_alerts:
        banner_title = []
        if event_count: banner_title.append(f"{event_count} אירועים נותרו היום")
        if chore_count: banner_title.append(f"{chore_count} משימות להיום")
        
        st.warning(f"🔔 **{' | '.join(banner_title)}**\n\n" + "\n".join([f"- {alert}" for alert in today_alerts]))
        
    st.divider()
    urgent_events_count = db.get_urgent_events_count()
    overdue_cat_count = len(overdue_cat_tasks) if overdue_cat_tasks else 0

    # --- NAVIGATION CONFIG ---
    TAB_EXPENSES = "expenses"
    TAB_SHOPPING = "shopping"
    TAB_CHORES = "chores"
    TAB_EVENTS = "events"
    TAB_CAT = "cat"

    TABS = [TAB_EXPENSES, TAB_SHOPPING, TAB_CHORES, TAB_EVENTS, TAB_CAT]

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = TAB_EXPENSES

    def get_tab_label(key):
        if key == TAB_EXPENSES: return "💰 הוצאות"
        elif key == TAB_SHOPPING: return "🛒 קניות"
        elif key == TAB_CHORES: return "✅ משימות"
        elif key == TAB_EVENTS: return f"📅 אירועים ({urgent_events_count})" if urgent_events_count else "📅 אירועים"
        elif key == TAB_CAT: return f"🐱 טיפול ({overdue_cat_count})" if overdue_cat_count else "🐱 טיפול"
        return key

    # Navigation Bar (Persistent)
    try:
        current_index = TABS.index(st.session_state.active_tab)
    except ValueError:
        current_index = 0
        st.session_state.active_tab = TABS[0]

    selected_tab = st.radio(
        "ניווט", TABS, index=current_index, format_func=get_tab_label,
        horizontal=True, label_visibility="collapsed", key="nav_radio"
    )
    st.session_state.active_tab = selected_tab

    st.divider()

    # ================== EXPENSES TAB ==================
    if st.session_state.active_tab == TAB_EXPENSES:
        st.header("הוצאות")
        
        # Calculate Balance - Absolute display
        raw_balance = db.calculate_balance()
        # raw_balance > 0 means Talor paid more (Romi owes Talor)
        # raw_balance < 0 means Romi paid more (Talor owes Romi)
        
        # Determine Status
        status_title = "הכל מאוזן ✅"
        amount_display = "₪0"
        card_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        
        if abs(raw_balance) >= 0.01:
            if raw_balance > 0:
                # Talor paid more - Romi owes Talor
                status_title = "רומי חייבת לטלאור"
                amount_display = f"₪{raw_balance:.2f}"
                card_bg = "linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)"
            else:
                # Romi paid more - Talor owes Romi
                status_title = "טלאור חייב לרומי"
                amount_display = f"₪{abs(raw_balance):.2f}"
                card_bg = "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)"

        # Render Balance Card
        balance_html = f"""
            <div style="background: {card_bg}; color: white; padding: 30px; border-radius: 25px; text-align: center; box-shadow: 0 15px 30px rgba(0,0,0,0.2); margin-bottom: 30px; position: relative; overflow: hidden;">
                <div style="font-size: 1.2rem; opacity: 0.9;">{status_title}</div>
                <div style="font-size: 3.5rem; font-weight: 900;">{amount_display}</div>
            </div>
        """
        st.markdown(balance_html, unsafe_allow_html=True)
        
        with st.expander("➕ הוסף הוצאה חדשה", expanded=False):
            col1, col2 = st.columns(2)
            with col1: amount = st.number_input("סכום (₪)", min_value=0.0, step=1.0)
            with col2: description = st.text_input("תיאור")
            
            col3, col4 = st.columns(2)
            with col3: payer = st.radio("מי שילם?", ["טלאור", "רומי"], horizontal=True, index=0)
            with col4: split = st.radio("חלוקה", ["שווה בשווה", "מלא עליי", "מלא עליו/ה"], horizontal=True)
            
            if st.button("שמור הוצאה", type="primary", use_container_width=True):
                if amount > 0 and description:
                    # Calculate Shares
                    t_share, r_share = 0.0, 0.0
                    if split == "שווה בשווה":
                        t_share = amount / 2
                        r_share = amount / 2
                    elif split == "מלא עליי":
                        if payer == "טלאור": 
                            t_share = amount; r_share = 0
                        else:
                            r_share = amount; t_share = 0
                    else: # Full on Other
                        if payer == "טלאור":
                            t_share = 0; r_share = amount
                        else:
                            r_share = 0; t_share = amount
                    
                    db.add_expense(amount, description, payer, split, t_share, r_share)
                    st.success("נוסף בהצלחה!")
                    st.rerun()
                else:
                    st.warning("נא למלא סכום ותיאור")
        
        # Recent Expenses List
        st.subheader("פירוט אחרון")
        expenses = db.get_all_expenses()
        if expenses:
            for ex in expenses:
                created_dt = datetime.fromisoformat(ex['created_at'])
                date_str = created_dt.strftime("%d/%m/%Y")
                time_str = created_dt.strftime("%H:%M")
                
                # Build the HTML card
                html_card = f"""
                <div class="custom-card border-blue" style="padding: 15px;">
                    <div class="card-price" style="color: #3498db; float: left;">₪{float(ex['amount']):.0f}</div>
                    <div class="card-title" style="margin-right: 0;">{ex['description']}</div>
                    <div class="card-sub">{date_str} • {time_str} • שולם ע"י {ex['payer']}</div>
                    <div style="clear: both;"></div>
                </div>
                """
                
                if st.session_state.get('edit_mode', False):
                    # EDIT MODE ON: Show Card + Delete Button
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(html_card, unsafe_allow_html=True)
                    with col2:
                        st.write("")
                        st.write("")
                        with st.popover("🗑️", use_container_width=True):
                            st.write("למחוק?")
                            if st.button("מחק", key=f"del_ex_{ex['id']}", type="primary"):
                                db.delete_expense(ex['id'])
                                st.rerun()
                else:
                    # EDIT MODE OFF: Show Card ONLY (No columns needed)
                    st.markdown(html_card, unsafe_allow_html=True)

    # ================== SHOPPING LIST TAB ==================
    elif st.session_state.active_tab == TAB_SHOPPING:
        st.header("רשימת קניות 🛒")
        
        with st.expander("➕ הוסף פריט חדש", expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1: new_item = st.text_input("שם הפריט")
            with col2: item_qty = st.text_input("כמות", value="1")
            item_cat = st.selectbox("קטגוריה", ["🥛 מוצרי חלב", "🥬 ירקות", "🍎 פירות", "🥩 בשר ודגים", "🍞 מאפים", "🧹 ניקיון", "🧴 טיפוח", "🏠 לבית", "🍬 מתוקים וחטיפים", "📦 אחר"])
            
            if st.button("הוסף פריט", type="primary", use_container_width=True):
                if new_item:
                    db.add_shopping_item(new_item, item_cat, item_qty)
                    st.success(f"נוסף: {new_item}")
                    st.rerun()
        
        items = db.get_all_shopping_items()
        if not items:
            st.info("הרשימה ריקה. הוסף פריטים! 📝")
        else:
            active = [i for i in items if not i['bought']]
            bought = [i for i in items if i['bought']]
            
            if active:
                categories = {}
                for item in active:
                    cat = item['category']
                    if cat not in categories: categories[cat] = []
                    categories[cat].append(item)
                
                for category, cat_items in categories.items():
                    st.markdown(f"##### {category}")
                    for item in cat_items:
                        if st.session_state.get('edit_mode'):
                            # Edit mode: show card + delete button
                            col1, col2 = st.columns([0.85, 0.15])
                            with col1:
                                html_card = f"""
                                <div class="custom-card border-green" style="padding: 15px; margin-bottom: 5px;">
                                    <div class="card-title" style="font-size: 16px;">{item['name']} 
                                        <span style="color:#2ecc71; font-weight:400;">({item['quantity']})</span>
                                    </div>
                                </div>
                                """
                                st.markdown(html_card, unsafe_allow_html=True)
                            with col2:
                                with st.popover("🗑️"):
                                    if st.button("מחק", key=f"del_shop_{item['id']}", type="primary"):
                                        db.delete_shopping_item(item['id'])
                                        st.rerun()
                        else:
                            # Normal mode: clicking the item marks it as bought
                            if st.button(f"🛒 {item['name']} ({item['quantity']})", key=f"buy_{item['id']}", use_container_width=True):
                                db.update_shopping_item(item['id'], bought=True)
                                st.rerun()
                        st.write("") 
            else:
                 if not bought: st.info("אין פריטים לקנייה כרגע")

            if bought:
                st.markdown("### נאסף בסל 🧺")
                if st.button("נקה סל (מחק שנקנו)", use_container_width=True):
                    db.clear_bought_items()
                    st.rerun()
                for item in bought:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1: st.markdown(f"~~{item['name']}~~")
                    with col2:
                        if st.button("↩️", key=f"ret_{item['id']}"):
                            db.update_shopping_item(item['id'], bought=False)
                            st.rerun()
        
        with st.expander("📦 היסטוריה", expanded=False):
            archive = db.get_archive_shopping()
            if archive:
                for item in archive[:10]: st.caption(f"{item['name']} • {item['action']}")

    # ================== CHORES TAB ==================
    elif st.session_state.active_tab == TAB_CHORES:
        st.header("משימות בית ✅")
        
        with st.expander("➕ הוסף משימה חדשה", expanded=False):
            c_name = st.text_input("שם המשימה")
            col1, col2 = st.columns(2)
            with col1: c_priority = st.selectbox("עדיפות", ["Regular 🔵", "Urgent 🔴"], index=0)
            with col2: c_due_date = st.date_input("תאריך יעד", value=None)
            
            if st.button("הוסף משימה", type="primary", use_container_width=True):
                if c_name:
                    due_str = c_due_date.isoformat() if c_due_date else None
                    db.add_chore(c_name, c_priority, due_str)
                    st.success("נוסף בהצלחה!")
                    st.rerun()
                else: st.warning("נא להזין שם משימה")
        
        chores = db.get_all_chores()
        
        active_chores = [c for c in chores if not c['done']]
        done_chores = [c for c in chores if c['done']]

        if not active_chores:
            if not done_chores:
                st.info("אין משימות. הוסף משימה חדשה! ✨")
            else:
                st.success("אין משימות פתוחות! כל הכבוד! 🎉")
        else:
            st.subheader("משימות פתוחות")
            for chore in active_chores:
                with st.container():
                    accent_class = "border-blue"
                    if chore['priority']:
                        if "🔴" in chore['priority']: accent_class = "border-orange"
                    
                    priority_emoji = "🔴" if chore['priority'] and "🔴" in chore['priority'] else "🔵"
                    due_text = chore['due_date'] or 'ללא תאריך'
                    
                    if st.session_state.get('edit_mode'):
                        # Edit mode: show card + delete button
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            html_card = f"""
                                <div class="custom-card {accent_class}">
                                    <div class="card-title">{chore['name']}</div>
                                    <div class="card-sub">📅 {due_text} • {priority_emoji}</div>
                                </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)
                        with col2:
                            st.write("")
                            st.write("")
                            with st.popover("🗑️", use_container_width=True):
                                st.write("למחוק?")
                                if st.button("מחק", key=f"del_chore_{chore['id']}", type="primary"):
                                    db.delete_chore(chore['id'])
                                    st.rerun()
                    else:
                        # Normal mode: clicking the task marks it as done
                        if st.button(f"{priority_emoji} {chore['name']} (📅 {due_text})", key=f"do_chore_{chore['id']}", use_container_width=True):
                            db.mark_chore_done(chore['id'], "מישהו")
                            st.rerun()
                    st.write("")

        if done_chores:
            st.subheader("משימות שבוצעו")
            for chore in done_chores:
                with st.container():
                    col1, col2 = st.columns([0.75, 0.25])
                    with col1:
                        st.markdown(f"<s style='color: #888;'>{chore['name']}</s>", unsafe_allow_html=True)
                        if chore['done_by']:
                            st.caption(f"בוצע ע״י {chore['done_by']}")
                    with col2:
                        if st.button("↩️ החזר", key=f"undo_chore_{chore['id']}", use_container_width=True):
                            db.mark_chore_undone(chore['id'])
                            st.rerun()
                st.divider()

    # ================== EVENTS TAB ==================
    elif st.session_state.active_tab == TAB_EVENTS:
        st.header("אירועים")

        if 'default_event_time' not in st.session_state:
            st.session_state.default_event_time = datetime.now().time()

        with st.expander("➕ הוסף אירוע חדש", expanded=False):
            e_title = st.text_input("שם האירוע", placeholder="לדוגמה: יום הולדת ל...")
            col1, col2 = st.columns(2)
            with col1: e_date = st.date_input("תאריך", value=datetime.today())
            with col2: e_time = st.time_input("שעה", value=st.session_state.default_event_time, step=timedelta(minutes=1))
            e_notes = st.text_area("הערות (אופציונלי)", height=70)
            
            if st.button("שמור אירוע", type="primary", use_container_width=True):
                if e_title and e_date:
                    time_str = e_time.strftime("%H:%M")
                    date_str = e_date.isoformat()
                    db.add_event(e_title, date_str, time_str, e_notes)
                    st.success("אירוע נשמר בהצלחה! 📅")
                    st.rerun()
                else:
                    st.warning("נא להזין כותרת ותאריך")

        all_events = db.get_all_events()
        upcoming_events = []
        past_events = []
        now = datetime.now()

        for ev in all_events:
            try:
                ev_date = datetime.fromisoformat(ev['date']).date()
                if ev['time']:
                    ev_time_obj = datetime.strptime(ev['time'], "%H:%M").time()
                else:
                    ev_time_obj = datetime.min.time()
                
                ev_datetime = datetime.combine(ev_date, ev_time_obj)
                
                if ev_datetime < now:
                     past_events.append(ev)
                else:
                     upcoming_events.append(ev)

            except ValueError:
                upcoming_events.append(ev)

        st.subheader(f"אירועים קרובים ({len(upcoming_events)})")
        if upcoming_events:
            for ev in upcoming_events:
                # Build the HTML card
                meta_parts = [f"📅 {ev['date']}"]
                if ev['time']: meta_parts.append(f"⏰ {ev['time']}")
                
                html_card = f"""
                    <div class="custom-card border-green">
                        <div class="card-title">{ev['title']}</div>
                        <div class="card-sub">{' • '.join(meta_parts)}</div>
                        <div class="card-sub" style="font-size: 13px;">{ev['description'] or ''}</div>
                    </div>
                """
                
                if st.session_state.get('edit_mode', False):
                    # EDIT MODE ON: Show Card + Delete Button
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(html_card, unsafe_allow_html=True)
                    with col2:
                        st.write("") 
                        st.write("") 
                        with st.popover("🗑️", use_container_width=True):
                            st.write("למחוק?")
                            if st.button("מחק", key=f"del_ev_up_{ev['id']}", type="primary"):
                                db.delete_event(ev['id'])
                                st.rerun()
                else:
                    # EDIT MODE OFF: Show Card ONLY
                    st.markdown(html_card, unsafe_allow_html=True)
                st.write("")
        else:
            st.info("אין אירועים קרובים. זמן לנוח! 🏖️")

        if past_events:
            st.subheader("אירועים שזמנם עבר")
            for ev in past_events:
                if st.session_state.get('edit_mode', False):
                    # EDIT MODE ON: Show content + Delete Button
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"<s style='color: #888;'>{ev['title']}</s>", unsafe_allow_html=True)
                        st.caption(f"{ev['date']} • {ev['time'] or ''}")
                    with col2:
                        with st.popover("🗑️", use_container_width=True):
                            st.write("למחוק את ההיסטוריה?")
                            if st.button("מחק", key=f"del_ev_past_{ev['id']}", type="primary"):
                                db.delete_event(ev['id'])
                                st.rerun()
                else:
                    # EDIT MODE OFF: Show content ONLY
                    st.markdown(f"<s style='color: #888;'>{ev['title']}</s>", unsafe_allow_html=True)
                    st.caption(f"{ev['date']} • {ev['time'] or ''}")
                st.divider()

    # ================== CAT CARE TAB ==================
    elif st.session_state.active_tab == TAB_CAT:
        st.header("מרכז טיפול בחתול 🐱")
        
        if overdue_cat_tasks: st.error(f"התראה: {len(overdue_cat_tasks)} משימות לטיפול!")
        else: st.success("הכל מטופל! 😺")

        time_units = {"שעות": 1, "ימים": 24, "שבועות": 168, "חודשים": 720}

        with st.expander("➕ הוסף משימת טיפול", expanded=False):
            new_task_name = st.text_input("שם", key="new_cat_task")
            col1, col2 = st.columns([1, 1])
            with col1: new_val = st.number_input("כמות", min_value=1, value=1, key="n_cv")
            with col2: new_unit = st.selectbox("יחידה", list(time_units.keys()), key="n_cu")
            
            hours = new_val * time_units[new_unit]
            
            if st.button("הוסף", key="add_cat_btn", use_container_width=True, type="primary"):
                if new_task_name:
                    db.add_cat_task(new_task_name, hours)
                    st.success("נוסף!")
                    st.rerun()
        
        if 'edit_cat_id' not in st.session_state: st.session_state.edit_cat_id = None
            
        tasks = db.get_all_cat_tasks()
        for task in tasks:
            if st.session_state.edit_cat_id == task['id']:
                st.markdown("---")
                st.markdown(f"**✏️ עריכה: {task['task_name']}**")
                ed_name = st.text_input("שם", value=task['task_name'], key=f"ed_cn_{task['id']}")
                
                cur_hrs = task['frequency_hours']
                if cur_hrs >= 720 and cur_hrs % 720 == 0: d_v, d_u = cur_hrs // 720, 3
                elif cur_hrs >= 168 and cur_hrs % 168 == 0: d_v, d_u = cur_hrs // 168, 2
                elif cur_hrs >= 24 and cur_hrs % 24 == 0: d_v, d_u = cur_hrs // 24, 1
                else: d_v, d_u = cur_hrs, 0
                
                c1, c2 = st.columns([1, 1])
                with c1: ed_val = st.number_input("כמות", value=int(d_v), key=f"ed_cv_{task['id']}")
                with c2: ed_unit = st.selectbox("יחידה", list(time_units.keys()), index=d_u, key=f"ed_cu_{task['id']}")
                
                new_hrs = ed_val * time_units[ed_unit]
                
                if st.button("שמור", key=f"sv_c_{task['id']}", type="primary"):
                    db.edit_cat_task(task['id'], ed_name, new_hrs)
                    st.session_state.edit_cat_id = None
                    st.rerun()
                if st.button("ביטול", key=f"cn_c_{task['id']}"):
                    st.session_state.edit_cat_id = None
                    st.rerun()
                st.markdown("---")
            else:
                is_overdue = db.is_cat_task_overdue(task['last_done_at'], task['frequency_hours'])
                status_text = "דחוף!" if is_overdue else "תקין"
                status_color = "#dc3545" if is_overdue else "#28a745"
                
                last_done_text = "טרם בוצע"
                if task['last_done_at']:
                    dt = datetime.fromisoformat(task['last_done_at'])
                    hrs = (datetime.now() - dt).total_seconds() / 3600
                    if hrs < 1: last_done_text = f"לפני {int(hrs*60)} דקות"
                    elif hrs < 24: last_done_text = f"לפני {int(hrs)} שעות"
                    else: last_done_text = f"לפני {int(hrs/24)} ימים"
                    if task['done_by']: last_done_text += f" ({task['done_by']})"

                html_card = f"""
                <div style="border: 1px solid #ddd; border-radius: 12px; padding: 15px; margin-bottom: 10px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="background-color: {status_color}; color: white; padding: 2px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">{status_text}</div>
                        <div style="text-align: left;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{task['task_name']}</span>
                             <span style="font-size: 1.2rem;">🐱</span>
                        </div>
                    </div>
                    <div style="text-align: left; font-size: 0.9rem; color: #666; direction: rtl;">
                        <div>תדירות: כל {task['frequency_hours']} שעות</div>
                        <div>בוצע לאחרונה: {last_done_text}</div>
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Show edit/delete only in edit mode
                if st.session_state.get('edit_mode'):
                    c1, c2, c3 = st.columns([0.15, 0.15, 0.7])
                    with c1:
                        with st.popover("🗑️"):
                            st.write("למחוק?")
                            if st.button("כן", key=f"del_cat_{task['id']}", type="primary"):
                                db.delete_cat_task(task['id'])
                                st.rerun()
                    with c2:
                        if st.button("✏️", key=f"ed_cat_{task['id']}"):
                            st.session_state.edit_cat_id = task['id']
                            st.rerun()
                    with c3:
                        if st.button("בוצע ✅", key=f"do_cat_{task['id']}", use_container_width=True):
                            db.update_cat_task(task['id'], "מישהו")
                            st.rerun()
                else:
                    # Clean view - only show "Done" button
                    if st.button("בוצע ✅", key=f"do_cat_{task['id']}", use_container_width=True):
                        db.update_cat_task(task['id'], "מישהו")
                        st.rerun()

    st.divider()

    # ================== RECYCLE BIN (Only in Edit Mode) ==================
    if st.session_state.get('edit_mode'):
        with st.expander("🗑️ סל מחזור (פריטים שנמחקו)", expanded=False):
            deleted_items = db.get_deleted_items()
            if not deleted_items:
                st.info("סל המחזור ריק")
            else:
                st.write("ניתן לשחזר פריטים שנמחקו בטעות:")
                for item in deleted_items:
                    c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                    with c1:
                        st.write(f"**{item['name']}** ({item['type_name']})")
                    with c2:
                        if st.button("♻️ שחזר", key=f"rest_{item['table_name']}_{item['id']}"):
                            db.restore_item(item['table_name'], item['id'])
                            st.rerun()
                    with c3:
                         if st.button("❌", key=f"perm_{item['table_name']}_{item['id']}", help="מחיקה לצמיתות"):
                            db.permanently_delete_item(item['table_name'], item['id'])
                            st.rerun()
                    st.divider()

# --- MAIN EXECUTION FLOW ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Check query params for auth token (set by JavaScript on page load)
query_params = st.query_params
if "auth" in query_params and query_params["auth"] == "ok":
    st.session_state["authenticated"] = True

# Set cookie if just logged in
if st.session_state.get('set_cookie', False):
    set_auth_cookie()
    st.session_state['set_cookie'] = False

if st.session_state["authenticated"]:
    main_app()
else:
    login_screen()
