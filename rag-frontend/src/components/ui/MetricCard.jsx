/**
 * MetricCard Component
 * Display statistics and metrics
 */

import { Card, CardBody } from './Card';
import './MetricCard.css';

export const MetricCard = ({ title, value, icon, trend, color = 'primary', className = '' }) => {
  return (
    <Card className={`metric-card metric-card-${color} ${className}`}>
      <CardBody>
        <div className="metric-header">
          <span className="metric-icon">{icon}</span>
          {trend && <span className={`metric-trend metric-trend-${trend > 0 ? 'up' : 'down'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>}
        </div>
        <div className="metric-value">{value}</div>
        <div className="metric-title">{title}</div>
      </CardBody>
    </Card>
  );
};
