# 🔧 Troubleshooting Sign Up Error

## Quick Diagnostic Steps

### 1️⃣ Test if Backend is Running

Open a new terminal and run:
```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"ok","total_jobs":0,"skills_loaded":0}
```

If you get an error, the backend isn't running. Start it:
```bash
venv\Scripts\activate
python backend/main.py
```

---

### 2️⃣ Test Registration Endpoint Directly

Use the test page I created:
```bash
# Open this file in your browser:
test_registration.html
```

This will show you:
- ✅ Exact error messages from the server
- ✅ Request/response details
- ✅ Password validation results
- ✅ Network connectivity status

**OR** test with curl:
```bash
curl -X POST http://localhost:8000/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"password\":\"TestPass123!\"}"
```

---

### 3️⃣ Check Browser Console

1. Open http://localhost:3000
2. Press `F12` to open Developer Tools
3. Go to "Console" tab
4. Try to sign up
5. Look for error messages

Common errors you might see:
- ❌ `Failed to fetch` → Backend not running
- ❌ `CORS error` → Backend CORS misconfigured
- ❌ `500 Internal Server Error` → Check backend terminal for error logs
- ❌ `400 Bad Request` → Check what the server is saying

---

### 4️⃣ Check Backend Terminal Logs

When you try to sign up, look at the terminal where you ran `python backend/main.py`.

You should see:
```
INFO:     127.0.0.1:xxxxx - "POST /auth/register HTTP/1.1" 200 OK
```

If you see errors, they'll show up here.

---

### 5️⃣ Common Issues & Solutions

#### Issue: "Cannot connect to server"
**Solution:**
```bash
# Make sure backend is running
python backend/main.py

# Check if port 8000 is free
netstat -ano | findstr :8000
```

#### Issue: "Email already registered"
**Solution:** Use a different email or check the database:
```sql
-- Connect to PostgreSQL
psql -U postgres -d resume_analyzer

-- Check existing users
SELECT id, name, is_verified FROM users;

-- Delete test user if needed
DELETE FROM users WHERE email_encrypted LIKE '%test%';
```

#### Issue: "Failed to send verification email"
**Solution:** Check `.env` file:
```env
MAIL_USERNAME=harnoorpcte@gmail.com
MAIL_PASSWORD=nyqs tthi yhyv clfn
MAIL_FROM=harnoorpcte@gmail.com
```

The backend will show: `Email error: ...` in the terminal if email sending fails.

#### Issue: Database connection error
**Solution:**
```bash
# Check PostgreSQL is running
# Windows: Open Services and look for "postgresql"

# Test connection
psql -U postgres -d resume_analyzer

# If database doesn't exist
createdb -U postgres resume_analyzer

# Initialize tables
python backend/database/database.py
```

---

### 6️⃣ Step-by-Step Debug Process

**A. Is Backend Running?**
```bash
curl http://localhost:8000/health
```
✅ If yes → Go to B  
❌ If no → Start backend: `python backend/main.py`

**B. Can You Register via Test Page?**
- Open `test_registration.html` in browser
- Click "Test Registration"
- Read the detailed log

✅ If yes → Frontend issue (check browser console)  
❌ If no → Backend issue (check backend terminal)

**C. Check Database**
```sql
-- Connect
psql -U postgres -d resume_analyzer

-- Check if users table exists
\dt

-- Check structure
\d users

-- Should show user_id column
\d resumes
```

---

### 7️⃣ Fresh Start (Nuclear Option)

If nothing works, try a complete reset:

```bash
# 1. Stop all servers (Ctrl+C in both terminals)

# 2. Drop and recreate database
psql -U postgres
DROP DATABASE resume_analyzer;
CREATE DATABASE resume_analyzer;
\q

# 3. Recreate tables
venv\Scripts\activate
python backend/database/database.py

# 4. Restart backend
python backend/main.py

# 5. In new terminal, restart frontend
cd frontend
python -m http.server 3000
```

---

### 8️⃣ What to Share if Still Stuck

If you're still getting errors, share:

1. **Backend terminal output** (copy the error messages)
2. **Browser console errors** (F12 → Console tab)
3. **Test page results** (from test_registration.html)
4. **Database check:**
   ```sql
   \dt
   SELECT COUNT(*) FROM users;
   ```

---

## Quick Test Commands

```bash
# Test backend health
curl http://localhost:8000/health

# Test registration
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"name\":\"Test\",\"email\":\"test@test.com\",\"password\":\"Test123!\"}"

# Check database
psql -U postgres -d resume_analyzer -c "SELECT COUNT(*) FROM users;"
```

---

## Most Likely Causes

1. **Backend not running** (90% of cases)
   - Solution: `python backend/main.py`

2. **Email already exists**
   - Solution: Use different email or delete from DB

3. **Database not initialized**
   - Solution: `python backend/database/database.py`

4. **CORS issues**
   - Backend should already have CORS enabled (`allow_origins=["*"]`)

5. **Email service failing**
   - Check `.env` MAIL_* settings
   - Backend will still create account but won't send OTP

---

Let me know what you see in:
1. Backend terminal
2. Browser console (F12)
3. Test page results

And I'll help you fix it! 🚀
