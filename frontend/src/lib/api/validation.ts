// Validation API Service

import { apiClient } from './client';
import { API_CONFIG } from '@/config/api';
import { ValidationResponse } from '@/types/api';

export async function getValidation(uploadId: string): Promise<ValidationResponse> {
    return apiClient.get<ValidationResponse>(
        `${API_CONFIG.endpoints.validation}/${uploadId}`
    );
}
