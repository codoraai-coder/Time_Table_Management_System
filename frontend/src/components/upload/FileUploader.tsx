'use client';

import { useState, useCallback } from 'react';
import { Button, Card } from '@/components/ui';

interface FileUploaderProps {
  onFilesSelected: (files: File[]) => void;
  acceptedTypes?: string[];
  maxFiles?: number;
  disabled?: boolean;
}

const defaultAcceptedTypes = ['.csv', '.json'];

export default function FileUploader({
  onFilesSelected,
  acceptedTypes = defaultAcceptedTypes,
  maxFiles = 10,
  disabled = false,
}: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) setIsDragOver(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (disabled) return;

      const files = Array.from(e.dataTransfer.files).filter((file) =>
        acceptedTypes.some(
          (type) =>
            file.name.endsWith(type) ||
            file.type === type.replace('.', 'application/')
        )
      );

      if (files.length > 0) {
        const newFiles = [...selectedFiles, ...files].slice(0, maxFiles);
        setSelectedFiles(newFiles);
        onFilesSelected(newFiles);
      }
    },
    [acceptedTypes, disabled, maxFiles, onFilesSelected, selectedFiles]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const files = Array.from(e.target.files);
        const newFiles = [...selectedFiles, ...files].slice(0, maxFiles);
        setSelectedFiles(newFiles);
        onFilesSelected(newFiles);
      }
    },
    [maxFiles, onFilesSelected, selectedFiles]
  );

  const removeFile = useCallback(
    (index: number) => {
      const newFiles = selectedFiles.filter((_, i) => i !== index);
      setSelectedFiles(newFiles);
      onFilesSelected(newFiles);
    },
    [onFilesSelected, selectedFiles]
  );

  const clearFiles = useCallback(() => {
    setSelectedFiles([]);
    onFilesSelected([]);
  }, [onFilesSelected]);

  return (
    <div className="space-y-8">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative rounded-3xl border-3 border-dashed p-16 text-center transition-all duration-300 ${
          isDragOver
            ? 'border-indigo-500 bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40 shadow-2xl'
            : disabled
            ? 'border-gray-200 bg-gray-50 dark:bg-gray-800 cursor-not-allowed'
            : 'border-indigo-300 dark:border-indigo-700 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 hover:border-indigo-500 hover:shadow-xl cursor-pointer'
        }`}
      >
        <input
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        <div className="space-y-4">
          <div className="mx-auto w-20 h-20 bg-gradient-to-br from-indigo-200 to-purple-200 dark:from-indigo-900/60 dark:to-purple-900/60 rounded-3xl flex items-center justify-center shadow-lg animate-bounce">
            <svg
              className="w-10 h-10 text-indigo-600 dark:text-indigo-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          <div>
            <p className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Drop files here or click to browse
            </p>
            <p className="text-base text-gray-600 dark:text-gray-400 mt-3">
              Supported:{' '}
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {acceptedTypes.join(', ')}
              </span>{' '}
              • Max {maxFiles} files
            </p>
          </div>
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <Card variant="glass" className="!p-6 border-l-4 border-l-green-500">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="text-2xl animate-pulse">✅</div>
              <p className="text-lg font-semibold">Selected Files</p>
            </div>
            <Button onClick={clearFiles} variant="destructive" size="sm">
              Clear All
            </Button>
          </div>

          <ul className="space-y-3">
            {selectedFiles.map((file, index) => (
              <li
                key={index}
                className="flex items-center justify-between p-3 rounded-xl bg-white/60 dark:bg-gray-800/60 shadow"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>

                <button
                  onClick={() => removeFile(index)}
                  className="ml-2 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
