# ATTYX AI Platform

[Previous content remains the same until Project Structure section...]

## Project Structure

````
ATTYX_AI/
│
├── README.md                # Project overview and setup instructions
├── .gitignore               # Files and folders to ignore in version control
├── requirements.txt         # Python dependencies
├── setup.py                 # Packaging script for the project
│
├── src/                     # Source code directory
│   ├── main.py              # Main entry point for the application
│   ├── config/              # Configuration files
│   │   ├── __init__.py
│   │   ├── settings.py      # Configuration settings (API keys, DB settings)
│   │   └── logging.py       # Logging configuration
│   │
│   ├── agents/              # Directory for agent implementations
│   │   ├── __init__.py
│   │   ├── lead_management_agent.py     # Lead Notification and Processing Agents
│   │   ├── call_queue_agent.py           # Queue Management and Call Handling Agents
│   │   ├── knowledge_management_agent.py  # Knowledge Retrieval and Verification Agents
│   │   └── sales_intelligence_agent.py    # Sales Strategy and Analytics Agents
│   │
│   ├── workflows/           # Directory for agent workflows
│   │   ├── __init__.py
│   │   ├── lead_workflow.py           # Workflow managing lead processes
│   │   ├── call_queue_workflow.py     # Workflow managing the call queue processes
│   │   ├── knowledge_management_workflow.py # Workflow for knowledge retrieval
│   │   └── sales_intelligence_workflow.py  # Workflow for sales intelligence
│   │
│   ├── services/            # Directory for service implementations
│   │   ├── __init__.py
│   │   ├── notification_service.py  # Handling notifications (Slack, Email)
│   │   ├── database_service.py      # DB interactions and queries
│   │   ├── api_service.py           # API interactions (e.g., OpenAI API)
│   │   └── analytics_service.py      # Performance tracking and analytics
│   │
│   ├── models/               # Data models and schemas
│   │   ├── __init__.py
│   │   ├── machine_state.py        # State representation
│   │   ├── lead.py                  # Lead data model
│   │   ├── product.py               # Product data model
│   │   └── user.py                  # User data model
│   │
│   ├── utils/               # Utilities and helper functions
│   │   ├── __init__.py
│   │   ├── logger.py               # Custom logging utilities
│   │   ├── validators.py           # Data validation functions
│   │   └── helpers.py              # Generic helper functions
│   │
│   └── tests/               # Directory for tests
│       ├── __init__.py
│       ├── test_agents.py         # Tests for agent behaviors
│       ├── test_workflows.py      # Tests for workflow processes
│       ├── test_services.py       # Tests for services
│       └── test_models.py         # Tests for data models
│
├── docs/                    # Documentation related folders
│   ├── API.md              # API documentation (endpoints, usage)
│   ├── Architecture.md      # Overview of system architecture
│   ├── Usage.md            # User guide and usage examples
│   └── Development.md       # Guidelines for contributing and development practices
│
└── docker/                 # Docker-related files
    ├── Dockerfile          # Dockerfile for setting up the application container
    └── docker-compose.yml   # Docker Compose file for multi-container setup


## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -e \".[dev]\"
````

2. Set up pre-commit hooks:

```bash
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy src

# Linting
flake8 src
```

## Documentation

- [API Documentation](docs/API.md) - API endpoints and usage
- [Architecture Guide](docs/Architecture.md) - System design and architecture
- [Development Guide](docs/Development.md) - Development guidelines and best practices
- [Usage Guide](docs/Usage.md) - Platform usage and examples

## Configuration

Key configuration options in `.env`:

```env
# Application
DEBUG=False
LOG_LEVEL=INFO

# API Keys
OPENAI_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here

# Services
SLACK_BOT_TOKEN=optional_token
SENDGRID_API_KEY=optional_key

# Database
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an [Issue](https://github.com/yourusername/ATTYX_AI/issues)
- Contact: <support@attyx.com>

## Acknowledgments

- Built with [PydanticAI](https://github.com/pydantic/pydantic-ai)
- Powered by [OpenAI](https://openai.com)
- Database by [Supabase](https://supabase.com)`
# ATTYX_AI
