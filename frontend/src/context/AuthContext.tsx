import React, { createContext, useContext, useEffect, useState} from "react";
import {type  ReactNode } from "react";

type User = {
  id: string;
  name: string;
  email: string;
  role: "user" | "admin";
};

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const apiUrl = import.meta.env.VITE_API_URL;

  const login = async (email: string, password: string) => {
    const response = await fetch(`${apiUrl}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }

    await response.json();
    await fetchUser();
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await fetch(`${apiUrl}/refresh/`, {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const fetchUser = async () => {
    try {
      const response = await fetch(`${apiUrl}/user`, {
        credentials: "include",
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${apiUrl}/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Handle error if needed
    }
    setUser(null);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};
