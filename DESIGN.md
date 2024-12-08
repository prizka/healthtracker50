# Health Tracker Dashboard: Design Document
***by Kelvin Supriami and Prizka Avilia Puspa***

This document provides a technical overview of the design and implementation of the Health Tracker Dashboard. It details the architecture, technologies, and design decisions that underpin this project.

## Overview

The Health Tracker Dashboard is a web application built to assist patients with chronic disease(s), such as hypertension, diabetes mellitus, hypercholesterolemia, and so on, in monitoring their health metrics over time. The application allows users to log data and visualize trends in various health parameters, enhancing their ability to manage chronic conditions effectively. Two of our goals are to motivate patients to be more aware of their health metric trends and signal prompt treatment modification from the health care team.

## Architecture and Technology Stack

### Backend

- Flask: A lightweight WSGI web framework that's used to build the server-side application logic.
- SQLite: A relational database used for storing user data, logs, and lab results. It’s chosen for its simplicity and ease of integration.
- CS50 Library: Utilized for simplified interaction with SQLite, allowing quick query execution and database management.

### Frontend

- HTML/CSS: Standard markup and styling languages for structuring and beautifying the application’s interface and aesthetics.
- JavaScript: Enhances interactivity, with jQuery used for DOM manipulation.
- Bootstrap: Provides responsive design elements to ensure usability across device sizes.

## Design Decisions

### Database Structure

> ***Data Organization:*** The database is normalized to reduce redundancy. Separate tables for users, logs, and lab results ensure clear relationships and scalable data handling.

>***Primary Keys and Foreign Keys:*** Implementing these ensures data integrity and efficient query processing because we have several tables, allowing effective use of relational database features.

### User Authentication

>***Session Management:*** Utilizes Flask sessions for state management. This design choice protects user data and ensures a robust authentication mechanism.

>***Password Hashing:*** Leverages module from werkzeug.security for hashing user passwords to enhance security.


### Frontend Design

>***Responsive Layout:*** Bootstrap is used to create a mobile-friendly interface without extensive CSS customizations, achieving a balance between simplicity and functionality.

>***Dynamic Content:*** JavaScript facilitates seamless user interactions, allowing dynamic updates to parts of the user interface without requiring full-page reloads.

## Implementation Highlights

>**1. User Profile Management:**

Users can update personal details and upload profile pictures. The system handles file uploads securely bystoring them in a specific directory while ensuring uploaded file types are checked against a whitelist.

>**2. Data Logging and Visualization:**

Users can log various health metrics. The application employs Chart.js to render these metrics visually. We chose to use line charts to best visualize the trends of the user's health metrics.

>**3. Security Practices:**

Protects against common vulnerabilities with secure form handling, session management, and data validation. Additionally, user inputs are sanitized to prevent SQL injection.


This design document outlines the foundational working principles of the Health Tracker Dashboard. Should you have further questions or require additional details, technical documentation, or support, please reach out!
