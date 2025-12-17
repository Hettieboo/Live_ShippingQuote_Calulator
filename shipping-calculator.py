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
        padding: 1.2rem;
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
        font-size: 1.8rem;
    }
    .metric-card h1 {
        color: #2d3748;
        margin: 0.3rem 0 0 0;
        font-size: 2.2rem;
    }
    .quote-header {
        background: white;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #2d3748;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    .quote-header h1 {
        color: #2d3748;
        font-size: 2rem;
        margin: 0;
    }
    .quote-header p {
        color: #718096;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    .lot-detail-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .lot-detail-card h3 {
        color: #2d3748;
        margin: 0 0 0.5rem 0;
    }
    .lot-detail-card p {
        color: #4a5568;
        margin: 0.3rem 0;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #f7fafc;
        padding: 0.8rem;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    .info-box-label {
        color: #718096;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0;
    }
    .info-box-value {
        color: #2d3748;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.2rem 0 0 0;
    }
    .badge-heavy { 
        background: #e53e3e; 
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-medium { 
        background: #f6ad55; 
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-light { 
        background: #48bb78; 
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
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
    div[data-baseweb="select"] {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

PARIS_COORD = (48.8566, 2.3522)
DAYS_LEFT = 7

geolocator = Nominatim(user_agent="shipquote_pro")

# ================= DEMO LOT DATA (HARDCODED) =================
DEMO_LOTS = {
    86: {"weight": "Heavy", "material": "Canvas", "title": "Abstract Expressionism #3", "artist": "J. Basquiat", "description": "Bold neo-expressionist work featuring vibrant colors and raw energy"},
    87: {"weight": "Medium", "material": "Canvas", "title": "Landscape Vista", "artist": "M. Rousseau", "description": "Dreamy landscape with lush vegetation and exotic wildlife"},
    88: {"weight": "Medium", "material": "Canvas", "title": "Urban Nocturne", "artist": "K. Tanaka", "description": "Contemporary cityscape capturing the essence of modern urban life"},
    89: {"weight": "Heavy", "material": "Glass/Steel", "title": "Reflections III", "artist": "L. Fontana", "description": "Minimalist sculpture exploring light and space"},
    90: {"weight": "Heavy", "material": "Metal", "title": "Kinetic Sculpture", "artist": "A. Calder", "description": "Dynamic mobile sculpture with suspended elements"},
    91: {"weight": "Medium", "material": "Canvas", "title": "Still Life with Fruit", "artist": "P. Cezanne", "description": "Post-impressionist composition of apples and vessels"},
    92: {"weight": "Heavy", "material": "Canvas", "title": "The Great Wave", "artist": "K. Hokusai", "description": "Iconic Japanese woodblock print depicting a towering wave"},
    93: {"weight": "Light", "material": "Photograph", "title": "Portrait Series #7", "artist": "A. Adams", "description": "Black and white landscape photograph with dramatic contrast"},
    94: {"weight": "Light", "material": "Photograph", "title": "Cityscape 2024", "artist": "D. LaChapelle", "description": "Vivid urban photography with saturated colors"},
    95: {"weight": "Medium", "material": "Photograph", "title": "Nature's Symmetry", "artist": "A. Gursky", "description": "Large-format photograph exploring patterns in nature"},
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
def suggest_packing_for_lots(selected_lot):
    if not selected_lot:
        return "Automatic (AI)", "ℹ️ Select a lot for packing suggestions"

    info = DEMO_LOTS.get(selected_lot)
    if not info:
        return "Automatic (AI)", "ℹ️ Lot not found"

    material = info["material"].lower()

    if any(k in material for k in ["glass", "metal", "steel"]):
        pack = "Wood crate"
        reason = f"💡 Recommended: **{pack}**\n\nFragile and rigid materials like {info['material']} require sturdy wooden crate protection to prevent damage during transport."
    elif "photo" in material:
        pack = "Cardboard box"
        reason = f"💡 Recommended: **{pack}**\n\nPaper-based artworks like photographs are best protected in cardboard boxes with acid-free materials."
    else:
        pack = "Automatic (AI)"
        reason = f"💡 Recommended: **{pack}**\n\nStandard canvas artworks can use our AI-optimized packing solution based on dimensions and destination."

    return pack, reason

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

def calculate_shipping(lot, packing, delivery, address):
    km, dist_mult = get_distance_and_multiplier(address)
    base = 220
    
    info = DEMO_LOTS[lot]
    price = (
        base
        * WEIGHT_MULT[info["weight"]]
        * MATERIAL_MULT[info["material"]]
        * dist_mult
    )
    price += DELIVERY_COST[delivery] + PACKING_COST[packing]
    
    breakdown = [[f"Lot {lot}", info["weight"], info["material"], f"{price:,.2f}"]]
    
    return price, breakdown, km

def generate_branded_pdf(quote_id, client, address, packing, delivery, breakdown, total, currency, lot_num):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<font size=22><b>ShipQuote Pro</b></font><br/><font size=10 color='grey'>Fine Art & High-Value Logistics</font>", styles["Normal"]))
    elements.append(Spacer(1, 16))

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
    ]))
    elements.append(meta)
    elements.append(Spacer(1, 20))

    lot_info = DEMO_LOTS[lot_num]
    elements.append(Paragraph("<b>Artwork Details</b>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>{lot_info['title']}</b> by {lot_info['artist']}", styles["Normal"]))
    elements.append(Paragraph(f"{lot_info['description']}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>Shipment Details</b>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Delivery:</b><br/>{address}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Packing:</b> {packing}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Delivery Type:</b> {delivery}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    table = Table([["Lot", "Weight", "Material", "Price (€)"]] + breakdown, colWidths=[3*cm, 3*cm, 5*cm, 3*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph(f"<font size=14><b>Total Quote: {CURRENCY_SYMBOL[currency]}{total:,.2f}</b></font>", styles["Heading1"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================= UI =================
if "quote_id" not in st.session_state:
    st.session_state.quote_id = f"SQ-{uuid4().hex[:8].upper()}"

QUOTE_ID = st.session_state.quote_id

# Header
st.markdown(f"""
<div class="quote-header">
    <h1>📦 ShipQuote Pro</h1>
    <p>Professional Shipping Quote System • Quote ID: <b>{QUOTE_ID}</b> • Valid for {DAYS_LEFT} days</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.5, 1])

with left:
    # Dropdown lot selector
    st.markdown("### 🎨 Select Artwork Lot")
    
    lot_options = {f"Lot {num} - {info['title']} ({info['artist']})": num 
                   for num, info in DEMO_LOTS.items()}
    
    selected_display = st.selectbox(
        "Choose a lot:",
        ["-- Select a lot --"] + list(lot_options.keys()),
        key="lot_selector"
    )
    
    selected_lot = lot_options.get(selected_display)
    
    # Display lot details when selected
    if selected_lot:
        lot_info = DEMO_LOTS[selected_lot]
        
        weight_badge = f"badge-{lot_info['weight'].lower()}"
        
        st.markdown(f"""
        <div class="lot-detail-card">
            <h3>Lot #{selected_lot}: {lot_info['title']}</h3>
            <p style="color: #718096; font-style: italic; margin-bottom: 1rem;">{lot_info['description']}</p>
            <div class="info-grid">
                <div class="info-box">
                    <p class="info-box-label">Artist</p>
                    <p class="info-box-value">{lot_info['artist']}</p>
                </div>
                <div class="info-box">
                    <p class="info-box-label">Weight Class</p>
                    <p class="info-box-value"><span class="{weight_badge}">{lot_info['weight']}</span></p>
                </div>
                <div class="info-box">
                    <p class="info-box-label">Material</p>
                    <p class="info-box-value">{lot_info['material']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Shipping options
        st.markdown("### ⚙️ Shipping Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            suggested_pack, pack_note = suggest_packing_for_lots(selected_lot)
            packing = st.selectbox("📦 Packing Type", PACKING_TYPES, 
                                  index=PACKING_TYPES.index(suggested_pack))
        
        with col2:
            delivery = st.selectbox("🚚 Delivery Type", DELIVERY_TYPES)
        
        # AI Recommendation
        with st.expander("💡 View AI Packing Recommendation"):
            st.markdown(pack_note)
        
        st.markdown("---")
        
        # Delivery details
        st.markdown("### 📍 Delivery Details")
        
        address_input = st.text_input(
            "Delivery Address",
            placeholder="e.g., London, UK or 10 Downing Street, London",
            help="Enter city, full address, or landmark"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("👤 Client Name", placeholder="Optional")
        with col2:
            currency = st.selectbox("💰 Currency", ["EUR", "USD", "GBP"])

with right:
    st.markdown("### 📊 Quote Summary")
    
    if selected_lot and address_input:
        shipping, breakdown, km = calculate_shipping(selected_lot, packing, delivery, address_input)
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
        
        # Cost breakdown
        with st.expander("📋 View Cost Breakdown", expanded=True):
            lot_info = DEMO_LOTS[selected_lot]
            base = 220
            km_calc, dist_mult = get_distance_and_multiplier(address_input)
            
            st.markdown(f"""
            **Base Rate:** €{base}  
            **Weight Multiplier:** {WEIGHT_MULT[lot_info['weight']]}x ({lot_info['weight']})  
            **Material Multiplier:** {MATERIAL_MULT[lot_info['material']]}x ({lot_info['material']})  
            **Distance Multiplier:** {dist_mult}x ({km} km)  
            **Packing Cost:** €{PACKING_COST[packing]}  
            **Delivery Cost:** €{DELIVERY_COST[delivery]}  
            """)
        
        st.markdown("---")
        
        if st.button("📥 Generate PDF Quote", type="primary"):
            pdf = generate_branded_pdf(QUOTE_ID, client_name, address_input, packing, 
                                     delivery, breakdown, final, currency, selected_lot)
            st.download_button(
                "⬇️ Download PDF",
                pdf,
                file_name=f"ShipQuote_{QUOTE_ID}_Lot{selected_lot}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("👈 **Select a lot and enter delivery address to generate quote**")
        
        st.markdown("---")
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Select** an artwork lot from dropdown
        2. **Review** lot details and AI recommendations
        3. **Enter** delivery address
        4. **Generate** professional PDF quote
        """)
