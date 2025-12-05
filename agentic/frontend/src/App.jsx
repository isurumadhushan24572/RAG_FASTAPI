import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Bot, FileText } from 'lucide-react';
import Dashboard from './components/Dashboard';
import TicketForm from './components/TicketForm';
import TicketResult from './components/TicketResult';

function MainLayout() {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { id: 'submit', label: 'New Ticket', icon: PlusCircle, path: '/submit' },
    { id: 'result', label: 'Results', icon: FileText, path: '/result' }
  ];

  React.useEffect(() => {
    const currentPath = location.pathname;
    if (currentPath === '/') setActiveTab('dashboard');
    else if (currentPath === '/submit') setActiveTab('submit');
    else if (currentPath === '/result') setActiveTab('result');
  }, [location]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 text-slate-900 font-sans">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                Agentic RAG Support
              </span>
            </div>
            <div className="flex space-x-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <Link
                    key={tab.id}
                    to={tab.path}
                    onClick={() => setActiveTab(tab.id)}
                    className={`inline-flex items-center px-4 py-2 my-auto text-sm font-medium rounded-lg transition-all ${
                      isActive
                        ? 'text-white bg-blue-600 shadow-md'
                        : 'text-slate-700 hover:bg-slate-100 hover:text-blue-600'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {tab.label}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/submit" element={
            <div className="max-w-3xl mx-auto">
              <TicketForm />
            </div>
          } />
          <Route path="/result" element={<TicketResult />} />
        </Routes>
      </main>

      <footer className="bg-white border-t border-slate-200 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>&copy; 2025 Agentic RAG Support System. Powered by GenAI.</p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <MainLayout />
    </Router>
  );
}

export default App;
