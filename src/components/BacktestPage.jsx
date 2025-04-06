"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import TradeList from "./TradeList";
// import BacktestChart from "./BacktestChart";

const BacktestPage = () => {
  const [symbols, setSymbols] = useState({});
  const [symbol, setSymbol] = useState("");
  const [timeframe, setTimeframe] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const response = await axios.get("https://forex-trading-2.onrender.com/get_symbols/");
        setSymbols(response.data);
  
        if (Object.keys(response.data).length > 0) {
          const firstSymbol = Object.keys(response.data)[0];
          setSymbol(firstSymbol);
          setTimeframe(Object.keys(response.data[firstSymbol])[0]);
        }
      } catch (error) {
        console.error("❌ Error fetching symbols:", error);
      }
    };
  
    fetchSymbols();
  }, []);


  return (
    <div className="trade-list container">
      <h2 className="text-center text-primary mb-4">Forex Backtest</h2>

      {/* Symbol and Timeframe Selectors */}
      <div className="card mx-auto mb-4 p-3 shadow" style={{ maxWidth: "500px" }}>
        <div className="d-flex flex-wrap justify-content-center gap-3">
          {/* Symbol Dropdown */}
          <select
            className="form-select w-auto"
            value={symbol}
            onChange={(e) => {
              const newSymbol = e.target.value;
              setSymbol(newSymbol);
              const availableTimeframes = Object.keys(symbols[newSymbol] || {});
              setTimeframe(availableTimeframes.includes(timeframe) ? timeframe : availableTimeframes[0]);
              setPage(1);
            }}
          >
            {Object.keys(symbols).map((sym) => (
              <option key={sym} value={sym}>{sym}</option>
            ))}
          </select>

          {/* Timeframe Dropdown */}
          <select
            className="form-select w-auto"
            value={timeframe}
            onChange={(e) => {
              setTimeframe(e.target.value);
              setPage(1);
            }}
            disabled={!symbol}
          >
            {symbols[symbol] &&
              Object.keys(symbols[symbol]).map((tf) => (
                <option key={tf} value={tf}>{tf}</option>
              ))}
          </select>
        </div>
      </div>

      {/* Render Chart and Table Together */}
      {symbol && timeframe && (
        <>
          {/* <BacktestChart symbol={symbol} timeframe={timeframe} page={page} setPage={setPage} /> */}
          <TradeList symbol={symbol} timeframe={timeframe} page={page} setPage={setPage} />
        </>
      )}
    </div>
  );
};

export default BacktestPage;
