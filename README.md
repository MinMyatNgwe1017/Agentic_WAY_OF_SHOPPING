# Agentic Way Of Shopping - Group Design Document

**Team Members:**
Min Myat Ngwe,Israel,Davut,Sufiyan
**Date:**
7/2/2026
**Version:** 1.0

## 1. Project Overview

We’re building an application where the user only needs to specify a category. Based on the user’s saved preferences—along with their
references and comments the agent will search across the internet and return the top items that best match what the user likes.
If the user clicks “Buy” on an item, the agent will complete the purchase automatically using the account information provided during onboarding (e.g., delivery details and payment method).

## 2. Goals & Objectives

_What are the specific things our program must accomplish to be considered "finished"?_

- **Core Goal:**
  Implement an AI agent that can perform all functions described in the Project Overview except completing the purchase
  (i.e., it can search the internet, rank results based on user preferences, and present top recommendations).
- **Secondary Goal:**
  Build a simple, user-friendly user interface that allows users to select a category, review recommended items, and interact with results smoothly.
- **Third Goal:**
  Design and implement a database system to securely store user information and preferences, and integrate the buying workflow (purchase step)
  using the details provided during account creation/onboarding.

## 3. The User Journey

_How will a person interact with our code?_

- **The Experience:**
  The user signs up or logs in, then types a product category in a text box (for example: “headphones” or “running shoes”).
  They can also type extra preferences as plain text (like “budget under €200, black, good battery, fast shipping”) and submit.
  The agent searches the internet, selects and ranks the best-matching items based on the user’s saved preferences and previous feedback, and returns
  a short list with key details and a short explanation of why each item fits. The user can open an item to see more details,
  save it, or click Buy; if buying is enabled, the app shows a final text-based confirmation (item, total price, delivery address, payment method)
  and then completes the purchase using the account information provided during onboarding

- **Inputs:**
  The system only accepts text inputs: a category typed by the user, optional preference text
  (budget, brand, color, size, features, shipping requirements), and optional comments that guide the agent’s ranking
  (e.g., “avoid refurbished” or “prefer lightweight”). The user also provides simple action inputs by clicking buttons such as Search,
  View, Buy, Confirm, or Cancel, and they can type short feedback after viewing or buying (e.g., “good match” / “not my style”) to improve future recommendations.

## 4. Program Logic (Step-by-Step)

_Describe the path our code takes from start to finish. Use a numbered list to show the sequence of events._

**Start / Authenticate**: User opens the app and logs in (or creates an account).

**Load user profile**: System fetches the user’s stored preferences, past feedback/comments, and onboarding details from the database.

**Receive user input**: User types a category (and optional preference text) and submits the request.

**Parse the request**: The agent extracts key constraints from the text (e.g., budget, brand, features, shipping needs) and merges them with saved preferences.

**Build search plan**: The agent generates search queries and decides which sites/sources to check based on the category and constraints.

**Web search & collection**: The agent browses the internet, gathers product candidates, and extracts relevant data (title, price, rating, seller, shipping, URL, key specs).

**Normalize & filter**: The system cleans and standardizes collected data (currency, duplicates, missing fields) and removes items that do not meet hard constraints (e.g., over budget).

**Rank recommendations**: The agent scores and ranks remaining items using user preferences + feedback history (best match first).

**Return results**: App displays the top items with key details and a short “why recommended” explanation for each.

**User action**: User selects one of the options: view details, save, refine search (by typing new text), or click Buy.

**Purchase confirmation**: If Buy is clicked, the system shows a final summary (item, price, shipping, address, payment method) and asks for confirmation.## 5. Team Responsibility Breakdown

**Note (click buy will be implemented only if we have enough time)

_How are we dividing the work? Each member should have a primary area of focus._

- **Min Myat Ngwe**
  Implement the agent that searches the internet based on the user’s text input (category + preferences) and returns the best-matching items ranked by relevance.

- **Iseral**: Design and build the user interface so users can easily type their request, view results, open item details, and trigger actions like “Buy.”

- **Sufiyan**: Develop the backend APIs and connect the UI to the database and agent, handling requests, responses, authentication, and overall system integration.

- **Davut**: Manage and maintain the database system, including designing the schema, ensuring data security, handling updates/backups, and keeping user data consistent.

## 6. Module & Function Breakdown

_List the main parts of our code and which team member is responsible for them._

- **`main.py`**:
  Entry point that starts the app, loads user data, routes user requests to the agent/backend, and returns results to the UI. (Handled by: Sufiyan)
- **`ai_agent.py`**:
  Core agent logic: parse user text input, generate search queries, collect items from the internet,
  filter and rank results, and prepare the final recommendations. (Handled by: Min Myat Ngwe)
- **`database_module.py`**:
  Database-related functions: create/update tables, store user profiles and preferences, save search history/feedback,
  and retrieve data for the agent and UI. (Handled by: Davut)
