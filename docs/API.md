# ATTYX AI API Documentation

## Overview
This document outlines the API endpoints and usage for the ATTYX AI platform. The API is built using FastAPI and follows RESTful principles.

## Authentication
All API endpoints require authentication using Bearer tokens. Tokens are managed through Supabase authentication services.

```typescript
headers: {
  'Authorization': 'Bearer <your_token>',
  'Content-Type': 'application/json'
}
```

## Core Endpoints

### Call Queue Management

#### Get Queue Status
```http
GET /api/queue/status
```
Returns the current queue status including active leads and agent availability.

#### Update Agent Status
```http
POST /api/queue/agent/status
{
  "status": "ready" | "busy" | "offline",
  "agent_id": string
}
```

#### Get Next Lead
```http
GET /api/queue/next
```
Returns the next prioritized lead in the queue.

### Knowledge Management

#### Search Products
```http
GET /api/knowledge/products
{
  "query": string,
  "category": string,
  "limit": number
}
```

#### Get Product Details
```http
GET /api/knowledge/products/{product_id}
```

#### Search Documentation
```http
POST /api/knowledge/search
{
  "query": string,
  "filters": {
    "category": string[],
    "type": string[]
  }
}
```

### Sales Intelligence

#### Get Lead Analytics
```http
GET /api/analytics/lead/{lead_id}
```

#### Generate Report
```http
POST /api/analytics/report
{
  "type": string,
  "dateRange": {
    "start": string,
    "end": string
  },
  "filters": object
}
```

#### Get Recommendations
```http
POST /api/intelligence/recommendations
{
  "lead_id": string,
  "context": object
}
```

## WebSocket Events

### Queue Updates
```typescript
socket.on('queue:update', (data: {
  queue_length: number,
  active_agents: number,
  priority_leads: number
}) => void)
```

### Lead Notifications
```typescript
socket.on('lead:new', (data: {
  lead_id: string,
  priority: number,
  source: string
}) => void)
```

### Agent Status
```typescript
socket.on('agent:status', (data: {
  agent_id: string,
  status: string,
  timestamp: string
}) => void)
```

## Error Handling
All endpoints follow standard HTTP status codes and return detailed error messages:

```json
{
  "error": {
    "code": string,
    "message": string,
    "details": object
  }
}
```

## Rate Limiting
- 100 requests per minute per authenticated user
- 1000 requests per hour per IP address
- WebSocket connections limited to 1 per authenticated user

## Development Guidelines
- Use TypeScript for all API interactions
- Implement proper error handling
- Follow RESTful naming conventions
- Document all custom types and interfaces
- Include request/response examples in documentation