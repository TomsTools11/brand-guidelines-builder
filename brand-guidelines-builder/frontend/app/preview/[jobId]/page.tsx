'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';

interface JobStatus {
  job_id: string;
  status: string;
  progress_percent: number;
  current_step: string;
  error_message?: string;
  pdf_path?: string;
  url?: string;
  brand_data?: {
    company_name?: string;
    colors?: {
      primary?: { hex: string; name: string };
      secondary?: { hex: string; name: string };
      accent?: { hex: string; name: string };
      neutrals?: Array<{ hex: string; name: string }>;
    };
    typography?: {
      primary?: { name: string; family: string };
      secondary?: { name: string; family: string };
    };
  };
}

// Mock extracted colors for demo (would come from API in production)
const MOCK_COLORS = [
  { hex: '#0A0A0A', name: 'Near Black' },
  { hex: '#1F1F1F', name: 'Dark Gray' },
  { hex: '#2383E2', name: 'Primary Blue' },
  { hex: '#3B82F6', name: 'Light Blue' },
  { hex: '#6B7280', name: 'Gray' },
  { hex: '#9CA3AF', name: 'Light Gray' },
  { hex: '#D1D5DB', name: 'Border Gray' },
  { hex: '#F3F4F6', name: 'Light Background' },
  { hex: '#FFFFFF', name: 'White' },
];

export default function PreviewPage() {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [downloading, setDownloading] = useState(false);
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string;

  useEffect(() => {
    if (!jobId) return;

    const fetchJob = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
        const res = await fetch(`${apiUrl}/api/jobs/${jobId}`);

        if (!res.ok) {
          throw new Error('Failed to fetch job status');
        }

        const data: JobStatus = await res.json();
        setJob(data);

        if (data.status !== 'completed') {
          router.push(`/extract/${jobId}`);
        }
      } catch (error) {
        console.error('Fetch error:', error);
        router.push('/');
      }
    };

    fetchJob();
  }, [jobId, router]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const res = await fetch(`${apiUrl}/api/jobs/${jobId}/pdf`);

      if (!res.ok) {
        throw new Error('Failed to download PDF');
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `style_guide_${jobId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const companyName = job?.brand_data?.company_name || 'Company';
  const sourceUrl = job?.url || '';

  if (!job) {
    return (
      <div className="min-h-screen bg-[#0D0D0D] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#2383E2] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0D0D0D]">
      {/* Header */}
      <header className="border-b border-[#1A1A1A]">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2383E2] rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="font-semibold text-white">Style Guide Generator</span>
          </div>
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-[#A0A0A0] hover:text-white transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            View Website
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Title Section */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-white mb-3">Your Style Guide is Ready!</h1>
          <p className="text-[#A0A0A0]">
            We&apos;ve analyzed {companyName} and created a comprehensive 19-page style guide document.
          </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4 mb-10">
          {[
            { value: '8', label: 'Colors', icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            )},
            { value: '1', label: 'Font Families', icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            )},
            { value: '22', label: 'Components', icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            )},
            { value: '19', label: 'Pages', icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            )},
          ].map((stat, i) => (
            <div key={i} className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5 text-center">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mx-auto mb-3 text-[#2383E2]">
                {stat.icon}
              </div>
              <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-xs text-[#6B6B6B]">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Two Column Layout */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* PDF Preview */}
          <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-[#6B6B6B]">PDF Preview</span>
              <span className="text-xs text-[#6B6B6B]">19 pages</span>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-lg">
              <div className="text-xs text-gray-500 mb-1">Brand Style Guide</div>
              <div className="text-sm font-bold text-gray-800 mb-1">{companyName}</div>
              <div className="text-[10px] text-gray-400 mb-4">AI-Powered Product Requirements Generator</div>
              <div className="h-20 bg-gradient-to-r from-gray-800 to-gray-600 rounded mb-3"></div>
              <div className="flex gap-1 mb-4">
                <div className="w-6 h-6 rounded bg-[#2383E2]"></div>
                <div className="w-6 h-6 rounded bg-[#1a6bc2]"></div>
                <div className="w-6 h-6 rounded bg-gray-800"></div>
                <div className="w-6 h-6 rounded bg-gray-400"></div>
              </div>
              <div className="space-y-1">
                <div className="h-2 bg-gray-200 rounded w-3/4"></div>
                <div className="h-2 bg-gray-200 rounded w-full"></div>
                <div className="h-2 bg-gray-200 rounded w-2/3"></div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="text-[10px] text-gray-400">Version: 1.0</div>
                <div className="text-[10px] text-gray-400">Generated: {new Date().toLocaleDateString()}</div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Download Section */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
              <h3 className="font-semibold text-white mb-2">Download Style Guide</h3>
              <p className="text-sm text-[#6B6B6B] mb-4">
                Get your professionally formatted PDF style guide, ready to share with your team.
              </p>
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="w-full h-12 bg-[#2383E2] hover:bg-[#1a6bc2] text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {downloading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Downloading...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download PDF
                  </>
                )}
              </button>
            </div>

            {/* What's Included */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
              <h3 className="font-semibold text-white mb-4">What&apos;s Included</h3>
              <ul className="space-y-2">
                {[
                  'Cover page & table of contents',
                  'Brand identity guidelines',
                  'Color palette with values',
                  'Typography specifications',
                  'UI component library',
                  'Layout & grid system',
                  'Accessibility report',
                  'Resource links'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-[#A0A0A0]">
                    <svg className="w-4 h-4 text-[#22C55E] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Source Website */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
              <h3 className="font-semibold text-white mb-2">Source Website</h3>
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-[#2383E2] hover:underline flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                {sourceUrl.replace(/^https?:\/\//, '')}
              </a>
            </div>
          </div>
        </div>

        {/* Extracted Color Palette */}
        <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 mb-8">
          <h3 className="font-semibold text-white mb-6">Extracted Color Palette</h3>
          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-4">
            {MOCK_COLORS.map((color, i) => (
              <div key={i} className="text-center">
                <div
                  className="w-full aspect-square rounded-lg mb-2 border border-[#2A2A2A]"
                  style={{ backgroundColor: color.hex }}
                />
                <div className="text-xs font-medium text-white mb-1">{color.hex}</div>
                <div className="text-[10px] text-[#6B6B6B]">{color.name}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Typography System */}
        <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 mb-8">
          <h3 className="font-semibold text-white mb-6">Typography System</h3>
          <div className="space-y-4">
            <div>
              <div className="text-xs text-[#6B6B6B] mb-2">Primary Font</div>
              <div className="text-2xl font-bold text-white">system-ui</div>
              <div className="text-sm text-[#A0A0A0]">system-ui, sans-serif</div>
            </div>
          </div>
        </div>

        {/* Generate Another */}
        <div className="text-center">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center gap-2 text-sm text-[#A0A0A0] hover:text-white transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate another style guide
          </button>
        </div>
      </main>
    </div>
  );
}
