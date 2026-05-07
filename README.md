# Agentic Way of Shopping

Agentic Way of Shopping is an AI-powered shopping assistant that helps users find products online based on a simple text request. Users can sign up or log in, describe what they want to buy, add preferences such as budget, color, brand, or shipping requirements, and receive ranked product recommendations with explanations.

The application is designed to search the internet, collect product candidates, filter and rank them based on user preferences, and display the best matches in a user-friendly interface.

> **Note:** The “Buy” feature is optional. If we have enough time, we will develop a purchase confirmation workflow. Otherwise, the system will focus on search, ranking, and recommendation.

---

## Features

- User signup and login
- Text-based product search
- Optional preference input, such as budget, color, brand, size, or features
- AI agent that searches the internet for relevant products
- Product filtering and ranking
- Product details including name, price, image, link, and recommendation reason
- User-friendly frontend interface
- Backend API built with FastAPI
- Database support for users, sessions, messages, and recommendations
- Optional future buying workflow

---

## Project Overview

The user only needs to describe a product category or shopping goal. The AI agent uses the user’s request, preferences, and comments to search across the internet and return the top items that best match the request.

Example user input:

```text
I need a birthday gift for my son. Budget around 100 euros. Maybe a watch.
```

The system then:

1. Parses the user request.
2. Creates search queries.
3. Searches online sources.
4. Collects product information.
5. Filters and ranks results.
6. Displays recommended products with short explanations.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLite
- LangChain
- Ollama
- Qwen model
- Playwright
- DuckDuckGo / Brave search tools

### Frontend

- React
- TypeScript
- Vite
- Material UI

---

## Requirements

Before running the project, make sure you have:

- Python installed (recommended: 3.10+)
- Node.js and npm installed (recommended: Node 18+)
- Ollama installed
- A supported GPU for acceptable performance

For testing, **Qwen 3.5 9B** is currently used.

For better results, **Qwen 3.6 35B** is recommended.

During testing, the team encountered issues when running the model on an **RTX PRO 5000 48GB GPU**. Since this is a newly released GPU, there may be compatibility conflicts.

Recommended GPU:

```text
RTX 3090
```

If you are running the app on the SAMK AI server, **server2** has this GPU available.

> We strongly recommend running this project on the SAMK AI server if your local machine does not have a GPU better than an RTX 3090. On a local RTX 4070 machine, the first result took around 30 minutes. On the AI server, it took around 5 minutes.

---

## Run After Cloning (Windows 11)

These steps assume your laptop is clean and you already installed Python, Node.js, and Ollama.

You must run **3 terminals**:

1. Ollama terminal
2. Backend terminal
3. Frontend terminal

### 1. Clone and open the project

```powershell
git clone https://github.com/MinMyatNgwe1017/Agentic_WAY_OF_SHOPPING.git
cd Agentic_WAY_OF_SHOPPING
```

### 2. Backend setup (first time only)

```powershell
cd backend\app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install
playwright install-deps
playwright install firefox
```

### 3. Ollama setup and run

Open a new terminal and run:

```powershell
ollama serve

ollama pull qwen3.5:9b
```

Keep this terminal open while using the app.

### 4. Start backend API

In the backend terminal (where `.venv` is activated), run:

```powershell
uvicorn main:app --reload
```

Backend should run at:

```text
http://127.0.0.1:8000
```

Quick test in browser:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{ "message": "This is root", "version": "1.0.0" }
```

### 5. Start frontend

Open another terminal and run:

```powershell
cd Agentic_WAY_OF_SHOPPING\frontend
npm install
npm run dev
```

Open the URL shown in the terminal (usually `http://localhost:5173` or `http://localhost:5174`).

### 6. If frontend cannot connect to backend

