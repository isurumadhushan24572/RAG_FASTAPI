/**
 * Ticket API Services
 * Handles all ticket-related API calls
 */

import apiClient from './apiClient';
import { API_CONFIG } from '../config/constants';

const API_VERSION = API_CONFIG.VERSION;  // v1

/**
 * Submit a new incident and get AI-generated solution
 * @param {Object} ticketData - Ticket submission data
 * @returns {Promise} AI-generated response
 */
export const submitIncident = async (ticketData) => {
  const response = await apiClient.post(`/api/${API_VERSION}/tickets/submit-user-input`, ticketData);
  return response.data;
};

/**
 * Upload a single ticket to the database
 * @param {Object} ticketData - Complete ticket data
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} Upload response
 */
export const uploadTicket = async (ticketData, collectionName = 'SupportTickets') => {
  const params = { collection_name: collectionName };
  const response = await apiClient.post(`/api/${API_VERSION}/tickets`, ticketData, { params });
  return response.data;
};

/**
 * Upload multiple tickets in batch
 * @param {Array} tickets - Array of ticket data
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} Batch upload response
 */
export const uploadTicketsBatch = async (tickets, collectionName = 'SupportTickets') => {
  const params = { collection_name: collectionName };
  const response = await apiClient.post(`/api/${API_VERSION}/tickets/batch`, tickets, { params });
  return response.data;
};

/**
 * Get all tickets with pagination
 * @param {number} limit - Maximum number of tickets
 * @param {number} offset - Number of tickets to skip
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} List of tickets
 */
export const getAllTickets = async (limit = 100, offset = 0, collectionName = 'SupportTickets') => {
  const params = { limit, offset, collection_name: collectionName };
  
  console.log('🎯 getAllTickets - Fetching from collection:', collectionName);
  console.log('📤 Request params:', params);
  
  const response = await apiClient.get(`/api/${API_VERSION}/tickets`, { params });
  
  console.log('✅ Response received:', response.data);
  console.log('📊 Total tickets:', response.data?.total || 0);
  
  return response.data;
};

/**
 * Search for similar tickets
 * @param {string} query - Search query
 * @param {number} limit - Maximum number of results
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} Search results
 */
export const searchTickets = async (query, limit = 3, collectionName = 'SupportTickets') => {
  const params = { query, limit, collection_name: collectionName };
  
  const response = await apiClient.get(`/api/${API_VERSION}/tickets/search`, { params });
  return response.data;
};

/**
 * Get a specific ticket by ID
 * @param {string} ticketId - Ticket ID
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} Ticket data
 */
export const getTicketById = async (ticketId, collectionName = 'SupportTickets') => {
  const params = { collection_name: collectionName };
  const response = await apiClient.get(`/api/${API_VERSION}/tickets/${ticketId}`, { params });
  return response.data;
};

/**
 * Delete a ticket by ID
 * @param {string} ticketId - Ticket ID
 * @param {string} collectionName - Collection name (default: SupportTickets)
 * @returns {Promise} Deletion response
 */
export const deleteTicket = async (ticketId, collectionName = 'SupportTickets') => {
  const params = { collection_name: collectionName };
  const response = await apiClient.delete(`/api/${API_VERSION}/tickets/${ticketId}`, { params });
  return response.data;
};
