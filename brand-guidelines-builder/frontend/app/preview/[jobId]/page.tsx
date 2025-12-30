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
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/api/jobs/${jobId}`);

        if (!res.ok) {
          throw new Error('Failed to fetch job status');
        }

        const data: JobStatus = await res.json();
        setJob(data);

        // Redirect to extract page if not completed
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/jobs/${jobId}/pdf`);

      if (!res.ok) {
        throw new Error('Failed to download PDF');
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `brand_guidelines_${jobId.slice(0, 8)}.pdf`;
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

  if (!job) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-xl w-full px-6">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Brand Guidelines Ready!
          </h1>
          <p className="text-slate-600">
            Your professional brand guidelines PDF has been generated successfully.
          </p>
        </div>

        {/* Preview Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="flex items-start gap-4">
            {/* PDF Icon */}
            <div className="w-16 h-20 bg-red-50 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-8 h-10 text-red-500" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 1.5L18.5 9H14V3.5zM6 20V4h6v6h6v10H6z"/>
                <path d="M8.5 13.5h1v3h-1v-3zm1.5 0h1.5c.8 0 1.5.7 1.5 1.5s-.7 1.5-1.5 1.5H10v-3zm1.5 2H11v-1h.5c.3 0 .5.2.5.5s-.2.5-.5.5zm2-.5v1.5h-1v-3h2v1h-1v.5h1z"/>
              </svg>
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-slate-900 truncate">
                brand_guidelines_{jobId.slice(0, 8)}.pdf
              </h3>
              <p className="text-sm text-slate-500 mt-1">
                Professional brand guidelines document
              </p>

              {/* Features List */}
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 text-xs text-slate-600">
                  Color Palette
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 text-xs text-slate-600">
                  Typography
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 text-xs text-slate-600">
                  Logo Usage
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 text-xs text-slate-600">
                  Brand Voice
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Download Button */}
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="w-full py-4 px-6 text-lg font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
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

        {/* Secondary Actions */}
        <div className="mt-6 flex justify-center gap-6 text-sm">
          <button
            onClick={() => router.push('/')}
            className="text-slate-600 hover:text-slate-900 flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate another
          </button>
        </div>

        {/* Info Footer */}
        <div className="mt-12 text-center">
          <p className="text-xs text-slate-400">
            Your PDF will be available for 24 hours. Make sure to download it before then.
          </p>
        </div>
      </div>
    </main>
  );
}