Create a file at `frontend\.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Then restart frontend:

```powershell
npm run dev
```

---

## Linux Notes

A Linux install script exists at `backend/app/install.sh`, but it includes system-level Node.js removal/purge commands. Review it carefully before use.

---

## Usage

1. Start Ollama, backend, and frontend.
2. Open the frontend URL in your browser.
3. Sign up or log in.
4. Type a shopping request.
5. Wait for the agent to search and return recommendations.
6. View product results and open product links.

Example input:

```text
Find me second-hand phones around 100 euros.
```

Example output:

```text
Product name: Example Phone
Price: €99
Reason: Good match because it fits the budget and has strong reviews.
Link: Product URL
```

---

## User Journey

1. User signs up or logs in.
2. User enters a product category or shopping request.
3. User optionally adds preferences, such as budget, color, brand, size, or shipping needs.
4. The backend sends the request to the AI agent.
5. The agent searches online sources.
6. Product data is collected and filtered.
7. The best products are ranked.
8. The frontend displays the recommendations.
9. The user can view product details or refine the search.
10. If time allows, the optional Buy workflow will show a final confirmation before purchase.

---

## Program Logic

1. **Authenticate user**
   The user logs in or creates an account.

2. **Load user profile**
   The system loads saved user data from the database.

3. **Receive user input**
   The user submits a product category and optional preferences.

4. **Parse request**
   The AI agent extracts key constraints such as budget, brand, color, and features.

5. **Build search plan**
   The agent generates search queries.

6. **Search the web**
   The system collects product candidates from online sources.

7. **Extract product data**
   The system extracts product name, price, image, link, and other useful details.

8. **Filter results**
   The system removes products that do not match hard constraints.

9. **Rank recommendations**
   The agent ranks products based on user needs and preferences.

10. **Return results**
    The frontend displays recommended products.

11. **Optional purchase flow**
    If we have enough time, the Buy button will show a final confirmation screen before completing a purchase workflow.

---

## Project Structure

```text
backend/
  app/
    main.py
    ai_model.py
    db.py
    ai_tools.py
    web_scraping.py
    prompts.py
    requirements.txt
    install.sh

frontend/
  src/
    services/
      api.ts
    pages/
    components/
```

---

## Main Modules

### `main.py`

Starts the FastAPI backend, defines API routes, connects the frontend to the AI agent, and handles authentication and chat requests.

Responsible team member: **Sufiyan**

### `ai_model.py`

Contains the main AI agent logic, including request parsing, search query generation, search handling, product ranking, and recommendation generation.

Responsible team member: **Min Myat Ngwe**

### `db.py`

Handles database setup and database operations such as creating users, verifying users, storing messages, and saving recommendations.

Responsible team member: **Davut**

### Frontend

Handles signup, login, chat input, product display, and user interaction.

Responsible team member: **Israel**

### Backend Integration

Connects the UI, database, and AI agent through API endpoints.

Responsible team members: **Sufiyan and Davut**

---

## Team Members

- **Min Myat Ngwe** — AI agent and internet search logic
- **Israel** — Frontend design and user interface
- **Sufiyan** — Backend APIs, authentication, and integration
- **Davut** — Database design, storage, and data consistency

---

## Development Timeline

### Milestone 1 — February 14, 2026

- Basic project structure completed
- Repository and folder structure ready
- `main.py` runs
- Basic login and input flow works
- Placeholder results displayed

### Milestone 2 — February 28, 2026

- Frontend, backend, agent, and database connected
- Real internet search returns product results
- Results display correctly in the UI

### Milestone 3 — March 7, 2026

- Testing completed
- Bugs fixed
- Edge cases handled
- Documentation completed
- Final version submitted

---

## Development Rules

- Use `snake_case` for Python variable and function names.
- Use clear function and file names.
- Test integration between frontend, backend, database, and agent regularly.
- Communicate using WhatsApp for quick updates.
- Use Discord or Teams for meetings and screen sharing.

---

## Known Limitations

- Product scraping may fail on some websites because of anti-bot protection or page structure changes.
- The AI model can be slow on weaker GPUs.
- Some search results may not contain complete price, image, or title data.
- The Buy workflow is optional and will only be developed if there is enough time.
- The project currently focuses on recommendation, not guaranteed purchase automation.

---

## Troubleshooting

### Backend is not connecting

Check that the backend is running:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{
  "message": "This is root",
  "version": "1.0.0"
}
```

### Frontend is calling the wrong port

Check `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

If missing, create it and restart frontend.

### Ollama model is slow

Check if the model is running:

```bash
ollama ps
```

Check GPU usage:

```bash
nvidia-smi
```

### Playwright errors

Reinstall Playwright browsers:

```bash
playwright install
playwright install firefox
```

---

## Contributing

Team members should create or update their assigned modules and test their changes before merging.

For major changes:

1. Discuss with the team first.
2. Make sure the backend and frontend still run.
3. Test integration with related modules.
4. Update documentation if needed.

---

## License

A license has not been finalized yet.

Useful license references:

- https://choosealicense.com/
- https://opensource.org/licenses

Popular choices include:

- MIT
- Apache
- GPL
- BSD

---

## Useful Resources

### README and Markdown

- https://www.makeareadme.com/
- https://docs.github.com/en/get-started/writing-on-github
- https://github.github.com/gfm/
- https://en.wikipedia.org/wiki/README

### Git

- https://gitignore.io/
- https://github.com/github/gitignore
- https://www.conventionalcommits.org/

### Possible API Sources

- https://api.nasa.gov/
- https://pokeapi.co/
- https://www.exchangerate-api.com/
- https://randomuser.me/
- https://softwium.com/fake-api/
- https://fakerapi.it/
- https://www.7timer.info/doc.php?lang=en
- https://github.com/chubin/wttr.in
