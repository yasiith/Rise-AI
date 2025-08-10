"use client";
import React, { useState } from "react";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login attempt with:", email);
  };

  return (
    <div className="fixed inset-0 w-full h-full bg-gradient-to-br from-black via-blue-950 to-purple-950 flex flex-col items-center justify-center">
      {/* Background Decorative Elements */}
      <div className="absolute top-16 left-16 w-8 h-8 border border-blue-500/20 opacity-30"></div>
      <div className="absolute bottom-32 left-32 w-10 h-10 border border-blue-500/20 opacity-20"></div>
      <div className="absolute top-32 right-64 w-7 h-7 border border-purple-500/20 opacity-20"></div>
      <div className="absolute right-24 bottom-48 w-9 h-9 border border-purple-500/20 opacity-30"></div>

      {/* Main Content */}
      <div className="flex flex-col items-center mb-20">
        {/* Logo */}
        <div className="grid grid-cols-3 gap-1 mb-3">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="w-2 h-2 bg-blue-400 opacity-80"></div>
          ))}
        </div>
        <h2 className="text-xl text-white font-medium tracking-wider mb-14">
          Rise AI
        </h2>

        {/* Login Form */}
        <form className="w-96 space-y-4" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-black/20 border border-gray-700 rounded text-white text-base placeholder-gray-400 focus:outline-none"
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-black/20 border border-gray-700 rounded text-white text-base placeholder-gray-400 focus:outline-none"
            required
          />

          <button
            type="submit"
            className="w-full py-3 bg-gray-700/50 hover:bg-gray-600/50 text-white rounded text-base mt-2"
          >
            Login
          </button>

          <div className="text-center mt-3">
            <a href="#" className="text-sm text-blue-400 hover:text-blue-300">
              Forgot password?
            </a>
          </div>
        </form>
      </div>

      {/* Footer */}
      <div className="absolute bottom-5 text-sm text-gray-500">
        © 2023 Rise AI. All rights reserved.
      </div>
    </div>
  );
};

export default Login;
