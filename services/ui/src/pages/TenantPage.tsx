import { useQuery } from '@tanstack/react-query'
import { meteringApi } from '../services/api'
import { subDays } from 'date-fns'

export default function TenantPage() {
  const endDate = new Date()
  const startDate = subDays(endDate, 30)

  // Fetch events and compute tenant stats client-side
  // Fetch first few pages for tenant stats
  const { data: eventsData, isLoading, error } = useQuery({
    queryKey: ['events', 'tenants', startDate.toISOString(), endDate.toISOString()],
    queryFn: async () => {
      // Fetch first 5 pages (5000 events) which should be enough for tenant stats
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
    console.log('No events found for tenants. Response:', eventsData)
  }
  
  // Group by tenant
  const tenantData = events.reduce((acc: any, event: any) => {
    const tenantId = event.tenant_id
    if (!acc[tenantId]) {
      acc[tenantId] = { total_quantity: 0, total_events: 0 }
    }
    acc[tenantId].total_quantity += event.quantity || 0
    acc[tenantId].total_events += 1
    return acc
  }, {})

  const tenants = Object.entries(tenantData).map(([tenant_id, data]: [string, any]) => ({
    tenant_id,
    ...data
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tenant Usage</h1>
        <p className="text-gray-600 mt-1">Usage analytics by tenant</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {tenants.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center text-gray-500">
            {events.length === 0 
              ? "No events found. Make sure you have data in the database and the date range is correct."
              : "No tenant data available"}
          </div>
        ) : (
          tenants.map((tenant) => (
            <div key={tenant.tenant_id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{tenant.tenant_id}</h3>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  Active
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Total Usage</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">{tenant.total_quantity.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Events</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">{tenant.total_events.toLocaleString()}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

