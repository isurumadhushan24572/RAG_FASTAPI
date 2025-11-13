/**
 * Utility Functions
 * Helper functions used throughout the application
 */

import { format, parseISO } from 'date-fns';
import { SEVERITY_OPTIONS, STATUS_OPTIONS } from '../config/constants';

/**
 * Format date string to readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return format(date, 'MMM dd, yyyy HH:mm');
  } catch (error) {
    return dateString;
  }
};

/**
 * Get severity configuration
 * @param {string} severity - Severity level
 * @returns {Object} Severity config
 */
export const getSeverityConfig = (severity) => {
  return SEVERITY_OPTIONS.find(opt => opt.value === severity) || SEVERITY_OPTIONS[2];
};

/**
 * Get status configuration
 * @param {string} status - Status value
 * @returns {Object} Status config
 */
export const getStatusConfig = (status) => {
  return STATUS_OPTIONS.find(opt => opt.value === status) || STATUS_OPTIONS[0];
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Calculate statistics from ticket list
 * @param {Array} tickets - Array of tickets
 * @returns {Object} Statistics
 */
export const calculateStats = (tickets) => {
  if (!tickets || tickets.length === 0) {
    return {
      total: 0,
      open: 0,
      resolved: 0,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      resolutionRate: 0,
      bySeverity: {},
      byCategory: {},
      byEnvironment: {},
    };
  }

  const stats = {
    total: tickets.length,
    open: 0,
    resolved: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    bySeverity: {},
    byCategory: {},
    byEnvironment: {},
  };

  tickets.forEach(ticket => {
    // Status
    if (ticket.status === 'Open') stats.open++;
    if (ticket.status === 'Resolved') stats.resolved++;

    // Severity
    if (ticket.severity === 'Critical') stats.critical++;
    if (ticket.severity === 'High') stats.high++;
    if (ticket.severity === 'Medium') stats.medium++;
    if (ticket.severity === 'Low') stats.low++;

    // By severity
    stats.bySeverity[ticket.severity] = (stats.bySeverity[ticket.severity] || 0) + 1;

    // By category
    stats.byCategory[ticket.category] = (stats.byCategory[ticket.category] || 0) + 1;

    // By environment
    stats.byEnvironment[ticket.environment] = (stats.byEnvironment[ticket.environment] || 0) + 1;
  });

  stats.resolutionRate = stats.total > 0 ? (stats.resolved / stats.total) * 100 : 0;

  return stats;
};

/**
 * Filter tickets based on criteria
 * @param {Array} tickets - Array of tickets
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered tickets
 */
export const filterTickets = (tickets, filters) => {
  if (!tickets) return [];

  return tickets.filter(ticket => {
    if (filters.status && filters.status !== 'All' && ticket.status !== filters.status) {
      return false;
    }
    if (filters.severity && filters.severity !== 'All' && ticket.severity !== filters.severity) {
      return false;
    }
    if (filters.category && filters.category !== 'All' && ticket.category !== filters.category) {
      return false;
    }
    if (filters.environment && filters.environment !== 'All' && ticket.environment !== filters.environment) {
      return false;
    }
    return true;
  });
};

/**
 * Sort tickets by date (newest first)
 * @param {Array} tickets - Array of tickets
 * @returns {Array} Sorted tickets
 */
export const sortTicketsByDate = (tickets) => {
  if (!tickets) return [];
  
  return [...tickets].sort((a, b) => {
    const dateA = new Date(a.timestamp);
    const dateB = new Date(b.timestamp);
    return dateB - dateA;
  });
};

/**
 * Generate unique ticket ID
 * @param {number} count - Current ticket count
 * @returns {string} Ticket ID
 */
export const generateTicketId = (count = 0) => {
  const num = String(count + 1).padStart(4, '0');
  return `TKT-${num}`;
};

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid
 */
export const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

/**
 * Class name utility (like clsx but simpler)
 * @param  {...any} classes - Class names or objects
 * @returns {string} Combined class names
 */
export const cn = (...classes) => {
  return classes
    .flat()
    .filter(x => typeof x === 'string' || typeof x === 'number')
    .join(' ')
    .trim();
};
