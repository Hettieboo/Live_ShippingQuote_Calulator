# Live_ShippingQuote_Calulator
# 📦 Shipping Calculator

A web-based shipping quote calculator for art logistics with intelligent packing suggestions, address lookup, and PDF quote generation.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Gradio](https://img.shields.io/badge/gradio-latest-orange)

## 🎯 Features

- **Multi-lot Support**: Calculate quotes for up to 10 lots simultaneously
- **Excel Integration**: Auto-populate lot descriptions from Excel database
- **Smart Address Lookup**: Real-time address suggestions using OpenStreetMap
- **Intelligent Packing Suggestions**: Automatic packing recommendations based on artwork type
- **PDF Export**: Generate professional PDF quotes (optional)
- **Live Calculations**: Real-time pricing updates
- **Quote Expiration Tracking**: Built-in countdown for quote validity

## 🚀 Quick Start

### Google Colab (Recommended for Testing)

1. Open the notebook in Google Colab
2. Install dependencies:
```python
!pip install reportlab
```
3. Run all cells
4. Upload your Excel file when prompted
5. Access the web interface via the generated link

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/convelio-calculator.git
cd convelio-calculator
```

2. **Install dependencies**
```bash
pip install gradio pandas openpyxl geopy reportlab
```

3. **Prepare your data**
   - Place your Excel file in the project directory
   - Update the `EXCEL_FILE` variable in the script with your filename

4. **Run the application**
```bash
python shipping_calculator.py
```

5. **Access the interface**
   - Local: `http://localhost:7860`
   - Public URL will be displayed in the console

## 📋 Requirements

### Required Dependencies
```
gradio
pandas
openpyxl
geopy
```

### Optional Dependencies
```
reportlab  # For PDF generation
```

## 📊 Excel File Format

Your Excel file should contain the following columns:

| Column | Description | Required |
|--------|-------------|----------|
| `LOT` | Lot number (integer) | ✅ |
| `TYPESET` | Artwork description | ✅ |
| `SALENO` | Sale number | ✅ |
| Additional columns | Dimensions, materials, etc. | ⚪ |

**Example:**
```
LOT  | TYPESET                        | SALENO
-----|--------------------------------|--------
86   | Oil on canvas, 100x80cm...     | 2302
87   | Bronze sculpture, 50cm...      | 2302
```

## 🎨 Usage

### Basic Workflow

1. **Enter Lot Numbers**
   - Single lot: `86`
   - Multiple lots: `86, 87, 88` (comma-separated, max 10)

2. **Review Auto-Populated Data**
   - Descriptions load automatically from Excel
   - Sale numbers are displayed

3. **Set Delivery Location**
   - Start typing an address
   - Select from auto-suggested addresses
   - Or enter manually

4. **Choose Options**
   - Packing type (or use automatic suggestions)
   - Delivery type (Front-delivery, White Glove, etc.)

5. **Enter Pricing**
   - Convelio offer amount
   - Insurance amount
   - Total calculates automatically

6. **Generate Quote**
   - Review the offer recap
   - Download PDF (if reportlab installed)

### Packing Type Options

| Option | Best For |
|--------|----------|
| **Automatic** | Let Convelio assess (default) |
| **Wood Crate** | Fragile items, sculptures, glass |
| **Cardboard Box** | Works on paper, prints, photos |
| **Bubble Wrap** | Small, sturdy items |
| **Custom Packing** | Special requirements |

### Delivery Type Options

- **Front-delivery**: Standard delivery to front door
- **White Glove (ground floor)**: Professional installation, ground level
- **White Glove (with elevator)**: Professional installation, any floor
- **Curbside delivery**: Delivery to curb only

## 🤖 Intelligent Features

### Automatic Packing Suggestions

The calculator analyzes artwork descriptions and suggests optimal packing:

- **Glass/Ceramic/Porcelain** → Wood crate
- **Sculptures/Bronze/Marble** → Wood crate
- **Photographs/Prints/Drawings** → Cardboard box
- **Canvas Paintings** → Automatic assessment
- **Mixed lots** → Most protective option

### Address Validation

- Real-time geocoding via OpenStreetMap
- Automatic address formatting
- Suggestion caching for performance

## ⚙️ Configuration

Edit these constants in the script:

```python
# Quote expiration date
VALID_UNTIL_DATE = datetime(2025, 12, 8)

# Excel filename (for local use)
EXCEL_FILE = "your_file.xlsx"
```

## 📄 PDF Generation

When reportlab is installed, quotes can be exported as professional PDFs including:

- Quote date and validity period
- Complete lot information
- Shipment details (location, packing, delivery)
- Itemized pricing breakdown
- Formatted for printing or email

## 🔧 Troubleshooting

### Excel File Not Loading
- Verify file is in the correct directory
- Check file permissions
- Ensure column names match expected format

### Address Lookup Not Working
- Check internet connection
- Verify geopy is installed correctly
- Clear geocode cache if stale

### PDF Download Unavailable
- Install reportlab: `pip install reportlab`
- Restart the application

### Application Won't Start
```bash
# Check Python version (3.7+ required)
python --version

# Reinstall dependencies
pip install --upgrade gradio pandas openpyxl geopy reportlab
```

## 🌐 Deployment

### Local Network Access
```python
demo.launch(server_name="0.0.0.0", server_port=7860)
```

### Share Publicly
```python
demo.launch(share=True)  # Generates temporary public URL
```

### Production Deployment
- Deploy to Hugging Face Spaces
- Use Docker container
- Deploy to cloud platform (AWS, GCP, Azure)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/)
- Address lookup powered by [OpenStreetMap](https://www.openstreetmap.org/) via [geopy](https://geopy.readthedocs.io/)
- PDF generation using [ReportLab](https://www.reportlab.com/)

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section

---

**Made for Art Logistics** | Powered by Gradio & OpenStreetMap
