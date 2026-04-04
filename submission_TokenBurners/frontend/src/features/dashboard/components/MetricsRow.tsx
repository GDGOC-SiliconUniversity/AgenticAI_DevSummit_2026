interface MetricsRowProps {
  total: number;
  approved: number;
  waiting: number;
  escalated: number;
}

export function MetricsRow({ total, approved, waiting, escalated }: MetricsRowProps) {
  return (
    <div className="metrics-row">
      <div className="metric-cell">
        <div className="metric-num">{total}</div>
        <div className="metric-label">Scripts in loop</div>
      </div>
      <div className="metric-cell">
        <div className="metric-num metric-approved">{approved}</div>
        <div className="metric-label">Approved</div>
      </div>
      <div className="metric-cell">
        <div className="metric-num metric-waiting">{waiting}</div>
        <div className="metric-label">Awaiting response</div>
      </div>
      <div className="metric-cell">
        <div className="metric-num metric-escalated">{escalated}</div>
        <div className="metric-label">Escalated or call</div>
      </div>
    </div>
  );
}
