/**
 * Sidebar Component
 * Navigation sidebar
 */

import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const menuItems = [
  {
    path: '/report',
    icon: '📝',
    label: 'Report New Incident',
  },
  {
    path: '/incidents',
    icon: '📊',
    label: 'All Incidents',
  },
  {
    path: '/metrics',
    icon: '📈',
    label: 'Support Metrics',
  },
];

export const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">
          <span className="sidebar-icon">☁️</span>
          Support System
        </h2>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <h3 className="nav-section-title">🎯 Dashboard</h3>
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'nav-item-active' : ''}`
              }
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          <p className="info-text">Cloud Application Support</p>
          <p className="info-subtitle">Management System v1.0</p>
        </div>
      </div>
    </aside>
  );
};
