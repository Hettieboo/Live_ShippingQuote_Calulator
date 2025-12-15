import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4
from io import BytesIO

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

# ================= CONFIG =================
st.set_page_config(page_title="ShipQuote Pro", page_icon="📦", layout="wide")

# Custom CSS for clean, compact design
st.markdown("""
<style>
    .stApp {
        background: #f8f9fa;
    }
    .lot-card {
        background: white;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0;
        border: 1.5px solid #e0e0e0;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .lot-card:hover {
        border-color: #2d3748;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .lot-card-selected {
        background: #2d3748;
        color: white;
        border-color: #2d3748;
    }
    .lot-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }
    .badge-heavy { background: #e53e3e; color: white; }
    .badge-medium { background: #f6ad55; color: white; }
    .badge-light { background: #48bb78; color: white; }
    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card h4 {
        color: #718096;
        font-size: 0.85rem;
        margin: 0;
        font-weight: 500;
    }
    .metric-card h2, .metric-card h1 {
        color: #2d3748;
        margin: 0.3rem 0 0 0;
    }
    .quote-header {
        background: white;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #2d3748;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    .quote-header h1 {
        color: #2d3748;
        font-size: 1.8rem;
        margin: 0;
    }
    .quote-header p {
        color: #718096;
        margin: 0.3rem 0 0 0;
    }
    .stButton>button {
        background: #2d3748;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #1a202c;
        box-shadow: 0 2px 8px rgba(45, 55, 72, 0.3);
    }
    .stButton>button[kind="secondary"] {
        background: white;
        color: #2d3748;
        border: 1px solid #e0e0e0;
    }
    .stButton>button[kind="secondary"]:hover {
        background: #f8f9fa;
        border-color: #2d3748;
    }
    .address-suggestion {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.6rem;
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
    }
    .address-suggestion:hover {
        border-color: #2d3748;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .section-divider {
        border-top: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    .stSelectbox, .stTextInput {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

PARIS_COORD = (48.8566, 2.3522)
DAYS_LEFT = 7
VALID_UNTIL = datetime.now() + timedelta(days=DAYS_LEFT)

geolocator = Nominatim(user_agent="shipquote_pro")

# ================= DEMO LOT DATA =================
DEMO_LOTS = {
    86: {"weight": "Heavy", "material": "Canvas", "title": "Abstract Expressionism #3", "artist": "Unknown"},
    87: {"weight": "Medium", "material": "Canvas", "title": "Landscape Vista", "artist": "M. Rousseau"},
    88: {"weight": "Medium", "material": "Canvas", "title": "Urban Nocturne", "artist": "K. Tanaka"},
    89: {"weight": "Heavy", "material": "Glass/Steel", "title": "Reflections III", "artist": "L. Fontana"},
    90: {"weight": "Heavy", "material": "Metal", "title": "Kinetic Sculpture", "artist": "A. Calder"},
    91: {"weight": "Medium", "material": "Canvas", "title": "Still Life with Fruit", "artist": "P. Cezanne"},
    92: {"weight": "Heavy", "material": "Canvas", "title": "The Great Wave", "artist": "K. Hokusai"},
    93: {"weight": "Light", "material": "Photograph", "title": "Portrait Series #7", "artist": "A. Adams"},
    94: {"weight": "Light", "material": "Photograph", "title": "Cityscape 2024", "artist": "D. LaChapelle"},
    95: {"weight": "Medium", "material": "Photograph", "title": "Nature's Symmetry", "artist": "S. Gursky"},
}

WEIGHT_MULT = {"Light": 1, "Medium": 1.5, "Heavy": 2}
MATERIAL_MULT = {
    "Canvas": 1,
    "Photograph": 1,
    "Metal": 1.5,
    "Glass/Steel": 1.6,
}

DELIVERY_COST = {
    "Front delivery": 0,
    "White Glove (ground)": 100,
    "White Glove (elevator)": 150,
    "Curbside": -30,
}

PACKING_COST = {
    "Automatic (AI)": 0,
    "Wood crate": 80,
    "Cardboard box": 20,
    "Bubble wrap": 40,
    "Custom": 100,
}

PACKING_TYPES = list(PACKING_COST.keys())
DELIVERY_TYPES = list(DELIVERY_COST.keys())

CURRENCY_RATE = {"EUR": 1, "USD": 1.1, "GBP": 0.85}
CURRENCY_SYMBOL = {"EUR": "€", "USD": "$", "GBP": "£"}

# Function to get address suggestions from Nominatim
def get_address_suggestions(query):
    if not query or len(query) < 3:
        return []
    
    try:
        results = geolocator.geocode(
            query, 
            exactly_one=False, 
            limit=5,
            timeout=3,
            addressdetails=True
        )
        
        if results:
            suggestions = []
            for result in results:
                suggestions.append(result.address)
            return suggestions
        return []
    except Exception as e:
        return []

# ================= AI PACKING =================
def suggest_packing_for_lots(selected_lots):
    if not selected_lots:
        return "Automatic (AI)", "ℹ️ Select lots for packing suggestions"

    suggestions = []
    votes = {}

    for lot in selected_lots:
        info = DEMO_LOTS.get(lot)
        if not info:
            continue

        material = info["material"].lower()

        if any(k in material for k in ["glass", "metal", "steel"]):
            pack = "Wood crate"
            reason = "Fragile / rigid materials"
        elif "photo" in material:
            pack = "Cardboard box"
            reason = "Paper-based artwork"
        else:
            pack = "Automatic (AI)"
            reason = "Standard canvas / mixed media"

        suggestions.append(f"Lot {lot}: {pack} — {reason}")
        votes[pack] = votes.get(pack, 0) + 1

    overall = max(votes, key=votes.get) if votes else "Automatic (AI)"
    explanation = "💡 AI Packing Analysis\n\n" + "\n".join(suggestions)
    explanation += f"\n\n✅ Recommended overall packing: {overall}"

    return overall, explanation

# ================= PRICING =================
def get_distance_and_multiplier(address):
    try:
        loc = geolocator.geocode(address, timeout=4)
        if not loc:
            return 0, 1
        km = geodesic(PARIS_COORD, (loc.latitude, loc.longitude)).km
        if km < 50:
            m = 1
        elif km < 300:
            m = 1.2
        elif km < 1000:
            m = 1.5
        else:
            m = 2
        return round(km), m
    except:
        return 0, 1

def calculate_shipping(lots, packing, delivery, address):
    km, dist_mult = get_distance_and_multiplier(address)
    base = 220
    total = 0
    breakdown = []

    for lot in lots:
        info = DEMO_LOTS[lot]
        price = (
            base
            * WEIGHT_MULT[info["weight"]]
            * MATERIAL_MULT[info["material"]]
            * dist_mult
        )
        price += DELIVERY_COST[delivery] + PACKING_COST[packing]
        total += price
        breakdown.append([f"Lot {lot}", info["weight"], info["material"], f"{price:,.2f}"])

    return total, breakdown, km

# ================= PDF =================
def generate_branded_pdf(
    quote_id,
    client,
    address,
    packing,
    delivery,
    breakdown,
    total,
    currency,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            "<font size=22><b>ShipQuote Pro</b></font><br/>"
            "<font size=10 color='grey'>Fine Art & High-Value Logistics</font>",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 16))

    meta = Table(
        [
            ["Quote ID", quote_id],
            ["Client", client or "—"],
            ["Issued", datetime.now().strftime("%d %b %Y")],
            ["Valid Until", (datetime.now() + timedelta(days=7)).strftime("%d %b %Y")],
        ],
        colWidths=[4 * cm, 10 * cm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(meta)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Shipment Details</b>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Delivery:</b><br/>{address}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Packing:</b> {packing}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Delivery Type:</b> {delivery}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    table = Table(
        [["Lot", "Weight", "Material", "Price (€)"]] + breakdown,
        colWidths=[3 * cm, 3 * cm, 5 * cm, 3 * cm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, None]),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(
        Paragraph(
            f"<font size=14><b>Total Quote: {CURRENCY_SYMBOL[currency]}{total:,.2f}</b></font>",
            styles["Heading1"],
        )
    )

    elements.append(
        Paragraph(
            "<font size=8 color='grey'>Demo quote generated by ShipQuote Pro. "
            "Non-binding and indicative.</font>",
            styles["Normal"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================= UI =================

# Initialize session state
if "quote_id" not in st.session_state:
    st.session_state.quote_id = f"SQ-{uuid4().hex[:8].upper()}"
if "selected_lots" not in st.session_state:
    st.session_state.selected_lots = []
if "address_input" not in st.session_state:
    st.session_state.address_input = ""
if "address_suggestions" not in st.session_state:
    st.session_state.address_suggestions = []
if "show_suggestions" not in st.session_state:
    st.session_state.show_suggestions = True

QUOTE_ID = st.session_state.quote_id

# Header
st.markdown(f"""
<div class="quote-header">
    <h1>📦 ShipQuote Pro</h1>
    <p style="font-size: 0.9rem;">Quote ID: <b>{QUOTE_ID}</b> • Valid for {DAYS_LEFT} days</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.4, 1])

