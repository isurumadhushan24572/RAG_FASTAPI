/**
 * Header Component
 * Top header bar
 */

import { useHealth } from '../../hooks/useApi';
import './Header.css';

export const Header = ({ title }) => {
  const { data: healthData, isLoading } = useHealth();

  const isHealthy = healthData?.status === 'healthy';

  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">{title}</h1>
        <div className="header-status">
          {isLoading ? (
            <span className="status-badge status-loading">⏳ Checking...</span>
          ) : isHealthy ? (
            <span className="status-badge status-online">🟢 API Online</span>
          ) : (
            <span className="status-badge status-offline">🔴 API Offline</span>
          )}
        </div>
      </div>
    </header>
  );
};
