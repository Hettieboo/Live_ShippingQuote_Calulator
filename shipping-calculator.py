import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Try to import geopy for address autocomplete
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# ========== DEMO DATA ==========
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

# ========== CONFIG ==========
st.set_page_config(page_title="ShipQuote Pro", page_icon="📦", layout="wide")

# Session state
if 'geocode_cache' not in st.session_state:
    st.session_state.geocode_cache = {}
if 'selected_address' not in st.session_state:
    st.session_state.selected_address = ""

# Geocoder
@st.cache_resource
def get_geolocator():
    if GEOPY_AVAILABLE:
        return Nominatim(user_agent="shipquote_pro_demo")
    return None

geolocator = get_geolocator()

# ========== FUNCTIONS ==========
def search_address(query):
    if not GEOPY_AVAILABLE or not geolocator or len(query) < 3:
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
    except (GeocoderTimedOut, GeocoderServiceError):
        return []
    except Exception as e:
        st.warning(f"Address search error: {e}")
        return []

def lookup_lots(lot_input):
    if not lot_input.strip():
        return "", "", []
    lot_nums = [n.strip() for n in lot_input.split(',') if n.strip()][:10]
    descriptions = []
    sales = set()
    valid_lots = []
    
    for num in lot_nums:
        try:
            lot_num = int(num)
            lot = DEMO_LOTS[DEMO_LOTS['LOT'] == lot_num]
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
    
    suggestions = []
    packing_votes = {}
    
    for lot_num in lot_nums:
        lot = DEMO_LOTS[DEMO_LOTS['LOT'] == lot_num]
        if lot.empty:
            continue
        desc = lot.iloc[0]['TYPESET'].lower()
        if any(kw in desc for kw in ['glass', 'steel', 'formaldehyde', 'metal']):
            pack = "Wood crate"; reason = "Fragile/heavy"
        elif any(kw in desc for kw in ['print', 'photograph', 'paper', 'gelatin']):
            pack = "Cardboard box"; reason = "Paper-based"
        else:
            pack = "Automatic (AI)"; reason = "Standard protection"
        
        suggestions.append(f"**Lot {lot_num}:** {reason}")
        packing_votes[pack] = packing_votes.get(pack, 0) + 1
    
    overall = max(packing_votes.items(), key=lambda x: x[1])[0] if packing_votes else "Automatic (AI)"
    suggestion_text = "💡 **AI Packing Suggestions:**\n" + "\n".join(suggestions)
    if len(packing_votes) > 1:
        suggestion_text += f"\n\n✅ **Overall:** {overall}"
    return overall, suggestion_text

# ========== MAIN APP ==========
days_left = max(0, (VALID_UNTIL - datetime.now()).days)

st.title("📦 ShipQuote Pro")
st.caption(f"Professional Shipping Quote Calculator • Demo: Lots 86-95 • Valid until {VALID_UNTIL.strftime('%b %d')} ({days_left}d)")

with st.expander("ℹ️ Quick Guide"):
    st.write("Enter lot numbers → Type address (autocomplete) → AI suggests packing → Set pricing → Download PDF")

st.divider()

# Layout
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("📦 Lot Information")
    col_lot1, col_lot2 = st.columns([2, 1])
    with col_lot1:
        lot_input = st.text_input("Lot Numbers", value="86, 89, 94", placeholder="e.g., 86, 87, 88")
    with col_lot2:
        descriptions, sale_no, valid_lots = lookup_lots(lot_input)
        st.text_input("Sale #", value=sale_no or "N/A", disabled=True)
    st.text_area("Descriptions", value=descriptions, height=140, disabled=True)
    
    # AI packing
    if valid_lots:
        suggested_pack, suggestion_text = suggest_packing(valid_lots)
        with st.expander("💡 AI Packing"):
            st.write(suggestion_text)
    else:
        suggested_pack = PACKING_TYPES[0]
    
    st.divider()
    st.subheader("📍 Shipment Parameters")
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    
    with col1:
        location_input = st.text_input("Delivery Location", placeholder="Start typing address...")
        if GEOPY_AVAILABLE and location_input and len(location_input) >= 3:
            suggestions = search_address(location_input)
            if suggestions:
                selected_address = st.selectbox("Select Address", options=suggestions, index=0)
                st.session_state.selected_address = selected_address
        location = st.session_state.selected_address
    
    with col2:
        packing = st.selectbox("Packing", PACKING_TYPES, index=PACKING_TYPES.index(suggested_pack))
    with col3:
        delivery = st.selectbox("Delivery", DELIVERY_TYPES)

with col_right:
    st.subheader("💰 Pricing")
    shipping = st.number_input("Shipping (EUR)", min_value=0.0, value=500.0, step=50.0)
    insurance = st.number_input("Insurance (EUR)", min_value=0.0, value=100.0, step=50.0)
    total = shipping + insurance
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
