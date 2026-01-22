'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ErrorMessage from '@/components/ui/ErrorMessage';
import { getTimetable } from '@/lib/api/timetable';
import { TimetableData, TimeSlotData } from '@/types/api';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const TIME_SLOTS = [
  '08:00-09:00',
  '09:00-10:00',
  '10:00-11:00',
  '11:00-12:00',
  '12:00-01:00',
  '01:00-02:00',
  '02:00-03:00',
  '03:00-04:00',
];

export default function TimetablePageContent() {
  const searchParams = useSearchParams();
  const uploadId = searchParams.get('upload_id');

  const [timetable, setTimetable] = useState<TimetableData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSlot, setSelectedSlot] = useState<TimeSlotData | null>(null);

  useEffect(() => {
    if (!uploadId) {
      setError('No upload ID provided.');
      setIsLoading(false);
      return;
    }

    const fetchTimetable = async () => {
      try {
        setIsLoading(true);
        setError('');
        const data = await getTimetable(uploadId);
        setTimetable(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch timetable');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTimetable();
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
        <div className="max-w-6xl mx-auto">
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

  if (!timetable) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-600 dark:text-gray-400">No timetable data available.</p>
        </div>
      </div>
    );
  }

  // Build a 2D grid: days × time slots
  const grid: (TimeSlotData | null)[][] = DAYS.map(() => Array(TIME_SLOTS.length).fill(null));

  timetable.slots.forEach((slot) => {
    const dayIndex = DAYS.indexOf(slot.day);
    const timeIndex = TIME_SLOTS.indexOf(
      `${slot.start_time}-${slot.end_time}`
    );

    if (dayIndex !== -1 && timeIndex !== -1) {
      grid[dayIndex][timeIndex] = slot;
    }
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Generated Timetable
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
            Upload ID: <code className="font-mono">{uploadId}</code>
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Generated on {new Date(timetable.generated_at).toLocaleString()}
          </p>
        </div>

        {/* Calendar Grid */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-800">
                  <th className="p-4 text-left font-semibold text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 w-24">
                    Time
                  </th>
                  {DAYS.map((day) => (
                    <th
                      key={day}
                      className="p-4 text-center font-semibold text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800"
                    >
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((timeSlot, timeIndex) => (
                  <tr key={timeSlot} className="border-b border-gray-200 dark:border-gray-800 last:border-0">
                    <td className="p-4 font-mono text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-800">
                      {timeSlot}
                    </td>
                    {DAYS.map((day, dayIndex) => {
                      const slot = grid[dayIndex][timeIndex];
                      return (
                        <td
                          key={`${day}-${timeSlot}`}
                          className="p-4 text-center border-r border-gray-200 dark:border-gray-800 last:border-0 cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                          onClick={() => slot && setSelectedSlot(slot)}
                        >
                          {slot ? (
                            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg p-3">
                              <p className="font-bold text-sm">{slot.course_code}</p>
                              <p className="text-xs opacity-90">{slot.section}</p>
                              <p className="text-xs opacity-75">{slot.room}</p>
                              <p className="text-xs opacity-75 truncate">{slot.faculty}</p>
                            </div>
                          ) : (
                            <div className="text-gray-300 dark:text-gray-600 text-sm">—</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-4">
            Legend
          </h3>
          <div className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
            <p>• Click on any class slot to view detailed information</p>
            <p>• This timetable is read-only and generated by the constraint solver</p>
            <p>• All classes are scheduled respecting all constraints from your data</p>
          </div>
        </div>

        {/* Slot Details Modal */}
        {selectedSlot && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-900 rounded-2xl max-w-md w-full p-8">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Class Details
                </h2>
                <button
                  onClick={() => setSelectedSlot(null)}
                  className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-2xl"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Course Code</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.course_code}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Course Name</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.course_name}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Section</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.section}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Faculty</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.faculty}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Room</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.room}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Schedule</p>
                  <p className="font-bold text-gray-900 dark:text-white">
                    {selectedSlot.day}, {selectedSlot.start_time} - {selectedSlot.end_time}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedSlot(null)}
                className="w-full mt-8 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Statistics */}
        {timetable.slots.length > 0 && (
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Classes</p>
              <p className="text-3xl font-bold text-indigo-600">{timetable.slots.length}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Unique Courses</p>
              <p className="text-3xl font-bold text-purple-600">
                {new Set(timetable.slots.map((s) => s.course_code)).size}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Unique Sections</p>
              <p className="text-3xl font-bold text-green-600">
                {new Set(timetable.slots.map((s) => s.section)).size}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rooms Used</p>
              <p className="text-3xl font-bold text-blue-600">
                {new Set(timetable.slots.map((s) => s.room)).size}
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mt-12">
          <Link href="/upload" className="flex-1">
            <Button size="lg" className="w-full">
              Create New Timetable
            </Button>
          </Link>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => window.print()}
            className="flex-1"
          >
            Print Timetable
          </Button>
        </div>
      </div>
    </div>
  );
}
