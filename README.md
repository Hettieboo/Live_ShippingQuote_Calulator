# 📦 ShipQuote Pro

**Professional shipping quote calculator for fine art and high-value logistics**

A Streamlit web application that generates intelligent shipping quotes for artwork and valuable items with AI-powered packing recommendations, distance-based pricing, and professional PDF quote generation.

---

## ✨ Features

- **🤖 AI Packing Recommendations** - Automatically suggests optimal packing based on artwork materials (canvas, glass, metal, photographs)
- **📍 Distance-Based Pricing** - Calculates shipping costs based on distance from Paris using geocoding
- **💰 Dynamic Pricing Model** - Factors in weight, materials, delivery type, and packing requirements
- **📄 Professional PDF Quotes** - Generates branded PDF documents with detailed breakdowns
- **💱 Multi-Currency Support** - Quote in EUR, USD, or GBP with live conversion
- **👔 Admin Mode** - Toggle admin view to add profit margins
- **🎨 Demo Mode** - Pre-loaded with 10 famous artwork lots for testing

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd shipquote-pro

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run shipping-calculator.py
```

### Requirements

Create a `requirements.txt` file:

```
streamlit
geopy
reportlab
```

---

## 📋 How It Works

### 1. **Lot Selection**
Enter comma-separated lot numbers (e.g., `86, 89, 94`). The demo includes 10 pre-configured lots:

| Lot | Weight | Material | Example Artwork |
|-----|--------|----------|-----------------|
| 86  | Heavy  | Canvas   | Basquiat painting |
| 89  | Heavy  | Glass/Steel | Hirst sculpture |
| 94  | Light  | Photograph | Sherman photo |

### 2. **AI Packing Analysis**
The system analyzes each lot's materials and suggests:
- **Wood crate** - For fragile items (glass, metal, steel)
- **Cardboard box** - For paper-based works (photographs, prints)
- **Automatic (AI)** - For standard canvas paintings

### 3. **Delivery Address**
Type any address - the app uses OpenStreetMap geocoding to:
- Calculate distance from Paris (in km)
- Apply distance multipliers:
  - < 50 km: 1x base rate
  - 50-300 km: 1.2x
  - 300-1000 km: 1.5x
  - > 1000 km: 2x

### 4. **Pricing Calculation**

**Base formula per lot:**
```
Price = Base Rate (€220) × Weight Multiplier × Material Multiplier × Distance Multiplier
      + Delivery Cost + Packing Cost
```

**Weight Multipliers:**
- Light: 1x
- Medium: 1.5x
- Heavy: 2x

**Material Multipliers:**
- Canvas/Photograph: 1x
- Metal: 1.5x
- Glass/Steel: 1.6x

**Delivery Costs:**
- Curbside: -€30 (discount)
- Front delivery: €0
- White Glove (ground): +€100
- White Glove (elevator): +€150

**Packing Costs:**
- Automatic: €0
- Cardboard box: €20
- Bubble wrap: €40
- Wood crate: €80
- Custom: €100

### 5. **PDF Generation**
Download a professional quote including:
- Unique quote ID
- Client information
- Shipment details
- Itemized breakdown per lot
- Total price in selected currency
- Validity period (7 days)

---

## 🎯 Use Cases

- **Art Galleries** - Quote shipping for auction items
- **Collectors** - Estimate transport costs for acquisitions
- **Logistics Companies** - Generate client-ready quotes
- **Museums** - Plan exhibition transport budgets

---

## 🔧 Configuration

### Change Base Location
Edit `PARIS_COORD` in the code:
```python
PARIS_COORD = (48.8566, 2.3522)  # (latitude, longitude)
```

### Adjust Pricing
Modify multipliers and costs in the config section:
```python
WEIGHT_MULT = {"Light": 1, "Medium": 1.5, "Heavy": 2}
DELIVERY_COST = {"Front delivery": 0, "White Glove (ground)": 100}
```

### Add Custom Lots
Extend the `DEMO_LOTS` dictionary:
```python
DEMO_LOTS = {
    96: {"weight": "Medium", "material": "Canvas"},
    # Add more lots...
}
```

---

## 👨‍💼 Admin Features

Toggle **Admin Mode** to:
- View base shipping costs before markup
- Add profit margins (0-40%)
- See transparent pricing breakdown

---

## 📱 Screenshots

```
┌─────────────────────────────────────────┐
│  📦 ShipQuote Pro                       │
│  Professional Shipping Quote • Demo     │
├─────────────────────────────────────────┤
│  📦 Lots              │ 📊 Quote Summary│
│  86, 89, 94           │ ID: SQ-A3F89C2  │
│                       │                 │
│  💡 AI Packing        │ Distance: 450km │
│  [View suggestions]   │ Total: €2,340   │
│                       │                 │
│  📍 Delivery          │ [Download PDF]  │
│  London, UK           │                 │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

**Address not found:**
- Check spelling and try adding city/country
- Geocoding uses OpenStreetMap - some addresses may not exist

**PDF not generating:**
- Ensure `reportlab` is installed: `pip install reportlab`
- Check file permissions in output directory

**Lots not recognized:**
- Only lots 86-95 exist in demo mode
- Ensure lot numbers are comma-separated integers

---

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect repository at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Add `requirements.txt` to repo
4. Deploy!

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY shipping-calculator.py .
CMD ["streamlit", "run", "shipping-calculator.py", "--server.port=8501"]
```

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add more artwork types and materials
- Integrate real carrier APIs (FedEx, DHL)
- Multi-language support
- Historical quote tracking
- Email quote delivery

---



---

## Acknowledgments

- **Streamlit** - Web framework
- **Geopy** - Geocoding and distance calculation
- **ReportLab** - PDF generation
- **OpenStreetMap** - Address geocoding data

---

**Built with ❤️ for the fine art logistics community**
