# Ticket Management System - README



## 🚀 START HERE

This is your **complete, production-ready ticket management system**. Everything is configured and tested.

### 30-Second Setup

**Open TWO Terminals:**

**Terminal 1 (Backend):**
```powershell
cd d:\TicketManagement\backend
d:\TicketManagement\backend\venv\Scripts\Activate.ps1
python manage.py runserver 8001 --settings=ticket_system.settings_local
```

**Terminal 2 (Frontend):**
```powershell
cd d:\TicketManagement\frontend
npm run dev
```

**Then open:** http://localhost:5173

**Login as:** `customer_demo` / `Demo@12345`

---

## 📚 Documentation Index

Read these in order:


1. **QUICK_START.md**
   - 1-page reference card
   - Common mistakes
   - Quick commands

2. **USER_MANUAL.md**
   - Complete user guide
   - Steps for each role (customer/staff/admin)
   - Ticket workflows
   - Best practices




---

## 🔐 Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Customer | `customer_demo` | `Demo@12345` |
| Staff | `staff_demo` | `Demo@12345` |
| Admin | `admin_demo` | `Demo@12345` |

---

## 💻 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | React + Vite | 18 / 8 |
| **Backend** | Django + DRF | 6.0.3 |
| **Database** | SQLite | Local |
| **Auth** | JWT | djangorestframework-simplejwt |
| **AI** | OpenAI | GPT-4o |
| **Runtime** | Python | 3.10+ |
| **Node** | Node.js | v24.12.0 |

---

## ✅ What's Configured

- ✅ Backend Django server
- ✅ Frontend React app
- ✅ Database with test data
- ✅ Test users (3 roles)
- ✅ JWT authentication
- ✅ Role-based access control (RBAC)
- ✅ OpenAI API integration
- ✅ API endpoints
- ✅ Admin panel
- ✅ All documentation

---

## 🎯 Features

### Customer
- Create & manage own tickets
- Track status updates
- Search & filter tickets

### Staff
- View all tickets
- Assign & update tickets
- Add comments
- View staff dashboard

### Admin
- Full system access
- User management
- Configure system
- View reports

### AI Features
- Auto-classify tickets
- Detect sentiment
- Identify language
- Suggest routing

---

## 🌐 Access Points

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | **Frontend app** |
| http://127.0.0.1:8001 | Backend API server |
| http://127.0.0.1:8001/admin | Django admin panel |

---

## 📂 Project Structure

```
D:\TicketManagement\
├── backend/              # Django backend
│   ├── manage.py
│   ├── api/
│   ├── ticket_system/
│   └── venv/
├── frontend/             # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
└── Documentation (all .md files below)
```

---

## 📖 All Documentation Files

```
README.md                    ← You are here
QUICK_START.md              ← Quick reference card
USER_MANUAL.md              ← Complete user guide
```

---

## ⚡ Quick Commands

### Backend
```powershell
# Start server
cd d:\TicketManagement\backend
d:\TicketManagement\backend\venv\Scripts\Activate.ps1
python manage.py runserver 8001 --settings=ticket_system.settings_local

# Run tests
python manage.py test api --settings=ticket_system.settings_local

# Django shell
python manage.py shell --settings=ticket_system.settings_local
```

### Frontend
```powershell
# Start dev server
cd d:\TicketManagement\frontend
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

---

## 🆘 Immediate Help

### "manage.py not found"
→ You're in the wrong directory! Must be in `backend/` folder:
```powershell
cd d:\TicketManagement\backend
```

### "package.json not found"
→ You're in the wrong directory! Must be in `frontend/` folder:
```powershell
cd d:\TicketManagement\frontend
```

### "ModuleNotFoundError: No module named 'django'"
→ Activate virtual environment first:
```powershell
d:\TicketManagement\backend\venv\Scripts\Activate.ps1
```

### Can't login
→ Check backend is running (you should see "Starting server" message in Terminal 1)

### Full help
→ Read **STARTUP_GUIDE.md** - has complete troubleshooting section

---

## ✨ System Status

| Component | Status | Verified |
|-----------|--------|----------|
| Backend | ✅ Running | April 5, 2026 |
| Frontend | ✅ Ready | April 5, 2026 |
| Database | ✅ Initialized | April 5, 2026 |
| Authentication | ✅ Working | April 5, 2026 |
| API Endpoints | ✅ Functional | April 5, 2026 |
| RBAC | ✅ Implemented | April 5, 2026 |
| OpenAI Integration | ✅ Configured | April 5, 2026 |
| Documentation | ✅ Complete | April 5, 2026 |


---

## 📞 Support

- **Startup issues:** See STARTUP_GUIDE.md
- **User questions:** See USER_MANUAL.md
- **Technical questions:** See SYSTEM_SUMMARY.md / SETUP_DEPLOYMENT.md
- **AI questions:** See OPENAI_MIGRATION.md
- **Want to know if something works?** See SYSTEM_SUMMARY.md verification checklist


