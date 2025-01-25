import type { NextApiRequest, NextApiResponse } from 'next';
import getConfig from 'next/config';

const { serverRuntimeConfig } = getConfig();

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('Proxying request to backend service');
    const backendResponse = await fetch('http://localhost:8001/api/sales-assistant', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serverRuntimeConfig.API_BEARER_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body)
    });

    const responseText = await backendResponse.text();
    console.log(`Backend response status: ${backendResponse.status}`, responseText);

    if (!backendResponse.ok) {
      throw new Error(`Backend request failed: ${responseText}`);
    }

    const responseData = JSON.parse(responseText);
    
    // Detect view change requests in user query
    const userQuery = req.body.query.toLowerCase();
    let viewCommand = null;
    
    if (userQuery.includes('pipeline')) {
      viewCommand = { type: 'command', action: 'setView', view: 'pipeline' };
    } else if (userQuery.includes('task') || userQuery.includes('todo')) {
      viewCommand = { type: 'command', action: 'setView', view: 'tasks' };
    } else if (userQuery.includes('report') || userQuery.includes('analytics')) {
      viewCommand = { type: 'command', action: 'setView', view: 'reporting' };
    }

    res.status(200).json(viewCommand || responseData);
  } catch (error: any) {
    res.status(500).json({ error: error.message || 'Internal server error' });
  }
}