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
        'Authorization': `Bearer ${serverRuntimeConfig.apiBearerToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body)
    });

    const responseText = await backendResponse.text();
    console.log(`Backend response status: ${backendResponse.status}`, responseText);

    if (!backendResponse.ok) {
      throw new Error(`Backend request failed: ${responseText}`);
    }

    res.status(200).json(JSON.parse(responseText));
  } catch (error: any) {
    res.status(500).json({ error: error.message || 'Internal server error' });
  }
}