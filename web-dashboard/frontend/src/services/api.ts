import axios from 'axios'

// API client configuration
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for debugging
apiClient.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    throw error
  }
)

// Types
export interface Project {
  project_id: number
  name: string
  root_path: string
  created_at: string
  updated_at: string
}

export interface AnalysisResult {
  project_id: number
  total_files: number
  success_count: number
  error_count: number
  java_files: number
  jsp_files: number
  xml_files: number
  total_classes: number
  total_methods: number
  total_sql_units: number
}

export interface ConfidenceReport {
  mean_absolute_error: number
  median_absolute_error: number
  error_distribution: {
    excellent: { count: number; percentage: number }
    good: { count: number; percentage: number }
    acceptable: { count: number; percentage: number }
    poor: { count: number; percentage: number }
  }
  total_validations: number
}

export interface GroundTruthEntry {
  file_path: string
  parser_type: string
  expected_confidence: number
  expected_classes?: number
  expected_methods?: number
  expected_sql_units?: number
  verified_tables?: string[]
  complexity_factors?: Record<string, any>
  notes?: string
  verifier?: string
  verification_date?: string
}

export interface CalibrationResult {
  current_weights: Record<string, number>
  current_mae: number
  best_weights: Record<string, number>
  best_mae: number
  improvement: number
  improvement_percentage: number
  calibration_attempts: number
  recommendation: string
}

// API functions
export const api = {
  // Health check
  async healthCheck() {
    return apiClient.get('/health')
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    return apiClient.get('/projects')
  },

  async getProjectAnalysis(projectId: number): Promise<AnalysisResult> {
    return apiClient.get(`/projects/${projectId}/analysis`)
  },

  async startAnalysis(data: { project_path: string; project_name: string; incremental?: boolean }) {
    return apiClient.post('/analysis/start', data)
  },

  // Confidence system
  async getConfidenceReport(): Promise<ConfidenceReport> {
    return apiClient.get('/confidence/report')
  },

  async calibrateConfidence(): Promise<CalibrationResult> {
    return apiClient.post('/confidence/calibrate')
  },

  // Ground truth management
  async getGroundTruthEntries(): Promise<GroundTruthEntry[]> {
    return apiClient.get('/ground-truth')
  },

  async addGroundTruthEntry(entry: GroundTruthEntry) {
    return apiClient.post('/ground-truth', entry)
  },
}

// WebSocket connection for real-time updates
export class WebSocketManager {
  private ws: WebSocket | null = null
  private listeners: Map<string, (data: any) => void> = new Map()

  connect() {
    try {
      this.ws = new WebSocket(`ws://localhost:8000/ws`)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          const { type, data } = message
          
          // Call registered listeners
          const listener = this.listeners.get(type)
          if (listener) {
            listener(data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        // Attempt to reconnect after 3 seconds
        setTimeout(() => this.connect(), 3000)
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  on(eventType: string, callback: (data: any) => void) {
    this.listeners.set(eventType, callback)
  }

  off(eventType: string) {
    this.listeners.delete(eventType)
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Singleton WebSocket manager
export const wsManager = new WebSocketManager()