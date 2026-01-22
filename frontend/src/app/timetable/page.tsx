'use client';

import { Suspense } from 'react';
import TimetablePageContent from './page-content';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function TimetablePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <TimetablePageContent />
    </Suspense>
  );
}
