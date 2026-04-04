interface MastheadProps {
  healthMessage: string;
  clientCount: number;
}

export function Masthead({ healthMessage, clientCount }: MastheadProps) {
  const today = new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date());

  return (
    <div className="masthead">
      <div className="masthead-left">
        <div className="masthead-title">ScriptAgent</div>
        <div className="masthead-sub">Content Approval Loop — Scrollhouse Ops</div>
      </div>
      <div className="masthead-meta">
        {today}
        <br />
        {clientCount} active clients
        <br />
        <span className="pulse" />
        {healthMessage}
      </div>
    </div>
  );
}
