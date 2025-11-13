/**
 * App Component
 * Main application entry point with routing
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './components/layout/MainLayout';
import { ReportIncident } from './pages/ReportIncident';
import { AllIncidents } from './pages/AllIncidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { SupportMetrics } from './pages/SupportMetrics';
import './App.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/report" replace />} />
            <Route path="report" element={<ReportIncident />} />
            <Route path="incidents" element={<AllIncidents />} />
            <Route path="incidents/:id" element={<IncidentDetails />} />
            <Route path="metrics" element={<SupportMetrics />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
