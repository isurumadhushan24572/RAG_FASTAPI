/**
 * Health API Service
 * Handles health check and system status
 */

import apiClient from './apiClient';

/**
 * Check API health status
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Get API root information
 * @returns {Promise} API information
 */
export const getApiInfo = async () => {
  const response = await apiClient.get('/');
  return response.data;
};
