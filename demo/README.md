# Task Manager API

Simple REST API for managing tasks built with Flask.

## Features

- Create, read, update, delete tasks
- Task priorities and status tracking
- Search functionality
- Statistics dashboard
- In-memory caching for performance

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python flask_app.py

# Run tests (some will fail due to bugs!)
pytest tests/ -v
```

### Using Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📚 API Endpoints

### Health Check
```bash
GET /
```

### Tasks
```bash
# Get all tasks
GET /tasks

# Get task statistics
GET /tasks/stats

# Create task
POST /tasks
{
  "title": "My Task",
  "description": "Optional description",
  "priority": 1
}

# Get specific task
GET /tasks/<id>

# Update task
PUT /tasks/<id>
{
  "title": "Updated Title",
  "done": true
}

# Delete task
DELETE /tasks/<id>

# Search tasks
GET /tasks/search?q=keyword
```

### Cache Management
```bash
# Get cache stats
GET /tasks/cache

# Clear cache
POST /tasks/clear-cache
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## API Examples
   
   Steps to reproduce:
   1. Start fresh application with no tasks
   2. Call GET /tasks/stats
   3. Application crashes
   
   Expected: Should return 0% completion rate
   Actual: ZeroDivisionError: division by zero
   
   File: demo/flask_app.py
   Function: get_stats()
   ```

2. **Create Issue for Bug #2:**
   ```
   Title: Missing input validation crashes POST /tasks endpoint
   
   Description:
   The POST /tasks endpoint doesn't validate required fields, causing KeyError.
   
   Steps to reproduce:
   1. POST /tasks with JSON missing 'title' field
   2. Application crashes
   
   Expected: Should return 400 Bad Request with error message
   Actual: 500 Internal Server Error - KeyError: 'title'
   
   File: demo/flask_app.py
   Function: create_task()
   ```

### Watch the Agent Work

1. Agent receives Issue from GitHub
2. Clones repository to `repos/{UUID}/`
3. Analyzes `demo/flask_app.py`
4. Detects bug (e.g., division by zero)
5. Generates fix with proper validation
6. Creates Pull Request
7. AI Reviewer checks the fix
8. Iterates until all tests pass

### Create a task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": 2}'
```

### Get all tasks
```bash
curl http://localhost:5000/tasks
```

### Search tasks
```bash
curl "http://localhost:5000/tasks/search?q=groceries"
```

### Get statistics
```bash
curl http://localhost:5000/tasks/stats
```

## Technology Stack

- **Flask 3.0** - Web framework
- **SQLite3** - Database
- **pytest** - Testing framework
- **Docker** - Containerization

## Known Issues

Please check the [Issues](https://github.com/nidzhadizzatov/megaschool-ai-izzatov-nidzhad-2026/issues) page for known bugs and feature requests.

## License

MIT

