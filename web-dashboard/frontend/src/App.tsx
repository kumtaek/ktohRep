import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProjectDetails from './pages/ProjectDetails'
import ConfidenceValidation from './pages/ConfidenceValidation'
import GroundTruthManagement from './pages/GroundTruthManagement'
import Settings from './pages/Settings'
import OwaspA03Doc from './components/OwaspA03Doc' // 새로 추가

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects/:projectId" element={<ProjectDetails />} />
        <Route path="/confidence" element={<ConfidenceValidation />} />
        <Route path="/ground-truth" element={<GroundTruthManagement />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/docs/owasp/a03" element={<OwaspA03Doc />} /> {/* 새로 추가 */}
      </Routes>
    </Layout>
  )
}

export default App