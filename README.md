# OCI Email Suppression Service

A FastAPI-based microservice for managing OCI Email Delivery suppressions.

## Project Goal

Create a scalable FastAPI server where multiple business logic scripts can be deployed as a single Docker image, with each script exposed via different API endpoints.

## Current Scripts

1. **Email Suppression Removal** - Check and remove email addresses from OCI suppression list

## Project Structure (To Be Created)

```
suppression_list/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── routers/                   # API endpoints (one router per script/feature)
│   │   ├── __init__.py
│   │   └── email_suppression.py  # Email suppression endpoints
│   └── services/                  # Business logic (refactored scripts)
│       ├── __init__.py
│       └── oci_email_suppression.py
├── script.py                      # Original script (keep for reference)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image definition
├── .dockerignore                  # Files to exclude from Docker build
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Implementation Checklist

### Phase 1: Setup Project Structure
- [ ] **Task 1.1**: Create folder structure (`app/`, `app/routers/`, `app/services/`)
- [ ] **Task 1.2**: Create `requirements.txt` with dependencies (FastAPI, uvicorn, oci, python-dotenv)
- [ ] **Task 1.3**: Create `__init__.py` files in all packages

### Phase 2: Refactor Script to Service
- [ ] **Task 2.1**: Create `app/services/oci_email_suppression.py`
- [ ] **Task 2.2**: Refactor `script.py` logic into reusable functions
- [ ] **Task 2.3**: Add proper error handling and return types

### Phase 3: Create FastAPI Application
- [ ] **Task 3.1**: Create `app/config.py` for configuration management
- [ ] **Task 3.2**: Create `app/main.py` with FastAPI app initialization
- [ ] **Task 3.3**: Add health check endpoint
- [ ] **Task 3.4**: Create `app/routers/email_suppression.py` with API endpoints

### Phase 4: Containerization
- [ ] **Task 4.1**: Create `Dockerfile` with multi-stage build
- [ ] **Task 4.2**: Create `.dockerignore` file
- [ ] **Task 4.3**: Create `.env.example` for environment variables
- [ ] **Task 4.4**: Test Docker build locally

### Phase 5: Documentation & Testing
- [ ] **Task 5.1**: Update README with API documentation
- [ ] **Task 5.2**: Add example API calls
- [ ] **Task 5.3**: Test all endpoints

## API Endpoints (Planned)

### Email Suppression
- `GET /` - Health check
- `GET /api/v1/email-suppression/{email}` - Check if email is suppressed
- `DELETE /api/v1/email-suppression/{email}` - Remove email from suppression list

## Future Scripts
As you add more scripts, each will follow the same pattern:
1. Add service in `app/services/your_service.py`
2. Add router in `app/routers/your_router.py`
3. Register router in `app/main.py`
4. Expose via different path (e.g., `/api/v1/your-feature/`)

## Configuration

The service will use environment variables for configuration:
- `OCI_TENANCY_OCID` - OCI Tenancy OCID
- `OCI_REGION` - OCI Region (default: ap-mumbai-1)

## Let's Start!

We'll go through each task one by one. Ready to begin with **Task 1.1**?
