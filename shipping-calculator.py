import React, { useState, useMemo } from 'react';
import { Package, MapPin, Clock, FileDown, Sparkles } from 'lucide-react';

// Demo data from Excel file
const DEMO_LOTS = [
  { LOT: 86, SALENO: 7185, TYPESET: "JEAN-MICHEL BASQUIAT (1960-1988)\nUntitled (Skull), 1981\nAcrylic and oil stick on canvas\n207.6 x 176.8 cm" },
  { LOT: 87, SALENO: 7185, TYPESET: "BANKSY (B. 1974)\nGirl with Balloon, 2006\nSpray paint on canvas\n150 x 150 cm" },
  { LOT: 88, SALENO: 7185, TYPESET: "YAYOI KUSAMA (B. 1929)\nPumpkin, 2015\nAcrylic on canvas\n162 x 162 cm" },
  { LOT: 89, SALENO: 7185, TYPESET: "DAMIEN HIRST (B. 1965)\nThe Physical Impossibility of Death, 1991\nGlass, steel, formaldehyde solution\n213 x 518 x 213 cm" },
  { LOT: 90, SALENO: 7185, TYPESET: "JEFF KOONS (B. 1955)\nBalloon Dog (Orange), 1994-2000\nMirror-polished stainless steel\n307.3 x 363.2 x 114.3 cm" },
  { LOT: 91, SALENO: 7185, TYPESET: "GERHARD RICHTER (B. 1932)\nAbstraktes Bild, 1986\nOil on canvas\n200 x 200 cm" },
  { LOT: 92, SALENO: 7185, TYPESET: "TAKASHI MURAKAMI (B. 1962)\nFlower Ball (3D), 2008\nAcrylic on canvas mounted on board\nDiameter: 300 cm" },
  { LOT: 93, SALENO: 7185, TYPESET: "ANSELM KIEFER (B. 1945)\nDie Meistersinger, 1981-1982\nOil, emulsion, straw on photograph\n280 x 380 cm" },
  { LOT: 94, SALENO: 7185, TYPESET: "CINDY SHERMAN (B. 1954)\nUntitled Film Still #21, 1978\nGelatin silver print\n20.3 x 25.4 cm" },
  { LOT: 95, SALENO: 7185, TYPESET: "ANDREAS GURSKY (B. 1955)\nRhein II, 1999\nC-print mounted on acrylic glass\n190 x 360 cm" }
];

const PACKING_TYPES = ['Automatic (AI)', 'Wood crate', 'Cardboard box', 'Bubble wrap', 'Custom'];
const DELIVERY_TYPES = ['Front delivery', 'White Glove (ground)', 'White Glove (elevator)', 'Curbside'];

