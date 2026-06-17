# Tennis Team Website

A comprehensive, secure, and scalable website for managing tennis competition teams with Docker Compose deployment.

## 🎯 Project Overview

This project provides a complete solution for managing tennis competition teams with features including:

- **User Management**: Role-based access control (Admin, Coordinator, Player)
- **Match Planning**: Schedule, edit, and manage tennis matches
- **Player Availability**: Track player availability for matches
- **Team Management**: Organize teams and players
- **Notifications**: Hourly bundled email and in-app notifications
- **Responsibilities**: Assign tasks like transportation and refreshments
- **Responsive UI**: Mobile-friendly interface using Vue.js and Vuetify

## 🏗️ Technical Architecture

### Stack
- **Backend**: Django (Python) with Django REST Framework
- **Frontend**: Vue.js 3 with Vuetify UI framework
- **Database**: PostgreSQL with persistent volumes
- **Web Server**: Apache2 in Docker container
- **Containerization**: Docker Compose for multi-container orchestration
- **Background Tasks**: Celery with Redis for notification bundling
- **Real-time**: WebSocket support via Django Channels

### Services
1. **webserver**: Apache2 serving frontend and proxying API requests
2. **backend**: Django application with REST API
3. **frontend**: Vue.js development server (or built static files)
4. **database**: PostgreSQL database with initialization scripts
5. **redis**: Redis for Celery broker and caching
6. **celery**: Celery worker for background tasks
7. **celery-beat**: Celery beat for scheduled tasks

## 🚀 Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (2.0+)
- Git
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**:
```bash
cd /workspace/WesRosss__UitWijk/tennis-team-website
git init
git add .
git commit -m "Initial project structure"
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Build and start the containers**:
```bash
docker-compose build
docker-compose up -d
```

4. **Wait for services to initialize** (this may take a few minutes):
```bash
docker-compose logs -f
```

5. **Access the application**:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Coordinator**: username: `coordinator`, password: `admin123`
- **Player**: username: `player1`, password: `admin123`

## 📁 Project Structure

```
tennis-team-website/
├── backend/                  # Django Backend
│   ├── tennis_backend/       # Main Django project
│   │   ├── apps/             # Django apps
│   │   │   ├── users/        # User management with RBAC
│   │   │   ├── teams/        # Team management
│   │   │   ├── matches/      # Match management
│   │   │   ├── notifications/ # Notification system
│   │   │   └── api/          # API endpoints
│   │   ├── settings/         # Django settings (base, dev, prod)
│   │   ├── urls.py           # URL routing
│   │   ├── wsgi.py           # WSGI config
│   │   └── asgi.py           # ASGI config
│   ├── manage.py             # Django management script
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Vue.js Frontend
│   ├── public/               # Static files
│   ├── src/                  # Source code
│   │   ├── components/       # Vue components
│   │   ├── views/            # Page views
│   │   ├── store/            # Pinia stores
│   │   ├── router/           # Vue Router
│   │   ├── plugins/          # Vue plugins
│   │   ├── styles/           # SCSS styles
│   │   ├── utils/            # Utility functions
│   │   ├── services/         # API services
│   │   ├── App.vue           # Main App component
│   │   └── main.js           # Vue entry point
│   ├── package.json          # Node.js dependencies
│   └── vue.config.js         # Vue CLI config
│
├── docker/                   # Docker configurations
│   ├── apache.Dockerfile     # Apache2 Dockerfile
│   ├── backend.Dockerfile    # Django Dockerfile
│   ├── frontend.Dockerfile   # Vue.js Dockerfile
│   └── postgres/             # PostgreSQL initialization
│
├── docker-compose.yml        # Docker Compose configuration
├── README.md                # This file
└── .env.example             # Environment variables template
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=tennis_backend.settings.production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,webserver

# Database
DATABASE_URL=postgres://tennis_user:tennis_password@database:5432/tennis_db

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=Tennis Team <noreply@tennis-team.local>

