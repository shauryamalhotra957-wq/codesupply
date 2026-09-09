import { Badge } from '@/components/ui/badge';
import { RiskLevel } from '@/types';
import { cn } from '@/lib/utils';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number | null;
  className?: string;
}

export function RiskBadge({ level, score, className }: RiskBadgeProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Badge variant={level as any} className="capitalize">
        {level}
      </Badge>
      {score !== undefined && score !== null && (
        <span className="text-xs text-muted-foreground">
          ({score.toFixed(1)})
        </span>
      )}
    </div>
  );
}
