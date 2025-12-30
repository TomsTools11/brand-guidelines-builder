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
}

const STEPS = [
  {
    key: 'scraping',
    label: 'Fetching website',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
    progress: 10
  },
  {
    key: 'extracting_colors',
    label: 'Extracting colors',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
    ),
    progress: 30
  },
  {
    key: 'extracting_typography',
    label: 'Analyzing typography',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
      </svg>
    ),
    progress: 45
  },
  {
    key: 'extracting_logo',
    label: 'Identifying components',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
    progress: 55
  },
  {
    key: 'generating_content',
    label: 'Generating content',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    progress: 70
  },
  {
    key: 'building_pdf',
    label: 'Generating PDF',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    progress: 90
  },
];

export default function ExtractPage() {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [estimatedTime, setEstimatedTime] = useState(60);
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string;

  useEffect(() => {
    if (!jobId) return;

    const poll = setInterval(async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
        const res = await fetch(`${apiUrl}/api/jobs/${jobId}`);

        if (!res.ok) {
          throw new Error('Failed to fetch job status');
        }

        const data: JobStatus = await res.json();
        setJob(data);

        // Update estimated time based on progress
        const remaining = Math.max(5, Math.round((100 - data.progress_percent) * 0.6));
        setEstimatedTime(remaining);

        if (data.status === 'completed') {
          clearInterval(poll);
          router.push(`/preview/${jobId}`);
        }
        if (data.status === 'failed') {
          clearInterval(poll);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 1500);

    return () => clearInterval(poll);
  }, [jobId, router]);

  const getStepStatus = (step: typeof STEPS[0]) => {
    if (!job) return 'pending';
    if (job.status === step.key) return 'active';
    if (job.progress_percent > step.progress) return 'complete';
    return 'pending';
  };

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
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-sm text-[#A0A0A0] hover:text-white transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Cancel
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-6 py-16">
        {/* URL Pill */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#1A1A1A] border border-[#2A2A2A] rounded-full text-sm text-[#A0A0A0]">
            <svg className="w-4 h-4 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
            {job?.url || 'Loading...'}
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-white mb-3">Analyzing Website</h1>
          <p className="text-[#A0A0A0]">Please wait while we extract your design system...</p>
        </div>

        {/* Progress Card */}
        <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
          {/* Overall Progress */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm mb-3">
              <span className="text-[#A0A0A0]">Overall Progress</span>
              <span className="text-white font-medium">{job?.progress_percent || 0}%</span>
            </div>
            <div className="h-2 bg-[#2A2A2A] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#2383E2] rounded-full transition-all duration-500 ease-out progress-bar-animated"
                style={{ width: `${job?.progress_percent || 0}%` }}
              />
            </div>
          </div>

          {/* Steps List */}
          <div className="space-y-2">
            {STEPS.map((step) => {
              const status = getStepStatus(step);

              return (
                <div
                  key={step.key}
                  className={`flex items-center gap-4 p-4 rounded-lg transition-all ${
                    status === 'active'
                      ? 'bg-[#2383E2]/10 border border-[#2383E2]/20'
                      : status === 'complete'
                        ? 'bg-[#22C55E]/5'
                        : ''
                  }`}
                >
                  {/* Status Icon */}
                  <div className={`
                    w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 transition-all
                    ${status === 'complete'
                      ? 'bg-[#22C55E] text-white'
                      : status === 'active'
                        ? 'bg-[#2383E2] text-white'
                        : 'bg-[#2A2A2A] text-[#6B6B6B]'}
                  `}>
                    {status === 'complete' ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : status === 'active' ? (
                      <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      step.icon
                    )}
                  </div>

                  {/* Label */}
                  <div className="flex-1">
                    <span className={`text-sm font-medium ${
                      status === 'complete' ? 'text-[#22C55E]' :
                      status === 'active' ? 'text-white' :
                      'text-[#6B6B6B]'
                    }`}>
                      {step.label}
                    </span>
                  </div>

                  {/* Status Text */}
                  <span className={`text-xs ${
                    status === 'complete' ? 'text-[#22C55E]' :
                    status === 'active' ? 'text-[#2383E2]' :
                    'text-[#6B6B6B]'
                  }`}>
                    {status === 'complete' ? 'Done' :
                     status === 'active' ? 'Processing...' : ''}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Tip Box */}
          <div className="mt-6 p-4 bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg">
            <p className="text-sm text-[#6B6B6B]">
              <span className="text-[#2383E2] font-medium">Tip:</span> Your style guide will include color palettes, typography specifications, component documentation, and accessibility compliance information.
            </p>
          </div>
        </div>

        {/* Error State */}
        {job?.status === 'failed' && (
          <div className="mt-6 p-4 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-xl">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-full bg-[#EF4444]/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-[#EF4444]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-[#EF4444] mb-1">Extraction failed</h3>
                <p className="text-sm text-[#EF4444]/80">
                  {job.error_message || 'An unexpected error occurred. Please try again.'}
                </p>
                <button
                  onClick={() => router.push('/')}
                  className="mt-3 text-sm font-medium text-[#2383E2] hover:text-[#5DB5FE] transition-colors"
                >
                  Try another URL
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Estimated Time */}
        {job?.status !== 'failed' && (
          <div className="mt-8 text-center">
            <p className="text-sm text-[#6B6B6B]">
              Estimated time remaining: <span className="text-[#A0A0A0]">{estimatedTime} seconds</span>
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
