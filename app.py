"""
Household Management App - אפליקציית ניהול משק בית
A mobile-first app for Talor and Romi to manage their shared household.
"""

import streamlit as st
from datetime import datetime, timedelta
import database as db

# Initialize database
db.init_database()

# Page config
st.set_page_config(
    page_title="🏠 ניהול משק בית",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-first design with RTL support
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* ============= VIEWPORT & OVERFLOW FIX ============= */
    
    html, body {
        overflow-x: hidden !important;
        width: 100% !important;
        max-width: 100vw !important;
    }
    
    * {
        box-sizing: border-box !important;
    }
    
    /* ============= MOBILE-FIRST BASE STYLES ============= */
    
    /* Force RTL on entire app */
    html, body, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        direction: rtl !important;
    }
    
    /* Main container - prevent overflow */
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
        padding: 0.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
        overflow-x: hidden !important;
    }
    
    [data-testid="stAppViewContainer"] {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ============= BUTTONS - TOUCH FRIENDLY ============= */
    
    .stButton > button {
        direction: rtl !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        min-height: 44px !important;
        touch-action: manipulation !important;
    }
    
    /* ============= INPUTS - MOBILE OPTIMIZED ============= */
    
    .stTextInput > div, .stNumberInput > div, .stSelectbox > div,
    .stTextArea > div, .stDateInput > div, .stTimeInput > div {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px !important;
        padding: 0.75rem !important;
        min-height: 44px !important;
    }
    
    /* ============= CHECKBOXES - LARGER TAP TARGETS ============= */
    
    .stCheckbox > label {
        direction: rtl !important;
        font-size: 1rem !important;
        padding: 0.5rem 0 !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* ============= RADIO BUTTONS ============= */
    
    .stRadio > div {
        direction: rtl !important;
    }
    
    .stRadio label {
        direction: rtl !important;
        font-size: 0.95rem !important;
    }
    
    /* ============= TABS - MOBILE FRIENDLY ============= */
    
    .stTabs, [data-baseweb="tab-list"] {
        direction: rtl !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 12px !important;
        font-size: 0.8rem !important;
        min-height: 44px !important;
        white-space: nowrap !important;
    }
    
    /* ============= EXPANDERS ============= */
    
    .streamlit-expanderHeader, [data-testid="stExpander"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ============= COLUMNS - FORCE INLINE & PREVENT OVERFLOW ============= */
    
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
        align-items: center !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }
    
    [data-testid="column"] {
        direction: rtl !important;
        text-align: right !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }
    
    /* ============= CARDS ============= */
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        direction: rtl;
        text-align: right;
    }
    
    .balance-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    
    .balance-card.negative {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .balance-amount {
        font-size: 1.75rem;
        font-weight: bold;
    }
    
    /* ============= STATUS INDICATORS ============= */
    
    .status-ok {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    
    .status-alert {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .notification-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.4rem;
        animation: pulse 2s infinite;
        text-align: center;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .event-soon {
        border-right: 4px solid #ff6b6b !important;
        background: #fff5f5;
    }
    
    .stMarkdown, .stCaption {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ============= MOBILE SPECIFIC ============= */
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.25rem !important;
        }
        
        .stButton > button {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.9rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 10px !important;
            font-size: 0.75rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'טלאור'

if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = {}

# Header with user selection
st.markdown("# 🏠 ניהול משק בית")

# User selector
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("👤 טלאור", use_container_width=True, 
                 type="primary" if st.session_state.current_user == "טלאור" else "secondary"):
        st.session_state.current_user = "טלאור"
        st.rerun()
with col2:
    if st.button("👤 רומי", use_container_width=True,
                 type="primary" if st.session_state.current_user == "רומי" else "secondary"):
        st.session_state.current_user = "רומי"
        st.rerun()

st.markdown(f"**משתמש פעיל:** {st.session_state.current_user}")

# Global cat care notifications
overdue_cat_tasks = db.get_overdue_cat_tasks()
if overdue_cat_tasks:
    for task in overdue_cat_tasks:
        st.markdown(f"""
        <div class="notification-banner">
            🔔 {task['task_name']} דורש טיפול!
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Get counts for badges
urgent_events_count = db.get_urgent_events_count()
overdue_cat_count = len(overdue_cat_tasks) if overdue_cat_tasks else 0

# Build tab names with badges
events_tab_name = f"📅 אירועים ({urgent_events_count})" if urgent_events_count > 0 else "📅 אירועים"
cat_tab_name = f"🐱 טיפול ({overdue_cat_count})" if overdue_cat_count > 0 else "🐱 טיפול בחתול"

# Navigation using Streamlit's built-in tabs - Expenses first
tab_expenses, tab_shopping, tab_chores, tab_events, tab_cat = st.tabs([
    "💰 הוצאות", "🛒 קניות", "✅ משימות", events_tab_name, cat_tab_name
])

# ================== SHOPPING LIST TAB ==================
with tab_shopping:
    st.markdown("### 🛒 רשימת קניות")
    
    # Add new item
    with st.expander("➕ הוסף פריט חדש", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            item_name = st.text_input("שם הפריט", key="new_item_name")
        with col2:
            quantity = st.text_input("כמות", value="1", key="new_item_qty")
        category = st.selectbox("קטגוריה", [
            "🥛 מוצרי חלב", "🥬 ירקות", "🍎 פירות", "🥩 בשר ודגים",
            "🍞 מאפים", "🧹 ניקיון", "🧴 טיפוח", "🏠 לבית", "📦 אחר"
        ])
        if st.button("הוסף פריט", use_container_width=True, type="primary"):
            if item_name:
                db.add_shopping_item(item_name, category, quantity)
                st.success(f"נוסף: {item_name}")
                st.rerun()
            else:
                st.warning("נא להזין שם פריט")
    
    # Display items grouped by category
    items = db.get_all_shopping_items()
    
    if items:
        categories = {}
        for item in items:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        col1, col2 = st.columns(2)
        with col2:
            if st.button("🗑️ נקה פריטים שנקנו", use_container_width=True):
                db.clear_bought_items()
                st.rerun()
        
        for category, cat_items in sorted(categories.items()):
            st.markdown(f"**{category}**")
            for item in cat_items:
                is_bought = bool(item['bought'])
                qty = item['quantity'] if item['quantity'] else "1"
                
                # Use horizontal_layout with checkbox and button side by side
                cols = st.columns([0.8, 0.2])
                with cols[0]:
                    label = f"~~{item['name']} ({qty})~~" if is_bought else f"{item['name']} ({qty})"
                    if st.checkbox(label, value=is_bought, key=f"shop_{item['id']}"):
                        if not is_bought:
                            db.update_shopping_item(item['id'], bought=True)
                            st.rerun()
                    else:
                        if is_bought:
                            db.update_shopping_item(item['id'], bought=False)
                            st.rerun()
                with cols[1]:
                    st.button("🗑", key=f"del_shop_{item['id']}", on_click=lambda i=item['id']: db.delete_shopping_item(i) or st.rerun())
    else:
        st.info("רשימת הקניות ריקה. הוסף פריטים!")
    
    with st.expander("📦 היסטוריית קניות", expanded=False):
        archive_shopping = db.get_archive_shopping()
        if archive_shopping:
            for item in archive_shopping[:20]:
                st.caption(f"{item['name']} ({item['quantity']}) • {item['category']} • {item['action']}")
        else:
            st.caption("אין היסטוריה")


# ================== EXPENSES TAB ==================
with tab_expenses:
    st.markdown("### 💰 הוצאות")
    
    balance = db.calculate_balance()
    current_user = st.session_state.current_user
    
    if abs(balance) < 0.01:
        st.markdown("""
        <div class="balance-card">
            <div>מאזן</div>
            <div class="balance-amount">✅ מאוזן!</div>
            <div>אף אחד לא חייב</div>
        </div>
        """, unsafe_allow_html=True)
    elif balance > 0:
        if current_user == "טלאור":
            st.markdown(f"""
            <div class="balance-card negative">
                <div>מאזן</div>
                <div class="balance-amount">₪{balance:.2f}</div>
                <div>אתה חייב לרומי</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="balance-card">
                <div>מאזן</div>
                <div class="balance-amount">₪{balance:.2f}</div>
                <div>טלאור חייב לך</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        if current_user == "רומי":
            st.markdown(f"""
            <div class="balance-card negative">
                <div>מאזן</div>
                <div class="balance-amount">₪{abs(balance):.2f}</div>
                <div>את חייבת לטלאור</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="balance-card">
                <div>מאזן</div>
                <div class="balance-amount">₪{abs(balance):.2f}</div>
                <div>רומי חייבת לך</div>
            </div>
            """, unsafe_allow_html=True)
    
    if 'expense_form_key' not in st.session_state:
        st.session_state.expense_form_key = 0
    
    with st.expander("➕ הוסף הוצאה חדשה", expanded=False):
        form_key = st.session_state.expense_form_key
        amount = st.number_input("סכום (₪)", min_value=0.0, step=1.0, format="%.2f", 
                                  key=f"expense_amount_{form_key}", value=0.0)
        description = st.text_input("תיאור", key=f"expense_desc_{form_key}", value="")
        
        # Auto-select current user as payer, but allow changing
        payer_options = ["טלאור", "רומי"]
        default_index = 0 if current_user == "טלאור" else 1
        payer = st.radio("מי שילם?", payer_options, horizontal=True, 
                         key=f"expense_payer_{form_key}", index=default_index)
        
        split_type = st.radio("חלוקה", ["50/50", "מותאם אישית"], horizontal=True, key=f"expense_split_{form_key}")
        
        if split_type == "מותאם אישית":
            col1, col2 = st.columns(2)
            with col1:
                talor_pct = st.slider("טלאור %", 0, 100, 50, key=f"expense_talor_pct_{form_key}")
            with col2:
                st.markdown(f"**רומי: {100-talor_pct}%**")
            talor_share = amount * talor_pct / 100
            romi_share = amount * (100 - talor_pct) / 100
        else:
            talor_share = amount / 2
            romi_share = amount / 2
        
        if st.button("הוסף הוצאה", use_container_width=True, type="primary", key=f"add_expense_btn_{form_key}"):
            if amount > 0 and description:
                db.add_expense(amount, description, payer, split_type, talor_share, romi_share)
                st.success("ההוצאה נוספה!")
                st.session_state.expense_form_key += 1
                st.rerun()
            else:
                st.warning("נא להזין סכום ותיאור")
    
    if 'edit_expense_id' not in st.session_state:
        st.session_state.edit_expense_id = None
    
    st.markdown("#### הוצאות אחרונות")
    expenses = db.get_all_expenses()
    
    if expenses:
        for expense in expenses[:15]:
            expense_id = expense['id']
            
            if st.session_state.edit_expense_id == expense_id:
                st.markdown("---")
                st.markdown("**✏️ עריכת הוצאה**")
                new_desc = st.text_input("תיאור", value=expense['description'], key=f"edit_desc_{expense_id}")
                new_amount = st.number_input("סכום (₪)", value=float(expense['amount']), 
                                              min_value=0.0, step=1.0, key=f"edit_amount_{expense_id}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 שמור", key=f"save_edit_{expense_id}", use_container_width=True, type="primary"):
                        db.update_expense(expense_id, amount=new_amount, description=new_desc)
                        st.session_state.edit_expense_id = None
                        st.success("ההוצאה עודכנה!")
                        st.rerun()
                with col2:
                    if st.button("❌ ביטול", key=f"cancel_edit_{expense_id}", use_container_width=True):
                        st.session_state.edit_expense_id = None
                        st.rerun()
                st.markdown("---")
            else:
                with st.container():
                    col1, col2, col3 = st.columns([0.55, 0.25, 0.20])
                    
                    # Color based on payer
                    is_my_expense = expense['payer'] == current_user
                    color = "#28a745" if is_my_expense else "#dc3545"  # Green if mine, red if other's
                    
                    with col1:
                        st.markdown(f"**{expense['description']}**")
                        try:
                            created = datetime.fromisoformat(expense['created_at'])
                            date_str = created.strftime("%d/%m/%Y")
                        except:
                            date_str = ""
                        st.caption(f"📅 {date_str} • שולם ע״י {expense['payer']} • {expense['split_type']}")
                    with col2:
                        st.markdown(f"<span style='color: {color}; font-weight: bold; font-size: 1.1rem;'>₪{expense['amount']:.2f}</span>", unsafe_allow_html=True)
                    with col3:
                        if st.button("✏️", key=f"edit_exp_{expense_id}", help="ערוך"):
                            st.session_state.edit_expense_id = expense_id
                            st.rerun()
                        
                        if st.session_state.delete_confirm.get(expense_id, False):
                            if st.button("✅", key=f"confirm_del_{expense_id}", help="אישור מחיקה"):
                                db.delete_expense(expense_id)
                                st.session_state.delete_confirm[expense_id] = False
                                st.rerun()
                            if st.button("❌", key=f"cancel_del_{expense_id}", help="ביטול"):
                                st.session_state.delete_confirm[expense_id] = False
                                st.rerun()
                        else:
                            st.markdown('<div class="small-delete-btn">', unsafe_allow_html=True)
                            if st.button("🗑", key=f"del_exp_{expense_id}", help="מחק"):
                                st.session_state.delete_confirm[expense_id] = True
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
    else:
        st.info("אין הוצאות עדיין.")
    
    with st.expander("📦 היסטוריית הוצאות שנמחקו", expanded=False):
        archive_expenses = db.get_archive_expenses()
        if archive_expenses:
            for item in archive_expenses[:20]:
                st.caption(f"₪{item['amount']:.2f} • {item['description']} • {item['payer']} • {item['action']}")
        else:
            st.caption("אין היסטוריה")


# ================== EVENTS TAB ==================
with tab_events:
    st.markdown("### 📅 אירועים ותזכורות")
    
    reminder_events = db.get_events_needing_reminder()
    if reminder_events:
        st.warning(f"🔔 יש {len(reminder_events)} אירועים מחר!")
        for event in reminder_events:
            st.info(f"📢 תזכורת: {event['title']} - מחר בשעה {event['time'] or 'כל היום'}")
    
    with st.expander("➕ הוסף אירוע חדש", expanded=False):
        title = st.text_input("כותרת האירוע", key="event_title")
        event_date = st.date_input("תאריך", value=datetime.today(), key="event_date")
        event_time = st.time_input("שעה", value=datetime.now().replace(hour=12, minute=0), key="event_time")
        description = st.text_area("תיאור (אופציונלי)", height=80, key="event_desc")
        
        preview_emoji = db.get_event_emoji(title, description)
        st.caption(f"אימוג'י אוטומטי: {preview_emoji}")
        
        if st.button("הוסף אירוע", use_container_width=True, type="primary", key="add_event_btn"):
            if title:
                db.add_event(title, event_date.isoformat(), event_time.strftime("%H:%M"), description)
                st.success("האירוע נוסף!")
                st.rerun()
            else:
                st.warning("נא להזין כותרת")
    
    events = db.get_all_events()
    now = datetime.now()
    
    if events:
        st.markdown("#### אירועים קרובים")
        for event in events:
            event_datetime_str = f"{event['date']} {event['time'] or '00:00'}"
            try:
                event_dt = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
            except:
                event_dt = datetime.strptime(event['date'], "%Y-%m-%d")
            
            is_soon = now <= event_dt <= now + timedelta(hours=24)
            is_past = event_dt < now
            event_emoji = db.get_event_emoji(event['title'], event['description'])
            
            if is_soon:
                st.markdown(f"""
                <div class="card event-soon">
                    <strong>⚠️ {event_emoji} {event['title']}</strong><br>
                    📆 {event['date']} • 🕐 {event['time'] or 'כל היום'}<br>
                    <small>{event['description'] or ''}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✅ הושלם", key=f"complete_event_{event['id']}", use_container_width=True):
                    db.delete_event(event['id'])
                    st.rerun()
            elif is_past:
                with st.container():
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"~~{event_emoji} **{event['title']}**~~ (עבר)")
                        st.caption(f"📆 {event['date']} • 🕐 {event['time'] or 'כל היום'}")
                    with col2:
                        if st.button("🗑️", key=f"del_event_{event['id']}"):
                            db.delete_event(event['id'])
                            st.rerun()
            else:
                with st.container():
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"**{event_emoji} {event['title']}**")
                        st.caption(f"📆 {event['date']} • 🕐 {event['time'] or 'כל היום'}")
                        if event['description']:
                            st.caption(event['description'])
                    with col2:
                        if st.button("🗑️", key=f"del_event_{event['id']}"):
                            db.delete_event(event['id'])
                            st.rerun()
            st.divider()
    else:
        st.info("אין אירועים מתוכננים. הוסף את האירוע הראשון!")
    
    with st.expander("📦 היסטוריית אירועים", expanded=False):
        archive_events = db.get_archive_events()
        if archive_events:
            for item in archive_events[:20]:
                st.caption(f"{item['title']} • {item['date']} • {item['action']}")
        else:
            st.caption("אין היסטוריה")


# ================== CHORES TAB ==================
with tab_chores:
    st.markdown("### ✅ משימות בית")
    
    with st.expander("➕ הוסף משימה חדשה", expanded=False):
        new_chore = st.text_input("שם המשימה", key="chore_name")
        col1, col2 = st.columns(2)
        with col1:
            urgency = st.selectbox("רמת דחיפות", ["רגיל", "נמוך", "גבוה", "דחוף"], key="chore_urgency")
        with col2:
            due_date = st.date_input("תאריך יעד (אופציונלי)", value=None, key="chore_due_date")
        
        if st.button("הוסף משימה", use_container_width=True, type="primary", key="add_chore_btn"):
            if new_chore:
                due_date_str = due_date.isoformat() if due_date else None
                db.add_chore(new_chore, urgency, due_date_str)
                st.success(f"נוסף: {new_chore}")
                st.rerun()
            else:
                st.warning("נא להזין שם משימה")
    
    chores = db.get_all_chores()
    
    if chores:
        st.markdown("#### משימות פתוחות")
        
        urgency_icons = {
            "דחוף": "🔴",
            "גבוה": "🟠", 
            "רגיל": "🔵",
            "נמוך": "⚪"
        }
        
        for chore in chores:
            with st.container():
                urgency_icon = urgency_icons.get(chore['urgency'], "🔵")
                
                col1, col2, col3 = st.columns([0.55, 0.30, 0.15])
                
                with col1:
                    st.markdown(f"**{urgency_icon} {chore['name']}**")
                    info_parts = []
                    if chore['urgency']:
                        info_parts.append(f"דחיפות: {chore['urgency']}")
                    if chore['due_date']:
                        info_parts.append(f"עד: {chore['due_date']}")
                    if info_parts:
                        st.caption(" • ".join(info_parts))
                
                with col2:
                    if st.button("✅ סיימתי", key=f"do_chore_{chore['id']}", use_container_width=True):
                        db.mark_chore_done(chore['id'], st.session_state.current_user)
                        st.rerun()
                
                with col3:
                    if st.button("🗑", key=f"del_chore_{chore['id']}", help="מחק"):
                        db.delete_chore(chore['id'])
                        st.rerun()
                
                st.divider()
    else:
        st.info("אין משימות פתוחות. הוסף משימה חדשה!")
    
    with st.expander("📦 היסטוריית משימות", expanded=False):
        archive_chores = db.get_archive_chores()
        if archive_chores:
            for item in archive_chores[:20]:
                done_info = f" • ע״י {item['done_by']}" if item['done_by'] else ""
                st.caption(f"{item['name']} • {item['action']}{done_info}")
        else:
            st.caption("אין היסטוריה")


# ================== CAT CARE TAB ==================
with tab_cat:
    st.markdown("### 🐱 מרכז טיפול בחתול")
    
    # Check for overdue tasks and show notifications
    overdue_tasks = db.get_overdue_cat_tasks()
    if overdue_tasks:
        for task in overdue_tasks:
            st.markdown(f"""
            <div class="notification-banner">
                🔔 התראה: {task['task_name']} דורש טיפול!
            </div>
            """, unsafe_allow_html=True)
    
    # Time unit multipliers
    time_units = {"שעות": 1, "ימים": 24, "שבועות": 168, "חודשים": 720}
    
    # Add new task
    with st.expander("➕ הוסף משימת טיפול חדשה", expanded=False):
        new_task_name = st.text_input("שם המשימה", key="new_cat_task")
        col1, col2 = st.columns([1, 1])
        with col1:
            new_freq_value = st.number_input("כמות", min_value=1, value=1, key="new_cat_freq_val")
        with col2:
            new_freq_unit = st.selectbox("יחידת זמן", list(time_units.keys()), key="new_cat_freq_unit")
        
        # Calculate hours
        new_frequency_hours = new_freq_value * time_units[new_freq_unit]
        st.caption(f"תדירות: כל {new_freq_value} {new_freq_unit} ({new_frequency_hours} שעות)")
        
        if st.button("הוסף משימה", key="add_cat_task_btn", use_container_width=True, type="primary"):
            if new_task_name:
                db.add_cat_task(new_task_name, new_frequency_hours)
                st.success(f"נוסף: {new_task_name}")
                st.rerun()
    
    # Initialize edit state
    if 'edit_cat_id' not in st.session_state:
        st.session_state.edit_cat_id = None
    
    tasks = db.get_all_cat_tasks()
    
    for task in tasks:
        is_overdue = db.is_cat_task_overdue(task['last_done_at'], task['frequency_hours'])
        
        if is_overdue:
            status_html = '<span class="status-alert">🔴 דחוף!</span>'
            card_style = "border-right: 4px solid #dc3545;"
        else:
            status_html = '<span class="status-ok">🟢 תקין</span>'
            card_style = "border-right: 4px solid #28a745;"
        
        if task['last_done_at']:
            last_done = datetime.fromisoformat(task['last_done_at'])
            hours_ago = (datetime.now() - last_done).total_seconds() / 3600
            if hours_ago < 1:
                time_ago = f"לפני {int(hours_ago * 60)} דקות"
            elif hours_ago < 24:
                time_ago = f"לפני {int(hours_ago)} שעות"
            else:
                time_ago = f"לפני {int(hours_ago / 24)} ימים"
            done_by = task['done_by'] or "לא ידוע"
        else:
            time_ago = "מעולם לא"
            done_by = "-"
        
        task_icon = "🚰" if "מים" in task['task_name'] else "🍽️" if "אוכל" in task['task_name'] else "🧹"
        
        # Edit mode
        if st.session_state.edit_cat_id == task['id']:
            st.markdown("---")
            st.markdown(f"**✏️ עריכת: {task['task_name']}**")
            edit_name = st.text_input("שם", value=task['task_name'], key=f"edit_cat_name_{task['id']}")
            
            # Convert current hours to best unit for display
            current_hours = task['frequency_hours']
            if current_hours >= 720 and current_hours % 720 == 0:
                default_val, default_unit_idx = current_hours // 720, 3  # months
            elif current_hours >= 168 and current_hours % 168 == 0:
                default_val, default_unit_idx = current_hours // 168, 2  # weeks
            elif current_hours >= 24 and current_hours % 24 == 0:
                default_val, default_unit_idx = current_hours // 24, 1  # days
            else:
                default_val, default_unit_idx = current_hours, 0  # hours
            
            col1, col2 = st.columns([1, 1])
            with col1:
                edit_freq_val = st.number_input("כמות", min_value=1, value=int(default_val), key=f"edit_cat_freq_val_{task['id']}")
            with col2:
                edit_freq_unit = st.selectbox("יחידת זמן", list(time_units.keys()), index=default_unit_idx, key=f"edit_cat_freq_unit_{task['id']}")
            
            edit_freq_hours = edit_freq_val * time_units[edit_freq_unit]
            st.caption(f"תדירות: כל {edit_freq_val} {edit_freq_unit} ({edit_freq_hours} שעות)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 שמור", key=f"save_cat_{task['id']}", use_container_width=True, type="primary"):
                    db.edit_cat_task(task['id'], edit_name, edit_freq_hours)
                    st.session_state.edit_cat_id = None
                    st.rerun()
            with col2:
                if st.button("❌ ביטול", key=f"cancel_cat_{task['id']}", use_container_width=True):
                    st.session_state.edit_cat_id = None
                    st.rerun()
            st.markdown("---")
        else:
            # Display mode
            st.markdown(f"""
            <div class="card" style="{card_style}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1.1rem;">{task_icon} {task['task_name']}</strong>
                    {status_html}
                </div>
                <div style="color: #666; margin-top: 0.5rem;">
                    <small>תדירות: כל {task['frequency_hours']} שעות</small><br>
                    <small>בוצע לאחרונה: {time_ago} ע״י {done_by}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            with col1:
                if st.button(f"✅ בוצע", key=f"cat_{task['id']}", use_container_width=True):
                    db.update_cat_task(task['id'], st.session_state.current_user)
                    st.success(f"{task['task_name']} סומן כבוצע!")
                    st.rerun()
            with col2:
                if st.button("✏️", key=f"edit_cat_{task['id']}", help="ערוך"):
                    st.session_state.edit_cat_id = task['id']
                    st.rerun()
            with col3:
                if st.button("🗑", key=f"del_cat_{task['id']}", help="מחק"):
                    db.delete_cat_task(task['id'])
                    st.rerun()
        
        st.markdown("")


# Footer
st.markdown("---")
st.caption(f"🏠 ניהול משק בית • משתמש פעיל: {st.session_state.current_user}")

