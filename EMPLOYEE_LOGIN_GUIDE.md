# Employee Login Portal Guide

## Overview
The Employee Login Portal is a separate entry point for employees to check in and out of the office. When employees log in, their presence status is automatically updated in the Presence Tracking system.

## Access the Portal
**URL:** `http://127.0.0.1:5001/employee/login`

## How to Use

### For Employees Without Presence Logs
Currently, these employees have no presence logs:
- **Aden Weir** - Support Department
- **Rushdeen White** - Support Department  
- **Alex Abrahams** - Product Development

### Login Credentials Format
All employees use the same password for this demo system:

**Username:** `firstname.lastname@mrisoftware.com`  
**Password:** `password123`

### Example Credentials

#### Aden Weir (Support)
- Email: `aden.weir@mrisoftware.com`
- Password: `password123`

#### Rushdeen White (Support)
- Email: `rushdeen.white@mrisoftware.com`
- Password: `password123`

#### Alex Abrahams (Product Development)
- Email: `alex.abrahams@mrisoftware.com`
- Password: `password123`

### All Employee Emails
1. `lilitha.nomaxayi@mrisoftware.com` - Business Operations
2. `anshah.shabangu@mrisoftware.com` - Business Operations
3. `eathon.groenewald@mrisoftware.com` - Data Management
4. `kayleigh.jonkers@mrisoftware.com` - Lease Administration
5. `stacy.clarke@mrisoftware.com` - GPS
6. `amber-lee.november@mrisoftware.com` - GPS
7. `aden.weir@mrisoftware.com` - Support
8. `rushdeen.white@mrisoftware.com` - Support
9. `alex.abrahams@mrisoftware.com` - Product Development
10. `sakhe.dudula@mrisoftware.com` - Product Development

## Features

### Check In
1. Enter your email and password
2. Click **"Check In"** button
3. You'll see a success message with your name and department
4. Your status will be updated to "IN" in the Presence Tracking system
5. You'll appear in the "Current Presence" grid on the Presence page

### Check Out
1. Enter your email and password
2. Click **"Check Out"** button
3. You'll see a success message
4. Your status will be updated to "OUT" in the Presence Tracking system
5. You'll be removed from the "Current Presence" grid

## Integration with Presence Tracking

### Real-Time Updates
- When you check in/out, the system creates a new PresenceLog entry
- The Presence Tracking page auto-refreshes every 30 seconds
- Your presence status will appear in:
  - **Total in Building** count
  - **Current Presence** grid (if checked in)
  - **All Occupants in Building** list under "Employees" section

### API Endpoint
The login portal uses the `/api/employee/check-in` endpoint which:
- Validates your credentials
- Creates a presence log with your status (IN or OUT)
- Returns your employee information
- Logs the activity in the terminal

## Technical Details

### Files Created
1. `templates/employee_login.html` - Login page UI
2. `api/safety.py` - Added `/api/employee/check-in` endpoint
3. `app.py` - Added `/employee/login` route

### Database Updates
- Updates email addresses from `@mri.com` to `@mrisoftware.com`
- Creates PresenceLog entries linked to your User and Employee records
- Status can be either `IN` or `OUT`

## Testing

### Test Scenario 1: Check In Aden
1. Go to `http://127.0.0.1:5001/employee/login`
2. Enter: `aden.weir@mrisoftware.com` / `password123`
3. Click "Check In"
4. Go to `http://127.0.0.1:5001/presence`
5. Verify Aden appears in the presence grid and employee list
6. Total count should increase by 1

### Test Scenario 2: Check Out Existing Employee
1. Go to `http://127.0.0.1:5001/employee/login`
2. Enter credentials for someone already in office (e.g., `eathon.groenewald@mrisoftware.com`)
3. Click "Check Out"
4. Go to `http://127.0.0.1:5001/presence`
5. Verify they no longer appear in the presence grid
6. Total count should decrease by 1

## Terminal Logs
Check the terminal for detailed logging:
```
🔐 Employee check-in attempt: aden.weir@mrisoftware.com - Status: in
✅ Aden Weir checked in successfully
```

## Security Note
⚠️ This is a demo system using a shared password (`password123`). In production, each employee would have a unique secure password stored with proper hashing.
