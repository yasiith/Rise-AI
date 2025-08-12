"use client";
import React, { useState, useEffect, useRef } from "react";
import { chatService, ChatMessage } from "../../services/chatService";

const Chatbot = () => {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<
    Array<{ role: string; content: string; timestamp?: string }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showHelp, setShowHelp] = useState(true);

  useEffect(() => {
    // Get user from localStorage
    const userJson = localStorage.getItem("user");
    if (userJson) {
      try {
        const userData = JSON.parse(userJson);
        setUser(userData);

        // Just load chat history if needed
        loadChatHistory(userData.email);
      } catch (e) {
        console.error("Error parsing user data", e);
      }
    }
  }, []);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async (username: string) => {
    try {
      setLoading(true);
      const response = await chatService.getChatHistory(username);

      if (response.success && response.data?.history) {
        const formattedHistory = response.data.history
          .map((msg: ChatMessage) => [
            {
              role: "user",
              content: msg.user_message,
              timestamp: new Date(msg.timestamp).toLocaleTimeString(),
            },
            {
              role: "assistant",
              content: msg.ai_response,
              timestamp: new Date(msg.timestamp).toLocaleTimeString(),
            },
          ])
          .flat();

        // Reverse to get correct chronological order and add welcome message
        setMessages((prevMessages) => [
          ...formattedHistory.reverse(),
          ...prevMessages,
        ]);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !user) return;

    const userMessage = inputValue;
    setInputValue("");
    setShowHelp(false);

    // Add user message to chat
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: "user",
        content: userMessage,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);

    // Show loading indicator
    setLoading(true);

    try {
      console.log("Sending message:", userMessage, "User email:", user.email);

      // Direct fetch approach - bypass the utility function temporarily
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors", // Explicit CORS mode
        body: JSON.stringify({
          username: user.email,
          message: userMessage,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response received:", data);

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: data.response || "Sorry, no response received.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: "Network error. Please check your connection and try again.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Helper function to get role-specific quick actions
  const getQuickActions = () => {
    if (!user) return [];

    const commonActions = [
      { icon: "✏️", text: "Log My Task", prompt: "I need to log a new task" },
      {
        icon: "📋",
        text: "My Task History",
        prompt: "Show me my task history",
      },
      { icon: "❓", text: "Ask for Help", prompt: "I need help with my tasks" },
    ];

    const managerActions = [
      { icon: "👥", text: "Team Overview", prompt: "Show me my team's tasks" },
      {
        icon: "📊",
        text: "Performance Stats",
        prompt: "Show team performance statistics",
      },
      {
        icon: "✅",
        text: "Assign Tasks",
        prompt: "I want to assign a new task",
      },
    ];

    const employeeActions = [
      { icon: "🔋", text: "My Progress", prompt: "Show my task progress" },
      {
        icon: "📈",
        text: "My Stats",
        prompt: "Show my performance statistics",
      },
      { icon: "🏆", text: "Achievements", prompt: "Show my achievements" },
    ];

    return [
      ...commonActions,
      ...(user.role === "manager" ? managerActions : employeeActions),
    ];
  };

  const handleQuickAction = (prompt: string) => {
    setInputValue(prompt);
    // Optional: Auto-submit after a short delay
    setTimeout(() => {
      const form = document.querySelector("form");
      form?.dispatchEvent(
        new Event("submit", { cancelable: true, bubbles: true })
      );
    }, 100);
  };

  return (
    <div className="fixed inset-0 w-full h-full bg-gradient-to-br from-black via-blue-950 to-purple-950 flex flex-col">
      {/* Header */}
      <header className="p-4 flex items-center justify-between border-b border-gray-800">
        <div className="flex items-center">
          <div className="grid grid-cols-3 gap-0.5 mr-3">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-1.5 h-1.5 bg-blue-400 opacity-80"></div>
            ))}
          </div>
          <h1 className="text-xl font-light text-white">Rise AI</h1>
        </div>
        {user && (
          <div className="text-sm text-blue-300">
            {user.full_name} ({user.role})
          </div>
        )}
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-3/4 p-3 rounded-lg ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-100"
              }`}
            >
              <div
                dangerouslySetInnerHTML={{
                  __html: message.content.replace(/\n/g, "<br>"),
                }}
              />
              {message.timestamp && (
                <div
                  className={`text-xs mt-1 ${
                    message.role === "user" ? "text-blue-200" : "text-gray-400"
                  }`}
                >
                  {message.timestamp}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-100 p-3 rounded-lg">
              <div className="flex space-x-2 items-center">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"></div>
                <div
                  className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"
                  style={{ animationDelay: "0.2s" }}
                ></div>
                <div
                  className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"
                  style={{ animationDelay: "0.4s" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {showHelp && (
        <div className="px-4 pt-2 pb-4">
          <p className="text-gray-400 text-sm mb-2 text-center">
            Quick actions
          </p>
          <div className="flex flex-wrap justify-center gap-2 mb-4">
            {getQuickActions().map((action, index) => (
              <button
                key={index}
                className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white flex items-center"
                onClick={() => handleQuickAction(action.prompt)}
              >
                <span className="mr-2">{action.icon}</span> {action.text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Field */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
        <div className="flex">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 bg-gray-800/50 border border-gray-700 rounded-l-full py-3 px-6 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-600"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-r-full"
            disabled={loading || !inputValue.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chatbot;
