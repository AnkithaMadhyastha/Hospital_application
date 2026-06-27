# 🏥 HealthPredict AI

## Overview

HealthPredict AI is a web-based healthcare application developed using **Python Flask** and **SQLite**. The system allows users to manage patient records and perform AI-powered health risk assessments based on blood test results.

The application analyzes Glucose, Haemoglobin, and Cholesterol values and generates AI-powered health assessments using the Google Gemini AI API. Based on the patient's blood test values, the system provides personalized health analysis, identifies potential health risks, and offers professional recommendations.

---

## Features

### CRUD Operations

- Create Patient Records
- View Patient Records
- Update Patient Records
- Delete Patient Records

### Patient Information

- Full Name
- Date of Birth
- Email Address
- Glucose Level
- Haemoglobin Level
- Cholesterol Level

### AI Health Analysis

- Google Gemini AI Integration
- AI-Powered Health Assessment
- Blood Test Analysis
- Possible Health Risk Identification
- Personalized Medical Recommendations
- Healthy / Monitor / At Risk Classification

### Data Validation

- Email Format Validation
- Date of Birth Validation
- Numeric Blood Test Validation
- Required Field Validation

### Dashboard

- Total Patients
- Healthy Patients
- At Risk Patients

---

## Technology Stack

### Backend

- Python
- Flask

### Database

- SQLite

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap


### AI Module

- Google Gemini AI API
- Google GenAI SDK

---

## Project Structure

```
Hospital_application/
│
├── app.py
├── database.py
├── ai_service.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    └── index.html
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/AnkithaMadhyastha/Hospital_application.git
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## Application Features

- Add New Patient
- Edit Patient Details
- Delete Patient Record
- View AI Health Analysis
- Dashboard Statistics
- Responsive User Interface

---

## Future Enhancements

- Machine Learning Model
- Authentication System
- PDF Report Generation
- Cloud Deployment

---
## Project Highlights

- Flask REST API
- SQLite Database
- Google Gemini AI Integration
- Responsive UI
- CRUD Operations
- Input Validation
- AI-generated Health Assessment
- Real-time Dashboard Statistics
