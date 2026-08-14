# ERP System

A modular ERP (Enterprise Resource Planning) system built with Python and Django, initially designed to solve real-world management needs for a small business.

The project is being developed incrementally with a focus on learning backend development, applying good software engineering practices, and building a solid portfolio project.

## Goals

- Build a practical ERP system for small businesses.
- Gain hands-on experience with Python and Django.
- Learn relational database design with PostgreSQL.
- Apply software engineering and backend development best practices.
- Develop a modular and maintainable architecture.
- Gradually introduce testing, APIs, Docker, and deployment.

## Tech Stack

### Current

- **Python**
- **Django**
- **PostgreSQL**
- **Git**

### Planned

- Django REST Framework
- HTML / CSS / JavaScript
- Automated testing
- Docker / Docker Compose
- Production deployment

## Current Features

The project currently includes:

- Custom user model with email-based authentication.
- Django Admin integration.
- PostgreSQL database integration.
- Reusable timestamped model.
- Customer management model.
- Customer type support for:
  - Individuals
  - Companies
- Customer data validation.
- PostgreSQL database constraints for customer data integrity.
- Database migrations.

## Project Structure

```text
erp/
├── backend/
│   ├── config/
│   ├── core/
│   ├── customers/
│   ├── users/
│   └── manage.py
├── .gitignore
└── README.md
```

## Development

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Configure the environment variables required by the project, then run the database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Roadmap

The project will be developed incrementally. Planned modules include:

- [x] Project setup
- [x] PostgreSQL integration
- [x] Custom user model
- [x] Django Admin setup
- [x] Core timestamped model
- [x] Customer model
- [x] Customer database constraints
- [ ] Customer Admin interface
- [ ] Suppliers
- [ ] Products and categories
- [ ] Inventory
- [ ] Sales
- [ ] Purchases
- [ ] Payments
- [ ] Reporting and dashboard
- [ ] REST API
- [ ] Automated testing
- [ ] Docker
- [ ] Deployment
- [ ] Documentation and portfolio preparation

## License

License to be determined.
