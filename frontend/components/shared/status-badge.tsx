import { Badge } from '@/components/ui/badge';
import { ScanStatus } from '@/types';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: ScanStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const getStatusColor = (s: ScanStatus) => {
    if (s === 'complete') return 'bg-green-500/10 text-green-700 hover:bg-green-500/20';
    if (s === 'failed') return 'bg-red-500/10 text-red-700 hover:bg-red-500/20';
    if (s === 'queued') return 'bg-gray-500/10 text-gray-700 hover:bg-gray-500/20';
    return 'bg-blue-500/10 text-blue-700 hover:bg-blue-500/20';
  };

  return (
    <Badge 
      variant="outline" 
      className={cn("capitalize border-transparent", getStatusColor(status), className)}
    >
      {status.replace('_', ' ')}
    </Badge>
  );
}
