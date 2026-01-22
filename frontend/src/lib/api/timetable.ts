// Timetable API Service

import { apiClient } from './client';
import { API_CONFIG } from '@/config/api';
import { TimetableData } from '@/types/api';

export async function getTimetable(uploadId: string): Promise<TimetableData> {
    return apiClient.get<TimetableData>(
        `${API_CONFIG.endpoints.timetable}/${uploadId}`
    );
}
