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
}

const STEPS = [
  { key: 'scraping', label: 'Scraping website', progress: 10 },
  { key: 'extracting_colors', label: 'Extracting colors', progress: 30 },
  { key: 'extracting_typography', label: 'Analyzing typography', progress: 45 },
  { key: 'extracting_logo', label: 'Finding logo', progress: 55 },
  { key: 'generating_content', label: 'Generating brand content', progress: 70 },
  { key: 'building_pdf', label: 'Building PDF', progress: 90 },
];

export default function ExtractPage() {
  const [job, setJob] = useState<JobStatus | null>(null);
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string;

  useEffect(() => {
    if (!jobId) return;

    const poll = setInterval(async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/api/jobs/${jobId}`);

        if (!res.ok) {
          throw new Error('Failed to fetch job status');
        }

        const data: JobStatus = await res.json();
        setJob(data);

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
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-lg w-full px-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Analyzing Website
          </h1>
          <p className="text-slate-600">
            Extracting brand elements and generating guidelines...
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-slate-500 mb-2">
            <span>{job?.current_step || 'Starting...'}</span>
            <span>{job?.progress_percent || 0}%</span>
          </div>
          <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${job?.progress_percent || 0}%` }}
            />
          </div>
        </div>

        {/* Steps List */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="space-y-4">
            {STEPS.map((step) => {
              const status = getStepStatus(step);

              return (
                <div key={step.key} className="flex items-center gap-4">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    transition-all duration-300
                    ${status === 'complete'
                      ? 'bg-green-500 text-white'
                      : status === 'active'
                        ? 'bg-blue-500 text-white animate-pulse'
                        : 'bg-slate-100 text-slate-400'}
                  `}>
                    {status === 'complete' ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : status === 'active' ? (
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      <span className="w-2 h-2 bg-slate-300 rounded-full" />
                    )}
                  </div>
                  <span className={`
                    transition-colors duration-300
                    ${status === 'complete'
                      ? 'text-slate-900'
                      : status === 'active'
                        ? 'text-slate-900 font-medium'
                        : 'text-slate-400'}
                  `}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Error State */}
        {job?.status === 'failed' && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-500 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-medium text-red-800">Extraction Failed</h3>
                <p className="text-sm text-red-600 mt-1">
                  {job.error_message || 'An unexpected error occurred. Please try again.'}
                </p>
                <button
                  onClick={() => router.push('/')}
                  className="mt-3 text-sm font-medium text-red-700 hover:text-red-800"
                >
                  Try another URL
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Cancel Link */}
        {job?.status !== 'failed' && (
          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/')}
              className="text-sm text-slate-500 hover:text-slate-700"
            >
              Cancel and start over
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
