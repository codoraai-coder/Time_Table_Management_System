'use client';

import { useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ErrorMessage from '@/components/ui/ErrorMessage';
import { triggerSolve, getSolveStatus } from '@/lib/api/solve';
import { SolveResponse } from '@/types/api';

const STATUS_MESSAGES = {
  queued: 'Your job is queued and waiting to be processed...',
  running: 'Solving the timetable constraints...',
  completed: 'Timetable generated successfully!',
  failed: 'Failed to generate timetable. Please try again.',
};

const STATUS_ICONS = {
  queued: '⏳',
  running: '⚙️',
  completed: '✓',
  failed: '✕',
};

export default function GenerationPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const uploadId = searchParams.get('upload_id');

  const [solveResponse, setSolveResponse] = useState<SolveResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasStarted, setHasStarted] = useState(false);

  // Start solver
  const handleStartSolve = async () => {
    if (!uploadId) {
      setError('No upload ID provided.');
      return;
    }

    setIsLoading(true);
    setError('');
    setHasStarted(true);

    try {
      const response = await triggerSolve(uploadId);
      setSolveResponse(response);

      if (response.status === 'completed') {
        setTimeout(() => {
          router.push(`/timetable?upload_id=${uploadId}`);
        }, 2000);
      } else if (response.status !== 'failed') {
        // Poll for status updates
        pollSolveStatus(response.job_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start solver');
      setIsLoading(false);
    }
  };

  // Poll for solver status
  const pollSolveStatus = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await getSolveStatus(jobId);
        setSolveResponse(status);

        if (status.status === 'completed') {
          clearInterval(interval);
          setIsLoading(false);
          setTimeout(() => {
            router.push(`/timetable?upload_id=${uploadId}`);
          }, 2000);
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setIsLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setError(err instanceof Error ? err.message : 'Failed to check status');
        setIsLoading(false);
      }
    }, 2000); // Poll every 2 seconds
  };

  if (!uploadId) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <ErrorMessage message="No upload ID provided. Please upload files first." />
          <div className="mt-8">
            <Link href="/upload">
              <Button>← Back to Upload</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-900/20 dark:to-purple-900/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-16 text-center">
          <div className="inline-block mb-6">
            <span className="text-6xl animate-bounce">⚙️</span>
          </div>
          <h1 className="text-6xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Generate Timetable
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Use intelligent constraint solving to create an optimized timetable.
          </p>
        </div>

        {/* Main Content */}
        {!hasStarted && (
          <>
            {/* Start Button */}
            <div className="flex gap-4">
              <Button
                size="lg"
                onClick={handleStartSolve}
                disabled={isLoading}
                isLoading={isLoading}
                className="flex-1"
              >
                {isLoading ? 'Starting...' : 'Start Generation'}
              </Button>
              <Link href={`/validation?upload_id=${uploadId}`} className="flex-1">
                <Button variant="secondary" size="lg" className="w-full">
                  ← Back to Validation
                </Button>
              </Link>
            </div>
          </>
        )}

        {/* Status Section */}
        {hasStarted && solveResponse && (
          <div className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 rounded-3xl border-2 border-gradient border-indigo-200 dark:border-indigo-800 p-16 text-center shadow-2xl">
            <div className="mb-8">
              <div className="text-7xl mb-6 inline-block animate-bounce">
                {STATUS_ICONS[solveResponse.status as keyof typeof STATUS_ICONS]}
              </div>
              <h2 className="text-4xl font-black text-gray-900 dark:text-white mb-4">
                {solveResponse.status === 'completed'
                  ? '✨ Timetable Generated!'
                  : '⏳ Generating Timetable...'}
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed">
                {STATUS_MESSAGES[solveResponse.status as keyof typeof STATUS_MESSAGES]}
              </p>
            </div>

            {/* Progress Indicator */}
            {solveResponse.status !== 'completed' && solveResponse.status !== 'failed' && (
              <div className="mb-8">
                <div className="flex justify-center mb-4">
                  <LoadingSpinner />
                </div>
                {solveResponse.progress !== undefined && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${solveResponse.progress}%` }}
                    ></div>
                  </div>
                )}
              </div>
            )}

            {/* Job ID */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-8">
              <p className="text-sm text-gray-600 dark:text-gray-400">Job ID</p>
              <code className="font-mono text-gray-900 dark:text-white break-all">
                {solveResponse.job_id}
              </code>
            </div>

            {/* Error Display */}
            {solveResponse.status === 'failed' && (
              <div className="mb-8">
                <ErrorMessage message={solveResponse.message || 'Generation failed'} />
              </div>
            )}

            {/* Action Buttons */}
            {solveResponse.status === 'completed' && (
              <div className="flex gap-4">
                <Link href={`/timetable?upload_id=${uploadId}`} className="flex-1">
                  <Button size="lg" className="w-full">
                    View Timetable →
                  </Button>
                </Link>
                <Link href="/upload" className="flex-1">
                  <Button variant="secondary" size="lg" className="w-full">
                    Upload New Data
                  </Button>
                </Link>
              </div>
            )}

            {solveResponse.status === 'failed' && (
              <div className="flex gap-4">
                <Button
                  size="lg"
                  onClick={handleStartSolve}
                  className="flex-1"
                >
                  Try Again
                </Button>
                <Link href={`/validation?upload_id=${uploadId}`} className="flex-1">
                  <Button variant="secondary" size="lg" className="w-full">
                    ← Back to Validation
                  </Button>
                </Link>
              </div>
            )}
          </div>
        )}

        {error && <ErrorMessage message={error} />}
      </div>
    </div>
  );
}
