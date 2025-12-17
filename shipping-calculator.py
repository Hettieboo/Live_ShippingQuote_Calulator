{/* Lot Selector */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Select Land Lot
        </label>
        <select
          value={selectedLot?.id || ""}
          onChange={(e) => {
            const lot = lots.find((l) => l.id === e.target.value);
            setSelectedLot(lot || null);
          }}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">-- Choose a lot --</option>
          {lots.map((lot) => (
            <option key={lot.id} value={lot.id}>
              {lot.title} - {lot.location} ({lot.size})
            </option>
          ))}
        </select>
      </div>

      {/* Lot Details */}
      {selectedLot && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
          <img
            src={selectedLot.image}
            alt={selectedLot.title}
            className="w-full h-64 object-cover"
          />
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-3">{selectedLot.title}</h3>
            <p className="text-gray-600 mb-4">{selectedLot.description}</p>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600">Size</p>
                <p className="font-semibold">{selectedLot.size}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600">Location</p>
                <p className="font-semibold">{selectedLot.location}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600">Starting Bid</p>
                <p className="font-semibold text-green-600">
                  ${selectedLot.startingBid.toLocaleString()}
                </p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600">Current Bid</p>
                <p className="font-semibold text-blue-600">
                  ${selectedLot.currentBid.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
