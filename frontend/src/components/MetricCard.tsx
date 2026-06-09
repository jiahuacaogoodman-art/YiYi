import { Card, Typography } from "antd";
import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
}

export function MetricCard({ label, value, hint, icon }: MetricCardProps) {
  return (
    <Card className="metric-card" variant="borderless">
      <div className="metric-card__top">
        <Typography.Text type="secondary">{label}</Typography.Text>
        {icon ? <span className="metric-card__icon">{icon}</span> : null}
      </div>
      <div className="metric-card__value">{value}</div>
      {hint ? <div className="metric-card__hint">{hint}</div> : null}
    </Card>
  );
}