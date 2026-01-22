# Codora Timetable Frontend

A Next.js frontend for **Codora Timetable**, a deterministic college scheduling system with constraint solving capabilities.

## Overview

The Codora Timetable frontend is a **viewer and controller**, not a decision-maker. It provides:
- **Data Upload**: Upload CSV/JSON files for scheduling data
- **Validation Display**: Show validation results with clear error/warning messages
- **Timetable Generation**: Trigger the backend constraint solver
- **Calendar View**: Display the generated schedule in a clean, read-only grid

## System Architecture

```
Frontend (Next.js/React)
    ↓
FastAPI Backend
    ↓
Constraint Solver (OR-Tools CP-SAT)
```

The frontend never enforces business logic or constraints—it only displays data and triggers backend operations.

## Project Structure

```
src/
├── app/                      # Next.js pages (App Router)
│   ├── page.tsx             # Home/Dashboard
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles
│   ├── upload/
│   │   └── page.tsx         # File upload interface
│   ├── validation/
│   │   └── page.tsx         # Validation results display
│   ├── generation/
│   │   └── page.tsx         # Solver trigger & status
│   └── timetable/
│       └── page.tsx         # Calendar view of schedule
├── components/
│   ├── layout/
│   │   ├── Header.tsx       # Navigation header
│   │   ├── Footer.tsx       # Footer with links
│   │   └── index.ts
│   ├── ui/
│   │   ├── Button.tsx       # Reusable button component
│   │   ├── Card.tsx         # Card wrapper
│   │   ├── ErrorMessage.tsx # Error display
│   │   ├── LoadingSpinner.tsx
│   │   ├── StatusBadge.tsx
│   │   └── index.ts
│   └── upload/
│       ├── FileUploader.tsx # Drag-and-drop file upload
│       └── index.ts
├── config/
│   └── api.ts              # API configuration & endpoints
├── lib/
│   └── api/
│       ├── client.ts       # Base HTTP client
│       ├── upload.ts       # Upload API service
│       ├── validation.ts   # Validation API service
│       ├── solve.ts        # Solver API service
│       ├── timetable.ts    # Timetable API service
│       └── index.ts        # API exports
└── types/
    └── api.ts              # TypeScript types for API responses
```

## Key Features

### 1. Upload Page (`/upload`)
- Drag-and-drop file upload interface
- Support for CSV and JSON files
- Upload all required files in one operation:
  - `sections.csv`
  - `faculty.csv`
  - `courses.csv`
  - `rooms.csv`
  - `faculty_course_map.csv`
  - `time_config.json`
- Generates `upload_id` for tracking

### 2. Validation Page (`/validation`)
- Displays validation results from backend
- Shows **errors**, **warnings**, and **suggestions**
- Detailed information per issue (file, line, field)
- Status badges for quick overview
- Proceed to generation if valid, or upload new files

### 3. Generation Page (`/generation`)
- Explains the constraint solving process
- Trigger timetable generation
- Real-time status polling (queued → running → completed)
- Progress indicator for long-running operations
- Error handling with retry capability

### 4. Timetable Page (`/timetable`)
- Calendar-like grid: Days × Time Slots
- Interactive class slots showing details:
  - Course code & name
  - Section
  - Faculty
  - Room
  - Schedule
- Statistics: Total classes, unique courses, sections, rooms
- Print-friendly layout
- Read-only view (no direct edits)

## API Integration

### Base URL
```
http://localhost:8000  (development)
```

Configured in `src/config/api.ts`

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload scheduling data files |
| `/api/validation/{upload_id}` | GET | Fetch validation results |
| `/api/solve` | POST | Trigger constraint solver |
| `/api/solve/{job_id}` | GET | Check solver status |
| `/api/timetable/{upload_id}` | GET | Fetch generated timetable |

### Request/Response Examples

**Upload Files:**
```typescript
const response = await uploadFiles(files);
// Returns: { upload_id: string, files_received: string[], status: 'success' | 'error' }
```

**Get Validation:**
```typescript
const validation = await getValidation(uploadId);
// Returns: { upload_id, status, errors, warnings, suggestions }
```

**Start Solver:**
```typescript
const result = await triggerSolve(uploadId);
// Returns: { job_id, status: 'queued' | 'running' | 'completed' | 'failed', progress? }
```

**Get Timetable:**
```typescript
const timetable = await getTimetable(uploadId);
// Returns: { upload_id, generated_at, slots: TimeSlotData[] }
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend/TimeTable\ website
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Configuration

### Backend URL
Set `NEXT_PUBLIC_API_URL` environment variable:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Design Principles

### 1. **No Hidden Changes**
- All operations require explicit user action
- Clear loading states and status indicators
- Transparent error messages

### 2. **Read-Only Viewer**
- Timetable cannot be edited in frontend
- Changes only via backend re-generation
- Users review output before any action

### 3. **Human-in-the-Loop**
- Frontend displays data, doesn't enforce logic
- Validation results guide user decisions
- Clear explanations for errors and warnings

### 4. **Minimal, Clean UI**
- TailwindCSS for styling
- Dark mode support
- Responsive design (mobile-first)
- Accessible components

## Component Hierarchy

```
RootLayout
├── Header (Navigation)
├── Main Content
│   ├── HomePage
│   ├── UploadPage
│   │   └── FileUploader
│   ├── ValidationPage
│   │   └── Card (Error/Warning/Suggestion)
│   ├── GenerationPage
│   │   └── LoadingSpinner
│   └── TimetablePage
│       ├── Calendar Grid
│       └── Slot Details Modal
└── Footer
```

## State Management

Currently uses React hooks (`useState`, `useEffect`) for local state. For larger scale, consider:
- TanStack Query for server state
- Zustand or Redux for client state

## Testing

(To be implemented)

```bash
npm run test
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Performance Considerations

- **Image Optimization**: Next.js Image component ready
- **Code Splitting**: Automatic per-route
- **API Caching**: Implement SWR/React Query for better UX
- **Lazy Loading**: Modal components load on demand

## Error Handling

All API calls include:
- Try-catch error boundaries
- User-friendly error messages
- Retry mechanisms where applicable
- Detailed error logging in console

## Security

- All API calls use HTTPS in production
- No sensitive data in local storage
- Environment variables for API URLs
- CORS handling via backend

## Future Enhancements

- [ ] Real-time collaboration features
- [ ] Schedule comparison & diff view
- [ ] Export to various formats (PDF, iCal, Excel)
- [ ] Constraint visualization
- [ ] Advanced filtering/search in timetable
- [ ] Undo/redo for re-generation attempts
- [ ] Dark mode toggle in header
- [ ] Keyboard navigation

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/codora/timetable/issues)
- Documentation: [Docs](https://docs.example.com)
