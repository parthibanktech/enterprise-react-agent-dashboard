import React from "react";
import { BookOpen, RefreshCw, Play, FileCode, Copy, Terminal } from "lucide-react";

export default function Academy({
  lessons,
  selectedLessonId,
  setSelectedLessonId,
  lessonCode,
  isLoadingLesson,
  isLessonRunning,
  handleRunLesson,
  lessonTerminalLogs
}) {
  return (
    <main style={{ display: "flex", flex: 1, gap: "16px", padding: "0 16px 16px", minHeight: 0 }}>
      {/* LEFT COLUMN: Lesson List */}
      <section className="glass-panel" style={{ flex: 4, display: "flex", flexDirection: "column", padding: "20px", minWidth: "320px", maxWidth: "420px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "hsl(var(--secondary))", display: "flex", alignItems: "center", gap: "8px" }}>
            <BookOpen size={18} /> Syllabus
          </h2>
          <span style={{ fontSize: "0.75rem", color: "hsl(var(--text-muted))" }}>
            11 Lessons • Syllabus Modules
          </span>
        </div>
        
        {/* Scrollable Lesson cards list */}
        <div className="custom-scrollbar" style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px", paddingRight: "4px" }}>
          {lessons.length === 0 ? (
            <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100%", color: "hsl(var(--text-muted))", gap: "10px" }}>
              <RefreshCw size={24} className="animate-spin" />
              <span style={{ fontSize: "0.8rem" }}>Loading lesson syllabus...</span>
            </div>
          ) : (
            lessons.map((lesson) => (
              <button
                key={lesson.id}
                onClick={() => setSelectedLessonId(lesson.id)}
                className={`lesson-card ${selectedLessonId === lesson.id ? "active" : ""}`}
              >
                <div className="lesson-badge">
                  {lesson.id}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px", minWidth: 0, flex: 1 }}>
                  <span style={{ fontSize: "0.82rem", fontWeight: "700", color: "#fff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {lesson.title.split(": ")[1] || lesson.title}
                  </span>
                  <span style={{ fontSize: "0.72rem", color: "hsl(var(--text-muted))", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {lesson.concept}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </section>

      {/* RIGHT COLUMN: Code View & Subprocess terminal runner */}
      <section className="glass-panel" style={{ flex: 6, display: "flex", flexDirection: "column", gap: "16px", padding: "20px", minWidth: 0 }}>
        {(() => {
          const currentLesson = lessons.find(l => l.id === selectedLessonId) || {
            title: `Lesson ${selectedLessonId}`,
            concept: "Loading Lesson Details...",
            description: "Contacting gateway...",
            filename: `${selectedLessonId}_lesson.py`
          };

          return (
            <>
              {/* Top lesson info header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "16px" }}>
                <div>
                  <h2 style={{ fontSize: "1.2rem", fontWeight: "800", color: "hsl(var(--primary))", fontFamily: "Outfit" }}>
                    {currentLesson.title}
                  </h2>
                  <p style={{ fontSize: "0.85rem", color: "hsl(var(--text-muted))", marginTop: "4px", fontWeight: "500" }}>
                    💡 Concept: <span style={{ color: "hsl(var(--secondary))" }}>{currentLesson.concept}</span>
                  </p>
                </div>
                
                <button
                  disabled={isLessonRunning || isLoadingLesson}
                  onClick={handleRunLesson}
                  className="run-btn"
                >
                  {isLessonRunning ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play size={14} style={{ fill: "currentColor" }} />
                      Run Lesson Code
                    </>
                  )}
                </button>
              </div>

              {/* Summary/Description Card */}
              <div style={{
                background: "rgba(139, 92, 246, 0.04)",
                border: "1px solid rgba(139, 92, 246, 0.12)",
                borderRadius: "10px",
                padding: "12px 16px",
                fontSize: "0.82rem",
                color: "hsl(var(--text-primary))",
                lineHeight: "1.5",
                whiteSpace: "pre-line"
              }}>
                {currentLesson.description}
              </div>

              {/* Code View + Subprocess DEV Terminal */}
              <div style={{ display: "flex", flex: 1, flexDirection: "column", gap: "16px", minHeight: 0 }}>
                
                {/* Code Editor */}
                <div style={{ display: "flex", flexDirection: "column", flex: 5, minHeight: 0 }}>
                  <div className="code-editor-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <FileCode size={14} style={{ color: "hsl(var(--primary))" }} />
                      <span style={{ fontSize: "0.75rem", fontFamily: "var(--font-mono)", color: "hsl(var(--text-muted))" }}>
                        {currentLesson.filename}
                      </span>
                    </div>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(lessonCode);
                        alert("Code successfully copied to clipboard!");
                      }}
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "hsl(var(--text-muted))",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        fontSize: "0.75rem",
                        fontWeight: "500"
                      }}
                    >
                      <Copy size={12} /> Copy Code
                    </button>
                  </div>
                  
                  <pre className="custom-scrollbar" style={{
                    flex: 1,
                    background: "#070a13",
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                    borderTop: "none",
                    borderRadius: "0 0 12px 12px",
                    padding: "16px",
                    overflow: "auto",
                    fontSize: "0.76rem",
                    fontFamily: "var(--font-mono)",
                    color: "#a9b1d6",
                    lineHeight: "1.5"
                  }}>
                    {isLoadingLesson ? "Loading lesson script code..." : lessonCode}
                  </pre>
                </div>

                {/* Integrated Hacker Output Terminal */}
                <div className="terminal-hacker" style={{ display: "flex", flexDirection: "column", flex: 4, minHeight: 0 }}>
                  <div className="terminal-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <Terminal size={14} style={{ color: "hsl(var(--secondary))" }} />
                      <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "#fff", letterSpacing: "0.5px" }}>
                        INTEGRATED RUNNER TERMINAL
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "5px" }}>
                      <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444" }} />
                      <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#eab308" }} />
                      <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e" }} />
                    </div>
                  </div>
                  
                  <div className="terminal-output-box custom-scrollbar">
                    {lessonTerminalLogs.map((log, idx) => (
                      <div key={idx} className={`terminal-line ${log.type}`}>
                        {log.text}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          );
        })()}
      </section>
    </main>
  );
}
