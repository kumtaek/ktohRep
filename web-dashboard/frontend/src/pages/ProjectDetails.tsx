import React, { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  CodeBracketIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  FolderIcon
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api, wsManager } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>()

  const { data: analysis, isLoading, error, refetch } = useQuery({
    queryKey: ['project-analysis', projectId],
    queryFn: () => api.getProjectAnalysis(Number(projectId)),
    enabled: !!projectId
  })

  useEffect(() => {
    wsManager.connect()
    wsManager.on('analysis_progress', (data) => {
      if (data.project_id === Number(projectId)) {
        refetch()
      }
    })

    return () => {
      wsManager.off('analysis_progress')
    }
  }, [projectId, refetch])

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-8" />
  }

  if (error) {
    return <ErrorMessage message="Failed to load project analysis" className="mt-8" />
  }

  if (!analysis) {
    return <div className="text-center mt-8">No analysis data found</div>
  }

  const fileTypeData = [
    { name: 'Java', count: analysis.java_files, color: '#3B82F6' },
    { name: 'JSP', count: analysis.jsp_files, color: '#10B981' },
    { name: 'XML', count: analysis.xml_files, color: '#F59E0B' },
  ]

  const successRate = analysis.total_files > 0 
    ? ((analysis.success_count / analysis.total_files) * 100).toFixed(1)
    : '0'

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Project Analysis</h1>
        <p className="mt-2 text-sm text-gray-600">
          Detailed analysis results for project #{projectId}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FolderIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Files</dt>
                  <dd className="text-lg font-medium text-gray-900">{analysis.total_files}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CodeBracketIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Classes</dt>
                  <dd className="text-lg font-medium text-gray-900">{analysis.total_classes}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Methods</dt>
                  <dd className="text-lg font-medium text-gray-900">{analysis.total_methods}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">SQL Units</dt>
                  <dd className="text-lg font-medium text-gray-900">{analysis.total_sql_units}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="bg-white p-6 shadow rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">File Type Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fileTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 shadow rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Summary</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-600">Success Rate</span>
              <span className="text-sm text-gray-900">{successRate}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-600">Successful Files</span>
              <span className="text-sm text-green-600">{analysis.success_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-600">Failed Files</span>
              <span className="text-sm text-red-600">{analysis.error_count}</span>
            </div>
            <div className="mt-6">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${successRate}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}