- **frontend.py**
  Text-based UI screens/flows: login/signup, input category/preferences, show results, show details, and trigger buy/confirm actions. (Handled by: Iseral)
- **backend_module.py**:
  API endpoints and integration layer between UI, agent, and database (authentication, request handling, error handling). (Handled by: Sufiyan and Davut)

## 7. Data Storage & Structures

_How are we keeping track of information?_

- **Variables/Collections:**
  We will use lists to store the product results returned from the internet (each item contains title, price, rating, link, and reason).
  We will use dictionaries/JSON objects to represent a single product and a single user profile
  (preferences like budget, brands, sizes, shipping needs, and feedback history).
  We will also use simple strings for the user’s category and preference text input, and arrays/lists for search queries and filtering rules.

- **Persistence:**
  We will store long-term data in a database (e.g., SQLite/PostgreSQL). The database will keep user accounts, onboarding information,
  saved preferences, search history, clicked items,
  and feedback so the agent can personalize future recommendations.
  The app will read from the database at login and write updates after each search, click, feedback, or purchase attempt.

## 8. Development Timeline (Milestones)

_What is our plan for finishing on time?_
**Milestone 1:**
February 14, 2026 – Basic project structure is ready (repo setup, folder structure, main.py runs),
and the text-based flow works (login → enter category/preferences → placeholder results).

**Milestone 2:**
Milestone 2: February 28, 2026 – Modules are connected end-to-end (UI → backend → agent → database).
Real internet search returns items, and results display correctly.
**Milestone 3:**
Milestone 3: March 7, 2026 – Full testing and bug fixes completed, edge cases handled (no results, bad input, timeouts), documentation finished, and final version submitted.

---

### Team Checklist:

- **Consistency:** Are we all using the same variable naming style (e.g., `snake_case`)?
- Yes — we will use snake_case, clear function names, and consistent file/module naming
- **Communication:** How will we communicate? (e.g., Discord, Teams, Email, WhatsApp)
- We will communicate using WhatsApp for quick updates and Discord (or Teams) for meetings + screen sharing.
- **Integration:** Have we tested if Member A's function actually works with Member B's function?
- es — we will schedule integration tests twice per week (e.g., midweek + weekend) to confirm Member A’s functions work with Member B’s modules,
- and we will keep a shared checklist of “working connections” (UI↔Backend, Backend↔DB, Backend↔Agent).

## Setup 

**we strongly urge to run on samk ai sever if your gpu does not have enough gpu which is better   than RTX 3090 
we test our local machine which has RTX 4070 it took  around 30 mins to get first result
while if we run on ai server it tokk around 5mins to get result**
## Backend Setup

Go to the backend app folder:

```bash
cd backend/app
```

---

## Windows Setup

This project requires Ollama.

Download Ollama for Windows here:

https://www.ollama.com/download

After installing Ollama, pull the model:

```bash
ollama pull qwen3.5:9b
```

Create and activate the virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r .\requirements.txt
```

Install Playwright browsers and dependencies:

```bash
playwright install
playwright install-deps
playwright install firefox
```

---

## Linux Setup

Go to the backend app folder:

```bash
cd backend/app
```

Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

---

## Frontend Setup

Go to the frontend folder:

```bash
cd ../../frontend
```

Install frontend dependencies:

```bash
npm install
```

---

## Model Information

For testing purposes, **Qwen 3.5 9B** is currently used.

For better results, **Qwen 3.6 35B** is recommended.

During testing, the team encountered issues when running the model on an **RTX PRO 5000 48GB GPU**. Since this is a newly released GPU, there may be compatibility conflicts with the Qwen model.

The recommended GPU is:

```text
RTX 3090
```

If you are running the app on the AI server, **server2** has this GPU available.

To change the model, update the variable named `model` in:

```text
backend/app/main.py
```

---

## Running the App

### Start the Backend

From the backend app folder:

```bash
cd backend/app
uvicorn main:app --reload
```

By default, the backend runs on:

```text
http://127.0.0.1:8000
```

If you change the Uvicorn port, you must also update the backend URL in:

```text
frontend/src/services/api.ts
```

---

### Start the Frontend

Open a new terminal, then run:

```bash
cd frontend
npm run dev
```

The frontend usually runs on:

```text
http://localhost:5173
```

or:

```text
http://localhost:5174
```

Check the terminal output to confirm the exact URL.

License
https://choosealicense.com/

Popular choices: MIT, Apache, GPL, BSD

https://opensource.org/licenses

README/Markdown

https://en.wikipedia.org/wiki/README
https://www.makeareadme.com/
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
https://github.github.com/gfm/

Possible API sources:

https://api.nasa.gov/
https://pokeapi.co/
https://www.exchangerate-api.com/
https://randomuser.me/
https://softwium.com/fake-api/
https://fakerapi.it/
https://www.7timer.info/doc.php?lang=en
https://github.com/chubin/wttr.in

Git

https://gitignore.io/
https://github.com/github/gitignore
https://www.conventionalcommits.org/
