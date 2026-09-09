import React from 'react';
import { render, screen } from '@testing-library/react';
import { RiskBadge } from '@/components/shared/risk-badge';
import { EcosystemBadge } from '@/components/shared/ecosystem-badge';
import { ConfidenceBadge } from '@/components/shared/confidence-badge';
import { MetricCard } from '@/components/shared/metric-card';
import { Package } from 'lucide-react';

describe('Shared UI Components', () => {
  describe('RiskBadge', () => {
    it('renders critical risk badge with correct text', () => {
      render(<RiskBadge level="critical" />);
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
    });

    it('renders high risk badge with custom score', () => {
      render(<RiskBadge level="high" score={75.5} />);
      expect(screen.getByText(/high/i)).toBeInTheDocument();
      expect(screen.getByText('(75.5)')).toBeInTheDocument();
    });

    it('renders none risk badge', () => {
      render(<RiskBadge level="none" />);
      expect(screen.getByText(/none/i)).toBeInTheDocument();
    });

    it('renders unknown risk badge', () => {
      render(<RiskBadge level="unknown" />);
      expect(screen.getByText(/unknown/i)).toBeInTheDocument();
    });
  });

  describe('EcosystemBadge', () => {
    it('renders npm ecosystem', () => {
      render(<EcosystemBadge ecosystem="npm" />);
      expect(screen.getByText(/npm/i)).toBeInTheDocument();
    });

    it('renders PyPI ecosystem', () => {
      render(<EcosystemBadge ecosystem="pypi" />);
      expect(screen.getByText(/pypi/i)).toBeInTheDocument();
    });

    it('renders Maven ecosystem', () => {
      render(<EcosystemBadge ecosystem="maven" />);
      expect(screen.getByText(/maven/i)).toBeInTheDocument();
    });

    it('renders Go ecosystem', () => {
      render(<EcosystemBadge ecosystem="golang" />);
      expect(screen.getByText(/golang/i)).toBeInTheDocument();
    });

    it('renders Cargo ecosystem', () => {
      render(<EcosystemBadge ecosystem="cargo" />);
      expect(screen.getByText(/cargo/i)).toBeInTheDocument();
    });
  });

  describe('ConfidenceBadge', () => {
    it('renders exact confidence', () => {
      render(<ConfidenceBadge confidence="exact" />);
      expect(screen.getByText(/exact/i)).toBeInTheDocument();
    });

    it('renders declared range confidence', () => {
      render(<ConfidenceBadge confidence="declared_range" />);
      expect(screen.getByText(/declared range/i)).toBeInTheDocument();
    });

    it('renders unknown confidence', () => {
      render(<ConfidenceBadge confidence="unknown" />);
      expect(screen.getByText(/unknown/i)).toBeInTheDocument();
    });
  });

  describe('MetricCard', () => {
    it('renders title, value, and subtitle', () => {
      render(
        <MetricCard
          title="Total Components"
          value={424}
          subtitle="Across all manifests"
          icon={Package}
        />
      );
      expect(screen.getByText('Total Components')).toBeInTheDocument();
      expect(screen.getByText('424')).toBeInTheDocument();
      expect(screen.getByText('Across all manifests')).toBeInTheDocument();
    });
  });
});
