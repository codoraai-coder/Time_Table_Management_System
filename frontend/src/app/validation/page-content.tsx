'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ErrorMessage from '@/components/ui/ErrorMessage';
import Card from '@/components/ui/Card';
import { getValidation } from '@/lib/api/validation';
import { ValidationResponse, ValidationMessage } from '@/types/api';

export default function ValidationPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const uploadId = searchParams.get('upload_id');

  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!uploadId) {
      setError('No upload ID provided. Please upload files first.');
      setIsLoading(false);
      return;
    }

    const fetchValidation = async () => {
      try {
        setIsLoading(true);
        setError('');
        const data = await getValidation(uploadId);
        setValidation(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch validation results'
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchValidation();
  }, [uploadId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <ErrorMessage message={error} />
          <div className="mt-8">
            <Link href="/upload">
              <Button>← Back to Upload</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!validation) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <p className="text-gray-600 dark:text-gray-400">No validation data available.</p>
        </div>
      </div>
    );
  }

  const statusColors = {
    valid: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', icon: '✓' },
    warnings: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', icon: '⚠' },
    invalid: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', icon: '✕' },
  };

  const currentStatus = statusColors[validation.status as keyof typeof statusColors];

  const MessageItem = ({ message, type }: { message: ValidationMessage; type: 'error' | 'warning' | 'suggestion' }) => {
    const typeStyles = {
      error: 'border-l-4 border-l-red-500 bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20',
      warning: 'border-l-4 border-l-yellow-500 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20',
      suggestion: 'border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20',
    };

    const typeIcons = {
      error: '🔴',
      warning: '⚠️',
      suggestion: 'ℹ️',
    };

    return (
      <div className={`p-5 rounded-xl shadow-md hover:shadow-lg transition-shadow ${typeStyles[type]}`}>
        <div className="flex items-start gap-4">
          <span className="text-2xl flex-shrink-0">{typeIcons[type]}</span>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-lg text-gray-900 dark:text-white">
              {message.message}
            </p>
            {message.code && (
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-2 font-mono bg-black/5 dark:bg-white/5 px-3 py-1 rounded inline-block">
                Code: {message.code}
              </p>
            )}
            <div className="text-xs text-gray-600 dark:text-gray-400 mt-3 space-y-1 grid grid-cols-2 gap-2">
              {message.file && <p>📄 File: {message.file}</p>}
              {message.line && <p>📍 Line: {message.line}</p>}
              {message.field && <p>🏷️ Field: {message.field}</p>}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-900/20 dark:to-purple-900/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-16 text-center">
          <div className="inline-block mb-6">
            <span className="text-6xl">✅</span>
          </div>
          <h1 className="text-6xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Validation Results
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Upload ID: <code className="font-mono font-semibold text-indigo-600 dark:text-indigo-400">{uploadId}</code>
          </p>
        </div>

        {/* Status Badge */}
        <div className={`rounded-3xl p-8 mb-12 border-2 shadow-2xl ${
          validation.status === 'valid'
            ? 'border-green-400 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30'
            : validation.status === 'warnings'
              ? 'border-yellow-400 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/30 dark:to-amber-900/30'
              : 'border-red-400 bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/30 dark:to-rose-900/30'
        }`}>
          <div className="flex items-start gap-5">
            <span className="text-5xl animate-bounce">{currentStatus.icon}</span>
            <div className="flex-1">
              <h2 className={`text-3xl font-black mb-3 ${currentStatus.text}`}>
                {validation.status === 'valid'
                  ? '✓ Validation Passed'
                  : validation.status === 'warnings'
                    ? '⚠ Validation Passed with Warnings'
                    : '✕ Validation Failed'}
              </h2>
              <p className={`text-lg ${currentStatus.text}`}>
                {validation.errors.length === 0 && validation.warnings.length === 0
                  ? 'All files are correctly formatted and ready for timetable generation.'
                  : `${validation.errors.length} error(s), ${validation.warnings.length} warning(s), ${validation.suggestions.length} suggestion(s)`}
              </p>
            </div>
          </div>
        </div>

        {/* Errors */}
        {validation.errors.length > 0 && (
          <Card title={`Errors (${validation.errors.length})`} className="mb-8">
            <div className="space-y-4">
              {validation.errors.map((error, idx) => (
                <MessageItem key={idx} message={error} type="error" />
              ))}
            </div>
          </Card>
        )}

        {/* Warnings */}
        {validation.warnings.length > 0 && (
          <Card title={`Warnings (${validation.warnings.length})`} className="mb-8">
            <div className="space-y-4">
              {validation.warnings.map((warning, idx) => (
                <MessageItem key={idx} message={warning} type="warning" />
              ))}
            </div>
          </Card>
        )}

        {/* Suggestions */}
        {validation.suggestions.length > 0 && (
          <Card title={`Suggestions (${validation.suggestions.length})`} className="mb-8">
            <div className="space-y-4">
              {validation.suggestions.map((suggestion, idx) => (
                <MessageItem key={idx} message={suggestion} type="suggestion" />
              ))}
            </div>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mt-12">
          {validation.status !== 'invalid' && (
            <Link href={`/generation?upload_id=${uploadId}`} className="flex-1">
              <Button size="lg" className="w-full">
                Generate Timetable →
              </Button>
            </Link>
          )}
          <Link href="/upload" className="flex-1">
            <Button variant="secondary" size="lg" className="w-full">
              Upload Different Files
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
