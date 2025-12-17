import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4
from io import BytesIO
import pandas as pd

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

# Custom CSS
st.markdown("""
<style>
    .stApp { background: #f8f9fa; }
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
    .metric-card h2 {
        color: #2d3748;
        margin: 0.3rem 0 0 0;
        font-size: 1.5rem;
    }
    .metric-card h1 {
        color: #2d3748;
        margin: 0.3rem 0 0 0;
        font-size: 2rem;
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
        font-size: 0.9rem;
    }
    .lot-compact-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
    }
    .lot-compact-card h4 {
        color: #2d3748;
        margin: 0 0 0.3rem 0;
        font-size: 0.95rem;
    }
    .lot-compact-card p {
        color: #718096;
        margin: 0.2rem 0;
        font-size: 0.85rem;
    }
    .badge-heavy { 
        background: #e53e3e; 
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-medium { 
        background: #f6ad55; 
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-light { 
        background: #48bb78; 
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .stButton>button {
        background: #2d3748;
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        width: 100%;
    }
    .stButton>button:hover {
        background: #1a202c;
    }
</style>
""", unsafe_allow_html=True)

PARIS_COORD = (48.8566, 2.3522)
DAYS_LEFT = 7

geolocator = Nominatim(user_agent="shipquote_pro")

# ================= DEMO LOT DATA =================
DEMO_LOTS = {
    86: {"weight": "Heavy", "material": "Canvas", "title": "Abstract Expressionism #3", "artist": "J. Basquiat"},
    87: {"weight": "Medium", "material": "Canvas", "title": "Landscape Vista", "artist": "M. Rousseau"},
    88: {"weight": "Medium", "material": "Canvas", "title": "Urban Nocturne", "artist": "K. Tanaka"},
    89: {"weight": "Heavy", "material": "Glass/Steel", "title": "Reflections III", "artist": "L. Fontana"},
    90: {"weight": "Heavy", "material": "Metal", "title": "Kinetic Sculpture", "artist": "A. Calder"},
    91: {"weight": "Medium", "material": "Canvas", "title": "Still Life with Fruit", "artist": "P. Cezanne"},
    92: {"weight": "Heavy", "material": "Canvas", "title": "The Great Wave", "artist": "K. Hokusai"},
    93: {"weight": "Light", "material": "Photograph", "title": "Portrait Series #7", "artist": "A. Adams"},
    94: {"weight": "Light", "material": "Photograph", "title": "Cityscape 2024", "artist": "D. LaChapelle"},
    95: {"weight": "Medium", "material": "Photograph", "title": "Nature's Symmetry", "artist": "A. Gursky"},
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

# ================= HELPER FUNCTIONS =================
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
        elif "photo" in material:
            pack = "Cardboard box"
        else:
            pack = "Automatic (AI)"

        votes[pack] = votes.get(pack, 0) + 1

    overall = max(votes, key=votes.get) if votes else "Automatic (AI)"
    return overall, f"💡 Recommended: {overall}"

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

def generate_branded_pdf(quote_id, client, address, packing, delivery, breakdown, total, currency):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<font size=22><b>ShipQuote Pro</b></font><br/><font size=10 color='grey'>Fine Art & High-Value Logistics</font>", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Quote metadata table
    meta = Table([
        ["Quote ID", quote_id],
        ["Client", client or "—"],
        ["Issued", datetime.now().strftime("%d %b %Y")],
        ["Valid Until", (datetime.now() + timedelta(days=7)).strftime("%d %b %Y")],
    ], colWidths=[4*cm, 10*cm])
    meta.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(meta)
    elements.append(Spacer(1, 20))

    # Shipment details
    elements.append(Paragraph("<b>Shipment Details</b>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Delivery:</b><br/>{address}", styles["Normal"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Packing:</b> {packing}", styles["Normal"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Delivery Type:</b> {delivery}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Breakdown table
    table = Table([["Lot", "Weight", "Material", "Price (€)"]] + breakdown, colWidths=[3*cm, 3*cm, 5*cm, 3*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, None]),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    # Total
    elements.append(Paragraph(f"<font size=14><b>Total Quote: {CURRENCY_SYMBOL[currency]}{total:,.2f}</b></font>", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    # Footer
    elements.append(Paragraph("<font size=8 color='grey'>Demo quote generated by ShipQuote Pro. Non-binding and indicative.</font>", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================= UI =================
if "quote_id" not in st.session_state:
    st.session_state.quote_id = f"SQ-{uuid4().hex[:8].upper()}"
if "selected_lots" not in st.session_state:
    st.session_state.selected_lots = []

QUOTE_ID = st.session_state.quote_id

# Header
st.markdown(f"""
<div class="quote-header">
    <h1>📦 ShipQuote Pro</h1>
    <p>Quote ID: <b>{QUOTE_ID}</b> • Valid for {DAYS_LEFT} days</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.5, 1])

with left:
    # Multi-select dropdown for lots
    st.markdown("### 🎨 Select Artwork Lots (Max 5)")
    
    lot_options = [f"Lot {num} - {info['title']} ({info['artist']})" 
                   for num, info in DEMO_LOTS.items()]
    
    # Convert stored lot numbers to display strings for default
    default_displays = []
    if st.session_state.selected_lots:
        for lot_num in st.session_state.selected_lots:
            if lot_num in DEMO_LOTS:
                info = DEMO_LOTS[lot_num]
                default_displays.append(f"Lot {lot_num} - {info['title']} ({info['artist']})")
    
    selected_displays = st.multiselect(
        "Choose up to 5 lots:",
        lot_options,
        default=default_displays,
        max_selections=5,
        key="lot_multiselect"
    )
    
    # Extract lot numbers from selections
    selected_lots = []
    for display in selected_displays:
        lot_num = int(display.split(" - ")[0].replace("Lot ", ""))
        selected_lots.append(lot_num)
    
    st.session_state.selected_lots = selected_lots
    
    # Display selected lots compactly
    if selected_lots:
        st.markdown("#### 📋 Selected Lots")
        for lot in selected_lots:
            lot_info = DEMO_LOTS[lot]
            weight_badge = f"badge-{lot_info['weight'].lower()}"
            
            st.markdown(f"""
            <div class="lot-compact-card">
                <h4>Lot #{lot}: {lot_info['title']}</h4>
                <p><b>Artist:</b> {lot_info['artist']} • <b>Material:</b> {lot_info['material']} • <span class="{weight_badge}">{lot_info['weight']}</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Shipping options (always visible)
    st.markdown("### ⚙️ Shipping Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        suggested_pack, pack_note = suggest_packing_for_lots(selected_lots)
        packing = st.selectbox("📦 Packing Type", PACKING_TYPES, 
                              index=PACKING_TYPES.index(suggested_pack))
    
    with col2:
        delivery = st.selectbox("🚚 Delivery Type", DELIVERY_TYPES)
    
    if selected_lots:
        with st.expander("💡 AI Packing Recommendation"):
            st.markdown(pack_note)
    
    st.markdown("---")
    
    # Delivery details (always visible)
    st.markdown("### 📍 Delivery Details")
    
    address_input = st.text_input(
        "Delivery Address",
        placeholder="e.g., 2 avenue de palavas, London, UK",
        help="Enter full address for accurate quote"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("👤 Client Name", placeholder="e.g., Henrietta Atsenokhai")
    with col2:
        currency = st.selectbox("💰 Currency", ["EUR", "USD", "GBP"])

with right:
    st.markdown("### 📊 Quote Summary")
    
    if selected_lots and address_input:
        shipping, breakdown, km = calculate_shipping(selected_lots, packing, delivery, address_input)
        final = shipping * CURRENCY_RATE[currency]
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>🗺️ Distance from Paris</h4>
            <h2>{km:,} km</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>💵 Total Shipping Cost</h4>
            <h1>{CURRENCY_SYMBOL[currency]}{final:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Selected lots count
        st.markdown(f"""
        <div class="metric-card">
            <h4>📦 Total Lots</h4>
            <h2>{len(selected_lots)}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Cost breakdown
        with st.expander("📋 View Itemized Breakdown", expanded=False):
            for lot in selected_lots:
                lot_info = DEMO_LOTS[lot]
                st.markdown(f"**Lot {lot}:** {lot_info['title']}")
                st.caption(f"{lot_info['weight']} • {lot_info['material']}")
            
            st.markdown("---")
            st.markdown(f"""
            **Packing:** {packing} (€{PACKING_COST[packing]})  
            **Delivery:** {delivery} (€{DELIVERY_COST[delivery]})  
            **Distance:** {km} km
            """)
        
        st.markdown("---")
        
        if st.button("📥 Generate PDF Quote", type="primary"):
            pdf = generate_branded_pdf(QUOTE_ID, client_name, address_input, packing, 
                                     delivery, breakdown, final, currency)
            st.download_button(
                "⬇️ Download PDF Receipt",
                pdf,
                file_name=f"ShipQuote_{QUOTE_ID}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("👈 **Select lots and enter details to generate quote**")
        
        st.markdown("---")
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Select** up to 5 artwork lots
        2. **Choose** packing & delivery options
        3. **Enter** client name & address
        4. **Generate** PDF receipt
        """)
