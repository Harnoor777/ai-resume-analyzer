# 🚀 Quick Start Guide - AI Resume Analyzer

Follow these steps to get the application running on your Windows machine.

---

## ✅ Prerequisites Check

You already have:
- ✓ PostgreSQL database running at `localhost:5432`
- ✓ Database `resume_analyzer` created
- ✓ Environment variables configured in `.env`
- ✓ Python project with dependencies listed in `requirements.txt`

---

## 📋 Step-by-Step Instructions

### 1️⃣ Activate Virtual Environment

Open a terminal in the project root directory:

```bash
# Activate the virtual environment
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### 2️⃣ Install/Update Dependencies

Since you made changes to the database models, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Key dependencies include:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- psycopg2-binary (PostgreSQL driver)
- python-jose (JWT tokens)
- passlib (password hashing)
- pycryptodome (email encryption)

---

### 3️⃣ Initialize/Update Database Tables

The database schema was just updated with the new `user_id` foreign key. Run this command to create/update all tables:

```bash
python backend/database/database.py
```

Expected output:
```
Database tables created.
```

This will:
- Create the `users` table (if not exists)
- Create/update the `resumes` table with the new `user_id` column
- Create the `jobs` table (if not exists)
- Create the `analyses` table (if not exists)

---

### 4️⃣ Optional: Load Sample Jobs Data

If you haven't already scraped jobs, you can:

**Option A: Scrape Fresh Jobs** (Recommended)
```bash
# Install Playwright browser
playwright install chromium

# Scrape jobs from various companies
python backend/services/scrape_jobs.py https://job-boards.greenhouse.io/anthropic
python backend/services/scrape_jobs.py https://job-boards.greenhouse.io/stripe
python backend/services/scrape_jobs.py https://jobs.ashbyhq.com/openai
```

**Option B: Skip for Now**
You can test the application without job data first. The resume upload and parsing will still work.

**After scraping (if you did it):**
```bash
# Clean and process the job data
python backend/services/clean_jobs.py

# Extract skills from job descriptions
python backend/utils/build_skills_list.py

# Build FAISS vector search index
python backend/embeddings/build_index.py
```

---

### 5️⃣ Start the Backend API

```bash
python backend/main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Database tables created.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is ready!**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Leave this terminal running.

---

### 6️⃣ Start the Frontend

Open a **NEW terminal** window, navigate to the project directory, and run:

```bash
cd frontend
python -m http.server 3000
```

Expected output:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

**✅ Frontend is ready!**
- Open your browser to: http://localhost:3000

---

## 🎯 Testing the Fixes

### Test #1: Database Foreign Key (Issue 1)
1. The backend should start without any SQLAlchemy relationship errors
2. Check the logs - no error like "Could not determine join condition"

### Test #2: Password Validation (Issue 2)
1. Go to http://localhost:3000
2. Click "Sign up"
3. Try registering with a weak password (e.g., "password")
4. ✅ Should see: "Password must include at least one uppercase letter"
5. Try: "Password1" 
6. ✅ Should see: "Password must include at least one special character"
7. Try: "Password1!" 
8. ✅ Should work and send verification email

### Test #3: UX Feedback (Issue 3)
1. Register with valid credentials: "Password1!"
2. ✅ Should see green success message: "Account created! Check your email for the code."
3. ✅ After 1.2 seconds, automatically redirects to verification page
4. Check the password field hints - should show requirements below the input

### Test #4: User Association (Issue 4)
1. Login to your account
2. Upload a resume (PDF or DOCX)
3. Check the database:
```sql
SELECT id, user_id, name, created_at FROM resumes ORDER BY created_at DESC LIMIT 1;
```
4. ✅ The `user_id` column should have your user's ID (not NULL)

5. Logout and upload another resume (anonymous)
6. Check the database again
7. ✅ The `user_id` should be NULL for anonymous upload

---

## 🔧 Troubleshooting

### Port Already in Use
**Backend (8000):**
```bash
# Use a different port
python backend/main.py --port 8001
# Then update the API URL in frontend/index.html line 826: const API = "http://localhost:8001";
```

**Frontend (3000):**
```bash
python -m http.server 3001
```

### Database Connection Error
```bash
# Test PostgreSQL connection
psql -U postgres -d resume_analyzer

# If connection fails, check:
# 1. PostgreSQL service is running
# 2. Password is correct in .env: noor@123
# 3. Database exists: CREATE DATABASE resume_analyzer;
```

### Module Not Found Errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# If still failing, try upgrading pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Email Verification Not Working
The `.env` file has Gmail credentials configured. If emails aren't sending:
1. Check the MAIL_PASSWORD - Gmail App Password should have spaces: `nyqs tthi yhyv clfn`
2. Make sure "Less secure app access" or "App Passwords" is enabled in Gmail
3. Check backend terminal for email error logs

---

## 🎨 What You Can Do Now

1. **Register & Login**: Full authentication with email verification
2. **Upload Resume**: PDF/DOCX parsing with skill extraction
3. **View Matches**: If you loaded jobs, see ATS scores and job matches
4. **Password Reset**: Forgot password flow with OTP
5. **Theme Toggle**: Switch between dark and light mode

---

## 📁 Quick Reference

### Important URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Key Files Modified
- ✅ `backend/database/database.py` - Added user_id foreign key
- ✅ `backend/main.py` - Added optional user tracking
- ✅ `frontend/index.html` - Added password validation & UX improvements

### Database Tables
- `users` - User accounts with encrypted emails
- `resumes` - Uploaded resumes (now linked to users!)
- `jobs` - Job listings from scrapers
- `analyses` - Resume-job match results

---

## 🚀 You're All Set!

Both servers should now be running. Open http://localhost:3000 and try creating an account with a strong password like `SecurePass123!`

Enjoy your AI Resume Analyzer! 🎉
