import React from 'react';

export const TasksView: React.FC = () => {
  return (
    <div className="w-full max-w-4xl mx-auto p-8">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-gray-900">Tasks</h2>
          <div className="flex gap-3">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              Filter
            </button>
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
              New Task
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 divide-y divide-gray-200">
          {/* Sample Tasks */}
          <div className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-4">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded border-gray-300" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900">Follow up with John Doe</h3>
                <p className="text-sm text-gray-500">Discuss solar panel installation quote</p>
              </div>
              <span className="text-sm text-gray-500">Due today</span>
            </div>
          </div>

          <div className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-4">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded border-gray-300" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900">Schedule site visit</h3>
                <p className="text-sm text-gray-500">Property assessment for HVAC upgrade</p>
              </div>
              <span className="text-sm text-gray-500">Tomorrow</span>
            </div>
          </div>

          <div className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-4">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded border-gray-300" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900">Send proposal</h3>
                <p className="text-sm text-gray-500">Roofing project documentation</p>
              </div>
              <span className="text-sm text-gray-500">Next week</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};