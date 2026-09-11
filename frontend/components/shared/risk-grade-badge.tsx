'use client';
export function RiskGradeBadge({ grade }: { grade: string }) {
  return <span className='font-bold text-lg'>{grade}</span>;
}
