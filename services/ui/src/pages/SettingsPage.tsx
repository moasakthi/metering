export default function SettingsPage() {
  const apiKey = localStorage.getItem('api_key') || 'Not set'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and API configuration</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">API Key</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current API Key
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="password"
                value={apiKey}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-700"
              />
              <button
                onClick={() => {
                  navigator.clipboard.writeText(apiKey)
                  alert('API key copied to clipboard!')
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Copy
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            This API key is used to authenticate requests to the Metering API.
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">About</h2>
        <div className="space-y-2 text-gray-600">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>API URL:</strong> {import.meta.env.VITE_API_URL || 'http://localhost:8000'}</p>
        </div>
      </div>
    </div>
  )
}

