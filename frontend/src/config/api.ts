// API Configuration

export const API_CONFIG = {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    endpoints: {
        upload: '/api/upload',
        validation: '/api/validation',
        solve: '/api/solve',
        timetable: '/api/timetable',
    },
};
