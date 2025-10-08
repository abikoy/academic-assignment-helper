# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

A comprehensive backend + n8n automation system for analyzing student assignments and detecting plagiarism using AI and RAG (Retrieval Augmented Generation).

## 🎯 What This Does

- **Upload Assignments**: Students can upload their assignment files
- **Plagiarism Detection**: Checks assignments against academic sources
- **Source Suggestions**: Recommends relevant academic papers
- **Secure Access**: JWT authentication protects all endpoints

## 🔄 How The Project Works

### System Flow:
1. **Student registers** → Creates account in database
2. **Student logs in** → Gets JWT token for authentication
3. **Student uploads assignment** → File saved, triggers n8n workflow
4. **System analyzes** → RAG service checks for plagiarism and finds similar sources
5. **Student views results** → Gets plagiarism score, source suggestions, and recommendations

### Architecture:
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Student   │─────▶│  FastAPI     │─────▶│ PostgreSQL  │
│  (Browser)  │      │  Backend     │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  n8n Workflow│
                     │  (Optional)  │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  OpenAI API  │
                     │  (Embeddings)│
                     └──────────────┘
```

## 📁 Project Structure

```
academic-assignment-helper/
├── backend/
│   ├── main.py              # Main API application
│   ├── auth.py              # Authentication logic
│   ├── models.py            # Database models
│   ├── rag_service.py       # RAG and plagiarism detection
│   ├── requirements.txt     # Python packages
│   └── Dockerfile           # Docker configuration
├── workflows/
│   └── assignment_analysis_workflow.json  # n8n workflow
├── data/
│   └── sample_academic_sources.json       # Sample academic papers
├── docker-compose.yml       # Docker services setup
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🚀 Quick Start with Docker Compose

### Prerequisites

Before you begin, ensure you have the following installed:
- **Docker Desktop** (version 20.10 or higher)
  - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
  - Mac: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
  - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
