## Banking System Project

A scalable banking system designed to handle large volumes of transaction data with performance, consistency, and maintainability in mind.

### 🔧 Architecture Highlights

1. **CQRS Pattern**: Separates responsibility between the command and query models for better scalability and maintainability.
2. **Event Sourcing**: Ensures data consistency by synchronizing the database via events rather than direct state changes.
3. **Command Server**: Handles concurrency by managing transactions in controlled, consistent units.
4. **Query Server**:
   - Uses single and composite indexing to optimize search performance.
   - Implements Redis caching to deliver fast API response times.
   - Supports both **cursor-based pagination** for efficient navigation and **offset-based pagination** for direct page access.

## 🚀 Installation Guide

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd banking_system
   ```

### 2. Create and Activate a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install -r query_server/requirements.txt
```
### 4. Apply Database Migrations
- Be sure to apply migrations for both the query and command servers:
```
cd query_server
python manage.py makemigrations
python manage.py migrate
```
### 5. Create a Superuser
```
python manage.py createsuperuser
```
### 6. Run the Development Server
```
python manage.py runserver
```
## 🐳 Docker Support
### 7. Run with Docker Compose
```
docker-compose up --build -d
```
## 🧾 Event Consumer
### 8. Start the Consumer for Query Synchronization
bash
```
python query_server/manage.py consumer
```
