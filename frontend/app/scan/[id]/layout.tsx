import { Sidebar } from '@/components/layout/sidebar';
import { Topbar } from '@/components/layout/topbar';

export default function ScanLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { id: string };
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar scanId={params.id} />
      <div className="flex-1 flex flex-col lg:pl-64 overflow-hidden">
        <Topbar scanId={params.id} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