# CORS
CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:8080,https://your-domain.com
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Run tests
docker-compose exec backend python manage.py test

# Build frontend
docker-compose exec frontend npm run build

# Restart specific service
docker-compose restart backend
```

## 🎨 Features

### User Roles & Permissions
- **Admin**: Full access to all features, user management, system settings
- **Coordinator**: Can create/edit matches, assign players, manage notifications
- **Player**: Can view schedules, update availability, receive notifications

### Match Management
- Create, edit, and cancel matches
- Assign home and away teams
- Track match status (scheduled, confirmed, cancelled, completed, postponed)
- Add match details (location, court, time, notes)

### Player Availability
- Players can mark themselves as available/unavailable/maybe for matches
- Coordinators can view availability for all players
- Availability updates trigger notifications to coordinators

### Notifications
- **Hourly Bundling**: Notifications are bundled and sent every hour
- **Delivery Methods**: Email, in-app, or both
- **User Preferences**: Users can configure notification preferences
- **Real-time**: WebSocket support for instant in-app notifications
- **Types**: Match created/updated/cancelled, assignment created/updated, availability requests, responsibility assignments

### Team Management
- Create and manage teams
- Assign coaches and captains
- Add players to teams
- Track player information and status

### Responsive UI
- Mobile-first design
- Vuetify Material Design components
- Dark/light mode support
- Accessible and user-friendly

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/token/` - Get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token

### Users
- `GET /api/users/` - List users (Admin only)
- `POST /api/users/` - Create user (Admin only)
- `GET /api/users/me/` - Get current user profile
- `PATCH /api/users/me/` - Update current user profile
- `POST /api/users/me/change-password/` - Change password

### Teams
- `GET /api/teams/` - List teams
- `POST /api/teams/` - Create team (Coordinator+)
- `GET /api/teams/{id}/` - Get team details
- `PATCH /api/teams/{id}/` - Update team (Coordinator+)
- `DELETE /api/teams/{id}/` - Delete team (Coordinator+)

### Matches
- `GET /api/matches/` - List matches
- `POST /api/matches/` - Create match (Coordinator+)
- `GET /api/matches/{id}/` - Get match details
- `PATCH /api/matches/{id}/` - Update match (Coordinator+)
- `DELETE /api/matches/{id}/` - Delete match (Coordinator+)

### Availability
- `GET /api/matches/{id}/availability/` - Get availability for match
- `POST /api/matches/{id}/availability/` - Update availability

### Assignments
- `GET /api/matches/{id}/assignments/` - Get assignments for match
- `POST /api/matches/{id}/assignments/` - Create assignment (Coordinator+)
- `DELETE /api/matches/{id}/assignments/{assignment_id}/` - Remove assignment (Coordinator+)

### Responsibilities
- `GET /api/matches/{id}/responsibilities/` - Get responsibilities for match
- `POST /api/matches/{id}/responsibilities/` - Create responsibility (Coordinator+)
- `PATCH /api/matches/{id}/responsibilities/{responsibility_id}/` - Update responsibility
- `DELETE /api/matches/{id}/responsibilities/{responsibility_id}/` - Delete responsibility

### Notifications
- `GET /api/notifications/` - List notifications for current user
- `PATCH /api/notifications/{id}/mark-read/` - Mark notification as read
- `POST /api/notifications/mark-all-read/` - Mark all notifications as read
- `GET /api/notifications/unread-count/` - Get unread notification count
- `GET /api/notifications/preferences/` - Get notification preferences
- `POST /api/notifications/preferences/` - Update notification preferences

## 📊 Database Schema

