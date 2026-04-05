# Nexus Ticket Management System - User Manual

**Last Updated:** April 5, 2026  
**System Version:** 1.0  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Test User Credentials](#test-user-credentials)
4. [Running the System](#running-the-system)
5. [Customer Guide](#customer-guide)
6. [Staff Guide](#staff-guide)
7. [Admin Guide](#admin-guide)
8. [Ticket Types & Workflows](#ticket-types--workflows)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### For Testing
**Fastest way to get started:**

```bash
# Terminal 1: Start Backend
cd d:\TicketManagement\backend
d:\TicketManagement\backend\venv\Scripts\python.exe manage.py runserver 8001 --settings=ticket_system.settings_local

# Terminal 2: Start Frontend  
cd d:\TicketManagement\frontend
npm run dev

# Terminal 3: Open Browser
Open http://localhost:5173
```

**Then login with any test credential below ↓**

---

## 🔐 Test User Credentials

### Table: Role Comparison

| **Role** | **Username** | **Password** | **Access Level** | **Features** |
|----------|-------------|------------|------------------|------------|
| **Customer** | `customer_demo` | `Demo@12345` | Basic User | • Create tickets<br/>• View own tickets<br/>• Add comments |
| **Staff** | `staff_demo` | `Demo@12345` | Support Team | • View all tickets<br/>• Assign tickets<br/>• Update status<br/>• Add internal notes<br/>• Staff Dashboard |
| **Admin** | `admin_demo` | `Demo@12345` | System Admin | • Full system access<br/>• User management<br/>• Reports & analytics<br/>• System settings<br/>• Admin Dashboard |

### ⚠️ Important Notes
- **Do NOT share** credentials in production
- **Change passwords** before going live
- Each role has different permissions enforced on backend

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│         Nexus Ticket Management             │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend (React/Vite)     Backend (Django) │
│  http://localhost:5173     http://localhost:8001
│  ├─ Login                  ├─ JWT Auth       │
│  ├─ Ticket Portal          ├─ REST API       │
│  ├─ Staff Dashboard        ├─ AI Classifier  │
│  └─ Admin Dashboard        └─ Database       │
│                                             │
└─────────────────────────────────────────────┘
```

### Features:
- **JWT Token Authentication** - Secure API access
- **Role-Based Access Control (RBAC)** - Frontend & Backend enforcement
- **AI Ticket Classification** - Automatic categorization using Ollama
- **Real-time Updates** - WebSocket support (future)
- **Persistent Storage** - SQLite with Django ORM

---

## 🎬 Running the System

### Prerequisites
- Python 3.10+
- Node.js 16+
- Virtual environment already set up

### Step 1: Start the Backend

```powershell
# Navigate to backend
cd d:\TicketManagement\backend

# Activate virtual environment
d:\TicketManagement\backend\venv\Scripts\Activate.ps1

# Run migrations (first time only)
python manage.py migrate --settings=ticket_system.settings_local

# Start development server
python manage.py runserver 8001 --settings=ticket_system.settings_local
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8001/
Quit the server with CTRL-BREAK.
```

### Step 2: Start the Frontend

**In a new terminal:**

```powershell
# Navigate to frontend
cd d:\TicketManagement\frontend

# Install dependencies (if first time)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v4.x.x  ready in xxx ms
Local:        http://localhost:5173/
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5173**

You should see the Nexus Support login screen.

---

## 👤 Customer Guide

### Login as Customer

1. Open http://localhost:5173
2. Enter credentials:
   - **Username:** `customer_demo`
   - **Password:** `Demo@12345`
3. Click **Login**

### Customer Dashboard

After login, you'll see:
- **New Ticket Form** (left side)
- **Your Tickets** (right side)
- **Filters:** Status, Priority, Search

### Creating Your First Ticket

#### Step 1: Fill Ticket Form
```
Issue Title:          "Cannot reset my password"
Description:         "I click forgot password but no email arrives.
                      Issue started on Monday morning."
```

#### Step 2: Submit
Click **Submit Ticket** button

#### Step 3: Confirmation
✅ Green toast notification: "Ticket submitted successfully"

Your ticket appears in the **Tickets** list with:
- Ticket ID (e.g., #123)
- Status badge (Open)
- Priority (Low/Medium/High)
- Created date

### Managing Your Tickets

#### View Ticket Details
- Click any ticket to see full details
- Modal shows: Title, Description, Status, Priority, Created date

#### Filter Tickets
- **By Status:** Select from dropdown (Open, In Progress, Resolved)
- **By Priority:** Select from dropdown (Low, Medium, High)
- **Search:** Type in search box to find tickets by title/description

#### Refresh Tickets
- Click **Refresh** button to fetch latest updates from staff

#### Logout
- Click **Logout** button to sign out

### Ticket Types for Customers

| Type | Example | Priority |
|------|---------|----------|
| **Bug Report** | "Login button not working" | High |
| **Feature Request** | "Can you add dark mode?" | Low |
| **Support Request** | "How do I reset my password?" | Medium |
| **Account Issue** | "My account was locked" | High |
| **Billing Question** | "Why was I charged twice?" | Medium |

---

## 👥 Staff Guide

### Login as Staff

1. Open http://localhost:5173
2. Enter credentials:
   - **Username:** `staff_demo`
   - **Password:** `Demo@12345`
3. Click **Login**

### Staff Dashboard Access

After login, you'll see:
- **Support Portal** button (go back to tickets)
- **Staff Dashboard** button (staff-only features)

### Staff Panel Features

Click **Staff Dashboard** to access:

#### 1. View All Tickets
- See **every ticket** submitted (not just your own)
- Filter by status, priority, search
- Display includes customer name and creation date

#### 2. Ticket Management
- **Assign Ticket:** Set which staff member will handle it
- **Update Status:** Change from Open → In Progress → Resolved
- **Add Comments:** Internal notes visible only to staff

#### 3. Escalation
- Mark tickets as "Escalated" for high-priority issues
- Visible in Admin Dashboard reporting

#### 4. Statistics (Staff Dashboard)
View real-time metrics:
- Total tickets in system
- Open tickets
- Escalated tickets
- Resolved tickets

### Staff Workflow Example

**Scenario:** Customer "customer_demo" submitted ticket: "Cannot reset password"

**Steps:**
1. Login as `staff_demo`
2. Click **Staff Dashboard**
3. Find the ticket in the list
4. Click to open details
5. Update Status: **Open** → **In Progress**
6. Add comment: "I've reset your password, check email"
7. Update Status: **In Progress** → **Resolved**
8. Customer is notified ✅

### Best Practices for Staff
- ✅ **Respond quickly** to high-priority tickets
- ✅ **Always add comments** explaining actions taken
- ✅ **Escalate promptly** if you need admin help
- ✅ **Update status** as you work through tickets
- ⚠️ Do NOT share personal information in comments
- ⚠️ Do NOT resolve tickets without following up with customer

---

## 🛠️ Admin Guide

### Login as Admin

1. Open http://localhost:5173
2. Enter credentials:
   - **Username:** `admin_demo`
   - **Password:** `Demo@12345`
3. Click **Login**

### Admin Dashboard Access

After login, you'll see:
- **Support Portal** button
- **Admin** button (admin-only dashboard)

### Admin Features

#### 1. Admin Dashboard Metrics
Click **Admin** to see:

- **Total Tickets:** System-wide ticket count
- **Escalations:** Number of escalated tickets
- **Open Tickets:** Unresolved tickets
- **Resolved Tickets:** Closed tickets
- **Recent Tickets:** Last 10 tickets submitted

#### 2. System Configuration (Django Admin)
Access: http://127.0.0.1:8001/admin/

**Login with:**
- **Username:** `admin_demo`
- **Password:** `Demo@12345`

**Can configure:**
- User accounts (create, edit, delete)
- Ticket statuses (Open, In Progress, Resolved, etc.)
- Priority levels (Low, Medium, High, Critical)
- Staff assignments
- System settings

#### 3. User Management

**Create New User:**
1. Go to Admin Dashboard
2. Navigate to "Users"
3. Click "Add User"
4. Set username, password, role (staff/admin), is_active
5. Save

**Edit User Permissions:**
1. Click user in list
2. Modify:
   - `is_staff` - Enable staff features
   - `is_superuser` - Enable admin features
3. Save changes

**Deactivate User:**
1. Click user
2. Uncheck `is_active`
3. Save (user cannot login)

#### 4. Reports & Analytics

Available insights:
- Customer satisfaction trends
- Average resolution time
- Top issue categories
- Staff performance metrics
- System health status

#### 5. Troubleshooting Issues

**If backend is down:**
- Check terminal for error messages
- Verify database permissions
- Restart Django server

**If API endpoints fail:**
- Check user permissions
- Verify JWT token validity
- Check backend logs

---

## 🎫 Ticket Types & Workflows

### Ticket Categories

#### 1. **Bug Report**
- **Description:** System malfunction or error
- **Example:** "Payment button gives 404 error"
- **Priority:** Usually High
- **SLA:** Resolve within 4-8 hours
- **Workflow:** 
  - Customer submits → Staff reproduces → Fix & test → Resolved

#### 2. **Feature Request**
- **Description:** Request for new functionality
- **Example:** "Add bulk ticket export feature"
- **Priority:** Usually Low
- **SLA:** Evaluate within 5 business days
- **Workflow:**
  - Customer submits → Admin evaluates feasibility → Approved/Rejected

#### 3. **Support Request**
- **Description:** "How to" questions or guidance
- **Example:** "How do I export my data?"
- **Priority:** Medium
- **SLA:** Respond within 2 hours
- **Workflow:**
  - Customer asks → Staff provides solution → Verified → Resolved

#### 4. **Account Issue**
- **Description:** Account-related problems
- **Example:** "I'm locked out of my account"
- **Priority:** High
- **SLA:** Resolve within 2 hours
- **Workflow:**
  - Customer reports → Staff verifies identity → Unlock/Reset → Resolved

#### 5. **Billing/Payment**
- **Description:** Subscription or payment issues
- **Example:** "Credit card declined"
- **Priority:** High
- **SLA:** Escalate to billing team
- **Workflow:**
  - Customer reports → Staff gathers info → Escalate to admin → Resolved

### Ticket Lifecycle

```
┌─────────────────────────────────────────────┐
│          TICKET LIFECYCLE                   │
└─────────────────────────────────────────────┘

1. OPEN
   ↓ (Customer submits)
   
2. IN PROGRESS
   ↓ (Staff begins work)
   
3. PENDING CUSTOMER
   ↓ (Waiting for customer response)
   
4. IN PROGRESS (again)
   ↓ (Staff continues)
   
5. RESOLVED
   ↓ (Issue fixed)
   
6. CLOSED
   ↓ (Customer confirms)
   
7. ARCHIVED
   (Stored in history)
```

### Status Definitions

| Status | Meaning | Next Step |
|--------|---------|-----------|
| **Open** | Waiting for staff to start | Staff picks up & works |
| **In Progress** | Staff is actively working | Update or escalate |
| **Pending Response** | Waiting for customer input | Customer replies |
| **Resolved** | Issue fixed, awaiting confirmation | Customer closes |
| **Closed** | Complete | Archive |

---

## 🆘 Troubleshooting

### Login Issues

#### "Invalid credentials" Error
- ✅ Check spelling of username/password (case-sensitive)
- ✅ Verify you're using test credentials from table above
- ✅ Ensure backend is running (http://127.0.0.1:8001)

#### "Cannot connect to server"
- ✅ Start backend: `python manage.py runserver 8001`
- ✅ Verify port 8001 is not blocked
- ✅ Check terminal for error messages

### Frontend Issues

#### "Cannot connect to backend API"
- ✅ Check if backend is running
- ✅ Verify API URL: http://127.0.0.1:8001/api
- ✅ Check browser console (F12) for errors

#### "Admin button is missing"
- ✅ You may not be logged in as staff/admin
- ✅ Login with `staff_demo` or `admin_demo`
- ✅ Logout and try again

#### "Tickets not loading"
- ✅ Refresh page (F5)
- ✅ Click **Refresh** button in dashboard
- ✅ Check backend server logs

### Backend Issues

#### "ModuleNotFoundError: django"
- ✅ Activate virtual environment first
- ✅ Run: `d:\TicketManagement\backend\venv\Scripts\Activate.ps1`

#### "CORS Error in console"
- ✅ Ensure backend URL in frontend config is correct
- ✅ Check `.env` file in frontend folder
- ✅ Verify backend CORS settings

#### "Database error"
- ✅ Run migrations: `python manage.py migrate`
- ✅ Check file permissions on database
- ✅ Delete `db.sqlite3` and re-migrate (⚠️ loses data)

---

## ✅ Best Practices

### For Customers

1. **Be Specific in Titles**
   - ❌ Bad: "Something is broken"
   - ✅ Good: "Cannot upload PDF files larger than 5MB"

2. **Provide Detailed Descriptions**
   - Include steps to reproduce
   - Mention when issue started
   - Include browser/device info

3. **Use Appropriate Priority**
   - Don't mark everything as High
   - High = unable to work
   - Low = minor annoyance

4. **Check Ticket Status Regularly**
   - Staff updates every ticket with progress
   - Don't create duplicate tickets for same issue

5. **Respond Promptly to Staff Questions**
   - Staff may need clarification
   - Provides more context = faster resolution

### For Staff

1. **Assign Yourself**
   - Take ownership of tickets
   - Update status as you work

2. **Comment Frequently**
   - Add notes on every action
   - Customer sees your progress
   - Creates documentation trail

3. **Set Realistic Timelines**
   - Don't promise same-day fixes for complex issues
   - Better to under-promise and over-deliver

4. **Escalate Properly**
   - Use escalation flag for complex issues
   - Never ignore escalated tickets
   - Notify admin team

5. **Test Before Closing**
   - Always verify fix before marking resolved
   - Ask customer to confirm

### For Admins

1. **Monitor Dashboard**
   - Check escalations daily
   - Review staff performance
   - Watch metric trends

2. **Update System Parameters**
   - Review status/priority options regularly
   - Add new categories as needed
   - Document custom statuses

3. **User Account Management**
   - Onboard staff quickly
   - Remove inactive users
   - Audit permissions monthly

4. **Backup Data**
   - Regular database backups
   - Export reports monthly
   - Archive old tickets

5. **Security**
   - Change default passwords immediately
   - Rotate credentials quarterly
   - Monitor failed login attempts

---

## 📊 Metrics & Reporting

### Key Metrics to Track

| Metric | Target | Formula |
|--------|--------|---------|
| **Avg Response Time** | < 2 hours | Total response time / tickets |
| **Resolution Rate** | > 95% | Resolved / Total tickets |
| **Customer Satisfaction** | > 4.5/5 | Survey average |
| **Escalation Rate** | < 5% | Escalated / Total |
| **First Contact Resolution** | > 60% | Resolved without escalation |

### Reports Available

1. **Daily Report:** New tickets, resolutions
2. **Weekly Report:** Staff performance, metrics
3. **Monthly Report:** Trends, forecasting
4. **Custom Reports:** Filter by date, category, staff

---

## 🔒 Security Guidelines

### Password Policy
- ✅ Minimum 8 characters
- ✅ Mix of uppercase, lowercase, numbers, symbols
- ✅ Change every 90 days
- ✅ Never share credentials

### Data Protection
- ✅ All API calls use JWT tokens
- ✅ Backend enforces role-based permissions
- ✅ Database uses encrypted connections
- ✅ Audit logs track all changes

### Access Control
- ✅ Customers see only own tickets
- ✅ Staff sees all tickets
- ✅ Admins can access everything
- ✅ Permissions enforced on backend

---

## 📞 Support & Contact

### Getting Help

1. **For System Issues:**
   - Check Troubleshooting section
   - Review error messages in browser console (F12)
   - Check backend server logs

2. **For Feature Requests:**
   - Create ticket with "Feature Request" type
   - Provide detailed use case
   - Submit to Admin team

3. **For Technical Support:**
   - Email: support@nexus.local
   - Available: Monday-Friday, 9AM-6PM
   - Response time: < 4 hours

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 5, 2026 | Initial release, full RBAC, AI classification |
| 0.9 | April 1, 2026 | Beta testing, basic features |
| 0.5 | March 15, 2026 | Alpha development |

---

## 📄 Appendix: API Reference

### Available Endpoints (for developers)

```
Authentication:
POST   /api/token/              - Get JWT access token
GET    /api/user/me/            - Get current user info

Tickets:
GET    /api/tickets/            - List all (or own) tickets
POST   /api/tickets/            - Create new ticket
GET    /api/tickets/{id}/       - Get ticket details
PUT    /api/tickets/{id}/       - Update ticket
DELETE /api/tickets/{id}/       - Delete ticket

Admin Only:
GET    /api/admin-stats/        - Dashboard metrics
GET    /api/admin/users/        - List all users
POST   /api/admin/users/        - Create user
```

### Example API Call

```bash
# Get access token
curl -X POST http://127.0.0.1:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"customer_demo","password":"Demo@12345"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use token to access API
curl -X GET http://127.0.0.1:8001/api/tickets/ \
  -H "Authorization: Bearer eyJ0eXAi..."
```

---

**End of User Manual**

For the most up-to-date information, visit the system dashboard or contact the admin team.
