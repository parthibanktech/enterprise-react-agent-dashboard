import React from "react";
import { Brain, BookOpen, Activity } from "lucide-react";

export default function Header({ activeTab, setActiveTab, engineMode, setEngineMode, backendStatus }) {
  return (
    <header className="glass-panel pulse-border" style={{
      display: "flex", 
      justifyContent: "space-between", 
      alignItems: "center", 
      padding: "16px 24px",
      margin: "16px",
      background: "rgba(16, 22, 37, 0.85)",
      gap: "16px",
      flexWrap: "wrap"
    }}>
      {/* Brand logo & title */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{
          background: "linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--secondary)) 100%)",
          padding: "8px",
          borderRadius: "10px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}>
          <Brain size={24} style={{ color: "#fff" }} />
        </div>
        <div>
          <h1 style={{ fontFamily: "Outfit", fontWeight: "800", fontSize: "1.4rem", letterSpacing: "-0.5px", margin: 0, lineHeight: 1.2 }}>
            SENTRY AI
          </h1>
          <p style={{ fontSize: "0.75rem", color: "hsl(var(--text-muted))", margin: 0 }}>
            Parthiban's Consolidated Enterprise ReAct Dashboard
          </p>
        </div>
      </div>

      {/* Dynamic Center Navigation Tabs */}
      <div style={{ display: "flex", gap: "6px", background: "rgba(15, 23, 42, 0.4)", padding: "4px", borderRadius: "8px" }}>
        <button 
          onClick={() => setActiveTab("sandbox")}
          className={`nav-tab-button ${activeTab === "sandbox" ? "active" : ""}`}
        >
          <Brain size={16} />
          Agent Sandbox
        </button>
        <button 
          onClick={() => setActiveTab("academy")}
          className={`nav-tab-button ${activeTab === "academy" ? "active" : ""}`}
        >
          <BookOpen size={16} />
          Syllabus Reference
        </button>
      </div>

      {/* Engine selector and backend indicator */}
      <div style={{ display: "flex", alignItems: "center", gap: "20px", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.8rem" }}>
          <Activity size={14} style={{
            color: backendStatus === "online" ? "hsl(var(--success))" : "hsl(var(--danger))"
          }} />
          <span style={{ color: "hsl(var(--text-muted))" }}>Gateway:</span>
          <span style={{
            fontWeight: "600",
            color: backendStatus === "online" ? "hsl(var(--success))" : "hsl(var(--danger))"
          }}>
            {backendStatus.toUpperCase()}
          </span>
        </div>

        <div style={{ display: "flex", background: "rgba(15, 23, 42, 0.4)", padding: "4px", borderRadius: "8px" }}>
          {["Interactive Simulator", "Live DeepSeek Agent"].map((mode) => (
            <button 
              key={mode}
              onClick={() => setEngineMode(mode)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                border: "none",
                fontSize: "0.8rem",
                fontWeight: "600",
                cursor: "pointer",
                background: engineMode === mode ? "hsl(var(--primary))" : "transparent",
                color: "#fff",
                transition: "all 0.2s"
              }}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
