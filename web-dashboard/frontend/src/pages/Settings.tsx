import React, { useState } from 'react'
import {
  CogIcon,
  FolderIcon,
  PlayIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import { useMutation } from '@tanstack/react-query'
import { api } from '../services/api'

interface AnalysisForm {
  project_path: string
  project_name: string
  incremental: boolean
}

export default function Settings() {
  const [analysisForm, setAnalysisForm] = useState<AnalysisForm>({
    project_path: '',
    project_name: '',
    incremental: false
  })

  const startAnalysisMutation = useMutation({
    mutationFn: api.startAnalysis
  })

  const handleAnalysisSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (analysisForm.project_path && analysisForm.project_name) {
      startAnalysisMutation.mutate(analysisForm)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setAnalysisForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-600">
          Configure analysis parameters and start new project analysis
        </p>
      </div>

      {/* Start New Analysis */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center mb-4">
            <PlayIcon className="h-6 w-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Start New Analysis</h3>
          </div>
          
          <form onSubmit={handleAnalysisSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Project Name</label>
              <input
                type="text"
                name="project_name"
                required
                value={analysisForm.project_name}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="My Project"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Project Path</label>
              <input
                type="text"
                name="project_path"
                required
                value={analysisForm.project_path}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="C:/path/to/your/project"
              />
              <p className="mt-1 text-xs text-gray-500">
                Full path to the root directory of your Java/JSP project
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="incremental"
                checked={analysisForm.incremental}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Incremental analysis (only analyze changed files)
              </label>
            </div>

            {startAnalysisMutation.error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="text-sm text-red-700">
                  Analysis failed. Please check the project path and try again.
                </div>
              </div>
            )}

            {startAnalysisMutation.data && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="text-sm text-green-700">
                  Analysis started successfully! Check the dashboard for progress updates.
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={startAnalysisMutation.isPending}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {startAnalysisMutation.isPending ? 'Starting Analysis...' : 'Start Analysis'}
            </button>
          </form>
        </div>
      </div>

      {/* System Configuration */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center mb-4">
            <CogIcon className="h-6 w-6 text-gray-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">System Configuration</h3>
          </div>
          
          <div className="space-y-4">
            <div className="border-l-4 border-blue-400 pl-4">
              <h4 className="text-sm font-medium text-gray-900">Database</h4>
              <p className="text-sm text-gray-600">SQLite database for storing analysis results and metadata</p>
              <p className="text-xs text-gray-500 mt-1">Location: ./data/source_analyzer.db</p>
            </div>

            <div className="border-l-4 border-green-400 pl-4">
              <h4 className="text-sm font-medium text-gray-900">Confidence System</h4>
              <p className="text-sm text-gray-600">AI-powered confidence scoring for analysis accuracy</p>
              <p className="text-xs text-gray-500 mt-1">Requires ground truth data for calibration</p>
            </div>

            <div className="border-l-4 border-yellow-400 pl-4">
              <h4 className="text-sm font-medium text-gray-900">Supported File Types</h4>
              <p className="text-sm text-gray-600">Java (.java), JSP (.jsp), XML (.xml)</p>
              <p className="text-xs text-gray-500 mt-1">Automatic parser selection based on file extension</p>
            </div>
          </div>
        </div>
      </div>

      {/* Help & Documentation */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center mb-4">
            <DocumentTextIcon className="h-6 w-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Help & Documentation</h3>
          </div>
          
          <div className="space-y-3">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Getting Started</h4>
              <p className="text-sm text-gray-600">
                1. Start a new analysis by providing your project path and name above
              </p>
              <p className="text-sm text-gray-600">
                2. Monitor progress on the Dashboard with real-time updates
              </p>
              <p className="text-sm text-gray-600">
                3. Add ground truth data to enable confidence validation
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900">Ground Truth Data</h4>
              <p className="text-sm text-gray-600">
                Add verified analysis results to improve confidence scoring accuracy.
                The system learns from your corrections to provide better predictions.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900">Confidence Validation</h4>
              <p className="text-sm text-gray-600">
                Monitor how well the system predicts analysis outcomes.
                Use calibration to adjust the confidence scoring algorithm.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}