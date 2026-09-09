import { Scan, ScanStage } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface ScanProgressProps {
  scan: Scan;
}

export function ScanProgress({ scan }: ScanProgressProps) {
  const stages = scan.stages || [];
  
  // Find current active stage index
  let activeIndex = stages.findIndex(s => s.status === 'running');
  if (activeIndex === -1) {
    // If none running, find first failed
    activeIndex = stages.findIndex(s => s.status === 'failed');
  }
  if (activeIndex === -1) {
    // If none failed, find first pending
    activeIndex = stages.findIndex(s => s.status === 'pending');
  }
  
  const progress = activeIndex > 0 ? (activeIndex / stages.length) * 100 : 5;

  return (
    <Card className="w-full shadow-lg border-2">
      <CardHeader className="border-b bg-muted/30 pb-8">
        <CardTitle className="text-2xl">Analyzing Project</CardTitle>
        <CardDescription className="text-base mt-2">
          {scan.filename} • {(scan.file_size / 1024 / 1024).toFixed(2)} MB
        </CardDescription>
        <div className="mt-6">
          <Progress value={progress} className="h-2" />
        </div>
      </CardHeader>
      <CardContent className="p-6 pt-8">
        <div className="space-y-6">
          {stages.map((stage, index) => (
            <StageItem key={stage.id || index} stage={stage} isActive={index === activeIndex} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function StageItem({ stage, isActive }: { stage: ScanStage, isActive: boolean }) {
  const getIcon = () => {
    switch (stage.status) {
      case 'completed': return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed': return <XCircle className="h-5 w-5 text-destructive" />;
      case 'running': return <Loader2 className="h-5 w-5 text-primary animate-spin" />;
      default: return <Circle className="h-5 w-5 text-muted-foreground/50" />;
    }
  };

  const getStageLabel = (name: string) => {
    return name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div className={`flex gap-4 ${stage.status === 'pending' && !isActive ? 'opacity-50' : ''}`}>
      <div className="mt-0.5">{getIcon()}</div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <h4 className={`text-sm font-medium ${isActive ? 'text-primary' : 'text-foreground'}`}>
            {getStageLabel(stage.stage_name)}
          </h4>
          {stage.total_count !== null && stage.total_count > 0 && (
            <span className="text-xs font-mono text-muted-foreground">
              {stage.completed_count || 0} / {stage.total_count}
            </span>
          )}
        </div>
        {stage.message && (
          <p className="text-xs text-muted-foreground">
            {stage.message}
          </p>
        )}
      </div>
    </div>
  );
}
