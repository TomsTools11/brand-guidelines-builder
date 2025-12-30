'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const res = await fetch(`${apiUrl}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!res.ok) {
        throw new Error('Failed to start extraction');
      }

      const data = await res.json();
      router.push(`/extract/${data.job_id}`);
    } catch {
      setError('Failed to start extraction. Please check the URL and try again.');
      setLoading(false);
    }
  };

  const tryExample = (exampleUrl: string) => {
    setUrl(exampleUrl);
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
          <nav className="flex items-center gap-6 text-sm text-[#A0A0A0]">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-20 pb-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#1A1A1A] border border-[#2A2A2A] rounded-full text-sm text-[#A0A0A0] mb-8">
            <svg className="w-4 h-4 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            AI-Powered Design System Extraction
          </div>

          {/* Headline */}
          <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight mb-6">
            Generate Professional<br />
            Style Guides <span className="text-[#2383E2]">in Seconds</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg text-[#A0A0A0] max-w-2xl mx-auto mb-10">
            Enter any website URL and receive a comprehensive, beautifully
            formatted PDF style guide documenting colors, typography,
            components, and more.
          </p>

          {/* URL Input Form */}
          <form onSubmit={handleSubmit} className="max-w-xl mx-auto mb-4">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2">
                  <svg className="w-5 h-5 text-[#6B6B6B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                </div>
                <input
                  type="url"
                  placeholder="Enter website URL, e.g., stripe.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="w-full h-12 pl-12 pr-4 bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg text-white placeholder:text-[#6B6B6B] focus:border-[#2383E2] focus:ring-2 focus:ring-[#2383E2]/20 focus:outline-none transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="h-12 px-6 bg-[#2383E2] hover:bg-[#1a6bc2] text-white font-medium rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Starting...
                  </>
                ) : (
                  <>
                    Generate Guide
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="max-w-xl mx-auto mb-4 p-3 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg text-sm text-[#EF4444]">
              {error}
            </div>
          )}

          {/* Example Links */}
          <div className="flex items-center justify-center gap-2 text-sm text-[#6B6B6B]">
            <span>Try examples:</span>
            <button onClick={() => tryExample('https://stripe.com')} className="text-[#2383E2] hover:underline">stripe.com</button>
            <span>|</span>
            <button onClick={() => tryExample('https://notion.so')} className="text-[#2383E2] hover:underline">notion.so</button>
            <span>|</span>
            <button onClick={() => tryExample('https://linear.app')} className="text-[#2383E2] hover:underline">linear.app</button>
          </div>
        </div>
      </section>

      {/* Preview Card */}
      <section className="pb-20">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-[#141414] border border-[#2A2A2A] rounded-2xl p-6 shadow-2xl">
            <div className="grid md:grid-cols-3 gap-6">
              {/* Mock Site Preview */}
              <div className="bg-white rounded-lg p-4">
                <div className="text-xs font-semibold text-gray-800 mb-1">YourSite.com</div>
                <div className="text-[10px] text-gray-500 mb-3">Brand & Design Style Guide</div>
                <div className="h-20 bg-gradient-to-br from-gray-800 to-gray-600 rounded mb-2"></div>
                <div className="flex gap-1">
                  <div className="w-3 h-3 rounded bg-[#2383E2]"></div>
                  <div className="w-3 h-3 rounded bg-[#1a6bc2]"></div>
                  <div className="w-3 h-3 rounded bg-gray-800"></div>
                </div>
              </div>

              {/* Color Palette */}
              <div className="bg-[#1A1A1A] rounded-lg p-4 border border-[#2A2A2A]">
                <div className="text-xs text-[#6B6B6B] mb-2">2.2 Color Palette</div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-[#2383E2]"></div>
                    <span className="text-xs text-[#A0A0A0]">Primary</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-[#22C55E]"></div>
                    <span className="text-xs text-[#A0A0A0]">Accent</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-[#1A1A1A] border border-[#333]"></div>
                    <span className="text-xs text-[#A0A0A0]">Background</span>
                  </div>
                </div>
              </div>

              {/* Typography */}
              <div className="bg-[#1A1A1A] rounded-lg p-4 border border-[#2A2A2A]">
                <div className="text-xs text-[#6B6B6B] mb-2">2.3 Typography</div>
                <div className="space-y-1">
                  <div className="text-lg font-bold text-white">Heading 1</div>
                  <div className="text-base font-semibold text-white">Heading 2</div>
                  <div className="text-sm font-medium text-white">Heading 3</div>
                  <div className="text-xs text-[#A0A0A0] mt-2">Body text looks like this, with good readability.</div>
                </div>
              </div>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-center gap-2 mt-6 text-xs text-[#6B6B6B]">
              <span>&lt;</span>
              <span>1</span>
              <span>/</span>
              <span>18 pages total</span>
              <span>&gt;</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-[#0A0A0A]">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-white text-center mb-4">How It Works</h2>
          <p className="text-[#A0A0A0] text-center mb-16">
            Three simple steps to create a comprehensive style guide for any website
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <div className="w-12 h-12 bg-[#1A1A1A] border border-[#2A2A2A] rounded-full flex items-center justify-center text-[#2383E2] font-bold">
                    01
                  </div>
                  <div className="hidden md:block absolute top-1/2 left-full w-[calc(100%+2rem)] h-px bg-[#2A2A2A]"></div>
                </div>
              </div>
              <h3 className="font-semibold text-white mb-2">Enter URL</h3>
              <p className="text-sm text-[#6B6B6B]">Paste any website URL you want to analyze</p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <div className="w-12 h-12 bg-[#1A1A1A] border border-[#2A2A2A] rounded-full flex items-center justify-center text-[#2383E2] font-bold">
                    02
                  </div>
                  <div className="hidden md:block absolute top-1/2 left-full w-[calc(100%+2rem)] h-px bg-[#2A2A2A]"></div>
                </div>
              </div>
              <h3 className="font-semibold text-white mb-2">AI Analysis</h3>
              <p className="text-sm text-[#6B6B6B]">Our engine extracts design patterns automatically</p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="w-12 h-12 bg-[#1A1A1A] border border-[#2A2A2A] rounded-full flex items-center justify-center text-[#2383E2] font-bold">
                  03
                </div>
              </div>
              <h3 className="font-semibold text-white mb-2">Download PDF</h3>
              <p className="text-sm text-[#6B6B6B]">Get a professional style guide document</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-white text-center mb-4">Everything You Need</h2>
          <p className="text-[#A0A0A0] text-center mb-16 max-w-2xl mx-auto">
            Our AI analyzes every aspect of a website&apos;s design system and documents it professionally
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Color Extraction */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Color Extraction</h3>
              <p className="text-sm text-[#6B6B6B]">Automatically detects and organizes your color palette with hex, RGB values, and semantic roles.</p>
            </div>

            {/* Typography Analysis */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Typography Analysis</h3>
              <p className="text-sm text-[#6B6B6B]">Identifies font families, sizes, weights, and builds a comprehensive type scale.</p>
            </div>

            {/* Component Detection */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Component Detection</h3>
              <p className="text-sm text-[#6B6B6B]">Detects common patterns, forms, and navigation patterns used across your site.</p>
            </div>

            {/* Accessibility Audit */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Accessibility Audit</h3>
              <p className="text-sm text-[#6B6B6B]">Evaluates color contrast ratios and provides WCAG compliance documentation.</p>
            </div>

            {/* Professional PDF */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Professional PDF</h3>
              <p className="text-sm text-[#6B6B6B]">Generates a beautifully formatted, 18-page style guide ready for your team.</p>
            </div>

            {/* Instant Results */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6 hover:border-[#333] transition-colors">
              <div className="w-10 h-10 bg-[#2383E2]/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-[#2383E2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">Instant Results</h3>
              <p className="text-sm text-[#6B6B6B]">Complete analysis and PDF generation in under 60 seconds.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Professional PDF Output Section */}
      <section className="py-20 bg-[#0A0A0A]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-4">Professional PDF Output</h2>
              <p className="text-[#A0A0A0] mb-8">
                Every style guide includes comprehensive documentation following
                industry-standard structure, ready to share with your team or clients.
              </p>

              <ul className="space-y-3">
                {[
                  'Cover page with brand colors',
                  'Table of contents for easy navigation',
                  'Color palette with hex, RGB, CMYK',
                  'Typography scale and font specifications',
                  'UI component documentation',
                  'Layout and grid system specs',
                  'Accessibility compliance report',
                  'Resource links and changelog'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm text-[#A0A0A0]">
                    <svg className="w-4 h-4 text-[#22C55E] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* PDF Preview Mock */}
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-6">
              <div className="bg-white rounded-lg p-4 shadow-lg">
                <div className="text-xs text-gray-500 mb-1">Brand Style Guide</div>
                <div className="text-sm font-bold text-gray-800 mb-4">Company Name</div>
                <div className="h-16 bg-gradient-to-r from-gray-800 to-gray-600 rounded mb-3"></div>
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
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Create Your Style Guide?</h2>
          <p className="text-[#A0A0A0] mb-8">
            Join designers and developers who use our tool to document design systems
            quickly and professionally.
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="h-12 px-8 bg-[#2383E2] hover:bg-[#1a6bc2] text-white font-medium rounded-lg transition-colors"
          >
            Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1A1A1A] py-8">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-[#6B6B6B]">
            <div className="w-6 h-6 bg-[#2383E2] rounded flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            Style Guide Generator
          </div>
          <div className="text-sm text-[#6B6B6B]">
            Made with <span className="text-[#EF4444]">&#9829;</span> by Tom Panos
          </div>
        </div>
      </footer>
    </div>
  );
}
