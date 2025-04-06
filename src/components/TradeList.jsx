"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Spinner, Alert, Pagination, Badge, Container, OverlayTrigger, Tooltip } from "react-bootstrap";

const TradeList = ({ symbol, timeframe, page, setPage }) => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalPages, setTotalPages] = useState(1);

  const limitPerPage = 20;

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!symbol || !timeframe) {
          setError("Please select a symbol and timeframe.");
          setLoading(false);
          return;
        }

        const response = await axios.get("http://127.0.0.1:8000/api/backtest/", {
          params: { symbol, timeframe, page, limit: limitPerPage },
        });

        if (!response.data.signals || response.data.signals.length === 0) {
          setError("No trade history available.");
          setTrades([]);
          return;
        }

        setTrades(response.data.signals);
        setTotalPages(response.data.summary.total_pages);
      } catch (err) {
        setError("Failed to load trade history.");
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, [symbol, timeframe, page]);

  return (
    <Container className="mt-4">
      <h3 className="text-center mb-4">📊 Trade History for {symbol}</h3>

      {loading && <Loader />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && trades.length > 0 && <TradeTable trades={trades} page={page} />}
      {!loading && !error && totalPages > 1 && (
        <CustomPagination page={page} setPage={setPage} totalPages={totalPages} />
      )}
    </Container>
  );
};

export default TradeList;

// ✅ Loader Component
const Loader = () => (
  <div className="d-flex justify-content-center my-3">
    <Spinner animation="border" variant="primary" />
  </div>
);

// ✅ Error Message Component
const ErrorMessage = ({ message }) => (
  <Alert variant="danger" className="text-center">
    {message}
  </Alert>
);

// ✅ Trade Table Component
const TradeTable = ({ trades, page }) => {
  const limitPerPage = 20;

  return (
    <div className="table-responsive">
      <Table striped bordered hover responsive="md" className="shadow-sm text-nowrap">
        <thead className="bg-primary text-white text-center">
          <tr>
            <th>#</th>
            <th>Type</th>
            <th>Entry Price</th>
            <th>Target</th>
            <th>Stop Loss</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, index) => (
            <tr key={index} className="text-center">
              <td>{(page - 1) * limitPerPage + index + 1}</td>
              <td>
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>{trade.type === "BUY" ? "Buy Trade" : "Sell Trade"}</Tooltip>}
                >
                  <Badge bg={trade.type === "BUY" ? "success" : "danger"}>{trade.type}</Badge>
                </OverlayTrigger>
              </td>
              <td>${trade.entry_price.toFixed(4)}</td>
              <td>${trade.target.toFixed(4)}</td>
              <td>${trade.stop_loss.toFixed(4)}</td>
              <td>{new Date(trade.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

// ✅ Custom Pagination (Same style as your original version)
const CustomPagination = ({ page, setPage, totalPages }) => (
  <div className="d-flex justify-content-center mt-3">
    <Pagination>
      <Pagination.First disabled={page === 1} onClick={() => setPage(1)} />
      <Pagination.Prev disabled={page === 1} onClick={() => setPage(page - 1)} />

      {/* Page 1 */}
      <Pagination.Item active={page === 1} onClick={() => setPage(1)}>1</Pagination.Item>

      {/* Page 2 (if totalPages > 1) */}
      {totalPages > 1 && (
        <Pagination.Item active={page === 2} onClick={() => setPage(2)}>2</Pagination.Item>
      )}

      {/* Show last page (totalPages) */}
      {totalPages > 2 && (
        <>
          <Pagination.Ellipsis disabled />
          <Pagination.Item active={page === totalPages} onClick={() => setPage(totalPages)}>
            {totalPages}
          </Pagination.Item>
        </>
      )}

      <Pagination.Next disabled={page === totalPages} onClick={() => setPage(page + 1)} />
      <Pagination.Last disabled={page === totalPages} onClick={() => setPage(totalPages)} />
    </Pagination>
  </div>
);
