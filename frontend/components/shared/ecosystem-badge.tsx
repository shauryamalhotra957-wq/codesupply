import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface EcosystemBadgeProps {
  ecosystem: string;
  className?: string;
}

export function EcosystemBadge({ ecosystem, className }: EcosystemBadgeProps) {
  const getEcosystemColor = (eco: string) => {
    switch (eco.toLowerCase()) {
      case 'npm':
        return 'bg-red-500/10 text-red-700 hover:bg-red-500/20';
      case 'pypi':
      case 'python':
        return 'bg-blue-500/10 text-blue-700 hover:bg-blue-500/20';
      case 'maven':
        return 'bg-orange-500/10 text-orange-700 hover:bg-orange-500/20';
      case 'go':
      case 'golang':
        return 'bg-cyan-500/10 text-cyan-700 hover:bg-cyan-500/20';
      case 'cargo':
      case 'rust':
        return 'bg-amber-700/10 text-amber-900 hover:bg-amber-700/20';
      default:
        return 'bg-gray-500/10 text-gray-700 hover:bg-gray-500/20';
    }
  };

  return (
    <Badge 
      variant="outline" 
      className={cn("capitalize font-mono border-transparent", getEcosystemColor(ecosystem), className)}
    >
      {ecosystem}
    </Badge>
  );
}