const ShipQuotePro = () => {
  const [lotInput, setLotInput] = useState('86, 89, 94');
  const [location, setLocation] = useState('');
  const [packing, setPacking] = useState('Automatic (AI)');
  const [delivery, setDelivery] = useState('Front delivery');
  const [shippingCost, setShippingCost] = useState(500);
  const [insurance, setInsurance] = useState(100);

  const validUntil = new Date('2025-12-08');
  const daysRemaining = Math.max(0, Math.ceil((validUntil - new Date()) / (1000 * 60 * 60 * 24)));

  // Parse lot numbers and get descriptions
  const { lots, descriptions, saleNumbers } = useMemo(() => {
    const nums = lotInput.split(',').map(n => n.trim()).filter(n => n);
    const foundLots = [];
    const descs = [];
    const sales = new Set();

    nums.forEach(num => {
      const lotNum = parseInt(num);
      const lot = DEMO_LOTS.find(l => l.LOT === lotNum);
      if (lot) {
        foundLots.push(lotNum);
        descs.push(`--- LOT ${lotNum} ---\n${lot.TYPESET}`);
        sales.add(lot.SALENO);
      } else {
        descs.push(`--- LOT ${num} ---\n❌ Not found`);
      }
    });

    return {
      lots: foundLots,
      descriptions: descs.join('\n\n'),
      saleNumbers: Array.from(sales).join(', ')
    };
  }, [lotInput]);

  // AI packing suggestion
  const packingSuggestion = useMemo(() => {
    if (lots.length === 0) return 'Enter lot numbers for AI suggestions';
    
    const suggestions = lots.map(lotNum => {
      const lot = DEMO_LOTS.find(l => l.LOT === lotNum);
      if (!lot) return null;
      
      const desc = lot.TYPESET.toLowerCase();
      let suggestion = 'Automatic';
      
      if (desc.includes('glass') || desc.includes('steel') || desc.includes('formaldehyde')) {
        suggestion = 'Wood crate - fragile/heavy materials';
      } else if (desc.includes('print') || desc.includes('photograph') || desc.includes('paper')) {
        suggestion = 'Cardboard box - works on paper';
      } else if (desc.includes('canvas') || desc.includes('oil') || desc.includes('acrylic')) {
        suggestion = 'Automatic - canvas painting';
      }
      
      return { lot: lotNum, suggestion };
    }).filter(Boolean);

    return suggestions;
  }, [lots]);

  const total = shippingCost + insurance;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Package className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-800">ShipQuote Pro</h1>
          </div>
          <p className="text-gray-600">Professional Shipping Quote Calculator</p>
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded p-3 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-blue-800">DEMO MODE: Using auction sale #7185 with 10 sample lots (86-95)</span>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Lot Information */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Package className="w-6 h-6" />
                Lot Information
              </h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lot Numbers (comma-separated, max 10)
                </label>
                <input
                  type="text"
                  value={lotInput}
                  onChange={(e) => setLotInput(e.target.value)}
                  placeholder="e.g., 86, 87, 88"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Try: 86, 89, 94</p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Sale Number</label>
                <input
                  type="text"
                  value={saleNumbers || 'N/A'}
                  disabled
                  className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-600"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Descriptions</label>
                <textarea
                  value={descriptions}
                  disabled
                  rows={10}
                  className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-600 text-sm font-mono"
                />
              </div>

              {/* AI Suggestions */}
              {packingSuggestion.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <h3 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    AI Packing Suggestions
                  </h3>
                  {packingSuggestion.map(({ lot, suggestion }) => (
                    <div key={lot} className="text-sm text-amber-800 mb-1">
                      <strong>Lot {lot}:</strong> {suggestion}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Shipment Parameters */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <MapPin className="w-6 h-6" />
                Shipment Parameters
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="123 Main St, New York, NY"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Packing Type</label>
                  <select
                    value={packing}
                    onChange={(e) => setPacking(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {PACKING_TYPES.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Type</label>
                  <select
                    value={delivery}
                    onChange={(e) => setDelivery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {DELIVERY_TYPES.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Pricing */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">💰 Pricing</h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Shipping Cost (EUR)</label>
                  <input
                    type="number"
                    value={shippingCost}
                    onChange={(e) => setShippingCost(Number(e.target.value))}
                    min="0"
                    step="10"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Insurance (EUR)</label>
                  <input
                    type="number"
                    value={insurance}
                    onChange={(e) => setInsurance(Number(e.target.value))}
                    min="0"
                    step="10"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">TOTAL WITH INSURANCE</div>
                <div className="text-4xl font-bold text-blue-600">€{total.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
              </div>
            </div>

            {/* Quote Summary */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Quote Summary</h2>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Number of Lots:</span>
                  <span className="font-semibold">{lots.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sale Number:</span>
                  <span className="font-semibold">{saleNumbers || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Packing:</span>
                  <span className="font-semibold">{packing}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Delivery Type:</span>
                  <span className="font-semibold">{delivery}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Destination:</span>
                  <span className="font-semibold">{location || 'Not specified'}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                  <Clock className="w-4 h-4" />
                  <span>Quote valid until: {validUntil.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                </div>
                <div className="text-sm font-semibold text-red-600">
                  Days remaining: {daysRemaining} days
                </div>
              </div>

              <button
                onClick={() => alert('PDF generation would require backend integration')}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <FileDown className="w-5 h-5" />
                Download Quote as PDF
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h3 className="font-bold text-gray-800 mb-3">📋 How to use:</h3>
          <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
            <li><strong>Enter lot numbers</strong> (comma-separated, e.g., "86, 87, 88") - max 10 lots</li>
            <li><strong>Descriptions auto-populate</strong> from the demo database</li>
            <li><strong>AI suggests packing</strong> based on artwork type</li>
            <li><strong>Enter delivery address</strong> and select options</li>
            <li><strong>Set pricing</strong> to see total with insurance</li>
            <li><strong>Download PDF quote</strong> (requires backend)</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default ShipQuotePro;
