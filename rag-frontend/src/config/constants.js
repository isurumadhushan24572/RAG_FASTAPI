/**
 * Application Constants
 * Centralized configuration for the entire application
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  VERSION: import.meta.env.VITE_API_VERSION || 'v1',
  TIMEOUT: 30000, // 30 seconds
};

export const APP_CONFIG = {
  TITLE: import.meta.env.VITE_APP_TITLE || 'Cloud Application Support System',
  DEFAULT_COLLECTION: import.meta.env.VITE_DEFAULT_COLLECTION || 'SupportTickets',
};

export const SEVERITY_OPTIONS = [
  { value: 'Critical', label: 'Critical', color: 'red', icon: '🔴' },
  { value: 'High', label: 'High', color: 'orange', icon: '🟠' },
  { value: 'Medium', label: 'Medium', color: 'yellow', icon: '🟡' },
  { value: 'Low', label: 'Low', color: 'green', icon: '🟢' },
];

export const ENVIRONMENT_OPTIONS = [
  'Production',
  'Staging',
  'Development',
  'UAT',
];

export const CATEGORY_OPTIONS = [
  'API Issues',
  'Database',
  'Authentication',
  'Performance',
  'Deployment',
  'Integration',
  'UI/Frontend',
  'Backend Service',
  'Other',
];

export const STATUS_OPTIONS = [
  { value: 'Open', label: 'Open', color: 'red', icon: '🔴' },
  { value: 'Resolved', label: 'Resolved', color: 'green', icon: '🟢' },
];

export const SIMILARITY_THRESHOLD = 0.85; // 85% similarity threshold

export const ROUTES = {
  HOME: '/',
  REPORT_INCIDENT: '/report',
  ALL_INCIDENTS: '/incidents',
  INCIDENT_DETAILS: '/incidents/:id',
  SUPPORT_METRICS: '/metrics',
};
