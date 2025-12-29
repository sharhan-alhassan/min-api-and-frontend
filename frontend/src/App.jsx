import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const intentCardsFallback = {
  greeting: {
    keywords: ["hi", "hello", "hey"],
    response: "Hello! How can I help you today?",
  },
  help: {
    keywords: ["help", "assist", "support"],
    response: "Sure! Tell me what you need help with.",
  },
  python: {
    keywords: ["python", "code", "programming"],
    response: "Python is a beginner-friendly programming language.",
  },
  unknown: {
    response: "I'm not sure I understand. Can you rephrase?",
  },
};

const MessageBubble = ({ role, text, intent, matchedKeyword }) => {
  const isUser = role === "user";
  const bubbleClasses = isUser
    ? "bg-gradient-to-r from-sky-500/80 to-indigo-500/80 text-white shadow-lg shadow-sky-900/40"
    : "bg-panel text-gray-100 border border-white/5";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 whitespace-pre-wrap ${bubbleClasses}`}
      >
        <div className="flex items-center gap-2 mb-1 text-xs uppercase tracking-wide text-white/70">
          <span className="px-2 py-0.5 rounded-full bg-white/10 border border-white/10">
            {isUser ? "You" : "Bot"}
          </span>
          {!isUser && intent && (
            <span className="px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-200 border border-sky-500/30">
              intent: {intent}
            </span>
          )}
          {!isUser && matchedKeyword && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30">
              matched: {matchedKeyword}
            </span>
          )}
        </div>
        <p className="leading-relaxed text-sm md:text-base">{text}</p>
      </div>
    </div>
  );
};

const LoadingDots = () => (
  <div className="flex gap-1">
    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce [animation-delay:-0.2s]" />
    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce" />
    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce [animation-delay:0.2s]" />
  </div>
);

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [intents, setIntents] = useState(intentCardsFallback);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastReasoning, setLastReasoning] = useState({
    intent: "",
    matchedKeyword: "",
    steps: [],
  });
  const [historyLoaded, setHistoryLoaded] = useState(false);

  const fetchIntents = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/intents`);
      if (!res.ok) throw new Error("Unable to fetch intents");
      const data = await res.json();
      if (data?.intents) {
        setIntents(data.intents);
      }
    } catch (err) {
      console.warn("Using fallback intents:", err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      if (!res.ok) throw new Error("Failed to load history");
      const history = await res.json();
      setMessages(
        history.map((item) => ({
          role: item.role,
          text: item.content,
          intent: item.intent || "",
        }))
      );
    } catch (err) {
      console.warn("No history yet:", err);
    } finally {
      setHistoryLoaded(true);
    }
  };

  useEffect(() => {
    fetchIntents();
    fetchHistory();
  }, []);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setError("");
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail?.detail || "Something went wrong.");
      }

      const data = await res.json();
      const botMessage = {
        role: "bot",
        text: data.reply,
        intent: data.intent,
        matchedKeyword: data.matched_keyword,
      };

      setMessages((prev) => [...prev, botMessage]);
      setLastReasoning({
        intent: data.intent,
        matchedKeyword: data.matched_keyword || "",
        steps: data.steps || [],
      });
    } catch (err) {
      setError(err.message || "Unable to reach the backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const intentList = useMemo(() => Object.entries(intents), [intents]);

  return (
    <div className="min-h-screen px-4 pb-10">
      <header className="max-w-5xl mx-auto py-10">
        <p className="text-xs uppercase tracking-[0.4em] text-sky-200/70 mb-2">
          Mini ChatGPT
        </p>
        <h1 className="text-3xl md:text-4xl font-semibold text-white mb-4">
          Rule-based chatbot that explains how it “thinks”
        </h1>
        <p className="text-gray-300 max-w-3xl">
          No API keys. No magic. We simply match keywords to intents and return
          canned responses—so you can see the skeleton of how LLM prompts feel
          without any black box.
        </p>
      </header>

      <main className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
        <section className="bg-panel/80 backdrop-blur rounded-2xl border border-white/5 shadow-xl shadow-black/30">
          <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Chat</h2>
              <p className="text-sm text-gray-400">
                Looks like ChatGPT, but powered by simple rules.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Backend: {API_BASE}
            </div>
          </div>

          <div className="px-6 py-6 space-y-4 h-[60vh] overflow-y-auto">
            {!historyLoaded && (
              <div className="flex justify-center pt-6">
                <LoadingDots />
              </div>
            )}
            {messages.length === 0 && historyLoaded && (
              <div className="text-center text-gray-400 text-sm">
                Start the conversation — try typing “hello” or “help”.
              </div>
            )}
            {messages.map((msg, idx) => (
              <MessageBubble
                key={`${idx}-${msg.text}`}
                role={msg.role}
                text={msg.text}
                intent={msg.intent}
                matchedKeyword={msg.matchedKeyword}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-panel border border-white/5 rounded-2xl px-4 py-3 flex items-center gap-3">
                  <LoadingDots />
                  <span className="text-sm text-gray-300">Thinking...</span>
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-white/5 px-6 py-4 bg-panel/70 rounded-b-2xl">
            {error && (
              <div className="mb-3 text-sm text-rose-300 bg-rose-900/40 border border-rose-500/30 rounded-lg px-3 py-2">
                {error}
              </div>
            )}
            <div className="flex items-end gap-3">
              <textarea
                className="flex-1 rounded-xl bg-[#0f1a28] border border-white/10 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-sky-500/70 transition resize-none"
                rows={2}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask something (e.g., “Can you help?” or “Tell me about Python”)."
              />
              <button
                onClick={handleSend}
                disabled={isLoading}
                className="h-[46px] min-w-[100px] rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white font-semibold shadow-lg shadow-sky-900/40 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Send
              </button>
            </div>
          </div>
        </section>

        <aside className="space-y-6">
          <div className="bg-panel/80 backdrop-blur rounded-2xl border border-white/5 p-5">
            <h3 className="text-white font-semibold mb-2">Bot reasoning</h3>
            <p className="text-sm text-gray-400 mb-4">
              The exact steps the backend took to pick a response.
            </p>
            {lastReasoning.steps.length === 0 ? (
              <p className="text-sm text-gray-500">
                Send a message to see the thinking trace.
              </p>
            ) : (
              <div className="space-y-2">
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-2 py-1 rounded-full bg-sky-500/20 text-sky-100 border border-sky-500/40">
                    intent: {lastReasoning.intent}
                  </span>
                  {lastReasoning.matchedKeyword && (
                    <span className="px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-100 border border-emerald-500/40">
                      keyword: {lastReasoning.matchedKeyword}
                    </span>
                  )}
                </div>
                <ol className="list-decimal list-inside text-sm text-gray-200 space-y-1">
                  {lastReasoning.steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>

          <div className="bg-panel/80 backdrop-blur rounded-2xl border border-white/5 p-5">
            <h3 className="text-white font-semibold mb-2">Intent map</h3>
            <p className="text-sm text-gray-400 mb-4">
              The entire “brain” is just a dictionary of keywords and canned
              replies.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {intentList.map(([name, intent]) => (
                <div
                  key={name}
                  className="rounded-xl border border-white/10 bg-[#0f1a28] p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="uppercase text-[11px] tracking-wide text-sky-200">
                      {name}
                    </span>
                    {intent.keywords && (
                      <span className="text-[11px] text-gray-400">
                        {intent.keywords.length} keywords
                      </span>
                    )}
                  </div>
                  {intent.keywords && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {intent.keywords.map((kw) => (
                        <span
                          key={kw}
                          className="text-xs px-2 py-1 rounded-full bg-white/5 border border-white/10 text-gray-200"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                  <p className="text-sm text-gray-200 leading-snug">
                    {intent.response}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;

