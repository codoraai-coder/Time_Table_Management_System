// API Types for Codora Timetable

export interface UploadResponse {
  upload_id?: string;
  status: 'success' | 'error';
  message: string;
  validation_errors?: ValidationMessage[]; // Assuming ValidationError is ValidationMessage
  details?: any; // For flexible backend validation details
}

export interface ValidationMessage {
  type: 'error' | 'warning' | 'suggestion';
  code: string;
  message: string;
  file?: string;
  line?: number;
  field?: string;
}

export interface ValidationResponse {
  upload_id: string;
  status: 'valid' | 'invalid' | 'warnings';
  errors: ValidationMessage[];
  warnings: ValidationMessage[];
  suggestions: ValidationMessage[];
}

export interface TimeSlotData {
  id: string;
  day: string;
  start_time: string;
  end_time: string;
  course_code: string;
  course_name: string;
  section: string;
  faculty: string;
  room: string;
}

export interface TimetableData {
  upload_id: string;
  generated_at: string;
  slots: TimeSlotData[];
}

export interface SolveRequest {
  upload_id: string;
}

export interface SolveResponse {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  message?: string;
  progress?: number;
}

export interface ApiError {
  error: string;
  details?: string;
}
