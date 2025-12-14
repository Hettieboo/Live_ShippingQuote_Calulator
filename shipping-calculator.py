"""
SHIPQUOTE PRO - STREAMLIT DEMO
streamlit run shipping-calculator.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# ========== DEMO DATA ==========
DEMO_LOTS = pd.DataFrame({
    'LOT': [86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
    'SALENO': [7185] * 10,
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

# ========== FUNCTIONS ==========
def lookup_lots(lot_input):
    """Parse lot numbers and get descriptions"""
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
    """AI packing suggestions"""
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
            pack = "Wood crate"
            reason = "Wood crate - fragile/heavy materials"
        elif any(kw in desc for kw in ['print', 'photograph', 'paper', 'gelatin']):
            pack = "Cardboard box"
            reason = "Cardboard box - works on paper"
        elif any(kw in desc for kw in ['canvas', 'oil', 'acrylic']):
            pack = "Automatic (AI)"
            reason = "Automatic - canvas painting"
        else:
            pack = "Automatic (AI)"
            reason = "Automatic - standard protection"
        
        suggestions.append(f"**Lot {lot_num}:** {reason}")
        packing_votes[pack] = packing_votes.get(pack, 0) + 1
    
    # Determine overall
    if packing_votes:
        overall = max(packing_votes.items(), key=lambda x: (x[0] == "Wood crate", x[1]))[0]
    else:
        overall = "Automatic (AI)"
    
    suggestion_text = "💡 **AI Packing Suggestions:**\n\n" + "\n".join(suggestions)
    if len(packing_votes) > 1:
        suggestion_text += f"\n\n✅ **Overall:** {overall} (safest for mixed types)"
    
    return overall, suggestion_text

# ========== MAIN APP ==========
st.title("📦 ShipQuote Pro")
st.subheader("Professional Shipping Quote Calculator")

days_left = max(0, (VALID_UNTIL - datetime.now()).days)

st.info("🎨 **DEMO MODE:** Using auction sale #7185 with 10 sample lots (86-95)")

# Sidebar
with st.sidebar:
    st.header("⏰ Quote Validity")
    st.write(f"**Valid until:** {VALID_UNTIL.strftime('%B %d, %Y')}")
    st.error(f"**Days remaining:** {days_left} days")
    
    st.markdown("---")
    st.header("📋 Available Lots")
    st.dataframe(DEMO_LOTS[['LOT', 'SALENO']], hide_index=True, height=250)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.header("📦 Lot Information")
    
    lot_input = st.text_area(
        "Lot Numbers (comma-separated, max 10)",
        value="86, 89, 94",
        placeholder="e.g., 86, 87, 88",
        help="Available lots: 86-95"
    )
    
    descriptions, sale_no, valid_lots = lookup_lots(lot_input)
    
    st.text_input("Sale Number", value=sale_no or "N/A", disabled=True)
    st.text_area("Descriptions", value=descriptions, height=250, disabled=True)
    
    # AI Suggestions
    if valid_lots:
        suggested_pack, suggestion_text = suggest_packing(valid_lots)
        with st.expander("💡 AI Packing Suggestions", expanded=True):
            st.markdown(suggestion_text)
    else:
        suggested_pack = PACKING_TYPES[0]
    
    st.markdown("---")
    st.header("📍 Shipment Parameters")
    
    location = st.text_input("Delivery Location", placeholder="123 Main St, New York, NY")
    packing = st.selectbox("Packing Type", PACKING_TYPES, index=PACKING_TYPES.index(suggested_pack))
    delivery = st.selectbox("Delivery Type", DELIVERY_TYPES)

with col2:
    st.header("💰 Pricing")
    
    shipping = st.number_input("Shipping Cost (EUR)", min_value=0.0, value=500.0, step=10.0)
    insurance = st.number_input("Insurance (EUR)", min_value=0.0, value=100.0, step=10.0)
    
    total = shipping + insurance
    st.metric("💵 TOTAL WITH INSURANCE", f"€{total:,.2f}")
    
    st.markdown("---")
    st.header("📋 Quote Summary")
    
    st.markdown(f"""
    **Number of Lots:** {len(valid_lots)}  
    **Sale Number:** {sale_no or 'N/A'}  
    **Packing:** {packing}  
    **Delivery Type:** {delivery}  
    **Destination:** {location or 'Not specified'}  
    
    ---
    
    ⏰ **Valid until:** {VALID_UNTIL.strftime('%B %d, %Y')}  
    **Days remaining:** {days_left} days
    """)
    
    if st.button("📥 Download Quote as PDF", type="primary", use_container_width=True):
        if not lot_input or not location:
            st.error("Please enter lot numbers and location")
        else:
            st.success("✅ PDF would be generated here (requires reportlab)")

# Footer
st.markdown("---")
st.markdown("""
### 📋 How to use:
1. **Enter lot numbers** (e.g., "86, 89, 94") - comma-separated, max 10 lots
2. **Descriptions auto-populate** from demo database
3. **AI suggests packing** based on artwork materials
4. **Enter delivery location** and select delivery options
5. **Set pricing** to calculate total with insurance
6. **Download PDF quote** (feature requires reportlab library)

*Demo data includes 10 famous artworks from auction sale #7185*
""")
