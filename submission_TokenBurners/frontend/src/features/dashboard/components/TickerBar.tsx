interface TickerBarProps {
  lastClassified: string;
  escalated: string;
  queue: string;
}

export function TickerBar({ lastClassified, escalated, queue }: TickerBarProps) {
  return (
    <div className="ticker-bar">
      <div className="ticker-item">
        <span className="ticker-label">last classified:</span>
        <span className="ticker-val">{lastClassified}</span>
      </div>
      <div className="ticker-item">
        <span className="ticker-label">escalated:</span>
        <span className="ticker-val">{escalated}</span>
      </div>
      <div className="ticker-item">
        <span className="ticker-label">queue:</span>
        <span className="ticker-val">{queue}</span>
      </div>
    </div>
  );
}
