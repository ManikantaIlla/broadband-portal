Trailblazer Broadband Subscription Portal
A comprehensive broadband subscription management system built with Streamlit, featuring AI-powered plan recommendations, detailed analytics, and intuitive user and admin dashboards.

Introduction
Trailblazer is a modern broadband subscription portal that provides users with a seamless experience for managing their internet plans. The system leverages machine learning to offer personalized plan recommendations and includes comprehensive analytics for both users and administrators.

User Dashboard Features
1. Current Plan Management
Visual Plan Overview: Users can view their current subscription details with a semi-circular progress indicator showing days remaining.
Plan Actions: Users can easily upgrade, downgrade, or cancel their subscription with confirmation dialogs.
Prorated Billing: For upgrades, the system calculates prorated amounts for the remaining billing period.
2. Data Usage Insights
Usage Analytics: Comprehensive view of data consumption patterns with daily usage trends.
Usage Patterns: Analysis of user behavior (light, moderate, heavy) with personalized recommendations.
Plan Utilization: Visual indicators showing how much of the data limit has been used.
Peak vs. Off-Peak Analysis: Detailed breakdown of usage during different times of day.
3. Plan Exploration
All Available Plans: Browse all broadband plans with filtering options by price, speed, and type.
Plan Comparison: Side-by-side comparison of multiple plans to help users make informed decisions.
ML-Powered Recommendations: Personalized plan suggestions based on usage patterns and preferences.
4. Subscription History
Historical Data: Complete record of past subscriptions with status, dates, and plan details.
Billing History: Track all payments, including successful transactions and failed payments.
5. Quick Actions
Notification System: Real-time alerts for plan expirations and important account updates.
Self-Service Options: Easy access to manage WiFi, apply for new connections, pay bills, and get support.
Admin Dashboard Features
1. Analytics Dashboard
Revenue Analytics: Track daily revenue trends and transaction volumes.
User Growth: Monitor new user registrations and cumulative user growth.
Plan Performance: Analyze plan popularity and revenue distribution across different plans.
2. ML Model Management
Model Training: Train and retrain the recommendation model with updated data.
Performance Metrics: View model accuracy and feature importance.
Model Evaluation: Detailed classification reports and performance analysis.
3. Plans Management
CRUD Operations: Create, read, update, and delete broadband plans.
Bulk Upload: Import multiple plans at once using CSV files.
Plan Configuration: Set detailed plan attributes including speed, data limits, pricing, and features.
4. User Management
User Administration: Manage user accounts with full CRUD capabilities.
Role Management: Assign and modify user roles (user/admin).
Notification System: Send targeted messages to user segments (active, inactive, all).
5. Support Management
Ticket Tracking: Monitor support tickets by status and category.
Performance Metrics: Track resolution times and ticket volumes.
Categorized Views: Browse tickets by status (resolved, not resolved, ongoing).
6. System Settings
Configuration Management: View and modify system configurations.
Database Status: Monitor database health and migration status.
System Statistics: Track key metrics like database size and model information.
Technical Implementation
Architecture
Frontend: Built with Streamlit for rapid development and deployment.
Database: SQLite for data storage with comprehensive schema for users, plans, subscriptions, payments, and usage.
Machine Learning: Scikit-learn for plan recommendation models with feature engineering and model evaluation.
Key Components
Authentication System: Secure login for both users and administrators with password hashing.
Subscription Management: Handles plan upgrades, downgrades, and cancellations with proper business logic.
Usage Analytics: Tracks and analyzes user data consumption patterns.
Notification System: Real-time alerts and communications for users.
Data Models
Users: Stores user information, credentials, and preferences.
Plans: Contains broadband plan details including speed, data limits, and pricing.
Subscriptions: Links users to plans with status tracking and renewal information.
Payments: Records all financial transactions with status and method details.
Usage: Tracks daily data consumption with detailed breakdowns.
Notifications: Manages system communications to users.
Installation and Setup
Prerequisites
Python 3.8+
pip package manager
Installation
Clone the repository:
bash

Line Wrapping

Collapse
Copy
1
2
git clone https://github.com/yourusername/trailblazer-broadband.git
cd trailblazer-broadband
Install required packages:
bash

Line Wrapping

Collapse
Copy
1
pip install streamlit pandas scikit-learn numpy python-dateutil plotly joblib
Run the application:
bash

Line Wrapping

Collapse
Copy
1
streamlit run app.py
Initial Setup
The application automatically creates the database and required tables on first run.
Default admin account:
Username: admin
Password: admin123
Sample data is automatically generated for demonstration purposes.
Usage


For Users
Sign up for a new account or log in with existing credentials.
View your current plan and usage analytics.
Explore recommended plans based on your usage patterns.
Compare different plans to find the best fit.
Upgrade, downgrade, or cancel your subscription as needed.
Track your subscription and payment history.
For Administrators
Log in with admin credentials.
Monitor business analytics and user growth.
Manage broadband plans and pricing.
Handle user accounts and support tickets.
Train and evaluate the ML recommendation model.
Configure system settings and send notifications.
Features in Development
Enhanced payment gateway integration
Mobile application support
Advanced reporting and export features
Integration with external billing systems
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Support
For support, please open an issue in the GitHub repository or contact the development team.