import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  FolderIcon, 
  CodeBracketIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { api } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

interface Project {
  project_id: number
  name: string
  root_path: string
  created_at: string
  updated_at: string
}

interface AnalysisResult {
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

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']

export default function Dashboard() {
  // Fetch projects
  const { data: projects, isLoading: projectsLoading, error: projectsError } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects
  })

  // Fetch confidence report
  const { data: confidenceReport, isLoading: confidenceLoading } = useQuery({
    queryKey: ['confidence-report'],
    queryFn: api.getConfidenceReport,
    retry: 1 // Don't retry too much if ground truth data is missing
  })

  if (projectsLoading) {
    return <LoadingSpinner />
  }

  if (projectsError) {
    return <ErrorMessage message="Failed to load projects" />
  }

  // Prepare chart data
  const projectsData = projects?.slice(0, 5).map((project: Project) => ({
    name: project.name.substring(0, 20) + (project.name.length > 20 ? '...' : ''),
    files: Math.floor(Math.random() * 100) + 10, // Mock data for demo
    classes: Math.floor(Math.random() * 50) + 5,
    methods: Math.floor(Math.random() * 200) + 20,
  })) || []

  const languageDistribution = [
    { name: 'Java', value: 45, color: '#3B82F6' },
    { name: 'JSP', value: 25, color: '#10B981' },
    { name: 'XML', value: 20, color: '#F59E0B' },
    { name: 'Others', value: 10, color: '#EF4444' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Overview of your source code analysis projects and system health
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FolderIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Projects</dt>
                  <dd className="text-lg font-medium text-gray-900">{projects?.length || 0}</dd>
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
                  <dd className="text-lg font-medium text-gray-900">
                    {Math.floor(Math.random() * 1000) + 500} {/* Mock data */}
                  </dd>
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
                  <dd className="text-lg font-medium text-gray-900">
                    {Math.floor(Math.random() * 500) + 100} {/* Mock data */}
                  </dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Confidence</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {confidenceReport ? `${(100 - confidenceReport.mean_absolute_error * 100).toFixed(1)}%` : 'N/A'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Project Analysis Chart */}
        <div className="bg-white p-6 shadow rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Project Analysis Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={projectsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="files" fill="#3B82F6" name="Files" />
              <Bar dataKey="classes" fill="#10B981" name="Classes" />
              <Bar dataKey="methods" fill="#F59E0B" name="Methods" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Language Distribution */}
        <div className="bg-white p-6 shadow rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Language Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={languageDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {languageDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confidence Status */}
      {confidenceReport && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence Validation Status</h3>
            
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {confidenceReport.total_validations}
                </div>
                <div className="text-sm text-gray-500">Total Validations</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {((1 - confidenceReport.mean_absolute_error) * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">Average Accuracy</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {(confidenceReport.median_absolute_error * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">Median Error</div>
              </div>
            </div>
            
            <div className="mt-4">
              <Link
                to="/confidence"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                View Detailed Report
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Recent Projects */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Projects</h3>
          
          {projects && projects.length > 0 ? (
            <div className="space-y-4">
              {projects.slice(0, 5).map((project: Project) => (
                <div key={project.project_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{project.name}</h4>
                    <p className="text-sm text-gray-500">{project.root_path}</p>
                    <p className="text-xs text-gray-400">
                      Updated: {new Date(project.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link
                    to={`/projects/${project.project_id}`}
                    className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200"
                  >
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No projects yet</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by analyzing your first project.</p>
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      {confidenceLoading && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Confidence System Initializing
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>Setting up confidence validation system...</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}