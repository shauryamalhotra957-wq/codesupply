import type { Metadata } from 'next';
import { Plus_Jakarta_Sans, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

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
    <html lang="en" className={`dark ${plusJakartaSans.variable} ${jetbrainsMono.variable}`}>
      <body className="antialiased min-h-screen bg-background text-foreground font-sans selection:bg-purple-500/20 selection:text-purple-200">
        {children}
      </body>
    </html>
  );
}
