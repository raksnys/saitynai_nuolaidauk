import React from "react";

const StartPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-blue-600 text-white px-6 py-4 shadow">
        <div className="container mx-auto flex items-center justify-between">
          <span className="font-bold text-xl">Money app'as</span>
          <div className="space-x-4">
            <a href="/login" className="hover:underline">
              Login
            </a>
            <a href="/register" className="hover:underline">
              Register
            </a>
          </div>
        </div>
      </nav>
      <main className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-4xl font-bold mb-4 text-blue-700">Welcome to Money</h1>
        <p className="text-lg text-gray-700 mb-8">
          Ka ce karoce bazarini 
        </p>
        <div className="space-x-4">
          <a
            href="/login"
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          >
            Login
          </a>
          <a
            href="/register"
            className="bg-gray-200 text-blue-700 px-6 py-2 rounded hover:bg-gray-300 transition"
          >
            Register
          </a>
        </div>
      </main>
    </div>
  );
};

export default StartPage;