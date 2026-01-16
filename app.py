"""
Household Management App - אפליקציית ניהול משק בית
A mobile-first app for Talor and Romi to manage their shared household.
"""

import streamlit as st
from datetime import datetime, timedelta
import database as db

# Initialize database
db.init_database()
db.auto_cleanup_old_items()

# Page config
st.set_page_config(
    page_title="🏠 ניהול משק בית",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
    </style>
"""

# Apply CSS
st.markdown(APP_STYLE, unsafe_allow_html=True)


def login_screen():
    """Displays the Login Form."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 התחברות למערכת</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.markdown("### הכנס פרטים")
            email = st.text_input("אימייל", placeholder="user@example.com")
            password = st.text_input("סיסמה", type="password", placeholder="********")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("התחבר למערכת", use_container_width=True, type="primary")
            
            if submitted:
                # Validation Logic
                if email.lower() == "talor012@gmail.com" and password == "talorromy35":
                    st.session_state['authenticated'] = True
                    st.session_state['current_user'] = "טלאור" 
                    st.toast("התחברת בהצלחה! 🔓", icon="✅")
                    st.rerun()
                else:
                    st.error("❌ שם משתמש או סיסמה שגויים")

def main_app():
    """The Main Application Logic."""
    # Initialize session state for user-specific settings
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'טלאור'

    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = {}

    # --- USER SELECTION BUTTONS ---
    col1, col2 = st.columns([1, 1])
    with col1:
        is_active = st.session_state.current_user == "טלאור"
        if st.button("👨 טלאור", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_user = "טלאור"
            st.rerun()

    with col2:
        is_active = st.session_state.current_user == "רומי"
        if st.button("👩 רומי", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_user = "רומי"
            st.rerun()

    st.caption(f"משתמש פעיל: {st.session_state.current_user}")

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
        
        # Calculate Balance
        raw_balance = db.calculate_balance()
        current_user = st.session_state.current_user
        
        user_balance = -raw_balance if current_user == "טלאור" else raw_balance

        # Determine Status
        card_type = "neutral"
        status_title = "הכל מאוזן"
        amount_display = "✅"
        
        if abs(user_balance) >= 0.01:
            if user_balance > 0:
                card_type = "green"
                other_person = "רומי" if current_user == "טלאור" else "טלאור"
                status_title = f"{other_person} חייב/ת לך"
                amount_display = f"₪{user_balance:.2f}"
            else:
                card_type = "red"
                other_person = "רומי" if current_user == "טלאור" else "טלאור"
                status_title = f"את/ה חייב/ת ל{other_person}"
                amount_display = f"₪{abs(user_balance):.2f}"

        # Render Balance Card
        balance_html = f"""
            <div class="balance-card {card_type}">
                <div class="balance-title">{status_title}</div>
                <div class="balance-amount">{amount_display}</div>
            </div>
        """
        st.markdown(balance_html, unsafe_allow_html=True)
        
        with st.expander("➕ הוסף הוצאה חדשה", expanded=False):
            col1, col2 = st.columns(2)
            with col1: amount = st.number_input("סכום (₪)", min_value=0.0, step=1.0)
            with col2: description = st.text_input("תיאור")
            
            col3, col4 = st.columns(2)
            with col3: payer = st.radio("מי שילם?", ["טלאור", "רומי"], horizontal=True, index=0 if st.session_state.current_user == "טלאור" else 1)
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
                is_my_expense = (ex['payer'] == st.session_state.current_user)
                color = "#2ecc71" if is_my_expense else "#ff4b4b" 
                
                created_dt = datetime.fromisoformat(ex['created_at'])
                date_str = created_dt.strftime("%d/%m/%Y")
                
                with st.container():
                    col1, col2 = st.columns([0.85, 0.15])
                    
                    with col1:
                        # Construct HTML separately to be safe
                        html_card = f"""
                        <div class="custom-card" style="border-right: 5px solid {color}; padding: 15px;">
                            <div class="card-price" style="color: {color}; float: left;">₪{float(ex['amount']):.0f}</div>
                            <div class="card-title" style="margin-right: 0;">{ex['description']}</div>
                            <div class="card-sub">{date_str} • שולם ע"י {ex['payer']}</div>
                            <div style="clear: both;"></div>
                        </div>
                        """
                        st.markdown(html_card, unsafe_allow_html=True)
                    
                    with col2:
                        st.write("")
                        st.write("")
                        with st.popover("⋮", use_container_width=True):
                            st.write("למחוק?")
                            if st.button("מחק", key=f"del_ex_{ex['id']}", type="primary"):
                                db.delete_expense(ex['id'])
                                st.rerun()

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
                            if st.button("✅", key=f"buy_{item['id']}", help="סמן כנקנה"):
                                 db.update_shopping_item(item['id'], bought=True)
                                 st.rerun()
                            
                            with st.popover("⋮"):
                                if st.button("מחק", key=f"del_shop_{item['id']}", type="primary"):
                                    db.delete_shopping_item(item['id'])
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
                    
                    col1, col2, col3 = st.columns([0.65, 0.2, 0.15])
                    with col1:
                        html_card = f"""
                            <div class="custom-card {accent_class}">
                                <div class="card-title">{chore['name']}</div>
                                <div class="card-sub">📅 {chore['due_date'] or 'ללא תאריך'} • {chore['priority'] or 'רגיל'}</div>
                            </div>
                        """
                        st.markdown(html_card, unsafe_allow_html=True)

                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("✅", key=f"do_chore_{chore['id']}", use_container_width=True):
                            db.mark_chore_done(chore['id'], st.session_state.current_user)
                            st.rerun()
                    with col3:
                        st.write("")
                        st.write("")
                        with st.popover("⋮", use_container_width=True):
                            st.write("למחוק?")
                            if st.button("מחק", key=f"del_chore_{chore['id']}", type="primary"):
                                db.delete_chore(chore['id'])
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
                with st.container():
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        meta_parts = [f"📅 {ev['date']}"]
                        if ev['time']: meta_parts.append(f"⏰ {ev['time']}")
                        
                        html_card = f"""
                            <div class="custom-card border-green">
                                <div class="card-title">{ev['title']}</div>
                                <div class="card-sub">{' • '.join(meta_parts)}</div>
                                <div class="card-sub" style="font-size: 13px;">{ev['description'] or ''}</div>
                            </div>
                        """
                        st.markdown(html_card, unsafe_allow_html=True)
                        
                    with col2:
                        st.write("") 
                        st.write("") 
                        with st.popover("⋮", use_container_width=True):
                            st.write("למחוק?")
                            if st.button("מחק", key=f"del_ev_up_{ev['id']}", type="primary"):
                                db.delete_event(ev['id'])
                                st.rerun()
                    st.write("")
        else:
            st.info("אין אירועים קרובים. זמן לנוח! 🏖️")

        if past_events:
            st.subheader("אירועים שזמנם עבר")
            for ev in past_events:
                with st.container():
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"<s style='color: #888;'>{ev['title']}</s>", unsafe_allow_html=True)
                        st.caption(f"{ev['date']} • {ev['time'] or ''}")
                    with col2:
                        with st.popover("⋮", use_container_width=True):
                            st.write("למחוק את ההיסטוריה?")
                            if st.button("מחק", key=f"del_ev_past_{ev['id']}", type="primary"):
                                db.delete_event(ev['id'])
                                st.rerun()
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
                        db.update_cat_task(task['id'], st.session_state.current_user)
                        st.rerun()

    st.divider()

    # ================== RECYCLE BIN ==================
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

if st.session_state["authenticated"]:
    main_app()
else:
    login_screen()