with left:
    st.markdown("#### 🎨 Select Artwork Lots")
    
    # Display lots as compact interactive cards
    cols_per_row = 3
    lot_numbers = list(DEMO_LOTS.keys())
    
    for i in range(0, len(lot_numbers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(lot_numbers):
                lot_num = lot_numbers[i + j]
                lot_info = DEMO_LOTS[lot_num]
                
                with col:
                    is_selected = lot_num in st.session_state.selected_lots
                    
                    weight_class = f"badge-{lot_info['weight'].lower()}"
                    
                    card_html = f"""
                    <div class="lot-card {'lot-card-selected' if is_selected else ''}">
                        <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem;">Lot #{lot_num}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.4rem;">{lot_info['title'][:25]}...</div>
                        <div>
                            <span class="lot-badge {weight_class}">{lot_info['weight']}</span>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    if st.button(
                        "✓" if is_selected else "+",
                        key=f"lot_{lot_num}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        if is_selected:
                            st.session_state.selected_lots.remove(lot_num)
                        else:
                            st.session_state.selected_lots.append(lot_num)
                        st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Compact options in two columns
    st.markdown("#### ⚙️ Shipping Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        suggested_pack, pack_note = suggest_packing_for_lots(st.session_state.selected_lots)
        packing = st.selectbox("📦 Packing", PACKING_TYPES, index=PACKING_TYPES.index(suggested_pack))
    
    with col2:
        delivery = st.selectbox("🚚 Delivery", DELIVERY_TYPES)
    
    # AI Packing suggestion - compact
    with st.expander("💡 AI Recommendation"):
        st.caption(pack_note)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📍 Delivery Details")
    
    # Address input with real-time Nominatim autocomplete
    address_input = st.text_input(
        "Delivery Address",
        value=st.session_state.address_input,
        placeholder="Start typing (e.g., 'Paris', '10 Downing Street')...",
        key="address_text_input"
    )
    
    # Update suggestions when input changes
    if address_input != st.session_state.address_input:
        st.session_state.address_input = address_input
        st.session_state.show_suggestions = True
        
        if len(address_input) >= 3:
            with st.spinner("🔍 Searching addresses..."):
                st.session_state.address_suggestions = get_address_suggestions(address_input)
    
    # Show Nominatim suggestions
    if (st.session_state.show_suggestions and 
        st.session_state.address_suggestions and 
        len(address_input) >= 3):
        
        st.markdown("**Suggestions:**")
        
        for idx, addr in enumerate(st.session_state.address_suggestions):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="address-suggestion">
                    📍 {addr}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✓", key=f"select_addr_{idx}"):
                    st.session_state.address_input = addr
                    st.session_state.show_suggestions = False
                    st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("👤 Client Name", placeholder="Optional")
    with col2:
        currency = st.selectbox("💰 Currency", ["EUR", "USD", "GBP"])
    
    admin = st.toggle("🔧 Admin View")
    if admin:
        margin = st.slider("Margin (%)", 0, 40, 20, help="Add profit margin")
    else:
        margin = 0

with right:
    st.markdown("#### 📊 Quote Summary")
    
    if st.session_state.selected_lots and (address_input or st.session_state.address_input):
        final_address = address_input or st.session_state.address_input
        
        shipping, breakdown, km = calculate_shipping(
            st.session_state.selected_lots, 
            packing, 
            delivery, 
            final_address
        )
        cost = shipping
        client_price = cost * (1 + margin / 100)
        final = client_price * CURRENCY_RATE[currency]
        
        # Compact metrics
        st.markdown(f"""
        <div class="metric-card">
            <h4>Distance from Paris</h4>
            <h2>{km} km</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Quote</h4>
            <h1 style="font-size: 2rem;">{CURRENCY_SYMBOL[currency]}{final:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Selected lots summary - compact
        with st.expander(f"📦 Selected Lots ({len(st.session_state.selected_lots)})", expanded=True):
            for lot in st.session_state.selected_lots:
                info = DEMO_LOTS[lot]
                st.markdown(f"**Lot {lot}:** {info['title']}")
                st.caption(f"{info['weight']} • {info['material']}")
                st.markdown('<div style="height: 0.3rem;"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        if st.button("📥 Generate PDF Quote", use_container_width=True, type="primary"):
            pdf = generate_branded_pdf(
                QUOTE_ID,
                client_name,
                final_address,
                packing,
                delivery,
                breakdown,
                final,
                currency,
            )
            st.download_button(
                "⬇️ Download PDF",
                pdf,
                file_name=f"ShipQuote_{QUOTE_ID}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("👈 Select lots and enter address to generate quote")
        
        st.markdown("**Quick Start:**")
        st.markdown("""
        1. Select artwork lots
        2. Enter delivery address
        3. Choose options
        4. Generate quote
        """)
