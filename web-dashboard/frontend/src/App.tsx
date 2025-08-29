import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProjectDetails from './pages/ProjectDetails'
import ConfidenceValidation from './pages/ConfidenceValidation'
import GroundTruthManagement from './pages/GroundTruthManagement'
import Settings from './pages/Settings'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects/:projectId" element={<ProjectDetails />} />
        <Route path="/confidence" element={<ConfidenceValidation />} />
        <Route path="/ground-truth" element={<GroundTruthManagement />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App