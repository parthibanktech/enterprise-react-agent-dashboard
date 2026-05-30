import React from "react";
import { Bot, User, Send, Zap } from "lucide-react";

export default function Sandbox({
  history,
  currentMessage,
  setCurrentMessage,
  isLoading,
  handleSubmit,
  triggerPreset,
  activeTraceIndex,
  setActiveTraceIndex,
  chatEndRef
}) {
  return (
    <section className="glass-panel" style={{ flex: 1, display: "flex", flexDirection: "column", padding: "20px", minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "hsl(var(--secondary))" }}>
          💬 Conversational interface
        </h2>
        <span style={{ fontSize: "0.75rem", color: "hsl(var(--text-muted))" }}>
          Active Thread • Unified ReAct Model
        </span>
      </div>

      {/* Chat Messages scroll area */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "8px", display: "flex", flexDirection: "column", gap: "16px", marginBottom: "16px" }}>
        {history.length === 0 ? (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            textAlign: "center",
            color: "hsl(var(--text-muted))",
            padding: "20px"
          }}>
            <Bot size={48} style={{ color: "hsl(var(--primary))", marginBottom: "12px" }} className="float" />
            <h3 style={{ color: "#fff", marginBottom: "6px" }}>How can I help you today?</h3>
            <p style={{ fontSize: "0.85rem", maxWidth: "340px", marginBottom: "20px" }}>
              Ask questions about inventory listings, geocoded weather warnings, or bulk pricing invoices.
            </p>
          </div>
        ) : (
          history.map((chat, idx) => (
            <div key={idx} style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {/* User message */}
              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <div style={{
                  background: "rgba(139, 92, 246, 0.15)",
                  border: "1px solid rgba(139, 92, 246, 0.2)",
                  padding: "10px 14px",
                  borderRadius: "12px 12px 0 12px",
                  fontSize: "0.9rem",
                  maxWidth: "80%"
                }}>
                  {chat[0]}
                </div>
                <div style={{
                  background: "hsl(var(--primary))",
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  <User size={14} style={{ color: "#fff" }} />
                </div>
              </div>

              {/* Assistant response */}
              <div 
                onClick={() => setActiveTraceIndex(idx)}
                style={{ 
                  display: "flex", 
                  gap: "10px", 
                  cursor: "pointer",
                  borderRadius: "8px",
                  padding: "4px",
                  transition: "background 0.2s"
                }}
                className={activeTraceIndex === idx ? "pulse-border" : ""}
              >
                <div style={{
                  background: "hsl(var(--secondary))",
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  <Bot size={14} style={{ color: "#fff" }} />
                </div>
                <div style={{
                  background: activeTraceIndex === idx ? "rgba(6, 182, 212, 0.08)" : "rgba(15, 23, 42, 0.3)",
                  border: activeTraceIndex === idx ? "1px solid rgba(6, 182, 212, 0.25)" : "1px solid hsl(var(--border-glass))",
                  padding: "10px 14px",
                  borderRadius: "0 12px 12px 12px",
                  fontSize: "0.9rem",
                  maxWidth: "80%",
                  whiteSpace: "pre-wrap"
                }}>
                  {chat[1]}
                  <div style={{
                    marginTop: "8px", 
                    fontSize: "0.75rem", 
                    color: "hsl(var(--secondary))",
                    fontWeight: "600",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px"
                  }}>
                    <Zap size={10} /> Inspect Reasoning Timeline (Click here)
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Preset prompt triggers list */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
        <span style={{ fontSize: "0.75rem", color: "hsl(var(--text-muted))", alignSelf: "center" }}>
          💡 Preset Prompts:
        </span>
        {[
          "Which products in the database have a price greater than $200?",
          "I am traveling to Tokyo. Check if it's raining and tell me what to bring!",
          "What is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?",
          "What is 347 multiplied by 86, and then divide that result by 5?",
          "What is today's date? Check the system clock and tell me what day of the week it is.",
          "Search Google for top tourist spots and news in Noida, India.",
          "A professional laptop costs ₹65000 before tax. GST is 18%. Calculate the GST amount and total price.",
          "An designer Kurta costs ₹1800 and is currently on a 35% discount. What are my savings and final pay amount?",
          "What is the category and pric of the Ergonomic Desk Chair in the database?",
          "What is 50 divided by 0? Can you compute this mathematically?"
        ].map((p, idx) => (
          <button
            key={idx}
            onClick={() => triggerPreset(p)}
            style={{
              padding: "4px 8px",
              borderRadius: "6px",
              border: "1px dashed rgba(255,255,255,0.1)",
              background: "transparent",
              color: "hsl(var(--text-muted))",
              fontSize: "0.75rem",
              cursor: "pointer",
              transition: "all 0.2s"
            }}
            className="glow-hover"
          >
            Scenario {idx+1}
          </button>
        ))}
      </div>

      {/* Unified form input */}
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px" }}>
        <input 
          type="text"
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          placeholder="Ask Sentry AI a query... (e.g. 'What is 347 * 86?')"
          style={{
            flex: 1,
            background: "rgba(15, 23, 42, 0.4)",
            border: "1px solid hsl(var(--border-glass))",
            borderRadius: "10px",
            padding: "12px 16px",
            color: "#fff",
            fontFamily: "var(--font-sans)",
            fontSize: "0.9rem",
            outline: "none"
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !currentMessage.trim()}
          style={{
            background: "hsl(var(--primary))",
            border: "none",
            borderRadius: "10px",
            padding: "0 16px",
            color: "#fff",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: (isLoading || !currentMessage.trim()) ? 0.5 : 1
          }}
          className="glow-hover"
        >
          <Send size={16} />
        </button>
      </form>
    </section>
  );
}
