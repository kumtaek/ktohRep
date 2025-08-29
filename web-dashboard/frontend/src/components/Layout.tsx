import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  ChartBarIcon, 
  CogIcon,
  CircleStackIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  current?: boolean
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Confidence Validation', href: '/confidence', icon: ChartBarIcon },
  { name: 'Ground Truth Data', href: '/ground-truth', icon: CircleStackIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
]

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  // Update current navigation item
  const currentNavigation = navigation.map(item => ({
    ...item,
    current: location.pathname === item.href
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div className={clsx('lg:hidden', sidebarOpen ? 'block' : 'hidden')}>
        <div className="fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          
          <div className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <XMarkIcon className="h-6 w-6 text-white" />
              </button>
            </div>
            
            <div className="h-0 flex-1 overflow-y-auto pt-5 pb-4">
              <div className="flex flex-shrink-0 items-center px-4">
                <h1 className="text-xl font-bold text-gray-900">Source Analyzer</h1>
              </div>
              <nav className="mt-5 space-y-1 px-2">
                {currentNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={clsx(
                      item.current
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                      'group flex items-center px-2 py-2 text-base font-medium rounded-md'
                    )}
                  >
                    <item.icon
                      className={clsx(
                        item.current ? 'text-gray-500' : 'text-gray-400',
                        'mr-4 h-6 w-6'
                      )}
                    />
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-white shadow">
          <div className="flex flex-1 flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-xl font-bold text-gray-900">Source Analyzer</h1>
            </div>
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {currentNavigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    item.current
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                  )}
                >
                  <item.icon
                    className={clsx(
                      item.current ? 'text-gray-500' : 'text-gray-400',
                      'mr-3 h-6 w-6'
                    )}
                  />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col lg:pl-64">
        {/* Mobile header */}
        <div className="sticky top-0 z-10 bg-white pl-1 pt-1 sm:pl-3 sm:pt-3 lg:hidden">
          <button
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
        </div>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}