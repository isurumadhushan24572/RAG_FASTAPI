import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { Loader2, AlertCircle, CheckCircle2, Server, Activity, Ticket, Bot, Sparkles, ArrowRight } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/tickets/stats');
        setStats(response.data.stats);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching stats:", err);
        setError("Failed to load dashboard statistics. Ensure backend is running.");
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
        <span className="text-slate-500 font-medium">Connecting to Agent...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center shadow-sm">
        <AlertCircle className="w-6 h-6 mr-3" />
        <span className="font-medium">{error}</span>
      </div>
    );
  }

  if (!stats) return null;

  // Calculate totals
  const totalTickets = Object.values(stats.status).reduce((a, b) => a + b, 0);
  const openTickets = stats.status['Open'] || 0;
  const resolvedTickets = stats.status['Resolved'] || 0;

  const severityData = {
    labels: Object.keys(stats.severity),
    datasets: [
      {
        data: Object.values(stats.severity),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)', // Red
          'rgba(249, 115, 22, 0.8)', // Orange
          'rgba(234, 179, 8, 0.8)', // Yellow
          'rgba(59, 130, 246, 0.8)', // Blue
        ],
        borderColor: 'white',
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const statusData = {
    labels: Object.keys(stats.status),
    datasets: [
      {
        label: 'Tickets',
        data: Object.values(stats.status),
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)', // Green
          'rgba(59, 130, 246, 0.8)', // Blue
        ],
        borderRadius: 6,
      },
    ],
  };

  const environmentData = {
    labels: Object.keys(stats.environment),
    datasets: [
      {
        label: 'Tickets',
        data: Object.values(stats.environment),
        backgroundColor: 'rgba(99, 102, 241, 0.8)', // Indigo
        borderRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: { family: "'Inter', sans-serif", size: 12 }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { display: false }
      },
      x: {
        grid: { display: false }
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-8 -left-8 w-64 h-64 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start space-x-6">
            <div className="p-4 bg-white/10 rounded-2xl backdrop-blur-sm border border-white/10">
              <Bot className="w-12 h-12 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-2">Hello, I'm your AI Agent</h1>
              <p className="text-slate-300 max-w-xl text-lg">
                I'm monitoring your systems 24/7.
              </p>
              <div className="mt-6 flex gap-4">
                <a href="#submit" className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-all shadow-lg hover:shadow-blue-500/25">
                  <Sparkles className="w-5 h-5 mr-2" />
                  Ask me anything
                </a>
                <div className="flex items-center px-4 py-2 bg-white/5 rounded-xl border border-white/10">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                  <span className="text-sm font-medium text-slate-300">System Operational</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Mini Stats in Hero */}
          <div className="hidden md:block p-6 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-sm min-w-[200px]">
            <div className="text-center space-y-4">
              <div>
                <p className="text-slate-400 text-sm mb-1">Success Rate</p>
                <p className="text-3xl font-bold text-green-400">98.5%</p>
              </div>
              <div className="h-px bg-white/10 w-full"></div>
              <div>
                <p className="text-slate-400 text-sm mb-1">Avg. Response</p>
                <p className="text-xl font-bold text-blue-400">1.2s</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between px-2">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          Live System Metrics
        </h2>
        <div className="text-sm text-slate-400">
          Auto-refreshing
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center space-x-4 hover:shadow-md transition-shadow group">
          <div className="p-4 bg-blue-50 rounded-xl group-hover:bg-blue-100 transition-colors">
            <Ticket className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Total Tickets</p>
            <p className="text-3xl font-bold text-slate-800">{totalTickets}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center space-x-4 hover:shadow-md transition-shadow group">
          <div className="p-4 bg-orange-50 rounded-xl group-hover:bg-orange-100 transition-colors">
            <AlertCircle className="w-8 h-8 text-orange-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Active Incidents</p>
            <p className="text-3xl font-bold text-slate-800">{openTickets}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center space-x-4 hover:shadow-md transition-shadow group">
          <div className="p-4 bg-green-50 rounded-xl group-hover:bg-green-100 transition-colors">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Resolved by AI</p>
            <p className="text-3xl font-bold text-slate-800">{resolvedTickets}</p>
          </div>
        </div>
      </div>
      
      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Severity Chart */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex items-center mb-6">
            <h3 className="text-lg font-bold text-slate-700">Severity Distribution</h3>
          </div>
          <div className="h-64 flex justify-center">
            <Doughnut data={severityData} options={chartOptions} />
          </div>
        </div>

        {/* Status Chart */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex items-center mb-6">
            <h3 className="text-lg font-bold text-slate-700">Status Breakdown</h3>
          </div>
          <div className="h-64">
            <Bar 
              data={statusData} 
              options={{ 
                ...chartOptions, 
                plugins: { legend: { display: false } } 
              }} 
            />
          </div>
        </div>

        {/* Environment Chart */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex items-center mb-6">
            <h3 className="text-lg font-bold text-slate-700">Environment Stats</h3>
          </div>
          <div className="h-64">
            <Bar 
              data={environmentData} 
              options={{ 
                ...chartOptions, 
                indexAxis: 'y',
                plugins: { legend: { display: false } } 
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
