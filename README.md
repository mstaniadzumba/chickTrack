# ChickTrack 

A simple web application for managing chicken farming operations, tracking batches, orders, and expenses.

## Features

- **User Authentication**: Register and login system
- **Batch Management**: Create and update chicken batches by month
- **Order Tracking**: Manage customer orders with payment tracking
- **Expense Management**: Track farm expenses by batch
- **Dashboard**: View batch statistics (chickens bought, dead, live)
- **User Tracking**: Track who created and updated records

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Storage**: localStorage for user sessions

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install flask
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open browser to `http://localhost:5000`

## Usage

1. **Register** a new account or **Login** with existing credentials
2. **Create batches** for different months/periods
3. **Add orders** from customers and track payments
4. **Record expenses** related to each batch
5. **View dashboard** to see batch statistics
6. **Update records** as needed (payments, expenses, batch info)

## Database

The app uses SQLite with the following tables:
- `users` - User accounts
- `batch` - Chicken batches by month
- `orders` - Customer orders
- `expenses` - Farm expenses

## File Structure

```
chickTrack/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models/             # Database models
├── routes/             # API routes
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── chicken_management.db  # SQLite database
```