import "./index.css";

import React from "react";
import ReactDOM from "react-dom/client";
import AuditDashboard from "./admin/AuditDashboard";

const rootEl = document.getElementById("root");

if (rootEl) {
  const root = ReactDOM.createRoot(rootEl);
  root.render(
    <React.StrictMode>
      <AuditDashboard />
    </React.StrictMode>
  );
} else {
  console.error("Audit Dashboard: #root element not found");
}
