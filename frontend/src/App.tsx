import './App.css'
import { Routes, Route } from "react-router-dom";
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import StartPage from './pages/public/StartPage';
import LoginPage from './pages/auth/LoginPage';
import HomePage from './pages/user/HomePage';
import RegisterPage from './pages/auth/RegisterPage';
import DebtsPage from './pages/user/DebtsPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<StartPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/home" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
        <Route path="/debts" element={<ProtectedRoute><DebtsPage /></ProtectedRoute>} />
      </Routes>
    </Layout>
  );
}

export default App
