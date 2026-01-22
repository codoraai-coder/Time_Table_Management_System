// Solve API Service

import { apiClient } from './client';
import { API_CONFIG } from '@/config/api';
import { SolveRequest, SolveResponse } from '@/types/api';

export async function triggerSolve(uploadId: string): Promise<SolveResponse> {
    const request: SolveRequest = { upload_id: uploadId };
    return apiClient.post<SolveResponse>(API_CONFIG.endpoints.solve, request);
}

export async function getSolveStatus(jobId: string): Promise<SolveResponse> {
    return apiClient.get<SolveResponse>(`${API_CONFIG.endpoints.solve}/${jobId}`);
}
