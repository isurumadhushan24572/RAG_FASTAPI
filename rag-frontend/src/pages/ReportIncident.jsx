/**
 * ReportIncident Page
 * Form to submit new incidents and get AI-generated solutions
 */

import { useState, useEffect } from 'react';
import { Header } from '../components/layout/Header';
import { Card, CardBody } from '../components/ui/Card';
import { Input, TextArea, Select } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { Badge, SeverityBadge } from '../components/ui/Badge';
import { useSubmitIncident } from '../hooks/useApi';
import { CATEGORY_OPTIONS, SEVERITY_OPTIONS, ENVIRONMENT_OPTIONS } from '../config/constants';
import './ReportIncident.css';

export const ReportIncident = () => {
  const { mutate: submitIncident, isPending, isError, error } = useSubmitIncident();
  
  // Store response data in component state to persist it
  const [responseData, setResponseData] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: CATEGORY_OPTIONS[0],
    severity: 'Medium',
    application: '',
    affected_users: '',
    environment: 'Production',
  });

  // Debug effect to log state changes
  useEffect(() => {
    console.log('🔍 State update:', { isPending, isError, hasResponseData: !!responseData });
    if (responseData) console.log('📦 Response data stored:', responseData);
    if (error) console.error('❌ Error:', error);
  }, [isPending, isError, responseData, error]);

  // Scroll to results when they appear
  useEffect(() => {
    if (responseData) {
      console.log('📜 SUCCESS! Scrolling to results section');
      setTimeout(() => {
        const resultsSection = document.querySelector('.report-results-section');
        if (resultsSection) {
          console.log('📜 Results section found, scrolling...');
          resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          console.warn('⚠️ Results section not found in DOM');
        }
      }, 150);
    }
  }, [responseData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('📝 Submitting form:', formData);
    setResponseData(null); // Clear previous results
    
    submitIncident(formData, {
      onSuccess: (data) => {
        console.log('✅ SUCCESS! Received data:', data);
        setResponseData(data); // Store response in component state
      },
      onError: (err) => {
        console.error('❌ ERROR:', err);
      }
    });
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: CATEGORY_OPTIONS[0],
      severity: 'Medium',
      application: '',
      affected_users: '',
      environment: 'Production',
    });
    setResponseData(null); // Clear results
  };

  return (
    <div className="page-container">
      <Header title="📝 Report New Application Incident" />

      <div className="page-content">
        
        {/* Form Section */}
        <div className="report-form-section">
          <Card>
            <CardBody>
              <form onSubmit={handleSubmit}>
                <div className="form-grid">
                  <div className="form-col-full">
                    <Input
                      label="Incident Summary"
                      name="title"
                      value={formData.title}
                      onChange={handleChange}
                      placeholder="Brief description of the issue"
                      required
                    />
                  </div>

                  <div className="form-col-full">
                    <TextArea
                      label="Detailed Description"
                      name="description"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Include error messages, affected functionality, time started, steps to reproduce..."
                      rows={6}
                      required
                    />
                  </div>

                  <div className="form-col-half">
                    <Input
                      label="Application/Service"
                      name="application"
                      value={formData.application}
                      onChange={handleChange}
                      placeholder="e.g., Payment API, User Portal"
                    />
                  </div>

                  <div className="form-col-half">
                    <Select
                      label="Environment"
                      name="environment"
                      value={formData.environment}
                      onChange={handleChange}
                      options={ENVIRONMENT_OPTIONS}
                      required
                    />
                  </div>

                  <div className="form-col-half">
                    <Select
                      label="Category"
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      options={CATEGORY_OPTIONS}
                      required
                    />
                  </div>

                  <div className="form-col-half">
                    <Select
                      label="Severity"
                      name="severity"
                      value={formData.severity}
                      onChange={handleChange}
                      options={SEVERITY_OPTIONS.map((s) => s.value)}
                      required
                    />
                    <p className="field-hint">
                      Critical: Service down | High: Major feature broken | Medium: Moderate impact |
                      Low: Minor issue
                    </p>
                  </div>

                  <div className="form-col-full">
                    <Input
                      label="Affected Users"
                      name="affected_users"
                      value={formData.affected_users}
                      onChange={handleChange}
                      placeholder="All users / Specific tenant / Region"
                    />
                  </div>

                  <div className="form-col-full">
                    <Button
                      type="submit"
                      variant="primary"
                      size="large"
                      fullWidth
                      loading={isPending}
                      disabled={isPending}
                    >
                      {isPending ? 'Analyzing Incident...' : '🔍 Submit Incident & Get AI Analysis'}
                    </Button>
                  </div>
                </div>
              </form>
            </CardBody>
          </Card>
        </div>

        {/* Loading State */}
        {isPending && (
          <div className="report-results-section">
            <Alert variant="info">
              ⏳ Processing your incident report... Please wait.
            </Alert>
          </div>
        )}

        {/* Results Section */}
        {responseData && (
          <div className="report-results-section">
            <Alert variant="success" onClose={resetForm}>
              ✅ Incident {responseData.ticket_id} logged successfully! Status: {responseData.status}
            </Alert>

            <Card>
              <CardBody>
                <div className="result-header">
                  <h2>🔍 AI Analysis Results</h2>
                  <div className="result-badges">
                    <SeverityBadge severity={formData.severity} />
                    <Badge variant={responseData.status === 'Resolved' ? 'success' : 'warning'}>
                      {responseData.status}
                    </Badge>
                  </div>
                </div>

                {/* Status Message */}
                <div className="result-status">
                  <Alert variant={responseData.status === 'Resolved' ? 'success' : 'warning'}>
                    {responseData.message}
                  </Alert>
                </div>

                {/* Similar Incidents */}
                {responseData.similar_tickets && responseData.similar_tickets.length > 0 && (
                  <div className="result-section">
                    <h3>
                      📚 {responseData.similar_tickets.length} Similar Past Incident(s) Found (85%+ match)
                    </h3>
                    {responseData.similar_tickets.map((ticket, index) => {
                      const similarityPercent = (ticket.similarity_score * 100).toFixed(1);
                      const matchIcon =
                        similarityPercent >= 90 ? '🟢' : similarityPercent >= 80 ? '🟡' : '🟠';
                      
                      return (
                        <Card key={index} className="similar-ticket-card">
                          <CardBody>
                            <div className="similar-ticket-header">
                              <h4>
                                {matchIcon} {index + 1}. {ticket.title}
                              </h4>
                              <Badge variant="info">
                                Match: {similarityPercent}%
                              </Badge>
                            </div>
                            <p className="similar-ticket-id">ID: {ticket.ticket_id}</p>
                            {(ticket.content || ticket.description) && (
                              <p className="similar-ticket-content">
                                {(ticket.content || ticket.description).substring(0, 250)}
                                {(ticket.content || ticket.description).length > 250 && '...'}
                              </p>
                            )}
                          </CardBody>
                        </Card>
                      );
                    })}
                  </div>
                )}

                {responseData.similar_tickets && responseData.similar_tickets.length === 0 && (
                  <Alert variant="info">
                    ℹ️ No similar incidents found with 85% similarity. This appears to be a new type of
                    issue.
                  </Alert>
                )}

                {/* Root Cause Analysis */}
                <div className="result-section">
                  <h3>🔬 Root Cause Analysis</h3>
                  <Card className="analysis-card">
                    <CardBody>
                      {responseData.reasoning ? (
                        responseData.reasoning.startsWith('Unable to generate') ? (
                          <Alert variant="error">{responseData.reasoning}</Alert>
                        ) : (
                          <p className="analysis-text">{responseData.reasoning}</p>
                        )
                      ) : (
                        <Alert variant="warning">
                          ⚠️ No root cause analysis available. Manual investigation required.
                        </Alert>
                      )}
                    </CardBody>
                  </Card>
                </div>

                {/* Resolution Steps */}
                <div className="result-section">
                  <h3>✅ Resolution Steps</h3>
                  <Card className="solution-card">
                    <CardBody>
                      {responseData.solution ? (
                        responseData.solution.startsWith('Unable to generate') ? (
                          <>
                            <Alert variant="error">{responseData.solution}</Alert>
                            <Alert variant="warning">
                              ⚠️ Action Required: Please investigate manually and document the resolution
                              for future reference.
                            </Alert>
                          </>
                        ) : (
                          <pre className="solution-text">{responseData.solution}</pre>
                        )
                      ) : (
                        <Alert variant="warning">
                          ⚠️ No solution steps available. Manual resolution required.
                        </Alert>
                      )}
                    </CardBody>
                  </Card>
                </div>

                <div className="result-actions">
                  <Button variant="primary" onClick={resetForm}>
                    Report Another Incident
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {isError && (
          <Alert variant="error" onClose={() => window.location.reload()}>
            ❌ Error: {error?.response?.data?.detail || error?.message || 'Failed to submit incident'}
          </Alert>
        )}
      </div>
    </div>
  );
};
