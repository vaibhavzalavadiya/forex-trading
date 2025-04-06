import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Container, Navbar } from "react-bootstrap";
import BacktestPage from "./components/BacktestPage";
// import BacktestChart from "./components/BacktestChart";
import ErrorBoundary from "./components/ErrorBoundary";

function App() {
  return (
    <Router>
      <div className="bg-light min-vh-100 d-flex flex-column">
        {/* ✅ Navbar */}
        <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
          <Navbar.Brand href="/" className="mx-3">
            Forex Strategy Backtester
          </Navbar.Brand>
        </Navbar>

        {/* ✅ Main Content */}
        <Container className="flex-grow-1">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<BacktestPage />} />
              {/* <Route path="/backchart" element={<BacktestChart />} /> */}
            </Routes>
          </ErrorBoundary>
        </Container>
      </div>
    </Router>
  );
}

export default App;
