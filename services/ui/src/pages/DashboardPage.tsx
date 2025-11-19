import { useQuery } from '@tanstack/react-query'
import { meteringApi } from '../services/api'
import { format, subDays } from 'date-fns'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  const endDate = new Date()
  // Query last 30 days to ensure we get data (seeded data spans 30 days)
  const startDate = subDays(endDate, 30)

  // Fetch events and compute aggregates client-side
  // Fetch first few pages for dashboard (enough for accurate stats)
  const { data: eventsData, isLoading, error } = useQuery({
    queryKey: ['events', 'dashboard', startDate.toISOString(), endDate.toISOString()],
    queryFn: async () => {
      // Fetch first 5 pages (5000 events) which should be enough for dashboard stats
      const pagesToFetch = 5
      const pages = await Promise.all(
        Array.from({ length: pagesToFetch }, (_, i) =>
          meteringApi.getEvents({
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            page: i + 1,
            page_size: 1000, // Max allowed by API
          })
        )
      )
      
      // Combine all events
      const allItems = pages.flatMap(page => page.data.items)
      const total = pages[0]?.data.total || 0
      
      return {
        data: {
          items: allItems,
          page: 1,
          page_size: allItems.length,
          total: total,
          total_pages: Math.ceil(total / 1000)
        }
      }
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-blue-600">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">Error loading data: {String(error)}</div>
      </div>
    )
  }

  const events = eventsData?.data?.items || []
  
  // Debug: log if no events
  if (events.length === 0) {
    console.log('No events found. Response:', eventsData)
  }
  
  // Compute summary from events
  // Note: If we only fetched a subset, we'll show stats for that subset
  const totalEvents = eventsData?.data?.total || events.length
  const summary = {
    total_quantity: events.reduce((sum: number, e: any) => sum + (e.quantity || 0), 0),
    total_events: totalEvents, // Show total from API, not just fetched count
    fetched_events: events.length // For reference
  }

  // Group events by date for chart
  const eventsByDate = events.reduce((acc: any, event: any) => {
    const date = format(new Date(event.timestamp), 'MMM dd')
    if (!acc[date]) {
      acc[date] = { date, usage: 0, count: 0 }
    }
    acc[date].usage += event.quantity || 0
    acc[date].count += 1
    return acc
  }, {})

  const chartData = Object.values(eventsByDate).sort((a: any, b: any) => {
    return new Date(a.date).getTime() - new Date(b.date).getTime()
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your metering data</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600">Total Usage</h3>
              <p className="text-3xl font-bold text-blue-600 mt-2">{summary.total_quantity.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📊</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600">Total Events</h3>
              <p className="text-3xl font-bold text-blue-600 mt-2">{summary.total_events.toLocaleString()}</p>
              {summary.fetched_events < summary.total_events && (
                <p className="text-xs text-gray-500 mt-1">
                  Showing sample of {summary.fetched_events.toLocaleString()} events
                </p>
              )}
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📝</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600">Time Period</h3>
              <p className="text-2xl font-bold text-blue-600 mt-2">Last 30 Days</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Usage Trends</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="usage" stroke="#3b82f6" strokeWidth={2} name="Usage" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12 text-gray-500">
            {events.length === 0 
              ? "No events found. Make sure you have data in the database and the date range is correct."
              : "No data available for the selected period"}
          </div>
        )}
      </div>
    </div>
  )
}

