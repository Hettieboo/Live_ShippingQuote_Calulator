"""
SHIPQUOTE PRO - STREAMLIT APP (DEMO VERSION)

Installation:
pip install streamlit pandas openpyxl geopy reportlab

Usage:
streamlit run app.py

Demo data is pre-loaded. You can also upload your own Excel file.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Try to import geopy for geocoding
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    st.warning("⚠️ Geopy not installed. Address search disabled. Run: pip install geopy")

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="ShipQuote Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== DEMO DATA ==========
DEMO_DATA = {
    'LOT': [86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
    'SALENO': [7185] * 10,
    'TYPESET': [
        "JEAN-MICHEL BASQUIAT (1960-1988)\nUntitled (Skull), 1981\nAcrylic and oil stick on canvas\n207.6 x 176.8 cm (81 3/4 x 69 5/8 in.)",
        "BANKSY (B. 1974)\nGirl with Balloon, 2006\nSpray paint on canvas\n150 x 150 cm",
        "YAYOI KUSAMA (B. 1929)\nPumpkin, 2015\nAcrylic on canvas\n162 x 162 cm",
        "DAMIEN HIRST (B. 1965)\nThe Physical Impossibility of Death, 1991\nGlass, steel, formaldehyde solution\n213 x 518 x 213 cm",
        "JEFF KOONS (B. 1955)\nBalloon Dog (Orange), 1994-2000\nMirror-polished stainless steel with transparent color coating\n307.3 x 363.2 x 114.3 cm",
        "GERHARD RICHTER (B. 1932)\nAbstraktes Bild, 1986\nOil on canvas\n200 x 200 cm",
        "TAKASHI MURAKAMI (B. 1962)\nFlower Ball (3D), 2008\nAcrylic on canvas mounted on board\n Diameter: 300 cm",
        "ANSELM KIEFER (B. 1945)\nDie Meistersinger, 1981-1982\nOil, emulsion, straw on photograph mounted on canvas\n280 x 380 cm",
        "CINDY SHERMAN (B. 1954)\nUntitled Film Still #21, 1978\nGelatin silver print\n20.3 x 25.4 cm (8 x 10 in.)",
        "ANDREAS GURSKY (B. 1955)\nRhein II, 1999\nC-print mounted on acrylic glass\n190 x 360 cm"
    ]
}

# ========== CONFIGURATION ==========
VALID_UNTIL_DATE = datetime(2025, 12, 8)

DELIVERY_TYPES = [
    'Front-delivery',
    'White Glove (ground floor)',
    'White Glove (with elevator)',
    'Curbside delivery'
]

PACKING_TYPES = [
    'Automatic (AI suggestion)',
    'Wood crate',
    'Cardboard box',
    'Bubble wrap only',
    'Custom packing'
]

# Initialize geocoder
@st.cache_resource
def get_geolocator():
    if GEOPY_AVAILABLE:
        return Nominatim(user_agent="shipquote_pro_v1")
    return None

geolocator = get_geolocator()

# ========== SESSION STATE INITIALIZATION ==========
if 'lot_df' not in st.session_state:
    # Load demo data by default
    st.session_state.lot_df = pd.DataFrame(DEMO_DATA)
if 'geocode_cache' not in st.session_state:
    st.session_state.geocode_cache = {}
if 'using_demo_data' not in st.session_state:
    st.session_state.using_demo_data = True

# ========== HELPER FUNCTIONS ==========

def calculate_days_remaining():
    """Calculate days until quote expires"""
    today = datetime.now()
    diff = (VALID_UNTIL_DATE - today).days
    return max(0, diff)

def search_address(query):
    """Search for addresses using Geopy"""
    if not GEOPY_AVAILABLE or not geolocator:
        return []
    
    if not query or len(query) < 3:
        return []
    
    # Check cache first
    if query in st.session_state.geocode_cache:
        return st.session_state.geocode_cache[query]
    
    try:
        locations = geolocator.geocode(query, exactly_one=False, limit=5, timeout=3)
        
        if locations:
            results = [loc.address for loc in locations]
            st.session_state.geocode_cache[query] = results
            return results
        return []
    except (GeocoderTimedOut, GeocoderServiceError):
        return []
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return []

def format_address(address_text):
    """Format and validate address"""
    if not address_text:
        return "Not specified"
    
    if not GEOPY_AVAILABLE or not geolocator:
        return address_text
    
    try:
        location = geolocator.geocode(address_text, timeout=3)
        if location:
            return location.address
        return address_text
    except:
        return address_text

def lookup_multiple_lots(lot_numbers_text):
    """Look up multiple lots from comma-separated input"""
    if st.session_state.lot_df is None:
        return "⚠️ Please upload Excel file first", ""
    
    if not lot_numbers_text or lot_numbers_text.strip() == "":
        return "", ""
    
    # Parse comma-separated lot numbers
    lot_numbers = [num.strip() for num in lot_numbers_text.split(',') if num.strip()]
    
    if len(lot_numbers) > 10:
        return "❌ Maximum 10 lots allowed per quote", ""
    
    all_descriptions = []
    sale_numbers = set()
    
    for lot_num_str in lot_numbers:
        try:
            lot_num = int(float(lot_num_str))
            
            if lot_num < 0:
                all_descriptions.append(f"--- LOT {lot_num_str} ---\n❌ Invalid: negative number\n")
                continue
            
            lot_row = st.session_state.lot_df[st.session_state.lot_df['LOT'] == lot_num]
            
            if not lot_row.empty:
                description = str(lot_row.iloc[0]['TYPESET'])
                sale_no = str(int(lot_row.iloc[0]['SALENO'])) if 'SALENO' in st.session_state.lot_df.columns else "N/A"
                
                all_descriptions.append(f"--- LOT {lot_num} ---\n{description}\n")
                sale_numbers.add(sale_no)
            else:
                all_descriptions.append(f"--- LOT {lot_num} ---\n❌ Not found in database\n")
        except ValueError:
            all_descriptions.append(f"--- {lot_num_str} ---\n❌ Invalid: not a number\n")
        except Exception as e:
            all_descriptions.append(f"--- {lot_num_str} ---\n❌ Error: {str(e)}\n")
    
    combined_description = "\n".join(all_descriptions)
    combined_sale = ", ".join(sorted(sale_numbers)) if sale_numbers else ""
    
    return combined_description, combined_sale

def suggest_packing_type(description):
    """Suggest packing type based on artwork description"""
    if not description or description.strip() == "":
        return "Automatic (AI suggestion)", "Automatic - let AI assess best option"
    
    description_lower = description.lower()
    
    # Check for fragile items
    fragile_keywords = ['glass', 'ceramic', 'porcelain', 'fragile', 'caisson lumineux',
                        'light box', 'neon', 'installation', 'sculpture', 'bronze', 'marble',
                        'formaldehyde', 'steel']
    
    # Check for large/heavy items
    heavy_keywords = ['sculpture', 'bronze', 'marble', 'stone', 'metal', 'installation', 'steel', 'stainless']
    
    # Check for delicate works on paper
    paper_keywords = ['paper', 'watercolor', 'gouache', 'drawing', 'print', 'etching',
                      'lithograph', 'photograph', 'photo', 'c-print', 'tirage', 'gelatin silver']
    
    # Check for paintings
    painting_keywords = ['canvas', 'oil', 'acrylic', 'painting', 'huile', 'toile', 'oil stick']
    
    # Decision logic
    if any(keyword in description_lower for keyword in fragile_keywords):
        if any(keyword in description_lower for keyword in heavy_keywords):
            return "Wood crate", "Wood crate - fragile/heavy (glass, steel, or sculpture)"
        else:
            return "Wood crate", "Wood crate - fragile items (glass or delicate materials)"
    
    elif any(keyword in description_lower for keyword in paper_keywords):
        return "Cardboard box", "Cardboard box - works on paper (photograph, print, or paper-based)"
    
    elif any(keyword in description_lower for keyword in painting_keywords):
        return "Automatic (AI suggestion)", "Automatic - canvas paintings (standard protection)"
    
    elif any(keyword in description_lower for keyword in heavy_keywords):
        return "Wood crate", "Wood crate - heavy sculptures or installations"
    
    else:
        return "Automatic (AI suggestion)", "Automatic - let AI assess best option"

def suggest_packing_for_multiple_lots(lot_numbers_text):
    """Analyze each lot and provide individual packing suggestions"""
    if st.session_state.lot_df is None or not lot_numbers_text or lot_numbers_text.strip() == "":
        return "Automatic (AI suggestion)", "ℹ️ Enter lot numbers to get intelligent packing suggestions"
    
    lot_numbers = [num.strip() for num in lot_numbers_text.split(',') if num.strip()]
    
    if len(lot_numbers) == 0:
        return "Automatic (AI suggestion)", "ℹ️ Enter lot numbers to get intelligent packing suggestions"
    
    suggestions_list = []
    packing_recommendations = {}
    
    for lot_num_str in lot_numbers:
        try:
            lot_num = int(float(lot_num_str))
            lot_row = st.session_state.lot_df[st.session_state.lot_df['LOT'] == lot_num]
            
            if not lot_row.empty:
                description = str(lot_row.iloc[0]['TYPESET'])
                suggested_packing, reason = suggest_packing_type(description)
                
                suggestions_list.append(f"**Lot {lot_num}:** {reason}")
                
                if suggested_packing in packing_recommendations:
                    packing_recommendations[suggested_packing] += 1
                else:
                    packing_recommendations[suggested_packing] = 1
            else:
                suggestions_list.append(f"**Lot {lot_num}:** Not found in database")
        except:
            suggestions_list.append(f"**{lot_num_str}:** Invalid lot number")
    
    # Determine overall recommendation
    if packing_recommendations:
        if len(packing_recommendations) == 1:
            overall_packing = list(packing_recommendations.keys())[0]
            overall_message = f"\n\n✅ **Overall Recommendation:** {overall_packing} (all lots require same packing)"
        else:
            if "Wood crate" in packing_recommendations:
                overall_packing = "Wood crate"
                overall_message = f"\n\n⚠️ **Overall Recommendation:** {overall_packing} (most protective option for mixed lot types)"
            elif "Cardboard box" in packing_recommendations:
                overall_packing = "Cardboard box"
                overall_message = f"\n\n💡 **Overall Recommendation:** {overall_packing} (suitable for most items)"
            else:
                overall_packing = "Automatic (AI suggestion)"
                overall_message = f"\n\n💡 **Overall Recommendation:** {overall_packing} (let AI assess)"
    else:
        overall_packing = "Automatic (AI suggestion)"
        overall_message = ""
    
    full_suggestion = "💡 **Packing Suggestions by Lot:**\n\n" + "\n".join(suggestions_list) + overall_message
    
    return overall_packing, full_suggestion

def generate_pdf_quote(lot_numbers, description, sale_no, location, packing, delivery, shipping_cost, insurance):
    """Generate a PDF quote document"""
    
    if not PDF_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("📦 SHIPQUOTE PRO - SHIPPING QUOTE", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Quote Info
    quote_date = datetime.now().strftime('%B %d, %Y')
    valid_until = VALID_UNTIL_DATE.strftime('%B %d, %Y')
    
    info_data = [
        ['Quote Date:', quote_date],
        ['Valid Until:', valid_until],
        ['Sale Number:', sale_no if sale_no else 'N/A']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Lot Information
    elements.append(Paragraph("LOT INFORMATION", heading_style))
    lot_count = len([n for n in lot_numbers.split(',') if n.strip()]) if lot_numbers else 0
    elements.append(Paragraph(f"<b>Number of Lots:</b> {lot_count}", styles['Normal']))
    elements.append(Paragraph(f"<b>Lot Numbers:</b> {lot_numbers}", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Description (truncated for PDF)
    desc_text = description[:800] + "..." if len(description) > 800 else description
    desc_clean = desc_text.replace('\n', '<br/>')
    elements.append(Paragraph(f"<b>Description:</b><br/>{desc_clean}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Shipment Details
    elements.append(Paragraph("SHIPMENT DETAILS", heading_style))
    shipment_data = [
        ['Delivery Location:', location if location else 'Not specified'],
        ['Packing Type:', packing if packing else 'Not selected'],
        ['Delivery Type:', delivery if delivery else 'Not selected']
    ]
    
    shipment_table = Table(shipment_data, colWidths=[2*inch, 4*inch])
    shipment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(shipment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Pricing
    elements.append(Paragraph("PRICING", heading_style))
    
    cost_val = float(shipping_cost) if shipping_cost else 0
    insurance_val = float(insurance) if insurance else 0
    total_val = cost_val + insurance_val
    
    pricing_data = [
        ['Shipping Cost:', f'€{cost_val:,.2f}'],
        ['Insurance:', f'€{insurance_val:,.2f}'],
        ['', ''],
        ['TOTAL:', f'€{total_val:,.2f}']
    ]
    
    pricing_table = Table(pricing_data, colWidths=[4*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 1), 'Helvetica'),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, 3), (-1, 3), 14),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#1e40af')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(pricing_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer_text = f"""
    <para align=center>
    <font size=8 color="#6b7280">
    This quote is valid until {valid_until}.<br/>
    Generated by ShipQuote Pro<br/>
    Art moderne et contemporain
    </font>
    </para>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

