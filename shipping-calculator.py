import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ======== GEOLOCATOR ========
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# ======== DEMO DATA ========
DEMO_LOTS = pd.DataFrame({
    'LOT': [86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
    'SALENO': [7185]*10,
    'TYPESET': [
        "JEAN-MICHEL BASQUIAT (1960-1988)\nUntitled (Skull), 1981\nAcrylic and oil stick on canvas\n207.6 x 176.8 cm",
        "BANKSY (B. 1974)\nGirl with Balloon, 2006\nSpray paint on canvas\n150 x 150 cm",
        "YAYOI KUSAMA (B. 1929)\nPumpkin, 2015\nAcrylic on canvas\n162 x 162 cm",
        "DAMIEN HIRST (B. 1965)\nThe Physical Impossibility of Death, 1991\nGlass, steel, formaldehyde solution\n213 x 518 x 213 cm",
        "JEFF KOONS (B. 1955)\nBalloon Dog (Orange), 1994-2000\nMirror-polished stainless steel\n307.3 x 363.2 x 114.3 cm",
        "GERHARD RICHTER (B. 1932)\nAbstraktes Bild, 1986\nOil on canvas\n200 x 200 cm",
        "TAKASHI MURAKAMI (B. 1962)\nFlower Ball (3D), 2008\nAcrylic on canvas mounted on board\nDiameter: 300 cm",
        "ANSELM KIEFER (B. 1945)\nDie Meistersinger, 1981-1982\nOil, emulsion, straw on photograph\n280 x 380 cm",
        "CINDY SHERMAN (B. 1954)\nUntitled Film Still #21, 1978\nGelatin silver print\n20.3 x 25.4 cm",
        "ANDREAS GURSKY (B. 1955)\nRhein II, 1999\nC-print mounted on acrylic glass\n190 x 360 cm"
    ]
})

PACKING_TYPES = ['Automatic (AI)', 'Wood crate', 'Cardboard box', 'Bubble wrap', 'Custom']
DELIVERY_TYPES = ['Front delivery', 'White Glove (ground)', 'White Glove (elevator)', 'Curbside']
VALID_UNTIL = datetime(2025, 12, 8)

# ======== LOT INFO FOR PRICING ========
LOT_INFO = {
    86: {"weight": "Heavy", "material": "Canvas"},
    87: {"weight": "Medium", "material": "Paper"},
    88: {"weight": "Medium", "material": "Canvas"},
    89: {"weight": "Heavy", "material": "Glass/Steel"},
    90: {"weight": "Heavy", "material": "Metal"},
    91: {"weight": "Medium", "material": "Canvas"},
    92: {"weight": "Heavy", "material": "Oil on Canvas"},
    93: {"weight": "Light", "material": "Photograph"},
    94: {"weight": "Heavy", "material": "Canvas"},
    95: {"weight": "Heavy", "material": "Acrylic/Glass"}
}

WEIGHT_MULTIPLIER = {"Light": 1, "Medium": 1.5, "Heavy": 2}
MATERIAL_MULTIPLIER = {
    "Canvas":1, "Paper":1, "Photograph":1,
    "Glass/Steel":1.5, "Metal":1.5, "Oil on Canvas":1.2, "Acrylic/Glass":1.3
}
DELIVERY_COST = {"Front delivery":0, "White Glove (ground)":100,
                 "White Glove (elevator)":50, "Curbside":0}
PACKING_COST = {"Automatic (AI)":0, "Wood crate":50, "Cardboard box":0, "Bubble wrap":20, "Custom":30}

# ======== CONFIG ========
st.set_page_config(page_title="ShipQuote Pro", page_icon="📦", layout="wide")

if 'geocode_cache' not in st.session_state:
    st.session_state.geocode_cache = {}
if 'selected_address' not in st.session_state:
    st.session_state.selected_address = ""

@st.cache_resource
def get_geolocator():
    if GEOPY_AVAILABLE:
        return Nominatim(user_agent="shipquote_pro_demo")
    return None

geolocator = get_geolocator()

# ======== FUNCTIONS ========
def search_address(query):
    if not GEOPY_AVAILABLE or not geolocator or len(query)<3:
        return []
    if query in st.session_state.geocode_cache:
        return st.session_state.geocode_cache[query]
    try:
        locations = geolocator.geocode(query, exactly_one=False, limit=5, timeout=3)
        time.sleep(1)
        if locations:
            results = [loc.address for loc in locations]
            st.session_state.geocode_cache[query] = results
            return results
    except:
        return []

def lookup_lots(lot_input):
    if not lot_input.strip():
        return "", "", []
    lot_nums = [n.strip() for n in lot_input.split(',') if n.strip()][:10]
    descriptions, sales, valid_lots = [], set(), []
    for num in lot_nums:
        try:
            lot_num = int(num)
            lot = DEMO_LOTS[DEMO_LOTS['LOT']==lot_num]
            if not lot.empty:
                descriptions.append(f"--- LOT {lot_num} ---\n{lot.iloc[0]['TYPESET']}")
                sales.add(str(lot.iloc[0]['SALENO']))
                valid_lots.append(lot_num)
            else:
                descriptions.append(f"--- LOT {num} ---\n❌ Not found")
        except:
            descriptions.append(f"--- {num} ---\n❌ Invalid")
    return "\n\n".join(descriptions), ", ".join(sales), valid_lots

def suggest_packing(lot_nums):
    if not lot_nums:
        return "Automatic (AI)", "ℹ️ Enter lot numbers for AI suggestions"
    suggestions, votes = [], {}
    for lot_num in lot_nums:
        lot = DEMO_LOTS[DEMO_LOTS['LOT']==lot_num]
        if lot.empty: continue
        desc = lot.iloc[0]['TYPESET'].lower()
        if any(kw in desc for kw in ['glass','steel','formaldehyde','metal']):
            pack, reason = "Wood crate", "Fragile/heavy"
        elif any(kw in desc for kw in ['print','photograph','paper','gelatin']):
            pack, reason = "Cardboard box","Paper-based"
        else:
            pack, reason = "Automatic (AI)","Standard"
        suggestions.append(f"**Lot {lot_num}:** {reason}")
        votes[pack] = votes.get(pack,0)+1
    overall = max(votes.items(), key=lambda x:x[1])[0] if votes else "Automatic (AI)"
    text = "💡 **AI Packing Suggestions:**\n"+"\n".join(suggestions)
    if len(votes)>1: text += f"\n\n✅ **Overall:** {overall}"
    return overall, text

def calculate_shipping(lot_nums, delivery_type, packing_type):
    base_price = 200
    total, breakdown = 0, []
    for lot_num in lot_nums:
        info = LOT_INFO.get(lot_num, {"weight":"Medium","material":"Canvas"})
        price = base_price * WEIGHT_MULTIPLIER.get(info["weight"],1) \
                * MATERIAL_MULTIPLIER.get(info["material"],1) \
                + DELIVERY_COST.get(delivery_type,0) \
                + PACKING_COST.get(packing_type,0)
        breakdown.append(f"Lot {lot_num}: €{price:.2f} ({info['weight']}, {info['material']})")
        total += price
    return total, breakdown

# ======== MAIN APP ========
days_left = max(0,(VALID_UNTIL - datetime.now()).days)
st.title("📦 ShipQuote Pro")
st.caption(f"Professional Shipping Quote Calculator • Demo: Lots 86-95 • Valid until {VALID_UNTIL.strftime('%b %d')} ({days_left}d)")

with st.expander("ℹ️ Quick Guide"):
    st.write("Enter lot numbers → Type address → AI packing → Dynamic pricing → Download PDF")

st.divider()
col_left, col_right = st.columns([1.2,1])

# ===== LEFT PANEL =====
with col_left:
    st.subheader("📦 Lot Information")
    c1,c2 = st.columns([2,1])
    with c1:
        lot_input = st.text_input("Lot Numbers", value="86, 89, 94", placeholder="e.g., 86,87,88")
    with c2:
        descriptions, sale_no, valid_lots = lookup_lots(lot_input)
        st.text_input("Sale #", value=sale_no or "N/A", disabled=True)
    st.text_area("Descriptions", value=descriptions, height=140, disabled=True)
    
    if valid_lots:
        suggested_pack, packing_text = suggest_packing(valid_lots)
        with st.expander("💡 AI Packing"):
            st.write(packing_text)
    else:
        suggested_pack = PACKING_TYPES[0]

    st.divider()
    st.subheader("📍 Shipment Parameters")
    c1,c2,c3 = st.columns([2,1.5,1.5])
    with c1:
        location_input = st.text_input("Delivery Location", placeholder="Start typing address...")
        if GEOPY_AVAILABLE and location_input and len(location_input)>=3:
            suggestions = search_address(location_input)
            if suggestions:
                selected_address = st.selectbox("Select Address", options=suggestions, index=0)
                st.session_state.selected_address = selected_address
        location = st.session_state.selected_address
    with c2:
        packing = st.selectbox("Packing", PACKING_TYPES, index=PACKING_TYPES.index(suggested_pack))
    with c3:
        delivery = st.selectbox("Delivery", DELIVERY_TYPES)

# ===== RIGHT PANEL =====
with col_right:
    st.subheader("💰 Pricing")
    if valid_lots:
        shipping_total, shipping_breakdown = calculate_shipping(valid_lots, delivery, packing)
        with st.expander("📦 Shipping Breakdown"):
            for line in shipping_breakdown:
                st.write(line)
    else:
        shipping_total = 0
    
    insurance = st.number_input("Insurance (EUR)", min_value=0.0, value=100.0, step=50.0)
    total = shipping_total + insurance
    st.metric("TOTAL", f"€{total:,.2f}")

    st.divider()
    st.subheader("📋 Quote Summary")
    st.write(f"**Lots:** {len(valid_lots)} | **Sale:** {sale_no or 'N/A'}")
    st.write(f"**Pack:** {packing}")
    st.write(f"**Delivery:** {delivery}")
    st.write(f"**To:** {location or 'Not specified'}")
    st.write(f"⏰ {days_left} days remaining")

    st.divider()
    if st.button("📥 Download PDF", type="primary", use_container_width=True):
        if not lot_input or not location:
            st.error("Enter lots & location")
        else:
            st.success("✅ PDF ready")

if not GEOPY_AVAILABLE:
    st.warning("⚠️ Install `geopy` for address autocomplete")
