# Source Analyzer Web Dashboard

A comprehensive web-based interface for the Source Analyzer tool, providing real-time analysis monitoring, confidence validation, and project management capabilities.

## Features

- **Real-time Analysis Monitoring**: Track analysis progress with live updates
- **Confidence Validation System**: Monitor and calibrate AI-powered confidence scoring
- **Ground Truth Management**: Add and manage verified analysis results
- **Interactive Visualizations**: Charts and graphs for analysis insights
- **Project Management**: View and analyze multiple projects
- **Responsive Design**: Mobile-friendly interface

## Architecture

### Backend (FastAPI)
- REST API endpoints for data access
- WebSocket connections for real-time updates
- Integration with existing Source Analyzer components
- SQLite database for persistent storage

### Frontend (React)
- Modern React with TypeScript
- TailwindCSS for styling
- React Query for data fetching and caching
- Recharts for data visualization
- Real-time updates via WebSocket

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd web-dashboard/backend
   ```

2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn websockets
   ```

3. Start the backend server:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd web-dashboard/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The web interface will be available at `http://localhost:5173`

## Usage

1. **Start Analysis**: Use the Settings page to start analyzing a new project
2. **Monitor Progress**: View real-time progress on the Dashboard
3. **Add Ground Truth**: Use the Ground Truth Management page to add verified results
4. **Validate Confidence**: Monitor accuracy and calibrate the confidence system
5. **View Results**: Explore detailed analysis results for each project

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/projects` - Get all projects
- `GET /api/projects/{id}/analysis` - Get project analysis results
- `POST /api/analysis/start` - Start new analysis
- `GET /api/confidence/report` - Get confidence validation report
- `POST /api/confidence/calibrate` - Calibrate confidence system
- `GET /api/ground-truth` - Get ground truth entries
- `POST /api/ground-truth` - Add ground truth entry
- `WS /ws` - WebSocket for real-time updates

## Development

The system is designed to integrate seamlessly with the existing Source Analyzer CLI tool. The backend imports and uses existing components from the `phase1/src` directory, ensuring consistency between CLI and web interfaces.

## Technologies Used

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- WebSockets (real-time communication)
- SQLAlchemy (database ORM)

**Frontend:**
- React 18 with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- React Router (routing)
- Recharts (data visualization)
- Heroicons (icons)