# ========== MAIN APP ==========

def main():
    # Header
    st.title("📦 ShipQuote Pro")
    st.subheader("Professional Shipping Quote Calculator")
    
    # Demo banner
    if st.session_state.using_demo_data:
        st.info("🎨 **DEMO MODE:** Using sample auction data. Upload your own Excel file to customize.")
    
    # Sidebar - File Upload
    with st.sidebar:
        st.header("📁 Data Upload")
        
        with st.expander("📋 Required Excel Format", expanded=False):
            st.markdown("""
            **Required Columns:**
            - `LOT` (integer): Lot number
            - `TYPESET` (text): Item description
            - `SALENO` (integer): Sale/auction number
            
            **Example:**
            | LOT | SALENO | TYPESET |
            |-----|--------|---------|
            | 86  | 7185   | JEAN-MICHEL BASQUIAT... |
            | 87  | 7185   | BANKSY... |
            
            The app will auto-populate descriptions when you enter lot numbers.
            """)
        
        uploaded_file = st.file_uploader(
            "Upload Your Excel File",
            type=['xlsx', 'xls'],
            help="Upload your lot database Excel file with LOT, SALENO, and TYPESET columns"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                
                # Validate required columns
                required_columns = ['LOT', 'TYPESET']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    st.info("Please ensure your Excel file contains: LOT, TYPESET, and optionally SALENO")
                else:
                    st.session_state.lot_df = df
                    st.session_state.using_demo_data = False
                    st.session_state.geocode_cache = {}  # Clear cache on new upload
                    st.success(f"✅ Loaded {len(df)} lots from your file")
                    
                    # Display sale number if available
                    if 'SALENO' in df.columns:
                        first_sale = df['SALENO'].iloc[0]
                        st.info(f"📋 Sale Number: {int(first_sale)}")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
        elif st.session_state.using_demo_data:
            st.success(f"✅ Using demo data ({len(st.session_state.lot_df)} sample lots)")
            st.info(f"📋 Demo Sale Number: 7185")
        
        st.markdown("---")
        
        # Quote validity countdown
        days = calculate_days_remaining()
        st.markdown("### ⏰ Quote Validity")
        st.markdown(f"**Valid until:** {VALID_UNTIL_DATE.strftime('%B %d, %Y')}")
        st.markdown(f"**Days remaining:** :red[{days} days]")
        
        if not PDF_AVAILABLE:
            st.warning("⚠️ PDF download unavailable\nInstall reportlab to enable")
        
        if not GEOPY_AVAILABLE:
            st.warning("⚠️ Address search unavailable\nInstall geopy to enable")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📦 Lot Information")
        
        # Show example lot numbers for demo
        demo_hint = "Try: 86, 89, 94 (or any from 86-95)" if st.session_state.using_demo_data else "Enter lot numbers from your uploaded file"
        
        lot_numbers = st.text_area(
            "Lot Numbers (up to 10)",
            placeholder=demo_hint,
            help="Enter up to 10 lot numbers separated by commas. Descriptions will auto-populate.",
            height=100
        )
        
        # Auto-lookup when lot numbers change
        if lot_numbers:
            description, sale_no = lookup_multiple_lots(lot_numbers)
            
            st.text_input("Sale Number(s)", value=sale_no, disabled=True)
            
            st.text_area(
                "Description(s)",
                value=description,
                height=300,
                disabled=True
            )
            
            # Get packing suggestions
            suggested_packing, suggestion_text = suggest_packing_for_multiple_lots(lot_numbers)
            
            with st.expander("💡 AI Packing Suggestions", expanded=True):
                st.markdown(suggestion_text)
        else:
            sale_no = ""
            description = ""
            suggested_packing = PACKING_TYPES[0]
        
        st.markdown("---")
        st.header("📍 Shipment Parameters")
        
        location = st.text_input(
            "Delivery Location",
            placeholder="Start typing address (e.g., '123 Main St, New York' or 'Louvre Museum, Paris')",
            help="Type at least 3 characters to see suggestions (requires geopy)"
        )
        
        # Address suggestions
        if GEOPY_AVAILABLE and location and len(location) >= 3:
            suggestions = search_address(location)
            if suggestions:
                selected_address = st.selectbox(
                    "📍 Address Suggestions (select one)",
                    options=[""] + suggestions,
                    index=0
                )
                if selected_address:
                    location = selected_address
        
        packing = st.selectbox(
            "Type of Packing",
            options=PACKING_TYPES,
            index=PACKING_TYPES.index(suggested_packing) if lot_numbers else 0
        )
        
        delivery = st.selectbox(
            "Type of Delivery",
            options=DELIVERY_TYPES,
            index=0
        )
    
    with col2:
        st.header("💰 Pricing")
        
        shipping_cost = st.number_input(
            "Shipping Cost (EUR)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            format="%.2f"
        )
        
        insurance = st.number_input(
            "Insurance (EUR)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            format="%.2f"
        )
        
        total = shipping_cost + insurance
        
        st.metric(
            label="💵 TOTAL WITH INSURANCE (EUR)",
            value=f"€{total:,.2f}",
            delta=None
        )
        
        st.markdown("---")
        st.header("📋 Quote Summary")
        
        # Calculate lot count
        lot_count = len([n for n in lot_numbers.split(',') if n.strip()]) if lot_numbers else 0
        
        formatted_location = format_address(location) if location else "Not specified"
        
        st.markdown(f"""
        **Number of Lots:** {lot_count}  
        **Sale Number:** {sale_no if sale_no else 'N/A'}  
        **Packing:** {packing if packing else 'Not selected'}  
        **Delivery Type:** {delivery if delivery else 'Not selected'}  
        **Destination:** {formatted_location}
        
        ---
        
        ⏰ **Quote valid until:** {VALID_UNTIL_DATE.strftime('%B %d, %Y')}  
        **Days remaining:** {days} days
        """)
        
        st.markdown("---")
        
        # PDF Download
        if PDF_AVAILABLE:
            if st.button("📥 Download Quote as PDF", type="primary", use_container_width=True):
                if not lot_numbers or not location:
                    st.error("Please fill in lot numbers and location before downloading")
                else:
                    try:
                        pdf_data = generate_pdf_quote(
                            lot_numbers, description, sale_no, location,
                            packing, delivery, shipping_cost, insurance
                        )
                        
                        if pdf_data:
                            filename = f"ShipQuote_Pro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            st.download_button(
                                label="💾 Download PDF",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ PDF generated successfully!")
                        else:
                            st.error("Error generating PDF")
                    except Exception as e:
                        st.error(f"Error creating PDF: {str(e)}")
        else:
            st.info("📥 Install reportlab to enable PDF downloads")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📋 How to use:
    1. **Upload your Excel file** in the sidebar (or use demo data)
    2. **Enter lot numbers** (comma-separated for multiple, e.g., "86, 87, 88") - up to 10 lots per quote
    3. **Descriptions auto-populate** from your Excel file
    4. **Search for delivery address** - suggestions appear as you type (requires geopy)
    5. **Select packing and delivery options** (AI suggestions provided)
    6. **Enter pricing** to see total and summary
    7. **Download PDF** of your complete quote (requires reportlab)
    
    Made with Streamlit | Powered by OpenStreetMap
    """)

if __name__ == "__main__":
    main()
