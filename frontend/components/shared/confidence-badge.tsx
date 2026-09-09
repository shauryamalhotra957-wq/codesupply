import { Badge } from '@/components/ui/badge';
import { VersionConfidence } from '@/types';
import { cn } from '@/lib/utils';
import { CheckCircle2, HelpCircle, AlertCircle, Search } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: VersionConfidence;
  className?: string;
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const config = {
    exact: {
      color: 'bg-green-500/10 text-green-700 hover:bg-green-500/20',
      icon: CheckCircle2,
      label: 'Exact'
    },
    declared_range: {
      color: 'bg-blue-500/10 text-blue-700 hover:bg-blue-500/20',
      icon: Search,
      label: 'Declared Range'
    },
    inferred: {
      color: 'bg-amber-500/10 text-amber-700 hover:bg-amber-500/20',
      icon: AlertCircle,
      label: 'Inferred'
    },
    unknown: {
      color: 'bg-gray-500/10 text-gray-700 hover:bg-gray-500/20',
      icon: HelpCircle,
      label: 'Unknown'
    }
  };

  const current = config[confidence] || config.unknown;
  const Icon = current.icon;

  return (
    <Badge 
      variant="outline" 
      className={cn("flex items-center gap-1 border-transparent", current.color, className)}
    >
      <Icon className="h-3 w-3" />
      {current.label}
    </Badge>
  );
}
