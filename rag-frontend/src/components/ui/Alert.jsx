/**
 * Alert Component
 * Notifications and alerts
 */

import './Alert.css';

export const Alert = ({ children, variant = 'info', icon, onClose, className = '' }) => {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div className={`alert alert-${variant} ${className}`}>
      <span className="alert-icon">{icon || icons[variant]}</span>
      <div className="alert-content">{children}</div>
      {onClose && (
        <button className="alert-close" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  );
};
