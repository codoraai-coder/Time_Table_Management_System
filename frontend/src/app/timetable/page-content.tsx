'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import ErrorMessage from '@/components/ui/ErrorMessage';
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

interface TimetablePageContentProps {
  initialTimetable: TimetableData | null;
  initialError: string;
  uploadId: string;
}

export default function TimetablePageContent({
  initialTimetable,
  initialError,
  uploadId
}: TimetablePageContentProps) {
  const [selectedSlot, setSelectedSlot] = useState<TimeSlotData | null>(null);

  // Filters state
  const [selectedSection, setSelectedSection] = useState<string>('All');
  const [selectedFaculty, setSelectedFaculty] = useState<string>('All');
  const [selectedRoom, setSelectedRoom] = useState<string>('All');

  // Extract unique values for filters
  const filterOptions = useMemo(() => {
    if (!initialTimetable) return { sections: [], faculties: [], rooms: [] };

    const sections = Array.from(new Set(initialTimetable.slots.map(s => s.section))).sort();
    const faculties = Array.from(new Set(initialTimetable.slots.map(s => s.faculty))).sort();
    const rooms = Array.from(new Set(initialTimetable.slots.map(s => s.room))).sort();

    return { sections, faculties, rooms };
  }, [initialTimetable]);

  // Filter slots
  const filteredSlots = useMemo(() => {
    if (!initialTimetable) return [];

    return initialTimetable.slots.filter(slot => {
      if (selectedSection !== 'All' && slot.section !== selectedSection) return false;
      if (selectedFaculty !== 'All' && slot.faculty !== selectedFaculty) return false;
      if (selectedRoom !== 'All' && slot.room !== selectedRoom) return false;
      return true;
    });
  }, [initialTimetable, selectedSection, selectedFaculty, selectedRoom]);

  if (initialError) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <ErrorMessage message={initialError} />
          <div className="mt-8">
            <Link href="/upload">
              <Button>← Back to Upload</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!initialTimetable) {
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

  filteredSlots.forEach((slot) => {
    const dayIndex = DAYS.indexOf(slot.day);
    const timeIndex = TIME_SLOTS.indexOf(
      `${slot.start_time}-${slot.end_time}`
    );

    if (dayIndex !== -1 && timeIndex !== -1) {
      // Check for collision in visualization (if multiple classes match filters in same slot)
      // For now, we just overwrite, or we could handle multiple items per cell.
      // Given the constraints likely prevent collisions, overwriting might be visually safe for a valid schedule.
      // However, if filtering shows "All", there WILL be multiple classes per slot (e.g. different rooms).
      // We should probably show a count or list if multiple.
      // BUT, the requirements say "Each cell should show assignment details".
      // If we are viewing the "Master Timetable" (all classes), a single cell in a grid (Day x Time) naturally contains MANY classes happening simultaneously in different rooms.
      // A standard grid view usually filters by something (like Room or Faculty) to make sense.
      // When viewing ALL, displaying everything in one cell is impossible.
      // I will implement logic to render "Multiple Classes" or similar if collision, unless a specific filter narrows it down.
      // OR, better yet, just show the first one and indicate there are more?
      // Actually, for the "Master Timetable", typically one pivots by Room or Faculty.
      // If the user views EVERYTHING, it's a mess.
      // I'll stick to the current request: "Display timetable in a grid view".
      // I will attempt to show the first match and maybe a "+X more" badge if there are overlaps in the view.

      if (grid[dayIndex][timeIndex] === null) {
        grid[dayIndex][timeIndex] = slot;
      } else {
        // Mark as collision/multiple? 
        // We can't change the type of grid easily without changing usages.
        // Let's rely on the user filtering to see specific schedules.
        // But I'll add a visual indicator if I can.
        // For now, let's just let it overwrite, but ideally we should handle this.
        // Re-reading requirements: "Filtering updates the grid view dynamically".
        // If no filter is selected (All), showing a grid by Day/Time is problematic because many classes happen at 9am.
        // I will proceed with logic that populates the grid, but be aware that without filters, it might show arbitrary class for that slot.
        // Let's add a small indicator to the cell if there's an overlap?
        // I will change grid to store an array of slots.
      }
    }
  });

  // Re-thinking grid structure for display
  const gridCells: (TimeSlotData[])[][] = DAYS.map(() => Array(TIME_SLOTS.length).fill([]));

  filteredSlots.forEach((slot) => {
    const dayIndex = DAYS.indexOf(slot.day);
    const timeIndex = TIME_SLOTS.indexOf(`${slot.start_time}-${slot.end_time}`);
    if (dayIndex !== -1 && timeIndex !== -1) {
      gridCells[dayIndex][timeIndex] = [...gridCells[dayIndex][timeIndex], slot];
    }
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Generated Timetable
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
            Upload ID: <code className="font-mono">{uploadId}</code>
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Generated on {new Date(initialTimetable.generated_at).toLocaleString()}
          </p>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Section</label>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="w-full rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2.5 border"
            >
              <option value="All">All Sections</option>
              {filterOptions.sections.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Faculty</label>
            <select
              value={selectedFaculty}
              onChange={(e) => setSelectedFaculty(e.target.value)}
              className="w-full rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2.5 border"
            >
              <option value="All">All Faculty</option>
              {filterOptions.faculties.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Room</label>
            <select
              value={selectedRoom}
              onChange={(e) => setSelectedRoom(e.target.value)}
              className="w-full rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2.5 border"
            >
              <option value="All">All Rooms</option>
              {filterOptions.rooms.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
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
                      const slots = gridCells[dayIndex][timeIndex];
                      const slot = slots[0]; // Display first match
                      const count = slots.length;

                      return (
                        <td
                          key={`${day}-${timeSlot}`}
                          className="p-4 text-center border-r border-gray-200 dark:border-gray-800 last:border-0 cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                          onClick={() => slot && setSelectedSlot(slot)} // TODO: Handle showing multiple? For now just show first.
                        >
                          {slot ? (
                            <div className={`relative bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg p-3 ${count > 1 ? 'ring-2 ring-offset-2 ring-indigo-500' : ''}`}>
                              {count > 1 && (
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-sm">
                                  +{count - 1}
                                </span>
                              )}
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
            <p>• Use filters above to narrow down the view (e.g. by Room or Faculty)</p>
            <p>• If multiple classes are scheduled in the same slot (when viewing All), a badge (e.g. +1) will appear.</p>
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
        {filteredSlots.length > 0 && (
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Visible Classes</p>
              <p className="text-3xl font-bold text-indigo-600">{filteredSlots.length}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Unique Courses</p>
              <p className="text-3xl font-bold text-purple-600">
                {new Set(filteredSlots.map((s) => s.course_code)).size}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Unique Sections</p>
              <p className="text-3xl font-bold text-green-600">
                {new Set(filteredSlots.map((s) => s.section)).size}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rooms Used</p>
              <p className="text-3xl font-bold text-blue-600">
                {new Set(filteredSlots.map((s) => s.room)).size}
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
