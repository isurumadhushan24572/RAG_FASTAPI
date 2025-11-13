/**
 * AllIncidents Page
 * Display and filter all incidents
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { Card, CardBody } from '../components/ui/Card';
import { Select } from '../components/ui/Input';
import { SeverityBadge, StatusBadge } from '../components/ui/Badge';
import { MetricCard } from '../components/ui/MetricCard';
import { Spinner } from '../components/ui/Spinner';
import { Alert } from '../components/ui/Alert';
import { useTickets } from '../hooks/useApi';
import { calculateStats, filterTickets, sortTicketsByDate, formatDate, truncateText } from '../utils/helpers';
import { CATEGORY_OPTIONS, SEVERITY_OPTIONS, STATUS_OPTIONS, ENVIRONMENT_OPTIONS } from '../config/constants';
import './AllIncidents.css';

export const AllIncidents = () => {
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useTickets();

  const [filters, setFilters] = useState({
    status: 'All',
    category: 'All',
    severity: 'All',
    environment: 'All',
  });

  // Debug logging
  console.log('📊 AllIncidents - Raw data:', data);
  console.log('⏳ Loading:', isLoading);
  console.log('❌ Error:', error);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <Header title="📊 All Application Incidents" />
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <Spinner />
          <p style={{ marginTop: '1rem', color: '#666' }}>
            Loading incidents from SupportTickets collection...
          </p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="page-container">
        <Header title="📊 All Application Incidents" />
        <Alert variant="error">
          Error loading incidents: {error?.response?.data?.detail || error?.message}
        </Alert>
      </div>
    );
  }

  const allTickets = data?.tickets || [];
  console.log('📋 All Tickets:', allTickets);
  console.log('🔢 Total Count:', allTickets.length);
  
  const filteredTickets = filterTickets(allTickets, filters);
  console.log('🔍 Filtered Tickets:', filteredTickets.length);
  
  const sortedTickets = sortTicketsByDate(filteredTickets);
  const stats = calculateStats(allTickets);
  console.log('📊 Calculated Stats:', stats);

  return (
    <div className="page-container">
      <Header title="📊 All Application Incidents" />

      <div className="page-content">
        {/* Collection Info */}
        <Alert variant="info" style={{ marginBottom: '1.5rem' }}>
          📊 Displaying incidents from <strong>SupportTickets</strong> collection: {allTickets.length} total incidents
        </Alert>

        {/* Statistics */}
        <section className="stats-section">
          <h2 className="section-title">📈 Incident Statistics</h2>
          <div className="metrics-grid">
            <MetricCard
              title="Total Incidents"
              value={stats.total}
              icon="📋"
              color="primary"
            />
            <MetricCard
              title="Open"
              value={stats.open}
              icon="🔴"
              color="danger"
            />
            <MetricCard
              title="Resolved"
              value={stats.resolved}
              icon="🟢"
              color="success"
            />
            <MetricCard
              title="🔴 Critical"
              value={stats.critical}
              icon="⚠️"
              color="danger"
            />
            <MetricCard
              title="Resolution Rate"
              value={`${stats.resolutionRate.toFixed(1)}%`}
              icon="📊"
              color="info"
            />
          </div>
        </section>

        {/* Filters */}
        <section className="filters-section">
          <Card>
            <CardBody>
              <div className="filters-grid">
                <Select
                  label="Filter by Status"
                  name="status"
                  value={filters.status}
                  onChange={handleFilterChange}
                  options={['All', ...STATUS_OPTIONS.map(s => s.value)]}
                />
                <Select
                  label="Filter by Category"
                  name="category"
                  value={filters.category}
                  onChange={handleFilterChange}
                  options={['All', ...CATEGORY_OPTIONS]}
                />
                <Select
                  label="Filter by Severity"
                  name="severity"
                  value={filters.severity}
                  onChange={handleFilterChange}
                  options={['All', ...SEVERITY_OPTIONS.map(s => s.value)]}
                />
                <Select
                  label="Filter by Environment"
                  name="environment"
                  value={filters.environment}
                  onChange={handleFilterChange}
                  options={['All', ...ENVIRONMENT_OPTIONS]}
                />
              </div>
            </CardBody>
          </Card>
        </section>

        {/* Incidents List */}
        <section className="incidents-section">
          <h2 className="section-title">
            🎫 Incidents ({filteredTickets.length})
          </h2>

          {filteredTickets.length === 0 ? (
            <Alert variant="info">
              No incidents found matching the selected filters.
            </Alert>
          ) : (
            <div className="incidents-list">
              {sortedTickets.map((ticket) => (
                <Card
                  key={ticket.uuid || ticket.ticket_id}
                  hover
                  className="incident-card"
                  onClick={() => navigate(`/incidents/${ticket.ticket_id}`)}
                >
                  <CardBody>
                    <div className="incident-header">
                      <div className="incident-title-section">
                        <h3 className="incident-title">
                          [{ticket.ticket_id}] {ticket.title}
                        </h3>
                        <p className="incident-app">{ticket.application || 'N/A'}</p>
                      </div>
                      <div className="incident-badges">
                        <StatusBadge status={ticket.status} />
                        <SeverityBadge severity={ticket.severity} />
                      </div>
                    </div>

                    <p className="incident-description">
                      {truncateText(ticket.description, 150)}
                    </p>

                    {ticket.solution && (
                      <p className="incident-solution">
                        <strong>Resolution:</strong> {truncateText(ticket.solution, 100)}
                      </p>
                    )}

                    <div className="incident-meta">
                      <span className="meta-item">
                        <strong>Category:</strong> {ticket.category}
                      </span>
                      <span className="meta-item">
                        <strong>Environment:</strong> {ticket.environment}
                      </span>
                      <span className="meta-item">
                        <strong>Reported:</strong> {formatDate(ticket.timestamp)}
                      </span>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
