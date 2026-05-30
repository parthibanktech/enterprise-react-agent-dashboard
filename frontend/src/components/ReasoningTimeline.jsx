import React from "react";
import { Terminal, Brain, Eye } from "lucide-react";

export default function ReasoningTimeline({ activeSteps }) {
  return (
    <section className="glass-panel" style={{ flex: 1, display: "flex", flexDirection: "column", padding: "20px", minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "hsl(var(--primary))" }}>
          🧠 ReAct Reasoning Trace Terminal
        </h2>
        <span style={{ fontSize: "0.75rem", color: "hsl(var(--text-muted))" }}>
          Step-by-Step Thinking Pipeline
        </span>
      </div>

      {/* Reasoning Timeline Cards stack */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "8px", display: "flex", flexDirection: "column", gap: "20px" }}>
        {activeSteps.length === 0 ? (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            color: "hsl(var(--text-muted))",
            textAlign: "center",
            padding: "20px"
          }}>
            <Terminal size={40} style={{ color: "hsl(var(--text-muted))", opacity: 0.5, marginBottom: "12px" }} />
            <h3>No trace inspected</h3>
            <p style={{ fontSize: "0.8rem", maxWidth: "260px" }}>
              Select an assistant answer card on the left to inspect the color-coded reasoning trace timeline here.
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", position: "relative" }}>
            {/* Vertical Timeline axis line */}
            <div style={{
              position: "absolute",
              left: "15px",
              top: "10px",
              bottom: "10px",
              width: "2px",
              background: "linear-gradient(to bottom, hsl(var(--primary)), hsl(var(--secondary)))",
              opacity: 0.3
            }} />

            {activeSteps.map((step, idx) => (
              <div key={idx} style={{ display: "flex", gap: "16px", marginBottom: "24px", position: "relative" }}>
                
                {/* Stepper node dot */}
                <div style={{
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  background: "hsl(var(--bg-card))",
                  border: "2px solid hsl(var(--primary))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "hsl(var(--primary))",
                  fontWeight: "bold",
                  fontSize: "0.85rem",
                  zIndex: 1,
                  flexShrink: 0
                }}>
                  {idx + 1}
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "10px", flex: 1, minWidth: 0 }}>
                  {/* Sub-Card 1: Thinking thought */}
                  <div className="glass-panel" style={{ padding: "12px", background: "rgba(139, 92, 246, 0.05)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", fontWeight: "600", color: "hsl(var(--primary))", marginBottom: "6px" }}>
                      <Brain size={14} /> THINK
                    </div>
                    <p style={{ fontSize: "0.85rem", color: "hsl(var(--text-primary))", lineHeight: "1.4" }}>
                      {step.thought}
                    </p>
                  </div>

                  {/* Sub-Card 2: Tool Action Call */}
                  {step.tool_name && (
                    <div className="glass-panel" style={{ padding: "12px", background: "rgba(255,255,255,0.02)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", fontWeight: "600", color: "hsl(var(--accent))", marginBottom: "6px" }}>
                        <Terminal size={14} /> ACT (Call Tool)
                      </div>
                      <p style={{ fontSize: "0.8rem", fontFamily: "var(--font-mono)", color: "#fff", background: "#060913", padding: "6px 10px", borderRadius: "6px", marginBottom: "6px" }}>
                        {step.tool_name}
                      </p>
                      <pre style={{
                        fontSize: "0.75rem",
                        fontFamily: "var(--font-mono)",
                        color: "hsl(var(--text-muted))",
                        background: "#060913",
                        padding: "8px",
                        borderRadius: "6px",
                        overflowX: "auto"
                      }}>
                        {JSON.stringify(step.args, null, 2)}
                      </pre>
                    </div>
                  )}

                  {/* Sub-Card 3: Tool Observation */}
                  {step.observation && (
                    <div className="glass-panel" style={{ padding: "12px", background: "rgba(6, 182, 212, 0.05)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", fontWeight: "600", color: "hsl(var(--secondary))", marginBottom: "6px" }}>
                        <Eye size={14} /> OBSERVE
                      </div>
                      <pre style={{
                        fontSize: "0.75rem",
                        fontFamily: "var(--font-mono)",
                        color: "hsl(var(--text-primary))",
                        background: "#060913",
                        padding: "8px",
                        borderRadius: "6px",
                        overflowX: "auto",
                        maxHeight: "150px"
                      }}>
                        {step.observation}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
