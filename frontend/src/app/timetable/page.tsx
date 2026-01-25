import { Suspense } from 'react';
import TimetablePageContent from './page-content';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { getTimetable } from '@/lib/api/timetable';

interface PageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function TimetablePage({ searchParams }: PageProps) {
  const resolvedSearchParams = await searchParams;
  const uploadId = resolvedSearchParams?.upload_id as string | undefined;

  let initialTimetable = null;
  let initialError = '';

  if (uploadId) {
    try {
      initialTimetable = await getTimetable(uploadId);
    } catch (error) {
       console.error('Error fetching timetable:', error);
       initialError = error instanceof Error ? error.message : 'Failed to fetch timetable';
    }
  } else {
      initialError = 'No upload ID provided.';
  }

  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <TimetablePageContent 
        initialTimetable={initialTimetable} 
        initialError={initialError}
        uploadId={uploadId || ''}
      />
    </Suspense>
  );
}
