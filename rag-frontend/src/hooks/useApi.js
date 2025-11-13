/**
 * Custom React Hooks
 * Reusable hooks for common functionality
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getAllTickets,
  getTicketById,
  submitIncident,
  uploadTicket,
  deleteTicket,
} from '../services/ticketService';
import { checkHealth } from '../services/healthService';

/**
 * Hook to fetch all tickets
 * Default collection: SupportTickets
 */
export const useTickets = (limit = 100, offset = 0, collectionName = 'SupportTickets') => {
  return useQuery({
    queryKey: ['tickets', limit, offset, collectionName],
    queryFn: () => getAllTickets(limit, offset, collectionName),
    staleTime: 30000, // 30 seconds
  });
};

/**
 * Hook to fetch a single ticket
 * Default collection: SupportTickets
 */
export const useTicket = (ticketId, collectionName = 'SupportTickets') => {
  return useQuery({
    queryKey: ['ticket', ticketId, collectionName],
    queryFn: () => getTicketById(ticketId, collectionName),
    enabled: !!ticketId,
  });
};

/**
 * Hook to submit new incident
 */
export const useSubmitIncident = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: submitIncident,
    onSuccess: () => {
      // Invalidate tickets cache
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to upload ticket
 * Default collection: SupportTickets
 */
export const useUploadTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticketData, collectionName = 'SupportTickets' }) => 
      uploadTicket(ticketData, collectionName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to delete ticket
 * Default collection: SupportTickets
 */
export const useDeleteTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticketId, collectionName = 'SupportTickets' }) => 
      deleteTicket(ticketId, collectionName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to check API health
 */
export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    refetchInterval: 60000, // Check every minute
    retry: 3,
  });
};

/**
 * Hook for local storage
 */
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  };

  return [storedValue, setValue];
};

/**
 * Hook for debounced value
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Hook for window size
 */
export const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};
