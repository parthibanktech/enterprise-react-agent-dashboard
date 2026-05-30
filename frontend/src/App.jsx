import React, { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import Sandbox from "./components/Sandbox";
import ReasoningTimeline from "./components/ReasoningTimeline";
import Academy from "./components/Academy";
import { apiFetch } from "./services/api";

export default function App() {
  // ── SHARED STATE ──
  const [activeTab, setActiveTab] = useState("sandbox"); // "sandbox" or "academy"
  const [engineMode, setEngineMode] = useState("Interactive Simulator");
  const [backendStatus, setBackendStatus] = useState("checking");
  const [schemaText, setSchemaText] = useState("");

  // ── SANDBOX STATES ──
  const [history, setHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [activeTraceIndex, setActiveTraceIndex] = useState(-1);
  const [traceHistory, setTraceHistory] = useState([]); // Steps array for each conversation turn
  const [isLoading, setIsLoading] = useState(false);

  // ── ACADEMY STATES ──
  const [lessons, setLessons] = useState([]);
  const [selectedLessonId, setSelectedLessonId] = useState("01");
  const [lessonCode, setLessonCode] = useState("");
  const [lessonTerminalLogs, setLessonTerminalLogs] = useState([]);
  const [isLessonRunning, setIsLessonRunning] = useState(false);
  const [isLoadingLesson, setIsLoadingLesson] = useState(false);

  const chatEndRef = useRef(null);

  // ── 1. INITIAL MOUNT HEARTBEATS & CATALOG SCHEMA ──
  useEffect(() => {
    // Health probe check
    apiFetch("healthz")
      .then((data) => {
        if (data.status === "healthy") {
          setBackendStatus("online");
          if (data.live_agent_ready) {
            setEngineMode("Live DeepSeek Agent");
          }
        }
      })
      .catch(() => setBackendStatus("offline"));

    // Retrieve SQLite products DB schema representation
    apiFetch("api/db-schema")
      .then((data) => setSchemaText(data.schema))
      .catch(() => {});

    // Prefetch all 11 lesson syllabus files
    apiFetch("api/lessons")
      .then((data) => setLessons(data))
      .catch((err) => console.error("Failed to load course list:", err));
  }, []);

  // ── 2. SCROLL HEARTBEAT CHAT MESSAGES ──
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  // ── 3. LESSON CODE CONTENT LOADER ──
  useEffect(() => {
    if (!selectedLessonId) return;
    setIsLoadingLesson(true);
    
    apiFetch(`api/lessons/${selectedLessonId}/code`)
      .then((data) => {
        setLessonCode(data.code);
        setLessonTerminalLogs([
          { text: `[SYSTEM] Loaded Syllabus Module: ${data.filename}`, type: "system" },
          { text: `[SYSTEM] Ready to execute. Click the "Run Lesson Code" button above.`, type: "system" }
        ]);
      })
      .catch((err) => {
        setLessonCode(`# Error loading lesson code: ${err.message}`);
        setLessonTerminalLogs([{ text: `[ERROR] Failed to fetch script contents: ${err.message}`, type: "stderr" }]);
      })
      .finally(() => {
        setIsLoadingLesson(false);
      });
  }, [selectedLessonId]);

  // ── 4. CHAT HANDLER SUBMISSION ──
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || isLoading) return;

    const query = currentMessage.trim();
    setCurrentMessage("");
    setIsLoading(true);

    const tempIndex = history.length;
    setHistory((prev) => [...prev, [query, "⏳ Analyzing query and executing ReAct loop..."]]);
    setTraceHistory((prev) => [...prev, []]);
    setActiveTraceIndex(tempIndex);

    try {
      const data = await apiFetch("api/chat", {
        method: "POST",
        body: JSON.stringify({
          message: query,
          history: history,
          live: engineMode === "Live DeepSeek Agent"
        })
      });

      setHistory((prev) => {
        const copy = [...prev];
        copy[tempIndex] = [query, data.final_response];
        return copy;
      });
      setTraceHistory((prev) => {
        const copy = [...prev];
        copy[tempIndex] = data.steps || [];
        return copy;
      });
    } catch (err) {
      setHistory((prev) => {
        const copy = [...prev];
        copy[tempIndex] = [query, `❌ Request failed. Backend server could not resolve: ${err.message}`];
        return copy;
      });
      setTraceHistory((prev) => {
        const copy = [...prev];
        copy[tempIndex] = [{
          thought: "Execution crashed due to communication network failure.",
          tool_name: "network_error_handler",
          args: { error: err.message },
          observation: "Check that the FastAPI backend is running."
        }];
        return copy;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const triggerPreset = (text) => {
    setCurrentMessage(text);
  };

  // ── 5. SUBPROCESS RUN LESSON RUNNER ──
  const handleRunLesson = async () => {
    if (isLessonRunning || !selectedLessonId) return;
    setIsLessonRunning(true);

    setLessonTerminalLogs((prev) => [
      ...prev,
      { text: `\n[EXECUTION] $ python lessons/${selectedLessonId}_...`, type: "system" },
      { text: `[SYSTEM] Executing script inside workspace environment...`, type: "system" }
    ]);

    try {
      const data = await apiFetch(`api/lessons/${selectedLessonId}/run`, {
        method: "POST"
      });

      const newLogs = [];
      if (data.stdout) {
        newLogs.push({ text: data.stdout, type: "stdout" });
      }
      if (data.stderr) {
        newLogs.push({ text: data.stderr, type: "stderr" });
      }
      if (data.exit_code === 0) {
        newLogs.push({ text: `\n[SUCCESS] Script finished successfully (exit code 0).`, type: "success" });
      } else {
        newLogs.push({ text: `\n[ERROR] Script exited with non-zero exit code: ${data.exit_code}.`, type: "stderr" });
      }

      setLessonTerminalLogs((prev) => [...prev, ...newLogs]);
    } catch (err) {
      setLessonTerminalLogs((prev) => [
        ...prev,
        { text: `[FATAL] Subprocess execution failed: ${err.message}`, type: "stderr" }
      ]);
    } finally {
      setIsLessonRunning(false);
    }
  };

  const activeSteps = activeTraceIndex >= 0 && traceHistory[activeTraceIndex] 
    ? traceHistory[activeTraceIndex] 
    : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Central Header Component */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        engineMode={engineMode}
        setEngineMode={setEngineMode}
        backendStatus={backendStatus}
      />

      {/* Main Tab Render Grid Area */}
      {activeTab === "sandbox" ? (
        <main style={{ display: "flex", flex: 1, gap: "16px", padding: "0 16px 16px", minHeight: 0 }}>
          <Sandbox
            history={history}
            currentMessage={currentMessage}
            setCurrentMessage={setCurrentMessage}
            isLoading={isLoading}
            handleSubmit={handleSubmit}
            triggerPreset={triggerPreset}
            activeTraceIndex={activeTraceIndex}
            setActiveTraceIndex={setActiveTraceIndex}
            chatEndRef={chatEndRef}
          />
          <ReasoningTimeline activeSteps={activeSteps} />
        </main>
      ) : (
        <Academy
          lessons={lessons}
          selectedLessonId={selectedLessonId}
          setSelectedLessonId={setSelectedLessonId}
          lessonCode={lessonCode}
          isLoadingLesson={isLoadingLesson}
          isLessonRunning={isLessonRunning}
          handleRunLesson={handleRunLesson}
          lessonTerminalLogs={lessonTerminalLogs}
        />
      )}
    </div>
  );
}
