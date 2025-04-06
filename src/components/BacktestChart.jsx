import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import axios from "axios";

const BacktestChart = ({ symbol, timeframe }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol || !timeframe || !chartContainerRef.current) return;

    setLoading(true);
    setError(null);

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "#ffffff" },
        textColor: "#000000",
      },
      grid: {
        vertLines: { color: "#eee" },
        horzLines: { color: "#eee" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    });

    const candleSeries = chart.addCandlestickSeries();
    chartRef.current = chart;

    // Fetch data from backend
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/backtest/", {
          params: { symbol, timeframe },
        });

        const candlestickData = response.data.map((item) => ({
          time: Math.floor(new Date(item.time).getTime() / 1000),
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));

        candleSeries.setData(candlestickData);
        chart.timeScale().fitContent();
      } catch (err) {
        console.error("Failed to load data:", err);
        setError("Failed to load chart data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Cleanup
    return () => {
      chart.remove();
    };
  }, [symbol, timeframe]);

  return (
    <div>
      <h4>
        Backtest Chart {symbol && timeframe ? `(${symbol} - ${timeframe})` : ""}
      </h4>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div
        ref={chartContainerRef}
        style={{ width: "100%", height: 400, position: "relative" }}
      />
    </div>
  );
};

export default BacktestChart;
