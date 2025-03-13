# Baykuş OSINT Tool

Baykuş (Turkish for "Owl") is a comprehensive Open Source Intelligence (OSINT) tool designed for collecting, analyzing, and visualizing data from various online sources. Just like an owl's keen vision in the darkness, Baykuş helps security researchers, OSINT analysts, and security professionals find and extract meaningful insights from the digital realm.

## Features

- **Comprehensive OSINT Capabilities**: From social media monitoring to Google dorking, domain analysis to email verification
- **Asset Discovery and Tracking**: Identify and monitor digital assets associated with targets
- **Relationship Analysis**: Map connections between different digital assets
- **Risk Assessment**: Score and prioritize discovered assets based on security risks
- **Customizable Reports**: Generate detailed reports with various export options

## Technical Architecture

Baykuş is built with a modern, scalable architecture:

- **Backend**: Django and Django REST Framework
- **Frontend**: React with Tailwind CSS (dark theme)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Authentication**: JWT-based authentication

## Project Structure

```
baykus/
├── core/                  # Core functionality and models
│   ├── models.py          # Data models for targets, assets, etc.
│   ├── views.py           # API endpoints for core functionality
│   ├── serializers.py     # Serializers for API data
│   └── ...
├── users/                 # User management
│   ├── models.py          # Custom user model
│   ├── views.py           # User-related API endpoints
│   └── ...
├── connectors/            # External service integrations
│   ├── models.py          # Models for connectors and API keys
│   ├── adapters/          # Adapter classes for different services
│   │   ├── base.py        # Base adapter class
│   │   ├── social_media.py # Social media adapters
│   │   └── ...
│   └── ...
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
└── baykus/                # Main project settings
    ├── settings.py        # Django settings
    ├── urls.py            # Main URL configuration
    └── ...
```

## API Structure

Baykuş follows a RESTful API design with the following main endpoints:

- `/api/users/` - User management
- `/api/core/targets/` - Target management
- `/api/core/assets/` - Asset management
- `/api/core/dorks/` - Google dork management
- `/api/connectors/` - External connector management

All API endpoints are documented using Swagger/OpenAPI, accessible at `/api/docs/`.

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Node.js and npm (for frontend)

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/baykus.git
   cd baykus
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Usage

1. Access the web interface at `http://localhost:3000`
2. Log in with your credentials
3. Create a new target to begin your OSINT investigation
4. Use the various tools to discover and analyze assets related to your target
5. Generate reports based on your findings

## Contributing

We welcome contributions to Baykuş! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- The name "Baykuş" (Owl) was chosen to represent the tool's ability to see and gather intelligence in the digital darkness.
- Thanks to all the open-source projects that made this tool possible.

## Disclaimer

Baykuş is an OSINT tool meant for legitimate security research, digital asset management, and security assessment. Always use this tool in accordance with applicable laws and regulations. The authors are not responsible for any misuse of this software.