# Ticket System - Quick Reference Card

## 🚀 Quick Start (30 seconds)

### Terminal 1: Backend
```bash
cd d:\TicketManagement\backend
d:\TicketManagement\backend\venv\Scripts\python.exe manage.py runserver 8001 --settings=ticket_system.settings_local
```

### Terminal 2: Frontend
```bash
cd d:\TicketManagement\frontend
npm run dev
```

### Browser
Open: **http://localhost:5173**

---

## 🔐 Login Credentials

### Test Users
| Username | Password | Role |
|----------|----------|------|
| `customer_demo` | `Demo@12345` | Customer |
| `staff_demo` | `Demo@12345` | Staff |
| `admin_demo` | `Demo@12345` | Admin |

---

## 👤 Customer (Basic User)

**What you can do:**
- Create new tickets
- View your own tickets
- Add comments to your tickets
- See status updates from staff

**Steps:**
1. Login with `customer_demo`
2. Fill "New Ticket" form (required: title + description)
3. Click "Submit Ticket"
4. View ticket in your list below

**Ticket Types:**
- Bug Report (high priority)
- Feature Request (low priority)
- Support Question (medium priority)
- Account Issue (high priority)
- Billing (high priority)

---

## 👥 Staff (Support Team)

**What you can do:**
- Customers: Create & view own tickets
- Staff Extras:
  - View ALL tickets (not just own)
  - Click any ticket to open details
  - Update status (Open → In Progress → Resolved)
  - Add comments to tickets
  - See Staff Console with metrics

**Steps:**
1. Login with `staff_demo`
2. Click **Staff Console** button (not "Support Portal")
3. See all tickets in a searchable table
4. **Click any ticket row** to open it
5. Use **Update Status** dropdown to change status
6. Add comments in the comments section
7. Repeat for other tickets

**In the Staff Console:**
- **All Tickets table** - Shows every ticket with status, priority, customer
- **Search box** - Find tickets by ID or title
- **Status filter** - Show only Open/In Progress/Resolved
- **Metrics** - Total, Open, Escalations, Resolved counts
- **Click a row** → Opens ticket detail with comments & status update

---

## 🛠️ Admin (System Admin)

**What you can do:**
- Everything Staff can do, plus:
  - View Admin Dashboard (metrics, reports)
  - Manage users (create, edit, delete)
  - Configure system (statuses, priorities)
  - Access Django Admin Panel
  - View escalation reports

**Steps:**
1. Login with `admin_demo`
2. Click "Admin" button → see dashboard metrics
3. Go to http://127.0.0.1:8001/admin/ for full system control
4. Create users, manage permissions, etc.

**Admin Dashboard shows:**
- Total Tickets
- Escalations
- Open Tickets
- Resolved Tickets
- Recent Tickets

---

## 🎫 Creating a Ticket (Customer)

```
Issue Title:      "Brief description of problem"
Description:      "Detailed explanation with steps"
                  "Include when it happened"
                  "What you were trying to do"
```

**Example:**
```
Title: "Cannot reset password - no email received"

Description: 
I clicked "Forgot Password" link but never received 
the reset email. This started happening on Monday.
I've checked spam folder. Same issue on mobile & desktop.
Already tried clearing browser cache.
```

**After Submit:**
✅ Ticket appears in your list
✅ Staff is notified
✅ Staff will update you via ticket comments

---

## 📊 Ticket Workflow

```
Customer submits
    ↓
Staff sees it (24/7 monitoring)
    ↓
Staff assigns to themselves
    ↓
Status: Open → In Progress
    ↓
Staff works on issue
    ↓
Staff adds comments with progress
    ↓
Status: In Progress → Resolved
    ↓
Customer sees resolution
    ↓
Customer closes ticket
```

---

## ❌ Common Issues & Fixes

### "Invalid credentials"
- Copy-paste incorrect? 
- All lowercase/CAPS? (case-sensitive!)
- Copy from table above exactly

### "Cannot connect to backend"
- Is Terminal 1 running? Check for "Starting server at http://127.0.0.1:8001/"
- If not, run the command again
- Wait 5 seconds for server to start

### "Admin button missing"
- Are you logged in as `staff_demo` or `admin_demo`?
- Not showing for `customer_demo` (by design - RBAC)

### "Tickets not loading"
- Click **Refresh** button
- Or press F5 to reload page
- Check if backend is still running

---

## 🔑 Remember

✅ **DO:**
- Create specific, detailed tickets
- Update status as you work
- Add comments explaining actions
- Respond promptly to staff questions

❌ **DON'T:**
- Share passwords
- Create duplicate tickets
- Close tickets without confirmation
- Forget to update status

---

## 📞 Need Help?

1. Check the full **USER_MANUAL.md**
2. Look at browser console (Press F12)
3. Check backend terminal for errors
4. Create a support ticket via the app itself

---

**System Status:** ✅ Running
**API Base URL:** http://127.0.0.1:8001/api
**Frontend URL:** http://localhost:5173
**Admin Panel:** http://127.0.0.1:8001/admin/
