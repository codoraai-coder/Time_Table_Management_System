// Base API Client

import { API_CONFIG } from '@/config/api';
import { ApiError } from '@/types/api';

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_CONFIG.baseUrl;
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        if (!response.ok) {
            const errorData: ApiError = await response.json().catch(() => ({
                error: 'An unexpected error occurred',
            }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        return response.json();
    }

    async get<T>(endpoint: string): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        return this.handleResponse<T>(response);
    }

    async post<T>(endpoint: string, data?: unknown): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: data ? JSON.stringify(data) : undefined,
        });
        return this.handleResponse<T>(response);
    }

    async uploadFiles<T>(endpoint: string, files: File[]): Promise<T> {
        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files', file);
        });

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            body: formData,
        });
        return this.handleResponse<T>(response);
    }
}

export const apiClient = new ApiClient();
