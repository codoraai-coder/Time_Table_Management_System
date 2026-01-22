'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import FileUploader from '@/components/upload/FileUploader';
import Button from '@/components/ui/Button';
import ErrorMessage from '@/components/ui/ErrorMessage';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { uploadFiles } from '@/lib/api/upload';

const REQUIRED_FILES = [
  { name: 'sections.csv', type: 'CSV' },
  { name: 'faculty.csv', type: 'CSV' },
  { name: 'courses.csv', type: 'CSV' },
  { name: 'rooms.csv', type: 'CSV' },
  { name: 'faculty_course_map.csv', type: 'CSV' },
  { name: 'time_config.json', type: 'JSON' },
];

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadId, setUploadId] = useState('');
  const router = useRouter();

  const handleFilesChange = (newFiles: File[]) => {
    setFiles(newFiles);
    setError('');
  };

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setIsLoading(true);
    setError('');
    setUploadId('');

    try {
      const response = await uploadFiles(files);
      
      if (response.status === 'success') {
        setUploadId(response.upload_id);
        // Automatically redirect to validation page after 2 seconds
        setTimeout(() => {
          router.push(`/validation?upload_id=${response.upload_id}`);
        }, 2000);
      } else {
        setError(response.message || 'Upload failed. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-900/20 dark:to-purple-900/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-16 text-center">
          <div className="inline-block mb-6">
            <span className="text-6xl">⏱️</span>
          </div>
          <h1 className="text-6xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Upload Your Data
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Upload all required CSV and JSON files to get started with intelligent timetable generation. 
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 p-10 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Select Files</h2>
          <FileUploader onFilesSelected={handleFilesChange} />

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
                Selected Files ({files.length})
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {files.map((file) => (
                  <div
                    key={file.name}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl border border-green-200 dark:border-green-800"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">✓</span>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {file.name}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Required Files Reference */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-2xl p-8 mb-8">
          <h3 className="text-lg font-bold text-blue-900 dark:text-blue-100 mb-6 flex items-center gap-2">
            <span>📋</span> Required Files
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {REQUIRED_FILES.map((file) => (
              <div key={file.name} className="flex items-start gap-3 p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-blue-100 dark:border-blue-800">
                <span className="text-xl">✓</span>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {file.name}
                  </p>
                  <p className="text-sm text-blue-600 dark:text-blue-400">
                    {file.type} format
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Success Message */}
        {uploadId && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-300 dark:border-green-700 rounded-2xl p-6 mb-8">
            <div className="flex items-center gap-3">
              <span className="text-3xl">✓</span>
              <div>
                <p className="text-lg font-bold text-green-900 dark:text-green-100">
                  Upload Successful!
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Upload ID: <code className="font-mono bg-green-100 dark:bg-green-900 px-2 py-1 rounded">{uploadId}</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Submit Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            size="lg"
            onClick={handleSubmit}
            disabled={files.length === 0 || isLoading}
            isLoading={isLoading}
            className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
          >
            {isLoading ? 'Uploading...' : 'Upload Files'}
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => setFiles([])}
            disabled={isLoading}
            className="flex-1"
          >
            Clear Files
          </Button>
        </div>

        {isLoading && (
          <div className="mt-8 flex justify-center">
            <LoadingSpinner />
          </div>
        )}
      </div>
    </div>
  );
}
