import React from 'react';

interface Deal {
  id: string;
  name: string;
  value: number;
  probability: number;
  stage: string;
}

const STAGES = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed'];

const SAMPLE_DEALS: Deal[] = [
  {
    id: '1',
    name: 'Solar Installation - Smith Residence',
    value: 25000,
    probability: 60,
    stage: 'Qualified'
  },
  {
    id: '2',
    name: 'HVAC Upgrade - Office Complex',
    value: 45000,
    probability: 80,
    stage: 'Proposal'
  },
  {
    id: '3',
    name: 'Roofing Project - Downtown Mall',
    value: 120000,
    probability: 40,
    stage: 'Lead'
  }
];

export const PipelineView: React.FC = () => {
  return (
    <div className="w-full max-w-7xl mx-auto p-8">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-gray-900">Pipeline</h2>
          <div className="flex gap-3">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              Filter
            </button>
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
              Add Deal
            </button>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4">
          {STAGES.map((stage) => (
            <div key={stage} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium text-gray-900">{stage}</h3>
                <span className="text-sm text-gray-500">
                  {SAMPLE_DEALS.filter(deal => deal.stage === stage).length} deals
                </span>
              </div>
              
              <div className="space-y-3">
                {SAMPLE_DEALS
                  .filter(deal => deal.stage === stage)
                  .map(deal => (
                    <div
                      key={deal.id}
                      className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    >
                      <h4 className="text-sm font-medium text-gray-900 mb-1">{deal.name}</h4>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-500">
                          ${deal.value.toLocaleString()}
                        </span>
                        <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                          {deal.probability}%
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4 mt-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500">Total Pipeline</h3>
            <p className="text-2xl font-semibold text-gray-900 mt-1">
              ${SAMPLE_DEALS.reduce((sum, deal) => sum + deal.value, 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500">Average Deal Size</h3>
            <p className="text-2xl font-semibold text-gray-900 mt-1">
              ${Math.round(SAMPLE_DEALS.reduce((sum, deal) => sum + deal.value, 0) / SAMPLE_DEALS.length).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500">Win Rate</h3>
            <p className="text-2xl font-semibold text-gray-900 mt-1">65%</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500">Active Deals</h3>
            <p className="text-2xl font-semibold text-gray-900 mt-1">{SAMPLE_DEALS.length}</p>
          </div>
        </div>
      </div>
    </div>
  );
};