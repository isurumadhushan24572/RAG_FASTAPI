/**
 * Badge Component
 * Status and category badges
 */

import './Badge.css';

export const Badge = ({ children, variant = 'default', size = 'medium', icon, className = '' }) => {
  return (
    <span className={`badge badge-${variant} badge-${size} ${className}`}>
      {icon && <span className="badge-icon">{icon}</span>}
      {children}
    </span>
  );
};

export const SeverityBadge = ({ severity }) => {
  const variants = {
    Critical: { variant: 'danger', icon: '🔴' },
    High: { variant: 'warning', icon: '🟠' },
    Medium: { variant: 'info', icon: '🟡' },
    Low: { variant: 'success', icon: '🟢' },
  };

  const config = variants[severity] || variants.Medium;

  return (
    <Badge variant={config.variant} icon={config.icon}>
      {severity}
    </Badge>
  );
};

export const StatusBadge = ({ status }) => {
  const variants = {
    Open: { variant: 'danger', icon: '🔴' },
    Resolved: { variant: 'success', icon: '🟢' },
  };

  const config = variants[status] || variants.Open;

  return (
    <Badge variant={config.variant} icon={config.icon}>
      {status}
    </Badge>
  );
};
