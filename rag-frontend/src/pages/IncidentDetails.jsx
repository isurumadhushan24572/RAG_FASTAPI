/**
 * IncidentDetails Page
 * View detailed information about a specific incident
 */

import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SeverityBadge, StatusBadge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { Alert } from '../components/ui/Alert';
import { useTicket } from '../hooks/useApi';
import { formatDate } from '../utils/helpers';
import './IncidentDetails.css';

export const IncidentDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useTicket(id);

  if (isLoading) {
    return (
      <div className="page-container">
        <Header title="🔍 Incident Details" />
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="page-container">
        <Header title="🔍 Incident Details" />
        <Alert variant="error">
          Error loading incident: {error?.response?.data?.detail || error?.message}
        </Alert>
        <Button onClick={() => navigate('/incidents')}>← Back to All Incidents</Button>
      </div>
    );
  }

  const ticket = data?.ticket;

  if (!ticket) {
    return (
      <div className="page-container">
        <Header title="🔍 Incident Details" />
        <Alert variant="warning">Incident not found.</Alert>
        <Button onClick={() => navigate('/incidents')}>← Back to All Incidents</Button>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="🔍 Incident Details" />

      <div className="page-content">
        <div className="details-actions">
          <Button variant="outline" onClick={() => navigate('/incidents')}>
            ← Back to All Incidents
          </Button>
        </div>

        {/* Main Details */}
        <Card className="details-main-card">
          <CardBody>
            <div className="details-header">
              <div>
                <h1 className="details-title">{ticket.title}</h1>
                <p className="details-id">Incident ID: {ticket.ticket_id}</p>
              </div>
              <div className="details-badges">
                <StatusBadge status={ticket.status} />
                <SeverityBadge severity={ticket.severity} />
              </div>
            </div>

            <div className="details-grid">
              <div className="details-item">
                <label className="details-label">Application/Service</label>
                <p className="details-value">{ticket.application || 'N/A'}</p>
              </div>
              <div className="details-item">
                <label className="details-label">Environment</label>
                <p className="details-value">{ticket.environment}</p>
              </div>
              <div className="details-item">
                <label className="details-label">Category</label>
                <p className="details-value">{ticket.category}</p>
              </div>
              <div className="details-item">
                <label className="details-label">Affected Users</label>
                <p className="details-value">{ticket.affected_users || 'N/A'}</p>
              </div>
              <div className="details-item">
                <label className="details-label">Reported On</label>
                <p className="details-value">{formatDate(ticket.timestamp)}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Description */}
        <Card>
          <CardBody>
            <h2 className="section-heading">📝 Detailed Description</h2>
            <p className="description-text">{ticket.description}</p>
          </CardBody>
        </Card>

        {/* Root Cause Analysis */}
        {ticket.reasoning && (
          <Card>
            <CardBody>
              <h2 className="section-heading">🔬 Root Cause Analysis</h2>
              {ticket.reasoning.startsWith('Unable to generate') ? (
                <Alert variant="error">{ticket.reasoning}</Alert>
              ) : (
                <p className="analysis-text">{ticket.reasoning}</p>
              )}
            </CardBody>
          </Card>
        )}

        {/* Resolution Steps */}
        {ticket.solution && (
          <Card>
            <CardBody>
              <h2 className="section-heading">✅ Resolution Steps</h2>
              {ticket.solution.startsWith('Unable to generate') ? (
                <>
                  <Alert variant="error">{ticket.solution}</Alert>
                  <Alert variant="warning">
                    ⚠️ Action Required: This incident requires manual investigation and resolution.
                  </Alert>
                </>
              ) : (
                <pre className="solution-text">{ticket.solution}</pre>
              )}
            </CardBody>
          </Card>
        )}

        {!ticket.solution && (
          <Alert variant="warning">
            ⚠️ No resolution available yet for this incident.
          </Alert>
        )}
      </div>
    </div>
  );
};
