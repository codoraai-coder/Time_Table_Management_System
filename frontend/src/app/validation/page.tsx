'use client';

import { Suspense } from 'react';
import ValidationPageContent from './page-content';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function ValidationPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <ValidationPageContent />
    </Suspense>
  );
}