- **Docker Compose** (included with Docker Desktop, or install separately on Linux)
- **Git** (optional, for cloning): [Download Git](https://git-scm.com/downloads)

### Step 1: Get the Project

**Option A: Clone from GitHub**
```bash
git clone https://github.com/YOUR_USERNAME/academic-assignment-helper.git
cd academic-assignment-helper
```

**Option B: Download ZIP**
- Download the project ZIP file
- Extract it to a folder
- Open terminal/command prompt in that folder

### Step 2: Configure Environment Variables

Create a `.env` file from the template:

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**On Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**On Mac/Linux:**
```bash
cp .env.example .env
```

**Edit the `.env` file** and add your actual values:

```bash
# Database configuration
DATABASE_URL=postgresql://student:secure_password@db:5432/academic_helper

# JWT Authentication (change this!)
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here

# n8n Webhook URL (leave as is)
N8N_WEBHOOK_URL=http://n8n:5678/webhook/assignment
```

> **⚠️ Important:** Never commit the `.env` file to Git! It contains your secrets.

### Step 3: Start All Services with Docker Compose

**First time setup (builds and starts everything):**
```bash
docker-compose up --build
```

This command will:
1. ✅ Build the FastAPI backend Docker image
2. ✅ Pull PostgreSQL with pgvector extension
3. ✅ Pull n8n workflow automation
4. ✅ Pull pgAdmin database management tool
5. ✅ Create a Docker network for services to communicate
6. ✅ Start all containers
7. ✅ Initialize the database with tables
8. ✅ Load sample academic sources (if OpenAI API key is valid)

**Wait for these messages:**
```
✅ Database tables created successfully!
📚 Checking academic sources database...
✅ Successfully added 3 academic sources to database
✅ Server started successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**After first time (regular start):**
```bash
docker-compose up
```

**Run in background (detached mode):**
```bash
docker-compose up -d
```

Wait 30-60 seconds for all services to start.

### Step 4: Verify All Services Are Running

Check that all containers are up:
```bash
docker-compose ps
```

You should see:
```
NAME               STATUS              PORTS
academic_backend   Up                  0.0.0.0:8000->8000/tcp
academic_db        Up (healthy)        0.0.0.0:5432->5432/tcp
academic_n8n       Up                  0.0.0.0:5678->5678/tcp
academic_pgadmin   Up                  0.0.0.0:5050->80/tcp
```

### Step 5: Access the Services

Once all containers are running, you can access:

| Service | URL | Purpose | Credentials |
|---------|-----|---------|-------------|
| **Backend API** | http://localhost:8000/docs | Interactive API documentation | JWT token required for protected endpoints |
| **Health Check** | http://localhost:8000/health | Check if API is running | No auth needed |
| **n8n Workflow** | http://localhost:5678 | Workflow automation platform | Create account on first visit |
| **pgAdmin** | http://localhost:5050 | Database management GUI | Email: `admin@example.com`<br>Password: `admin` |
| **PostgreSQL** | localhost:5432 | Database (direct connection) | User: `student`<br>Password: `secure_password`<br>Database: `academic_helper` |

## 📋 Essential Commands

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start all services |
| `docker-compose up -d` | Start in background |
| `docker-compose up --build` | Rebuild and start |
| `docker-compose down` | Stop all services |
| `docker-compose down -v` | Stop and remove data |
| `docker-compose logs` | View all logs |
| `docker-compose logs backend` | View backend logs only |
| `docker-compose ps` | Check running services |
| `docker-compose restart` | Restart all services |
| `docker-compose restart backend` | Restart backend only |

### Check If Services Are Running

```bash
# Check all containers
docker-compose ps

# Check backend logs
docker-compose logs -f backend

# Check database logs
docker-compose logs -f db
```

### Stop the Application

```bash
# Stop services (keeps data)
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

## 📖 How to Use the API (Step-by-Step)

### Method 1: Using the Interactive API Docs (Easiest)

#### 1. Register a Student Account

1. Open http://localhost:8000/docs in your browser
2. Find `POST /auth/register` endpoint
3. Click "Try it out"
4. Enter this data:
   ```json
   {
     "email": "student@example.com",
     "password": "password123",
     "full_name": "John Doe",
     "student_id": "STU001"
   }
   ```
5. Click "Execute"
6. You should see: `"email": "student@example.com"` in response

#### 2. Login to Get Your Token

1. Find `POST /auth/login` endpoint
2. Click "Try it out"
3. Enter:
   - **username**: `student@example.com`
   - **password**: `password123`
4. Click "Execute"
5. **COPY** the `access_token` from response (looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

#### 3. Authorize Your Requests

1. Click the **"Authorize"** button at the top of the page (🔓 icon)
2. Paste your token in the "Value" field
3. Click "Authorize"
4. Click "Close"
5. Now you're logged in! 🎉

#### 4. Upload an Assignment

1. Find `POST /upload` endpoint
2. Click "Try it out"
3. Click "Choose File" and select a `.txt` file
4. Fill in:
   - **topic**: "Machine Learning"
   - **academic_level**: "Undergraduate"
5. Click "Execute"
6. **SAVE** the `id` from response (e.g., `"id": 1`)

#### 5. Get Analysis Results

1. Find `GET /analysis/{assignment_id}` endpoint
2. Click "Try it out"
3. Enter the assignment ID from step 4 (e.g., `1`)
4. Click "Execute"
5. View your results:
   - **plagiarism_score**: How much plagiarism detected (0.0 to 1.0)
   - **research_suggestions**: Recommended research topics
   - **citation_recommendations**: How to cite sources

### Method 2: Using cURL Commands

#### Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "student_id": "STU001"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@example.com&password=password123"
```

#### Upload Assignment (replace YOUR_TOKEN)
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@assignment.txt" \
  -F "topic=Machine Learning" \
  -F "academic_level=Undergraduate"
```

#### Get Analysis (replace YOUR_TOKEN and ASSIGNMENT_ID)
```bash
curl -X GET "http://localhost:8000/analysis/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new student | ❌ |
| `/auth/login` | POST | Login and get token | ❌ |
| `/upload` | POST | Upload assignment | ✅ |
| `/assignments` | GET | Get all assignments | ✅ |
| `/analysis/{id}` | GET | Get analysis results | ✅ |
| `/sources` | GET | Search academic sources | ✅ |
| `/health` | GET | Check API status | ❌ |

## 🗄️ Database Tables

### students
- **Purpose**: Stores student account information
- **Fields**: 
  - `id` - Unique student ID
  - `email` - Student email (used for login)
  - `password_hash` - Encrypted password
  - `full_name` - Student's full name
  - `student_id` - Student ID number
  - `created_at` - Account creation date

### assignments
- **Purpose**: Stores uploaded assignments
- **Fields**: 
  - `id` - Unique assignment ID
  - `student_id` - Which student uploaded this
  - `filename` - Original file name
  - `original_text` - Full text content
  - `topic` - Assignment topic
  - `academic_level` - Education level
  - `word_count` - Number of words
  - `uploaded_at` - Upload timestamp

### analysis_results
- **Purpose**: Stores plagiarism detection and analysis results
- **Fields**: 
  - `id` - Unique analysis ID
  - `assignment_id` - Which assignment was analyzed
  - `suggested_sources` - Recommended academic papers (JSON)
  - `plagiarism_score` - Plagiarism percentage (0.0 to 1.0)
  - `flagged_sections` - Sections that match other sources (JSON)
  - `research_suggestions` - AI-generated research tips
  - `citation_recommendations` - How to cite sources
  - `confidence_score` - How confident the AI is
  - `analyzed_at` - Analysis timestamp

### academic_sources
- **Purpose**: Stores academic papers for plagiarism comparison
- **Fields**: 
  - `id` - Unique source ID
  - `title` - Paper title
  - `authors` - Paper authors
  - `publication_year` - Year published
  - `abstract` - Paper summary
  - `full_text` - Complete paper text
  - `source_type` - Type: 'paper', 'textbook', or 'course_material'
  - `embedding` - AI vector representation (for similarity search)

## 🔍 How the System Works Internally

### 1. Authentication Flow
```
Student enters email/password
        ↓
Backend checks database
        ↓
Password matches? → Create JWT token
        ↓
Token sent to student
        ↓
Student includes token in all future requests
```

### 2. Assignment Upload Flow
```
Student uploads file via API
        ↓
Backend saves file to /uploads folder
        ↓
Backend reads file content
        ↓
Creates assignment record in database
        ↓
(Optional) Triggers n8n webhook for processing
        ↓
Returns assignment ID to student
```

### 3. Plagiarism Detection Flow
```
Student requests analysis
        ↓
RAG Service loads assignment text
        ↓
Splits text into paragraphs
        ↓
For each paragraph:
  - Convert to embedding (vector)
  - Search similar academic sources
  - Calculate similarity score
        ↓
If similarity > 85% → Flag as potential plagiarism
        ↓
Compile results and save to database
        ↓
Return analysis to student
```

### 4. RAG (Retrieval Augmented Generation) Process
```
Assignment text → OpenAI Embeddings API
        ↓
Gets vector representation [1536 numbers]
        ↓
Compare with academic_sources embeddings
        ↓
Calculate cosine similarity
        ↓
Return top 5 most similar papers
        ↓
These become "suggested sources"
```

## 🧩 Component Interactions

### What Each Service Does:

**PostgreSQL (Database)**
- Stores all data (students, assignments, results)
- Has pgvector extension for vector similarity search
- Runs on port 5432

**FastAPI Backend**
- Handles all API requests
- Validates JWT tokens
- Processes file uploads
- Runs plagiarism detection
- Communicates with database
- Runs on port 8000

**n8n (Workflow Automation)**
- Receives webhooks from backend
- Can trigger additional processing
- Can send notifications
- Can integrate with external services
- Runs on port 5678

**pgAdmin (Database UI)**
- Web interface to view database
- Can run SQL queries
- View tables and data
- Runs on port 5050

## 🛠️ Troubleshooting

### Docker Issues

**Problem**: Docker containers won't start
```bash
# Stop all containers
docker-compose down

# Remove old volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### Database Connection Issues

**Problem**: Backend can't connect to database
- Wait 30 seconds for database to fully start
- Check if port 5432 is available
- Restart containers: `docker-compose restart`

### API Errors

**Problem**: 401 Unauthorized error
- Make sure you're logged in
- Check if your token is valid
- Token expires after 30 minutes - login again

## 📝 Development Notes

### Running Without Docker

1. Install PostgreSQL with pgvector extension
2. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables in `.env`
5. Run the application:
   ```bash
   python main.py
   ```

### Adding Academic Sources

To add more academic sources for plagiarism detection:

1. Edit `data/sample_academic_sources.json`
2. Add new entries with title, authors, abstract, full_text
3. Restart the application

## 🔐 Security Notes

- Change `JWT_SECRET_KEY` in production
- Use strong passwords
- Keep your OpenAI API key secret
- Don't commit `.env` file to Git

## 📚 Technologies Used

- **FastAPI**: Python web framework
- **PostgreSQL**: Database with pgvector extension
- **n8n**: Workflow automation
- **OpenAI**: AI embeddings for RAG
- **Docker**: Containerization
- **JWT**: Authentication

## 🤝 Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify all services are running: `docker-compose ps`
3. Restart services: `docker-compose restart`

## 🎬 Complete Workflow Example

Here's a complete example of using the system from start to finish:

### Scenario: Student submits an assignment on Machine Learning

**Step 1: Start the system**
```bash
docker-compose up -d
```

**Step 2: Register account**
- Go to http://localhost:8000/docs
- Use `/auth/register` with email: `alice@university.edu`

**Step 3: Login**
- Use `/auth/login` with credentials
- Copy the JWT token

**Step 4: Authorize**
- Click "Authorize" button
- Paste token

**Step 5: Upload assignment**
- Use `/upload` endpoint
- Upload file: `ml_assignment.txt`
- Topic: "Neural Networks"
- Level: "Graduate"
- Get assignment ID: `1`

**Step 6: Get analysis**
- Use `/analysis/1` endpoint
- View results:
  ```json
  {
    "plagiarism_score": 0.15,
    "suggested_sources": [...],
    "research_suggestions": "Consider exploring...",
    "citation_recommendations": "Use APA format..."
  }
  ```

**Step 7: Search for more sources**
- Use `/sources?query=neural networks&limit=10`
- Get list of relevant academic papers

## 📊 Understanding the Results

### Plagiarism Score Interpretation
- **0.0 - 0.2**: Low plagiarism (acceptable)
- **0.2 - 0.5**: Moderate plagiarism (review needed)
- **0.5 - 0.8**: High plagiarism (significant issues)
- **0.8 - 1.0**: Very high plagiarism (major concerns)

### What Gets Analyzed
1. **Text similarity**: Compares your text with academic sources
2. **Source suggestions**: Papers related to your topic
3. **Research tips**: What to explore further
4. **Citation format**: How to properly cite sources

## 🚦 Project Status Indicators

### Check if everything is working:

```bash
# Check all services
docker-compose ps

# Should show:
# academic_backend    running    0.0.0.0:8000->8000/tcp
# academic_db         running    0.0.0.0:5432->5432/tcp
# academic_n8n        running    0.0.0.0:5678->5678/tcp
# academic_pgadmin    running    0.0.0.0:5050->80/tcp
```

### Test the API:
```bash
# Should return: {"status": "ok", "message": "API is running"}
curl http://localhost:8000/health
```

## 📝 Quick Reference Card

| Task | Command |
|------|---------|
| Start project | `docker-compose up -d` |
| Stop project | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Restart backend | `docker-compose restart backend` |
| Fresh start | `docker-compose down -v && docker-compose up --build` |
| Check status | `docker-compose ps` |
| Access API docs | http://localhost:8000/docs |
| Access database | http://localhost:5050 |
| Access n8n | http://localhost:5678 |

## 🔧 Troubleshooting Docker Compose

### Problem: Containers won't start

**Check Docker is running:**
```bash
docker --version
docker-compose --version
```

**View logs to see errors:**
```bash
docker-compose logs
```

### Problem: Port already in use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:** Stop the service using that port or change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Problem: Database connection failed

**Check database is healthy:**
```bash
docker-compose ps
# Look for "Up (healthy)" next to academic_db
```

**Wait longer:** Database takes 20-30 seconds to initialize

**Restart database:**
```bash
docker-compose restart db
```

### Problem: Backend shows errors

**View backend logs:**
```bash
docker-compose logs -f backend
```

**Common issues:**
- Missing `.env` file → Create from `.env.example`
- Invalid OpenAI API key → Check your key at https://platform.openai.com/api-keys
- Database not ready → Wait 30 seconds and restart backend

**Rebuild backend:**
```bash
docker-compose stop backend
docker-compose build backend
docker-compose up -d backend
```

### Problem: Out of disk space

**Clean up Docker:**
```bash
# Remove unused images and containers
docker system prune -a

# Remove volumes (WARNING: deletes all data!)
docker-compose down -v
```

### Problem: Need fresh start

**Complete reset:**
```bash
# Stop everything
docker-compose down -v

# Remove images
docker rmi academic-assignment-helper-backend

# Rebuild from scratch
docker-compose up --build
```

### Problem: OpenAI quota exceeded

**Error:** `Error code: 429 - You exceeded your current quota`

**Solution:** 
- Add credits to your OpenAI account at https://platform.openai.com/account/billing
- Or continue without embeddings (academic sources will be added without vector embeddings)

### Getting Help

**View all container logs:**
```bash
docker-compose logs
```

**View specific service logs:**
```bash
docker-compose logs backend
docker-compose logs db
docker-compose logs n8n
```

**Check container status:**
```bash
docker-compose ps
docker inspect academic_backend
```

## 🎓 Learning Resources

### Understanding the Technologies:
- **FastAPI**: Python web framework for building APIs
- **JWT**: JSON Web Tokens for secure authentication
- **PostgreSQL**: Relational database for storing data
- **pgvector**: Extension for vector similarity search
- **RAG**: Retrieval Augmented Generation for AI
- **Docker**: Containerization for easy deployment
- **n8n**: No-code workflow automation
- **Docker Compose**: Multi-container Docker applications

### Key Concepts:
- **Embeddings**: Converting text to numbers (vectors) for comparison
- **Cosine Similarity**: Measuring how similar two texts are
- **JWT Token**: A secure way to prove you're logged in
- **API Endpoint**: A URL that performs a specific function
- **Webhook**: A way for services to notify each other

## 📄 License

This project is for educational purposes.

---

**Made with ❤️ for students and educators**

For questions or issues, check the logs with `docker-compose logs`
