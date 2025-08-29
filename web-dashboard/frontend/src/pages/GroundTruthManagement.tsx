import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  PlusIcon,
  DocumentTextIcon,
  UserIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'
import { api, GroundTruthEntry } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

interface NewEntryForm {
  file_path: string
  parser_type: string
  expected_confidence: number
  expected_classes?: number
  expected_methods?: number
  expected_sql_units?: number
  verified_tables?: string
  notes?: string
  verifier?: string
}

export default function GroundTruthManagement() {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<NewEntryForm>({
    file_path: '',
    parser_type: 'java',
    expected_confidence: 0.95,
    expected_classes: 0,
    expected_methods: 0,
    expected_sql_units: 0,
    verified_tables: '',
    notes: '',
    verifier: ''
  })

  const queryClient = useQueryClient()

  const { data: entries, isLoading, error } = useQuery({
    queryKey: ['ground-truth'],
    queryFn: api.getGroundTruthEntries
  })

  const addEntryMutation = useMutation({
    mutationFn: (entry: GroundTruthEntry) => api.addGroundTruthEntry(entry),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ground-truth'] })
      queryClient.invalidateQueries({ queryKey: ['confidence-report'] })
      setShowForm(false)
      setFormData({
        file_path: '',
        parser_type: 'java',
        expected_confidence: 0.95,
        expected_classes: 0,
        expected_methods: 0,
        expected_sql_units: 0,
        verified_tables: '',
        notes: '',
        verifier: ''
      })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const entry: GroundTruthEntry = {
      ...formData,
      verified_tables: formData.verified_tables ? formData.verified_tables.split(',').map(t => t.trim()) : undefined,
      verification_date: new Date().toISOString()
    }

    addEntryMutation.mutate(entry)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }))
  }

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-8" />
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ground Truth Management</h1>
            <p className="mt-2 text-sm text-gray-600">
              Manage verified analysis results for confidence validation and system calibration
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Entry
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add Ground Truth Entry</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">File Path</label>
                  <input
                    type="text"
                    name="file_path"
                    required
                    value={formData.file_path}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="src/main/java/Example.java"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Parser Type</label>
                  <select
                    name="parser_type"
                    value={formData.parser_type}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="java">Java</option>
                    <option value="jsp">JSP</option>
                    <option value="xml">XML</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Expected Confidence</label>
                  <input
                    type="number"
                    name="expected_confidence"
                    min="0"
                    max="1"
                    step="0.01"
                    required
                    value={formData.expected_confidence}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Expected Classes</label>
                  <input
                    type="number"
                    name="expected_classes"
                    min="0"
                    value={formData.expected_classes}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Expected Methods</label>
                  <input
                    type="number"
                    name="expected_methods"
                    min="0"
                    value={formData.expected_methods}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Expected SQL Units</label>
                  <input
                    type="number"
                    name="expected_sql_units"
                    min="0"
                    value={formData.expected_sql_units}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Verified Tables (comma-separated)</label>
                <input
                  type="text"
                  name="verified_tables"
                  value={formData.verified_tables}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="users, orders, products"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Verifier</label>
                <input
                  type="text"
                  name="verifier"
                  value={formData.verifier}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Developer/Reviewer name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <textarea
                  name="notes"
                  rows={3}
                  value={formData.notes}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Additional notes about this verification..."
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addEntryMutation.isPending}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {addEntryMutation.isPending ? 'Adding...' : 'Add Entry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {addEntryMutation.error && (
        <ErrorMessage message="Failed to add ground truth entry. Please try again." />
      )}

      {error && (
        <ErrorMessage message="Failed to load ground truth entries" />
      )}

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Ground Truth Entries</h3>
          
          {entries && entries.length > 0 ? (
            <div className="space-y-4">
              {entries.map((entry, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center">
                      <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{entry.file_path}</span>
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {entry.parser_type}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-green-600">
                      {(entry.expected_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                    <div>Classes: {entry.expected_classes || 0}</div>
                    <div>Methods: {entry.expected_methods || 0}</div>
                    <div>SQL Units: {entry.expected_sql_units || 0}</div>
                  </div>

                  {entry.verified_tables && entry.verified_tables.length > 0 && (
                    <div className="text-sm text-gray-600 mb-2">
                      <strong>Tables:</strong> {entry.verified_tables.join(', ')}
                    </div>
                  )}

                  {entry.notes && (
                    <div className="text-sm text-gray-600 mb-2">
                      <strong>Notes:</strong> {entry.notes}
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {entry.verifier || 'Unknown'}
                    </div>
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {entry.verification_date ? new Date(entry.verification_date).toLocaleDateString() : 'Unknown'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No ground truth entries</h3>
              <p className="mt-1 text-sm text-gray-500">
                Add verified analysis results to enable confidence validation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}