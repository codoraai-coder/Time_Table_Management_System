export default function MockTimetable() {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const times = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00'];

    return (
        <div className="w-full overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm bg-white dark:bg-gray-900">
            <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 border-b border-indigo-100 dark:border-indigo-800/30">
                <h3 className="font-bold text-indigo-900 dark:text-indigo-200">Generated Timetable Preview</h3>
                <p className="text-sm text-indigo-600 dark:text-indigo-400">This is a mock view of how the timetable will look.</p>
            </div>
            <div className="overflow-x-auto p-4">
                <div className="min-w-[800px] grid grid-cols-6 gap-2">
                    {/* Header Row */}
                    <div className="p-2"></div>
                    {days.map(day => (
                        <div key={day} className="p-2 font-bold text-center text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            {day}
                        </div>
                    ))}

                    {/* Time Rows */}
                    {times.map((time, i) => (
                        <>
                            <div key={time} className="p-2 font-medium text-gray-500 dark:text-gray-400 flex items-center justify-center text-sm">
                                {time}
                            </div>
                            {days.map((day, j) => (
                                <div key={`${day}-${time}`} className={`
                  p-2 rounded-lg border border-dashed border-gray-200 dark:border-gray-800 min-h-[80px]
                  ${(i + j) % 3 === 0 ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 border-solid' : ''}
                  ${(i + j) % 5 === 0 ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 border-solid' : ''}
                `}>
                                    {(i + j) % 3 === 0 && (
                                        <div className="text-xs">
                                            <div className="font-bold text-indigo-700 dark:text-indigo-300">CS-101</div>
                                            <div className="text-indigo-600 dark:text-indigo-400">Room 302</div>
                                        </div>
                                    )}
                                    {(i + j) % 5 === 0 && (
                                        <div className="text-xs">
                                            <div className="font-bold text-purple-700 dark:text-purple-300">MATH-202</div>
                                            <div className="text-purple-600 dark:text-purple-400">Room 105</div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </>
                    ))}
                </div>
            </div>
        </div>
    );
}
