// Upload API Service

import { apiClient } from './client';
import { API_CONFIG } from '@/config/api';
import { UploadResponse } from '@/types/api';

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
    return apiClient.uploadFiles<UploadResponse>(
        API_CONFIG.endpoints.upload,
        files
    );
}
