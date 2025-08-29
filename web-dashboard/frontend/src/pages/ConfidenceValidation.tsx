import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ChartBarIcon,
  CogIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { api } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function ConfidenceValidation() {
  const [isCalibrating, setIsCalibrating] = useState(false)
  const queryClient = useQueryClient()

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['confidence-report'],
    queryFn: api.getConfidenceReport,
    retry: 1
  })

  const calibrationMutation = useMutation({
    mutationFn: api.calibrateConfidence,
    onMutate: () => setIsCalibrating(true),
    onSettled: () => setIsCalibrating(false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confidence-report'] })
    }
  })

  const handleCalibrate = () => {
    calibrationMutation.mutate()
  }

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-8" />
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 pb-4">
          <h1 className="text-3xl font-bold text-gray-900">Confidence Validation</h1>
          <p className="mt-2 text-sm text-gray-600">
            Monitor and calibrate confidence scoring accuracy
          </p>
        </div>
        <ErrorMessage message="No ground truth data available. Please add ground truth entries to enable confidence validation." />
      </div>
    )
  }

  const distributionData = report ? [
    { category: 'Excellent (>90%)', count: report.error_distribution.excellent.count, percentage: report.error_distribution.excellent.percentage },
    { category: 'Good (75-90%)', count: report.error_distribution.good.count, percentage: report.error_distribution.good.percentage },
    { category: 'Acceptable (50-75%)', count: report.error_distribution.acceptable.count, percentage: report.error_distribution.acceptable.percentage },
    { category: 'Poor (<50%)', count: report.error_distribution.poor.count, percentage: report.error_distribution.poor.percentage },
  ] : []

  const overallAccuracy = report ? ((1 - report.mean_absolute_error) * 100).toFixed(1) : '0'
  const medianError = report ? (report.median_absolute_error * 100).toFixed(1) : '0'

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Confidence Validation</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor and calibrate confidence scoring accuracy using ground truth data
        </p>
      </div>

      {report && (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Validations</dt>
                      <dd className="text-lg font-medium text-gray-900">{report.total_validations}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CheckCircleIcon className="h-6 w-6 text-green-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Overall Accuracy</dt>
                      <dd className="text-lg font-medium text-green-600">{overallAccuracy}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ExclamationTriangleIcon className="h-6 w-6 text-orange-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Mean Error</dt>
                      <dd className="text-lg font-medium text-orange-600">{(report.mean_absolute_error * 100).toFixed(1)}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-blue-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Median Error</dt>
                      <dd className="text-lg font-medium text-blue-600">{medianError}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-1">
            <div className="bg-white p-6 shadow rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Error Distribution by Category</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={distributionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [`${value} files`, 'Count']} />
                  <Bar dataKey="count" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence Calibration</h3>
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Calibrate the confidence scoring system to improve accuracy based on ground truth data.
                  This process adjusts internal weights to minimize prediction errors.
                </p>
              </div>
              
              {calibrationMutation.data && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
                  <h4 className="text-sm font-medium text-green-800">Calibration Results</h4>
                  <div className="mt-2 text-sm text-green-700">
                    <p>Current MAE: {(calibrationMutation.data.current_mae * 100).toFixed(2)}%</p>
                    <p>Best MAE: {(calibrationMutation.data.best_mae * 100).toFixed(2)}%</p>
                    <p>Improvement: {calibrationMutation.data.improvement_percentage.toFixed(1)}%</p>
                    <p className="mt-2 font-medium">{calibrationMutation.data.recommendation}</p>
                  </div>
                </div>
              )}

              {calibrationMutation.error && (
                <ErrorMessage 
                  message="Calibration failed. Please ensure you have sufficient ground truth data." 
                  className="mb-4"
                />
              )}

              <button
                onClick={handleCalibrate}
                disabled={isCalibrating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <CogIcon className="h-4 w-4 mr-2" />
                {isCalibrating ? 'Calibrating...' : 'Calibrate Confidence System'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}