### Core Tables
- **Users**: User accounts with role-based access control
- **Teams**: Tennis teams with coaches and captains
- **Players**: Players belonging to teams with positions and skill levels
- **Matches**: Match schedules with teams, locations, and status
- **PlayerAvailability**: Player availability for specific matches
- **MatchAssignments**: Player assignments to matches with positions
- **Responsibilities**: Tasks assigned to users for matches
- **Notifications**: User notifications with bundling support
- **NotificationPreferences**: User notification preferences
- **NotificationBatches**: Batch tracking for hourly notifications

## 🔄 Workflow

### Match Creation Flow
1. Coordinator creates a new match with date, time, location, and teams
2. System creates notifications for all players in both teams
3. Players receive notifications (email and/or in-app)
4. Players update their availability
5. Coordinators receive notifications about availability updates
6. Coordinator assigns players to positions
7. Assigned players receive notifications
8. Coordinator assigns responsibilities (transportation, refreshments, etc.)

### Notification Flow
1. Event occurs (match created, player assigned, etc.)
2. System creates notification records in database
3. Notifications are marked as PENDING with scheduled_for timestamp
4. Celery Beat runs hourly and triggers send_hourly_notifications task
5. Task groups notifications by user and delivery type
6. Email notifications are bundled and sent via SMTP
7. In-app notifications are marked as SENT
8. Users can view and mark notifications as read

## 🛡️ Security

### Authentication
- JWT (JSON Web Token) authentication
- Token expiration and refresh
- Secure password hashing (bcrypt)
- CSRF protection for forms

### Authorization
- Role-based access control (RBAC)
- Permission checks on API endpoints
- Object-level permissions

### Data Protection
- HTTPS support (SSL certificates)
- Secure cookies
- Security headers (XSS protection, HSTS, etc.)
- Input validation and sanitization

## 📈 Performance

### Caching
- Redis caching for frequently accessed data
- Celery result caching
- Browser caching for static assets

### Database Optimization
- Indexes on frequently queried fields
- Query optimization with select_related and prefetch_related
- Pagination for API endpoints

### Scalability
- Containerized architecture
- Horizontal scaling support
- Load balancing ready
- Database connection pooling

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test users

# Run with coverage
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
```

### Frontend Tests
```bash
# Run unit tests
docker-compose exec frontend npm run test:unit

# Run e2e tests
docker-compose exec frontend npm run test:e2e

# Run linting
docker-compose exec frontend npm run lint
```

## 📝 Deployment

### Production Deployment

1. **Set up server**:
   - Debian 11/12 server
   - Install Docker and Docker Compose
   - Configure firewall (open ports 80, 443)

2. **Configure environment**:
   - Set production environment variables
   - Configure email settings
   - Set up SSL certificates

3. **Deploy**:
   ```bash
   git clone <repository-url>
   cd tennis-team-website
   cp .env.example .env
   # Edit .env for production
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

4. **Initialize database**:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   docker-compose exec backend python manage.py collectstatic
   ```

5. **Set up monitoring**:
   - Log aggregation
   - Error tracking
   - Performance monitoring

### Development Deployment

For local development, use the standard docker-compose.yml:

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:8080
- Backend: http://localhost:8000
- Database: localhost:5432
- Redis: localhost:6379

## 📚 Documentation

### API Documentation
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

### User Manual
See the [User Manual](docs/user-manual.md) for detailed usage instructions.

### Developer Guide
See the [Developer Guide](docs/developer-guide.md) for development setup and best practices.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Python: PEP 8, Black formatter
- JavaScript: ESLint, Prettier
- CSS: SCSS, BEM methodology
- Commit messages: Conventional Commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django: https://www.djangoproject.com/
- Vue.js: https://vuejs.org/
- Vuetify: https://vuetifyjs.com/
- Docker: https://www.docker.com/
- PostgreSQL: https://www.postgresql.org/
- Celery: https://docs.celeryq.dev/

## 📞 Support

For support, questions, or feedback:
- Open an issue on GitHub
- Contact the development team

---

**Tennis Team Website** - Built with ❤️ for tennis competition management