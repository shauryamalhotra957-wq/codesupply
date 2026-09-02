import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import LandingView from '../components/LandingView';

describe('LandingView', () => {
  it('renders branding and upload dropzone', () => {
    render(<LandingView onUpload={vi.fn()} onLoadDemo={vi.fn()} isScanning={false} />);
    expect(screen.getByText(/Automated SBOM Generation/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload Project Archive/i)).toBeInTheDocument();
    expect(screen.getByText(/1-Click Pre-Packaged Demo Scenarios/i)).toBeInTheDocument();
  });

  it('triggers demo load when clicking demo scenario button', () => {
    const handleLoadDemo = vi.fn();
    render(<LandingView onUpload={vi.fn()} onLoadDemo={handleLoadDemo} isScanning={false} />);
    
    const demoButtons = screen.getAllByRole('button', { name: /Run Scan Demo/i });
    expect(demoButtons.length).toBe(4);
    
    fireEvent.click(demoButtons[0]);
    expect(handleLoadDemo).toHaveBeenCalledWith('python-project');
  });
});
