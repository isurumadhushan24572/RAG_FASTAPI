/**
 * SupportMetrics Page
 * Display analytics and metrics for support team
 */

import { Header } from '../components/layout/Header';
import { Card, CardBody } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { SeverityBadge, StatusBadge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { Alert } from '../components/ui/Alert';
import { useTickets } from '../hooks/useApi';
import { calculateStats, sortTicketsByDate, formatDate } from '../utils/helpers';
import './SupportMetrics.css';

export const SupportMetrics = () => {
  const { data, isLoading, isError, error } = useTickets();

  if (isLoading) {
    return (
      <div className="page-container">
        <Header title="📈 Support Team Metrics & Analytics" />
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="page-container">
        <Header title="📈 Support Team Metrics & Analytics" />
        <Alert variant="error">
          Error loading metrics: {error?.response?.data?.detail || error?.message}
        </Alert>
      </div>
    );
  }

  const allTickets = data?.tickets || [];
  const stats = calculateStats(allTickets);
  const recentTickets = sortTicketsByDate(allTickets).slice(0, 5);

  return (
    <div className="page-container">
      <Header title="📈 Support Team Metrics & Analytics" />

      <div className="page-content">
        {/* Overall Performance */}
        <section className="metrics-section">
          <h2 className="section-title">🎯 Overall Performance</h2>
          <div className="metrics-grid">
            <MetricCard
              title="Total Incidents"
              value={stats.total}
              icon="📋"
              color="primary"
            />
            <MetricCard
              title="Open Incidents"
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
              title="Resolution Rate"
              value={`${stats.resolutionRate.toFixed(1)}%`}
              icon="📊"
              color="info"
            />
          </div>
        </section>

        {/* Severity Breakdown */}
        <section className="metrics-section">
          <h2 className="section-title">🎚️ Incidents by Severity</h2>
          <div className="metrics-grid">
            <MetricCard
              title="🔴 Critical"
              value={stats.critical}
              icon="🔴"
              color="danger"
            />
            <MetricCard
              title="🟠 High"
              value={stats.high}
              icon="🟠"
              color="warning"
            />
            <MetricCard
              title="🟡 Medium"
              value={stats.medium}
              icon="🟡"
              color="info"
            />
            <MetricCard
              title="🟢 Low"
              value={stats.low}
              icon="🟢"
              color="success"
            />
          </div>
        </section>

        {/* Category Breakdown */}
        <section className="metrics-section">
          <h2 className="section-title">📂 Incidents by Category</h2>
          <div className="metrics-grid-auto">
            {Object.entries(stats.byCategory)
              .sort(([, a], [, b]) => b - a)
              .map(([category, count]) => (
                <MetricCard
                  key={category}
                  title={category}
                  value={count}
                  icon="📁"
                  color="primary"
                />
              ))}
          </div>
        </section>

        {/* Environment Breakdown */}
        <section className="metrics-section">
          <h2 className="section-title">🌐 Incidents by Environment</h2>
          <div className="metrics-grid">
            {Object.entries(stats.byEnvironment)
              .sort(([, a], [, b]) => b - a)
              .map(([environment, count]) => (
                <MetricCard
                  key={environment}
                  title={environment}
                  value={count}
                  icon="🌐"
                  color={environment === 'Production' ? 'danger' : 'info'}
                />
              ))}
          </div>
        </section>

        {/* Recent Activity */}
        <section className="metrics-section">
          <h2 className="section-title">🕐 Recent Incidents</h2>
          <Card>
            <CardBody>
              {recentTickets.length === 0 ? (
                <Alert variant="info">No incidents reported yet.</Alert>
              ) : (
                <div className="recent-list">
                  {recentTickets.map((ticket) => (
                    <div key={ticket.uuid || ticket.ticket_id} className="recent-item">
                      <div className="recent-badges">
                        <StatusBadge status={ticket.status} />
                        <SeverityBadge severity={ticket.severity} />
                      </div>
                      <div className="recent-content">
                        <p className="recent-title">
                          <strong>{ticket.ticket_id}</strong> - {ticket.title}
                        </p>
                        <p className="recent-meta">
                          {ticket.application || 'N/A'} • {formatDate(ticket.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>
        </section>

        {/* Knowledge Base Info */}
        <section className="metrics-section">
          <h2 className="section-title">📚 Knowledge Base</h2>
          <Alert variant="info">
            💡 The vector database contains pre-loaded sample incidents for similarity matching.
            User-reported incidents are stored separately for tracking and analysis.
          </Alert>
          <div className="metrics-grid">
            <MetricCard
              title="User Reported Incidents"
              value={stats.total}
              icon="📝"
              color="primary"
            />
          </div>
        </section>
      </div>
    </div>
  );
};
