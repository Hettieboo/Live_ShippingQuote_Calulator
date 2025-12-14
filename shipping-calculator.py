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

PARIS_COORD = (48.8566, 2.3522)
DAYS_LEFT = 7
VALID_UNTIL = datetime.now() + timedelta(days=DAYS_LEFT)

geolocator = Nominatim(user_agent="shipquote_pro")

# ================= DEMO LOT DATA =================
DEMO_LOTS = {
    86: {"weight": "Heavy", "material": "Canvas"},
    87: {"weight": "Medium", "material": "Canvas"},
    88: {"weight": "Medium", "material": "Canvas"},
    89: {"weight": "Heavy", "material": "Glass/Steel"},
    90: {"weight": "Heavy", "material": "Metal"},
    91: {"weight": "Medium", "material": "Canvas"},
    92: {"weight": "Heavy", "material": "Canvas"},
    93: {"weight": "Light", "material": "Photograph"},
    94: {"weight": "Light", "material": "Photograph"},
    95: {"weight": "Medium", "material": "Photograph"},
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

# ================= AI PACKING (RESTORED) =================
def suggest_packing_for_multiple_lots(lot_numbers_text):
    if not lot_numbers_text or lot_numbers_text.strip() == "":
        return "Automatic (AI)", "ℹ️ Enter lot numbers for packing suggestions"

    lot_numbers = [n.strip() for n in lot_numbers_text.split(",") if n.strip().isdigit()]
    if not lot_numbers:
        return "Automatic (AI)", "ℹ️ Enter valid lot numbers"

    suggestions = []
    votes = {}

    for num in lot_numbers:
        lot = int(num)
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

    # Brand header
    elements.append(
        Paragraph(
            "<font size=22><b>ShipQuote Pro</b></font><br/>"
            "<font size=10 color='grey'>Fine Art & High-Value Logistics</font>",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 16))

    # Meta
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
st.title("📦 ShipQuote Pro")
st.caption("Professional Shipping Quote • Demo • Always valid for 7 days")

if "quote_id" not in st.session_state:
    st.session_state.quote_id = f"SQ-{uuid4().hex[:8].upper()}"

QUOTE_ID = st.session_state.quote_id

left, right = st.columns([1.3, 1])

with left:
    st.subheader("📦 Lots")
    lot_input = st.text_input("Lot numbers", "86, 89, 94")
    lots = [int(x) for x in lot_input.split(",") if x.strip().isdigit() and int(x) in DEMO_LOTS]

    suggested_pack, pack_note = suggest_packing_for_multiple_lots(lot_input)
    with st.expander("💡 AI Packing"):
        st.text(pack_note)

    st.subheader("📍 Delivery")
    address = st.text_input("Delivery address")

    packing = st.selectbox("Packing", PACKING_TYPES, index=PACKING_TYPES.index(suggested_pack))
    delivery = st.selectbox("Delivery type", DELIVERY_TYPES)

    st.subheader("👤 Client")
    client_name = st.text_input("Client name / reference")

    currency = st.selectbox("Currency", ["EUR", "USD", "GBP"])
    admin = st.toggle("Admin pricing view")
    margin = st.slider("Margin (%)", 0, 40, 20) if admin else 0

with right:
    st.subheader("📊 Quote Summary")
    st.caption(f"🆔 Quote ID: `{QUOTE_ID}`")

    if lots and address:
        shipping, breakdown, km = calculate_shipping(lots, packing, delivery, address)
        cost = shipping
        client_price = cost * (1 + margin / 100)
        final = client_price * CURRENCY_RATE[currency]

        st.metric("Distance from Paris", f"{km} km")
        st.metric("Total Quote", f"{CURRENCY_SYMBOL[currency]}{final:,.2f}")

        if st.button("📥 Download Quote PDF", use_container_width=True):
            pdf = generate_branded_pdf(
                QUOTE_ID,
                client_name,
                address,
                packing,
                delivery,
                breakdown,
                final,
                currency,
            )
            st.download_button(
                "Download PDF",
                pdf,
                file_name=f"ShipQuote_{QUOTE_ID}.pdf",
                mime="application/pdf",
            )
    else:
        st.info("Enter lots and delivery address to generate quote.")
