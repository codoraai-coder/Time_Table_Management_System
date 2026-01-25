'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import FileUploader from '@/components/upload/FileUploader';
import Button from '@/components/ui/Button';
import ErrorMessage from '@/components/ui/ErrorMessage';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { uploadFiles } from '@/lib/api/upload';
import CsvPreview from '@/components/upload/CsvPreview';
import MockTimetable from '@/components/upload/MockTimetable';

const REQUIRED_FILES = [
  { name: 'sections.csv', type: 'CSV', icon: '👥', desc: 'Class sections & capacities' },
  { name: 'faculty.csv', type: 'CSV', icon: '👨‍🏫', desc: 'Professor details' },
  { name: 'courses.csv', type: 'CSV', icon: '📚', desc: 'Course catalog' },
  { name: 'rooms.csv', type: 'CSV', icon: '🏫', desc: 'Available classrooms' },
  { name: 'faculty_course_map.csv', type: 'CSV', icon: '🔗', desc: 'Who teaches what' },
  { name: 'time_config.json', type: 'JSON', icon: '⚙️', desc: 'Time slots & constraints' },
];

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadId, setUploadId] = useState('');
  const [validationResults, setValidationResults] = useState<any>(null); // To store backend validation/mock results
  const router = useRouter();

  const handleFilesChange = (newFiles: File[]) => {
    // Enforce single file selection for this flow (as per plan: Zip preferred, or single CSV)
    // The FileUploader might return multiple if configured, but we'll take the latest or force single in props.
    // For now, let's just take the first one if multiple are passed, effectively treating it as single mode.
    if (newFiles.length > 0) {
      setFiles([newFiles[0]]);
    } else {
      setFiles([]);
    }
    setError('');
    setValidationResults(null);
    setUploadId('');
  };

  const activeFile = files[0];
  const isZip = activeFile?.name.endsWith('.zip');
  const isCsv = activeFile?.name.endsWith('.csv');
  const isOther = activeFile && !isZip && !isCsv;

  const handleSubmit = async () => {
    if (!activeFile) {
      setError('Please select a file');
      return;
    }

    if (isOther) {
      // Mock flow for other files - no backend call needed for visual demo as per requirements
      return;
    }

    if (isCsv) {
      // purely frontend preview, maybe upload later? 
      // Plan says: "If .csv: Parse and display". 
      // We do that immediately upon selection in the render, so "Upload" might just be a no-op or "Validation" simulation.
      // Let's treat "Upload" for CSV as "Process this file" -> which just shows it's valid.
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setUploadId('mock-csv-upload-id');
      }, 1000);
      return;
    }

    // ZIP Flow - Real Backend Call
    setIsLoading(true);
    setError('');
    setUploadId('');
    setValidationResults(null);

    try {
      const response = await uploadFiles(files); // helper sends file[]

      if (response.status === 'success' && response.upload_id) {
        setUploadId(response.upload_id);
        // Store detailed validation results from backend if available
        if (response.details) {
          setValidationResults(response.details);
        }
      } else {
        setError(response.message || 'Upload failed. Please try again.');
        if (response.details) {
          setValidationResults(response.details); // Show errors if structured
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 space-y-4">
          <h1 className="text-4xl md:text-5xl font-black text-gray-900 dark:text-white tracking-tight">
            Upload Data
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Upload your institution's data to generate optimized timetables.
            <br />
            <span className="text-indigo-600 dark:text-indigo-400 font-medium">.zip archives</span> are recommended.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Upload Area & Status */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upload Card */}
            <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-xl shadow-indigo-500/5 border border-indigo-100 dark:border-indigo-900/20 p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <svg className="w-32 h-32 text-indigo-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" /></svg>
              </div>

              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 text-lg">📁</span>
                Select Data File
              </h2>

              <FileUploader
                onFilesSelected={handleFilesChange}
                acceptedTypes={['.zip', '.csv', '.json', '.txt', '.png', '.jpg']} // Broaden for demo (MockTimetable)
                maxFiles={1}
              />

              {/* Action Buttons */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4">
                <Button
                  size="lg"
                  onClick={handleSubmit}
                  disabled={!activeFile || isLoading}
                  isLoading={isLoading}
                  className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/20"
                >
                  {isLoading ? 'Processing...' : (isOther ? 'View Mock' : 'Upload & Validate')}
                </Button>
                {files.length > 0 && (
                  <Button
                    variant="secondary"
                    size="lg"
                    onClick={() => { setFiles([]); setError(''); setValidationResults(null); }}
                    disabled={isLoading}
                    className="flex-1"
                  >
                    Clear Selection
                  </Button>
                )}
              </div>
            </div>

            {/* Validation Results / Status Messages */}
            {error && (
              <div className="animate-fade-in-up">
                <ErrorMessage message={error} />
              </div>
            )}

            {uploadId && !error && (
              <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800 rounded-2xl p-6 animate-fade-in-up">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-800/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-xl">✅</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-emerald-900 dark:text-emerald-100">Upload Successful</h3>
                    <div className="mt-1 text-emerald-700 dark:text-emerald-300">
                      <p>File has been uploaded and validated successfully.</p>
                      <div className="mt-2 text-xs font-mono bg-white/50 dark:bg-black/20 p-2 rounded">ID: {uploadId}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {validationResults && (
              <div className="bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-200 dark:border-indigo-800 rounded-2xl p-6 animate-fade-in-up">
                <h3 className="font-bold text-indigo-900 dark:text-indigo-200 mb-2">Validation Details</h3>
                <pre className="text-xs overflow-auto max-h-64 p-4 bg-white dark:bg-black/40 rounded-xl font-mono text-gray-700 dark:text-gray-300 border border-gray-100 dark:border-gray-800">
                  {JSON.stringify(validationResults, null, 2)}
                </pre>
              </div>
            )}


            {/* CONTENT PREVIEWS */}
            {/* 1. CSV Preview */}
            {activeFile && isCsv && (
              <div className="animate-fade-in-up">
                <CsvPreview file={activeFile} />
              </div>
            )}

            {/* 2. Mock Timetable Preview (for non-zip/non-csv) */}
            {activeFile && isOther && (
              <div className="animate-fade-in-up">
                <MockTimetable />
              </div>
            )}

          </div>

          {/* Right Column: Required Files Info */}
          <div className="lg:col-span-1">
            <div className="bg-white/60 dark:bg-gray-900/60 backdrop-blur-xl rounded-3xl border border-gray-200 dark:border-gray-800 p-6 sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">📋</span>
                Required Files
              </h3>

              <div className="space-y-3">
                {REQUIRED_FILES.map((file) => (
                  <div
                    key={file.name}
                    className="group p-4 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-800 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-xl bg-gray-50 dark:bg-gray-700 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 flex items-center justify-center text-xl transition-colors">
                        {file.icon}
                      </div>
                      <div>
                        <p className="font-bold text-gray-900 dark:text-white text-sm group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {file.desc}
                        </p>
                        <span className="inline-block mt-2 text-[10px] font-bold uppercase tracking-wider text-gray-400 border border-gray-200 dark:border-gray-700 px-1.5 py-0.5 rounded">
                          {file.type}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-2xl border border-indigo-100 dark:border-indigo-800/50">
                <p className="text-xs text-indigo-800 dark:text-indigo-300 leading-relaxed font-medium">
                  💡 <span className="font-bold">Pro Tip:</span> Zip all these files together into a single archive for faster processing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
