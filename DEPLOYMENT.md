# Logeion MCP Server Deployment Guide

This guide covers various deployment options for the Logeion MCP Server, from local development to production environments.

## Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- Git
- Access to the Latin dictionary database file (`dvlg-wheel-mini.sqlite`)

## Local Development Deployment

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/logeion-mcp-server.git
cd logeion-mcp-server
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download la_core_web_lg
```

### 5. Add Database File

Place the `dvlg-wheel-mini.sqlite` file in the project root directory.

### 6. Run the Server

```bash
python logeion.py
```

The server will start on stdio transport and be ready to accept MCP client connections.

## Docker Deployment

### 1. Build the Image

```bash
docker build -t logeion-mcp-server .
```

### 2. Run the Container

```bash
docker run -it --rm \
  -v $(pwd)/dvlg-wheel-mini.sqlite:/app/dvlg-wheel-mini.sqlite:ro \
  logeion-mcp-server
```

### 3. Using Docker Compose

```bash
docker-compose up --build
```

## Production Deployment

### 1. Environment Variables

Create a `.env` file for production configuration:

```bash
# Production configuration
LOG_LEVEL=WARNING
PYTHONUNBUFFERED=1
DATABASE_PATH=/app/data/dvlg-wheel-mini.sqlite
```

### 2. Docker Production Build

```dockerfile
# Production Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install only production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download la_core_web_lg

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('/app/data/dvlg-wheel-mini.sqlite'); conn.close(); print('OK')" || exit 1

CMD ["python", "logeion.py"]
```

### 3. Kubernetes Deployment

Create a `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logeion-mcp-server
  labels:
    app: logeion-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: logeion-mcp-server
  template:
    metadata:
      labels:
        app: logeion-mcp-server
    spec:
      containers:
      - name: logeion-mcp
        image: logeion-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "WARNING"
        - name: PYTHONUNBUFFERED
          value: "1"
        volumeMounts:
        - name: database-storage
          mountPath: /app/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sqlite3; conn = sqlite3.connect('/app/data/dvlg-wheel-mini.sqlite'); conn.close(); print('OK')"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sqlite3; conn = sqlite3.connect('/app/data/dvlg-wheel-mini.sqlite'); conn.close(); print('OK')"
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: database-storage
        persistentVolumeClaim:
          claimName: logeion-database-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logeion-database-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## MCP Hub Integration

### 1. Server Configuration

To make your server discoverable on MCP Hub, ensure your server provides:

- Proper tool schemas with descriptions
- Server information endpoint
- Health check capabilities
- Clear documentation

### 2. Testing with MCP Clients

Test your server with various MCP clients:

```bash
# Test with MCP CLI client
mcp-client --server python logeion.py

# Test server info
mcp-client --server python logeion.py --tool get_server_info

# Test word lookup
mcp-client --server python logeion.py --tool get_word --args '{"word": "amare"}'
```

## Monitoring and Health Checks

### 1. Health Check Endpoint

The server includes built-in health checks:

```python
# Check database connectivity
python -c "import sqlite3; conn = sqlite3.connect('dvlg-wheel-mini.sqlite'); conn.close(); print('OK')"

# Check spaCy model
python -c "import spacy; nlp = spacy.load('la_core_web_lg'); print('OK')"
```

### 2. Logging

Configure logging levels for different environments:

```python
# Development
logging.basicConfig(level=logging.DEBUG)

# Production
logging.basicConfig(level=logging.WARNING)
```

### 3. Metrics

Consider adding metrics collection:

```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper
```

## Security Considerations

### 1. Database Access

- Use read-only access for the dictionary database
- Implement proper file permissions
- Consider database encryption for sensitive data

### 2. Network Security

- Use HTTPS in production
- Implement rate limiting
- Add authentication if needed

### 3. Container Security

- Run containers as non-root users
- Use minimal base images
- Regularly update dependencies

## Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download la_core_web_lg
   ```

2. **Database Connection Errors**
   - Verify database file exists and is readable
   - Check file permissions
   - Ensure correct file path

3. **Memory Issues**
   - Monitor container memory usage
   - Adjust resource limits
   - Consider database optimization

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python logeion.py
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_entries_head ON Entries(head);

-- Analyze table statistics
ANALYZE Entries;
```

### 2. Caching

Implement result caching for frequently searched words:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_word_search(word):
    return get_word(word)
```

### 3. Connection Pooling

For high-traffic scenarios, consider connection pooling:

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()
```

## Support and Maintenance

### 1. Regular Updates

- Keep dependencies updated
- Monitor for security vulnerabilities
- Update spaCy models regularly

### 2. Backup Strategy

- Regular database backups
- Configuration file backups
- Container image versioning

### 3. Documentation

- Keep deployment guides updated
- Document configuration changes
- Maintain troubleshooting guides

---

For additional support, please refer to the main README.md or create an issue on the project repository.
