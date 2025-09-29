import React, { type ReactNode } from 'react';
import { useLocation } from 'react-router-dom';

type LayoutProps = {
  children: ReactNode;
};

const AUTH_ROUTES = ["/login", "/register", "/"];

const NAV_LINKS = [
  { name: "Debts", href: "/debts" },
  { name: "Drinkings", href: "/drinkings" },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  if (AUTH_ROUTES.includes(location.pathname)) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-blue-600 text-white px-6 py-4 shadow">
        <div className="container mx-auto flex items-center justify-between">
          <span className="font-bold text-xl">Skolu Appas</span>
          <div className="space-x-4">
            {NAV_LINKS.map(link => (
              <a key={link.href} href={link.href} className="hover:underline">
                {link.name}
              </a>
            ))}
          </div>
        </div>
      </nav>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;