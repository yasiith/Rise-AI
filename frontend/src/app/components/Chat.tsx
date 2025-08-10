"use client";
import React, { useState } from "react";

const Chatbot = () => {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Query:", inputValue);
    setInputValue("");
  };

  return (
    <div className="fixed inset-0 w-full h-full bg-gradient-to-br from-black via-blue-950 to-purple-950 flex flex-col items-center justify-center p-6">
      {/* Background Decorative Elements */}
      <div className="absolute top-16 left-16 w-8 h-8 border border-blue-500/20 opacity-20"></div>
      <div className="absolute bottom-32 left-32 w-10 h-10 border border-blue-500/10 opacity-20"></div>
      <div className="absolute top-32 right-64 w-7 h-7 border border-blue-500/20 opacity-20"></div>
      <div className="absolute right-24 bottom-48 w-9 h-9 border border-blue-500/10 opacity-20"></div>

      {/* Title and Subtitle */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-light tracking-wide text-white">
          Rise AI
        </h1>
        <p className="text-white mt-2 text-sm">Your Intelligent AI Partner</p>
      </div>

      {/* Action Buttons - Row 1 */}
      <div className="flex flex-wrap justify-center gap-4 mb-4">
        <button className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white">
          <span className="mr-2">🔋</span> My Leave Balance
        </button>
        <button className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white">
          <span className="mr-2">✏️</span> Log My Task
        </button>
        <button className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white">
          <span className="mr-2">📋</span> My Task History
        </button>
        <button className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white">
          <span className="mr-2">❓</span> Ask Policy
        </button>
      </div>

      {/* Action Buttons - Row 2 */}
      <div className="flex justify-center mb-12">
        <button className="bg-gray-800/70 hover:bg-gray-700/70 px-4 py-2 rounded-full text-sm text-white">
          <span className="mr-2">❔</span> Ask Guidance
        </button>
      </div>

      {/* Input Field */}
      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask anything about HR..."
          className="w-full bg-gray-800/50 border border-gray-700 rounded-full py-3 px-6 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-600"
        />
      </form>
    </div>
  );
};

export default Chatbot;
