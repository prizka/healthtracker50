# Health Tracker Dashboard

Welcome to the Health Tracker Dashboard project! This application helps patients with chronic disease(s) to monitor their health metrics, including blood pressure, blood glucose levels, and some other important laboratory parameters. Below you will find everything you need to set up, configure, and use this application.


## Overview

The Health Tracker Dashboard is a personal health management app that allows users to log and visualize various health parameters. Users can register, log in, and manage their profiles while tracking health data over time.


## Features

- Register and manage user profiles
- Log health metrics including blood pressure, blood glucose, and laboratory (lipid profile and Hb1Ac) measurements
- Visualize logged data through line charts to show the trends
- Update and delete health entries


## Requirements

- Python version 3
- Flask
- SQLite3
- CS50 Library for Python


## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/health-tracker-dashboard.git
   cd health-tracker-dashboard
   ```

2. **Set Up Python Environment:**

    Create and activate a virtual environment
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**

    Install necessary packages:
    ```bash
    pip install -r requirements.txt
    ```
    

## Usage

1. **Run the Application:**

    Start the Flask app:
    ```
    flask run
    ```

2. **Access the Dashboard:**

    Navigate to http://localhost:5000 in your web browser.


## Routes and Functionality

- **Register:** `/register`  
  Create a new user account.

- **Login:** `/login`  
  Access your account and manage sessions.

- **Home:** `/dashboard`  
  View and log health metrics; visualize data trends.

- **Months at the Navigation Bar:** `/dashboard?month=?&year=?`  
  Access health metrics for a specific month and year, showcasing line trends for that specific month and year.

- **Daily Log:** `/log/<date>`  
  Log health metrics like blood pressure, blood glucose, symptoms for a specific date.

- **Laboratory Report:** `/report`  
  View and manage lab results, including visualization of logged data.

- **Profile:** `/profile`  
  Manage personal information, including updating details and profile picture.

- **Settings:** `/settings`  
  Access settings for account management, such as changing password, viewing summaries, and deleting entries.

- **Change Password:** `/settings/change_password`  
  Update your password securely.

- **Summary:** `/settings/summary`  
  View a consolidated summary of health logs and lab results by month.

- **Logout:** `/logout`  
  End your session and safely log out.

- **Delete Log:** `/delete/log/<int:log_id>`  
  Remove a specific health log entry by date.

- **Delete Lab Entry:** `/delete/lab/<int:lab_id>`  
  Delete a specific lab result by date.

- **Log Chart Data:** `/logs_chart`  
  Retrieve chart data for logs as JSON for visualization.

- **Lab Component:** `/lab_component`  
  Save additional laboratory data logs.

- **Lab Graph Data:** `/lab_graph`  
  Fetch lab metrics in JSON format for graph rendering.


## Troubleshooting

- Database Issues: Ensure the database is initialized and migrations are applied.
- Print the Error Messages: Check the console for error details and verify configurations.
- Missing Dependencies: Ensure all dependencies are installed from requirements.txt.


## Support

For additional support, please contact kelvinsupriami@hms.harvard.edu or prizka_aviliapuspa@hms.harvard.edu.

## Link to the short explanatory video
https://youtu.be/XJzgCoLOm8M

This README provides an overview and guide to effectively use the Health Tracker Dashboard. For further questions and feedback, feel free to reach out. Happy tracking!
