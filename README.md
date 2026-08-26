# ERP System

Backend for a modular ERP system under development, built with Python, Django, and Django REST Framework. The project models common small-business operations and prioritizes explicit business rules, data integrity, authorization, and transactional inventory operations.

The current scope is backend-only. There is no frontend, payments, reporting, dashboard, or production deployment configuration.

## Goals

- Build a practical ERP for small businesses.
- Practice relational design, REST APIs, and Django development.
- Keep business rules separate from the HTTP layer where appropriate.
- Apply validation, permissions, transactions, and automated testing.
- Evolve the project incrementally and maintainably.

## Stack

- Python 3.13
- Django 6.1
- Django REST Framework 3.18.0
- `django-filter` 26.1
- PostgreSQL through `psycopg` 3.3.4
- `python-dotenv` 1.2.2
- Git

The PostgreSQL server version is not fixed in the code. The connection is configured through environment variables.

## Architecture

The backend is organized as a Django project with one application per domain:

- `core`: abstract timestamped model and reusable permissions.
- `users`: custom user model using email as its identifier, and the authenticated-user endpoint.
- `customers`: individual and company customers.
- `suppliers`: individual and company suppliers.
- `products`: products and current stock levels.
- `sales`: sales and their line items.
- `purchases`: purchases and their line items.
- `stock_adjustments`: manual stock adjustments and their line items.

Routes are centralized in `backend/config/urls.py`. Sales and purchase stock operations are separated into dedicated services.

## Current Functionality

### Users and Permissions

- Custom user model with a unique email as `USERNAME_FIELD`.
- Passwords managed by Django's authentication system.
- Support for Django groups and permissions.
- Token authentication for the API.
- Global API permission requiring authenticated users.
- Model permissions for CRUD operations.
- Specific permissions to confirm or cancel sales and purchases, and to activate or deactivate customers and suppliers.
- `GET /api/users/me/` endpoint for the authenticated user.

There are currently no registration, login, or token-issuance endpoints. Tokens must be managed outside the implemented API.

### Customers and Suppliers

Both modules support managing individuals and companies with:

- Optional tax identification that is unique when provided.
- Contact details, address, and notes.
- Active/inactive status.
- Validation consistent with the record type: individuals require a first and last name; companies require a business name.
- API actions to activate and deactivate records.
- Filtering, searching, ordering, and pagination.

### Products and Inventory

Products include a name, unique SKU, description, price, cost, current stock, minimum stock, and active/inactive status.

- Stock is read-only in the product serializer.
- The API supports product filtering and ordering.
- Stock changes are made through sales, purchases, and adjustments.
- Sales and purchase operations lock product rows with `select_for_update()`.
- The `Product` model does not contain all logic needed to prevent negative stock by itself; that rule is applied in inventory operation services.

### Sales

```text
DRAFT -> CONFIRMED -> CANCELLED
```

A sale belongs to a customer and may contain line items with a product, quantity, and unit price. Each product can appear only once per sale, and each line exposes a calculated subtotal.

- Only draft sales can be modified or receive line items.
- A sale must have line items to be confirmed.
- Confirmation decreases stock and rejects insufficient inventory.
- Cancelling a confirmed sale restores stock.
- Confirmation and cancellation are atomic operations.
- These actions require the `confirm_sale` and `cancel_sale` permissions.

### Purchases

```text
DRAFT -> CONFIRMED -> CANCELLED
```

A purchase belongs to a supplier and may contain line items with a product, quantity, and unit cost. Each product can appear only once per purchase, and each line exposes a calculated subtotal.

- Only draft purchases can be modified or receive line items.
- A purchase must have line items to be confirmed.
- Confirmation increases stock.
- Cancelling a confirmed purchase decreases the stock it previously added.
- Cancellation is rejected if it would result in negative stock.
- Confirmation and cancellation are atomic operations.
- These actions require the `confirm_purchase` and `cancel_purchase` permissions.

### Stock Adjustments

Adjustments allow stock to be manually increased or decreased and follow an independent lifecycle:

```text
DRAFT -> CONFIRMED
```

Each line specifies a product, type (`INCREASE` or `DECREASE`), and quantity. Confirmation records the previous stock, resulting stock, confirming user, and confirmation date. Decreases cannot result in negative stock.

