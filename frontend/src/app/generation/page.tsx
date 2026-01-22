'use client';

import { Suspense } from 'react';
import GenerationPageContent from './page-content';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function GenerationPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <GenerationPageContent />
    </Suspense>
  );
}

