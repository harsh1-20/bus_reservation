# app.py
import streamlit as st
import base64
from datetime import datetime, timedelta
import random
from utils.auth import signup, login, add_booking, get_user_bookings, get_user_booking_count
from utils.email_sender import send_confirmation_email

# Page configuration
st.set_page_config(
    page_title="ZTravels!",
    page_icon="images/logo_web.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS for two-deck sleeper style seats ---
st.markdown("""
<style>
/* Page & header */
.header {
    text-align: center;
    padding: 18px;
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    color: white;
    border-radius: 12px;
    margin-bottom: 18px;
}

/* Deck container */
.deck {
    background: #ffffff;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

/* Deck title row */
.deck-title {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:10px;
}
.deck-title h3 {
    margin:0;
    font-size:18px;
}

/* Seat grid */
.seat-row {
    display:flex;
    gap:16px;
    margin-bottom:12px;
    align-items:flex-start;
}

/* Seat container (holds price bubble + seat box + button) */
.seat-wrap {
    display:flex;
    flex-direction:column;
    align-items:center;
    width:90px;
}

/* Price bubble */
.price-bubble {
    font-size:12px;
    padding:6px 8px;
    border-radius:12px;
    background:linear-gradient(90deg,#4facfe 0%,#00f2fe 100%);
    color:white;
    margin-bottom:6px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

/* Sleeper seat rectangle */
.seat-rect {
    width:78px;
    height:110px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
    font-size:18px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    position:relative;
}

/* Sold overlay */
.sold-overlay {
    position:absolute;
    inset:0;
    background:rgba(235,235,235,0.85);
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:10px;
    font-weight:700;
    color:#9a9a9a;
}

/* Gender & states */
.seat-male {
    background: linear-gradient(180deg,#2ecc71, #28a745);
    color:white;
    border: 3px solid rgba(0,0,0,0.04);
}

.seat-female {
    background: linear-gradient(180deg,#ff9acb,#ff6aa6);
    color:white;
    border: 3px solid rgba(0,0,0,0.04);
}

.seat-selected {
    background: linear-gradient(180deg,#ffffff,#e6f0ff);
    color:#0b57d0;
    border: 3px solid #0b57d0;
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(11,87,208,0.12);
}

/* small button under seat - keep streamlit default but tighten spacing */
.seat-action {
    margin-top:8px;
}

/* Legend */
.legend {
    display:flex;
    gap:12px;
    align-items:center;
    margin-top:12px;
}
.legend .item {
    display:flex;
    gap:8px;
    align-items:center;
}

/* Responsive small screens */
@media (max-width: 700px) {
    .seat-wrap { width:70px; }
    .seat-rect { width:64px; height:88px; font-size:16px; }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'selected_seats' not in st.session_state:
    st.session_state.selected_seats = []
if 'booking_details' not in st.session_state:
    st.session_state.booking_details = {}
if 'discount_applied' not in st.session_state:
    st.session_state.discount_applied = False
if 'show_party' not in st.session_state:
    st.session_state.show_party = False
if 'discount_percentage' not in st.session_state:
    st.session_state.discount_percentage = 0
if 'final_amount' not in st.session_state:
    st.session_state.final_amount = 0.0

# Ensure booked seats persist for session (random demo)
if 'booked_seats' not in st.session_state:
    random.seed(42)
    # pick about 20% seats as sold -> 30 seats total -> ~6 sold
    st.session_state.booked_seats = set(random.sample(range(1, 31), k=6))

import streamlit as st
import streamlit.components.v1 as components
import re, json
# Diwali discounts (unchanged)
DIWALI_DISCOUNTS = [
    {"code": "DIWALI25", "discount": 25, "description": "Diwali Special - 25% OFF"},
    {"code": "FESTIVE20", "discount": 20, "description": "Festival Bonanza - 20% OFF"},
    {"code": "LIGHTS15", "discount": 15, "description": "Festival of Lights - 15% OFF"},
]


def _id(s: str) -> str:
    # sanitize for use in element ids
    return re.sub(r'[^a-zA-Z0-9_-]', '_', s)

# Cities
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
          "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]

# Bus types (use existing prices; seat count will be fixed to 30)
BUS_TYPES = {
    "Sleeper": {"seats": 40, "price": 800},
    "Seater": {"seats": 50, "price": 600}
}

# ---------- Pages (login, dashboard, booking, confirmation) ----------
def login_page():
    """Login and Signup Page"""
    st.markdown('<div class="header"><h1>ZTrip</h1><p>Find the best bus routes, select your favorite seats, and get ready for an adventure with ZTrip</p></div>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if username and password:
                success, message = login(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields!")

    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone Number", key="signup_phone")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up", key="signup_btn"):
            if new_username and email and phone and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = signup(new_username, email, new_password, phone)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Passwords don't match!")
            else:
                st.warning("Please fill in all fields!")
image_path="C:\\Users\\dell\\OneDrive\\Documents\\bus_system_original\wave_web.jpg"
def add_bg_from_local(image_path):
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            return encoded
    except Exception:
        # If image can't be read, return empty string so CSS falls back gracefully
        return ""

# get encoded string once (prevents NameError)
encoded = add_bg_from_local(image_path)

# apply CSS; if encoded is empty use a safe fallback background
if encoded:
    st.markdown(
        f"""
        <style>
        .header {{
            text-align: center;
            background-image: 
                linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.35)),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            border-radius: 20px;
            padding: 100px 30px;
            color: white;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}

        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}

        .header p {{
            font-size: 1.3rem;
            font-weight: 400;
            color: #f3f3f3;
        }}

        .promo {{
            background: linear-gradient(90deg, #ff8fab, #ffc8dd);
            color: #2b2b2b;
            font-weight: 600;
            border-radius: 10px;
            text-align: center;
            padding: 12px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # fallback CSS if image missing / couldn't be read
    st.markdown(
        """
        <style>
        .header {
            text-align: center;
            background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            border-radius: 20px;
            padding: 60px 30px;
            color: white;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }

        .header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }

        .header p {
            font-size: 1rem;
            font-weight: 400;
            color: #f3f3f3;
        }

        .promo {
            background: linear-gradient(90deg, #ff8fab, #ffc8dd);
            color: #2b2b2b;
            font-weight: 600;
            border-radius: 10px;
            text-align: center;
            padding: 12px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def dashboard():
    """Main Dashboard"""
    st.markdown(
        f"""
    <div class="header" style="text-align:center;">
        <h1>Welcome back, {st.session_state.username}! 👋</h1>
        <p>Ready for your next adventure?</p>
    </div>
    """,
        unsafe_allow_html=True
    )

   # Diwali discount banner
    # Diwali discount banner with golden hour shimmer ✨
    st.markdown("""
<style>
@keyframes glowMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.glow-banner {
    background: linear-gradient(90deg, #ffcf6f, #ffb88c, #f9a826, #ffd27f);
    background-size: 300% 300%;
    animation: glowMove 6s ease-in-out infinite;
    padding: 14px 18px;
    border-radius: 12px;
    color: #3b2f2f;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    margin-bottom: 16px;
}
.glow-banner span {
    font-weight: 500;
}
</style>

<div class="glow-banner">
    <strong>✨ DIWALI GOLDEN HOUR DEALS ✨</strong> 
    <span>Score up to <b>25% OFF</b> on your next trip — glow & go!</span>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)


    with col1:
        st.markdown("""
        <div style="background:white;padding:18px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06);">
            <h3>📅 Book Your Journey</h3>
            <p>Find and book your perfect bus ride</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Book Now", key="book_now_btn"):
            st.session_state.page = 'booking'
            st.rerun()

    with col2:
        bookings = get_user_bookings(st.session_state.username)
        st.markdown(f"""
        <div style="background:white;
                    padding:18px;
                    border-radius:12px;
                    box-shadow:0 6px 18px rgba(0,0,0,0.06);">
            <h3>🎫 My Bookings</h3>
            <p>Total Bookings: {len(bookings)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background:white;
                    padding:18px;
                    border-radius:12px;
                    box-shadow:0 6px 18px rgba(0,0,0,0.06);">
            <h3>💰 Offers</h3>
            <p>Check out amazing deals!</p>
        </div>
        """, unsafe_allow_html=True)

    # Display user bookings
    bookings = get_user_bookings(st.session_state.username)
    if bookings:
        st.subheader("Your Recent Bookings")
        for booking in bookings[-3:]:
            with st.expander(f"Booking: {booking['from_city']} → {booking['to_city']} ({booking['date']})"):
                st.write(f"**Booking ID:** {booking['booking_id']}")
                st.write(f"**Passengers:** {booking['passengers']}")
                st.write(f"**Seats:** {', '.join(map(str, booking['seats']))}")
                st.write(f"**Total Amount:** ₹{booking['total_amount']}")
                st.write(f"**Bus Number:** {booking['bus_number']}")
                st.write(f"**Driver Contact:** {booking['driver_number']}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = 'login'
        st.rerun()


def booking_page():
    """Booking Page with redesigned sleeper two-deck UI (30 seats: 15 lower + 15 upper)"""
    st.markdown('<div class="header"><h1> Book Your Bus Ticket</h1></div>', unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.page = 'dashboard'
        st.session_state.selected_seats = []
        st.session_state.booking_details = {}
        st.rerun()

    # Journey details
    st.subheader("Journey Details")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        from_city = st.selectbox("From", CITIES, key="from_city")

    with col2:
        to_cities = [city for city in CITIES if city != from_city]
        to_city = st.selectbox("To", to_cities, key="to_city")

    with col3:
        min_date = datetime.now().date()
        max_date = min_date + timedelta(days=90)
        travel_date = st.date_input("Date", min_value=min_date, max_value=max_date, key="travel_date")

    with col4:
        passengers = st.number_input("Number of Passengers", min_value=1, max_value=6, value=1, key="passengers")
        if passengers > 6:
            st.error("⚠️ Maximum 6 passengers allowed per booking!")
            passengers = 6

    # Bus type selection (price taken from BUS_TYPES)
    st.subheader("Select Bus Type")
    bus_type = st.radio("Bus Type", list(BUS_TYPES.keys()), horizontal=True, key="bus_type")

    # Seat preferences
    st.subheader("Seat Preferences")
    colA, colB = st.columns(2)
    with colA:
        show_men_seats = st.checkbox("Show Men Seats", value=True, key="show_men")
    with colB:
        show_women_seats = st.checkbox("Show Women Seats", value=True, key="show_women")

    # Diwali discounts display
    DIWALI_DISCOUNTS = [
        {"code": "DIWALI25", "discount": 25, "description": "Diwali Special - 25% OFF"},
        {"code": "FESTIVE20", "discount": 20, "description": "Festival Bonanza - 20% OFF"},
        {"code": "LIGHTS15", "discount": 15, "description": "Festival of Lights - 15% OFF"},
    ]
    
    # --- Render coupon codes with a copy button beside each code ---
    def render_discount_codes(discounts):
        for d in discounts:
            code = d["code"]
            desc = d["description"]
            btn_id = f"btn_{_id(code)}"
            # small HTML row: code + description on left, Copy button on right
            html = f'''
            <div style="display:flex;align-items:center;justify-content:space-between;padding:8px;border-radius:8px;background:#f8fbff;margin-bottom:6px;font-family:inherit">
              <div style="flex:1;display:flex;align-items:center;gap:12px;">
                <strong style="color:#0047ab;font-size:16px;">{code}</strong>
                <span style="color:#333;">{desc}</span>
              </div>
              <button id="{btn_id}" style="padding:6px 10px;border-radius:6px;border:none;background:#0047ab;color:#fff;cursor:pointer">
                Copy
              </button>
            </div>
            <script>
            (function(){{
              const btn = document.getElementById("{btn_id}");
              if(!btn) return;
              btn.addEventListener('click', function() {{
                const text = "{code}";
                if (navigator && navigator.clipboard && navigator.clipboard.writeText) {{
                  navigator.clipboard.writeText(text).then(function() {{
                    const orig = btn.textContent;
                    btn.textContent = '✓ Copied';
                    btn.disabled = true;
                    setTimeout(function(){{ btn.textContent = orig; btn.disabled = false; }}, 1500);
                  }}).catch(function() {{
                    window.prompt('Copy the code:', text);
                  }});
                }} else {{
                  window.prompt('Copy the code:', text);
                }}
              }});
            }})();
            </script>
            '''
            components.html(html, height=72)

    # call the renderer so codes show up with copy buttons beside them
    render_discount_codes(DIWALI_DISCOUNTS)

    # Seat selection UI
    st.subheader(f"Select Your Seats (Sleeper layout)")

    # We'll use 30 seats total (regardless of BUS_TYPES 'seats' count),
    # but per-seat price comes from chosen bus_type
    TOTAL_SEATS = 30
    LOWER_SEATS = list(range(1, 16))   # 1..15
    UPPER_SEATS = list(range(16, 31))  # 16..30
    price_per_seat = BUS_TYPES[bus_type]["price"]

    # Determine female seats deterministically: every 3rd seat (like before)
    def is_female(seat_num):
        return seat_num % 3 == 0

    # Helper to render a deck
    def render_deck(deck_name, seats):
        st.markdown(f'<div class="deck"><div class="deck-title"><h3>{deck_name}</h3><div style="opacity:0.7;font-size:13px;">Driver at front</div></div>', unsafe_allow_html=True)

        # 5 rows x 3 seats = 15 seats per deck (sleeper)
        seats_per_row = 3
        rows = 5

        for r in range(rows):
            # Create a row of seat columns
            cols = st.columns(seats_per_row)
            with st.container():
                # Using markup + Streamlit button per seat
                for c in range(seats_per_row):
                    seat_index = r * seats_per_row + c
                    if seat_index >= len(seats):
                        continue
                    seat_num = seats[seat_index]

                    # booked? selected? female?
                    is_booked = (seat_num in st.session_state.booked_seats)
                    selected = (seat_num in st.session_state.selected_seats)
                    female = is_female(seat_num)

                    # inside each column, display price bubble if selected, seat box, and a toggle button
                    with cols[c]:
                        # price bubble display when selected
                        if selected:
                            st.markdown(f'<div class="price-bubble">₹{price_per_seat}</div>', unsafe_allow_html=True)
                        else:
                            # keep a small spacer for alignment
                            st.write("")

                        # seat box styling
                        if is_booked:
                            st.markdown(
                                f'''
                                <div class="seat-wrap">
                                    <div class="seat-rect seat-male" style="opacity:0.45;">
                                        <div class="sold-overlay">Sold</div>
                                        <div style="position:relative;z-index:2;">{seat_num}</div>
                                    </div>
                                </div>
                                ''',
                                unsafe_allow_html=True)
                        else:
                            if selected:
                                # render selected style
                                st.markdown(
                                    f'''
                                    <div class="seat-wrap">
                                        <div class="seat-rect seat-selected">{seat_num}</div>
                                    </div>
                                    ''',
                                    unsafe_allow_html=True
                                )
                            else:
                                # render male/female unselected
                                if female and show_women_seats:
                                    st.markdown(
                                        f'''
                                        <div class="seat-wrap">
                                            <div class="seat-rect seat-female">{seat_num}</div>
                                        </div>
                                        ''',
                                        unsafe_allow_html=True
                                    )
                                elif (not female) and show_men_seats:
                                    st.markdown(
                                        f'''
                                        <div class="seat-wrap">
                                            <div class="seat-rect seat-male">{seat_num}</div>
                                        </div>
                                        ''',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    # If preference filters hide this seat, show nothing (or small spacer)
                                    st.write("")

                        # Seat action button (select/deselect)
                        if is_booked:
                            # no button for booked seat
                            st.button(" ", key=f"noop_{seat_num}", disabled=True, args=None)
                        else:
                            if selected:
                                if st.button(f"Deselect {seat_num}", key=f"deselect_{seat_num}"):
                                    st.session_state.selected_seats.remove(seat_num)
                                    # reset discount when seats changed
                                    st.session_state.discount_applied = False
                                    st.session_state.discount_percentage = 0
                                    st.session_state.final_amount = 0.0
                                    st.rerun()
                            else:
                                if st.button(f"Select {seat_num}", key=f"select_{seat_num}"):
                                    if len(st.session_state.selected_seats) < passengers:
                                        st.session_state.selected_seats.append(seat_num)
                                        st.rerun()
                                    else:
                                        st.warning(f"You can only select {passengers} seats!")

        st.markdown("</div>", unsafe_allow_html=True)  # close deck div

    # Two columns for Lower and Upper deck
    deck_col1, spacer_col, deck_col2 = st.columns([1, 0.05, 1])

    with deck_col1:
        render_deck("Lower deck", LOWER_SEATS)

    with deck_col2:
        render_deck("Upper deck", UPPER_SEATS)

    # Legend and seat stats
    st.markdown("---")
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div class="legend">
            <div class="item"><div style="width:18px;height:18px;background:#28a745;border-radius:4px;"></div><div style="font-size:13px;">Men</div></div>
            <div class="item"><div style="width:18px;height:18px;background:#ff6aa6;border-radius:4px;"></div><div style="font-size:13px;">Women</div></div>
            <div class="item"><div style="width:18px;height:18px;background:#0b57d0;border-radius:4px;"></div><div style="font-size:13px;">Selected</div></div>
            <div class="item"><div style="width:18px;height:18px;background:#ebebeb;border-radius:4px;border:1px solid #d0d0d0;"></div><div style="font-size:13px;">Sold</div></div>
        </div>
        <div style="font-size:14px;color:#555;">
            <strong>Total seats:</strong> 30 &nbsp;&nbsp; | &nbsp;&nbsp; <strong>Available:</strong> {available_count}
        </div>
    </div>
    """.replace("{available_count}", str(TOTAL_SEATS - len(st.session_state.booked_seats))), unsafe_allow_html=True)

    # Show selected seats and pricing (same logic as your original)
    if st.session_state.selected_seats:
        st.success(f"Selected Seats: {', '.join(map(str, sorted(st.session_state.selected_seats)))}")

        total_amount = price_per_seat * len(st.session_state.selected_seats)

        # Discount code UI
        st.subheader("Apply Discount Code")
        discount_code = st.text_input("Enter Discount Code", key="discount_code")

        if st.button("Apply Discount"):
            discount_found = False
            for discount in DIWALI_DISCOUNTS:
                if discount_code.upper() == discount['code']:
                    discount_found = True
                    discount_amount = (total_amount * discount['discount']) / 100
                    final_amount = total_amount - discount_amount

                    st.session_state.discount_applied = True
                    st.session_state.discount_percentage = discount['discount']
                    st.session_state.final_amount = final_amount
                    st.session_state.show_party = True

                    st.markdown('<div style="text-align:center;font-size:28px;margin-top:6px;">🎉🎊</div>', unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"🎉 {discount['discount']}% discount applied! You saved ₹{discount_amount:.2f}!")
                    break
            if not discount_found:
                st.error("Invalid discount code!")

        # Pricing details
        st.markdown("---")
        st.subheader("Pricing Details")
        colp1, colp2 = st.columns(2)
        with colp1:
            st.write(f"**Base Price per Seat:** ₹{price_per_seat}")
            st.write(f"**Number of Seats:** {len(st.session_state.selected_seats)}")
            st.write(f"**Subtotal:** ₹{total_amount}")
        with colp2:
            if st.session_state.discount_applied:
                st.write(f"**Discount:** {st.session_state.discount_percentage}%")
                st.write(f"**Final Amount:** ₹{st.session_state.final_amount:.2f}")
            else:
                st.write(f"**Final Amount:** ₹{total_amount}")

        # policy box (copied/styled)
        st.markdown("""
    <div style="background: linear-gradient(90deg, #fff7d6, #fff1b8); 
                border-left: 6px solid #ffd43b; 
                padding: 18px 22px; 
                border-radius: 12px; 
                font-family: 'Poppins', sans-serif; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <h4 style="margin-bottom:10px; font-weight:600;">📋 Cancellation & Refund Policy</h4>
        <ul style="margin:0; padding-left:20px; line-height:1.8; font-size:1.05rem;">
            <li><strong>⏰ 24+ hrs left:</strong> You’re chill. Get a <b>full refund</b>, no questions asked.</li>
            <li><strong>🌤 12–24 hrs left:</strong> We’ll send <b>75% back</b> to your account — fair deal 😌</li>
            <li><strong>🌙 6–12 hrs left:</strong> Cutting it close, but you still get <b>50%</b> back.</li>
            <li><strong>🚨 Under 6 hrs:</strong> That’s basically takeoff time 😭 — <b>no refund</b> possible.</li>
        </ul>
        <p style="margin-top:12px; font-size:0.95rem; color:#444;">
            💡 Tip: If plans change, cancel early — more refund for you, less stress for us. Win-win 💛
        </p>
    </div>
    """, unsafe_allow_html=True)


        # Confirm / Modify
        colc1, colc2 = st.columns(2)
        with colc1:
            if st.button("✅ Confirm Booking", key="confirm_booking"):
                booking_id = f"BK{random.randint(100000, 999999)}"
                bus_number = f"BUS-{random.randint(1000, 9999)}"
                driver_number = f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"

                final_amt = st.session_state.final_amount if st.session_state.discount_applied else total_amount

                booking_details = {
                    'booking_id': booking_id,
                    'from_city': from_city,
                    'to_city': to_city,
                    'date': str(travel_date),
                    'passengers': passengers,
                    'seats': sorted(st.session_state.selected_seats),
                    'bus_type': bus_type,
                    'total_amount': final_amt,
                    'discount': st.session_state.discount_percentage if st.session_state.discount_applied else 0,
                    'bus_number': bus_number,
                    'driver_number': driver_number,
                    'payment_mode': 'Cash on Boarding',
                    'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                add_booking(st.session_state.username, booking_details)

                users = __import__('utils.auth', fromlist=['load_users']).load_users()
                user_email = users[st.session_state.username]['email']
                email_result = send_confirmation_email(user_email, booking_details)

                st.session_state.booking_details = booking_details
                st.session_state.email_result = email_result
                st.session_state.page = 'confirmation'
                st.rerun()

        with colc2:
            if st.button("🔄 Modify Booking", key="modify_booking"):
                st.session_state.selected_seats = []
                st.session_state.discount_applied = False
                st.session_state.show_party = False
                st.session_state.discount_percentage = 0
                st.session_state.final_amount = 0.0
                st.rerun()
    else:
        st.info(f"Please select {passengers} seat(s) to continue")


def confirmation_page():
    """Booking Confirmation Page"""
    booking = st.session_state.booking_details

    st.markdown("""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:18px;border-radius:12px;color:white;text-align:center;">
        <h1>🎉 Booking Confirmed! 🎉</h1>
        <h3>Thank You for Choosing Us!</h3>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()

    genz_messages = [
        "Slay your journey, bestie! 💅✨",
        "No cap, this ride gonna be fire! 🔥",
        "Periodt! You're all set to vibe! 💯",
        "Living your best life, one bus ride at a time! 🚌✨",
        "Main character energy activated! 🌟",
        "It's giving adventure vibes! 🎒✨",
        "Understood the assignment! Safe travels! 🙌",
        "That's on period! Have a lit journey! 🔥"
    ]
    st.markdown(f'<div style="font-weight:700;margin-top:12px;font-size:20px;">{random.choice(genz_messages)}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Your Booking Details")

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Booking ID:** {booking['booking_id']}
        
        **From:** {booking['from_city']}
        
        **To:** {booking['to_city']}
        
        **Date:** {booking['date']}
        
        **Passengers:** {booking['passengers']}
        
        **Seats:** {', '.join(map(str, booking['seats']))}
        """)
    with col2:
        st.success(f"""
        **Bus Type:** {booking['bus_type']}
        
        **Bus Number:** {booking['bus_number']}
        
        **Driver Contact:** {booking['driver_number']}
        
        **Total Amount:** ₹{booking['total_amount']}
        
        **Payment Mode:** {booking['payment_mode']}
        """)

    st.markdown("---")
    st.subheader("📧 Email Confirmation")
    if st.session_state.email_result.get('success', False):
        st.success("✅ Confirmation email has been sent to your registered email address!")
    else:
        st.warning("⚠️ Email sending is in demo mode. In production, you'll receive a confirmation email.")

    st.markdown("""
   <div style="background-color:#fff3cd;border-left:5px solid #ffc107;padding:12px;border-radius:6px;">
  <h4>🚌 Quick Ride Rules</h4>
  <ul>
    <li>Arrive <strong>15 mins early</strong></li>
    <li>Carry your <strong>ID</strong></li>
    <li><strong>Cash-only</strong> payment at bus</li>
    <li>Your <strong>Booking ID</strong> = your ticket</li>
  </ul>
</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.session_state.selected_seats = []
            st.session_state.booking_details = {}
            st.session_state.discount_applied = False
            st.rerun()
    with col2:
        if st.button("🎫 Book Another Ticket"):
            st.session_state.page = 'booking'
            st.session_state.selected_seats = []
            st.session_state.booking_details = {}
            st.session_state.discount_applied = False
            st.rerun()


def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.page == 'dashboard':
            dashboard()
        elif st.session_state.page == 'booking':
            booking_page()
        elif st.session_state.page == 'confirmation':
            confirmation_page()


if __name__ == "__main__":
    main()