The module provides an API and model validation, but does not yet have effective automated tests. It also has no cancellation state. Confirmation should be reviewed together with the common permission system before being considered ready for non-admin users.

## REST API

All API routes require authentication. Django Admin routes use Django's own authentication.

```text
/admin/
/api/users/me/
/api/customers/
/api/suppliers/
/api/products/
/api/sales/
/api/sale-items/
/api/purchases/
/api/purchase-items/
/api/stock-adjustments/
/api/stock-adjustment-items/
```

The main resources expose CRUD operations according to their permissions. Sales and purchases include `confirm` and `cancel` actions; customers and suppliers include `activate` and `deactivate`; adjustments include `confirm`.

The global DRF configuration enables:

- `TokenAuthentication`.
- `IsAuthenticated` as the default permission.
- Filtering with `django-filter`.
- Searching and ordering where configured by each view.
- Page-number pagination with 20 items per page.

Search is not available uniformly across all resources. For example, products have filters and ordering but do not configure `search_fields`.

## Integrity and Transactions

The project combines:

- Model and serializer validation.
- Database constraints, including unique SKUs, tax IDs, and document/product line items.
- Protected relationships using `on_delete=PROTECT` where appropriate.
- State restrictions for sales, purchases, and their line items.
- `transaction.atomic` for confirmations and cancellations that change stock.
- Row locking with `select_for_update()` during sales and purchase operations.
- Validation for positive quantities and non-negative prices and costs.

An inventory operation that fails should roll back its changes within the transaction.

## Automated Tests

The suite has effective coverage for:

- Authenticated users and the `/api/users/me/` endpoint.
- Customer and supplier CRUD, validation, filtering, searching, ordering, and activation.
- Product CRUD, permissions, filtering, ordering, and stock protection.
- Sales services and endpoints: states, stock, confirmation, cancellation, and transactional rollback.
- Purchases: CRUD, line items, permissions, states, stock, and cancellation.

`core/tests.py` and `stock_adjustments/tests.py` currently contain only test skeletons. Stock adjustment behavior therefore still needs automated coverage.

From `backend/`, tests can be run by module or for the entire project:

```bash
python manage.py test users
python manage.py test customers
python manage.py test suppliers
python manage.py test products
python manage.py test sales
python manage.py test purchases
python manage.py test stock_adjustments
python manage.py test
```

## Project Structure

```text
erp/
├── README.md
└── backend/
    ├── manage.py
    ├── requirements.txt
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   └── ...
    ├── core/
    ├── users/
    ├── customers/
    ├── suppliers/
    ├── products/
    ├── sales/
    ├── purchases/
    └── stock_adjustments/
```

Domain applications contain their models, serializers, views, URLs, migrations, and tests. Sales and purchases also contain services for transactional inventory operations.

## Local Development

The current configuration is for development: `DEBUG=True`, an empty `ALLOWED_HOSTS`, and a secret key defined in settings. It should not be used as-is in production.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies from `backend/`:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Create `backend/.env` with the PostgreSQL configuration:

   ```dotenv
   DB_NAME=database_name
   DB_USER=database_user
   DB_PASSWORD=database_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. Apply migrations, check the configuration, and start the server:

   ```bash
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```

   The server is available at `http://127.0.0.1:8000/`.

## Status and Next Steps

### Implemented

- [x] Modular Django structure.
- [x] PostgreSQL integration through environment variables.
- [x] Custom user and Django permissions.
- [x] Token-authenticated REST API.
- [x] Customers, suppliers, and products.
- [x] Sales and purchases with states and stock operations.
- [x] Manual stock adjustments.
- [x] Configurable filtering, ordering, and pagination.
- [x] Tests for the main modules.

### Pending or Under Review

- [ ] Add login, registration, and token-issuance endpoints.
- [ ] Complete permissions and tests for stock adjustment confirmation.
- [ ] Expand coverage for `core` and `stock_adjustments`.
- [ ] Formally document the API contract.
- [ ] Review and expand the Django Admin configuration.
- [ ] Separate development and production configuration.

### Future

- [ ] Frontend.
- [ ] Payments.
- [ ] Reporting and dashboard.
- [ ] Docker and Docker Compose.
- [ ] Deployment and continuous integration.
- [ ] External integrations.

## License

To be defined.
