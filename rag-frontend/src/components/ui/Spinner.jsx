/**
 * Loading Spinner Component
 */

import './Spinner.css';

export const Spinner = ({ size = 'medium', className = '' }) => {
  return (
    <div className={`spinner-container ${className}`}>
      <div className={`spinner spinner-${size}`}></div>
    </div>
  );
};

export const LoadingOverlay = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <Spinner size="large" />
        <p className="loading-message">{message}</p>
      </div>
    </div>
  );
};
