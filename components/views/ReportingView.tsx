import React from 'react';

interface Metric {
  id: string;
  name: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'neutral';
}

const METRICS: Metric[] = [
  {
    id: '1',
    name: 'Total Revenue',
    value: '$542,890',
    change: '+12.3%',
    trend: 'up'
  },
  {
    id: '2',
    name: 'Average Deal Size',
    value: '$45,240',
    change: '+5.8%',
    trend: 'up'
  },
  {
    id: '3',
    name: 'Win Rate',
    value: '68%',
    change: '-2.1%',
    trend: 'down'
  },
  {
    id: '4',
    name: 'Sales Cycle',
    value: '32 days',
    change: '-4 days',
    trend: 'up'
  },
  {
    id: '5',
    name: 'Active Deals',
    value: '24',
    change: '+3',
    trend: 'up'
  },
  {
    id: '6',
    name: 'Customer Satisfaction',
    value: '4.8/5.0',
    change: '+0.2',
    trend: 'up'
  }
];

export const ReportingView: React.FC = () => {
  const [timeframe, setTimeframe] = React.useState<'week' | 'month' | 'quarter' | 'year'>('month');

  return (
    <div className="w-full max-w-7xl mx-auto p-8">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-gray-900">Analytics</h2>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-6">
          {METRICS.map((metric) => (
            <div
              key={metric.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <h3 className="text-sm font-medium text-gray-500">{metric.name}</h3>
              <p className="text-2xl font-semibold text-gray-900 mt-2">{metric.value}</p>
              <div className="flex items-center mt-2">
                <span
                  className={`text-sm font-medium ${
                    metric.trend === 'up'
                      ? 'text-green-600'
                      : metric.trend === 'down'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}
                >
                  {metric.change}
                </span>
                <svg
                  className={`w-4 h-4 ml-1 ${
                    metric.trend === 'up'
                      ? 'text-green-600'
                      : metric.trend === 'down'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  {metric.trend === 'up' ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  ) : metric.trend === 'down' ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                  )}
                </svg>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Charts Section */}
        <div className="grid grid-cols-2 gap-6 mt-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Forecast</h3>
            <div className="h-64 flex items-center justify-center text-gray-500">
              Chart placeholder - Revenue projection over time
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pipeline Distribution</h3>
            <div className="h-64 flex items-center justify-center text-gray-500">
              Chart placeholder - Deal distribution by stage
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};