import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CodeSupply — Software Supply Chain & SBOM Intelligence',
  description: 'Enterprise-grade SBOM generation and vulnerability intelligence engine for SIH1449. CycloneDX 1.7, SPDX 2.3, OSV, and CISA KEV.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-background text-foreground selection:bg-purple-500/20 selection:text-purple-200">
        {children}
      </body>
    </html>
  );
}
