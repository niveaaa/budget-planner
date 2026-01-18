# 💰 Budget Planner

A simple, local-first **Budget Planner web app** built with **Streamlit** to help you track income, expenses, set monthly budgets, and visualize where your money mysteriously disappears every month.

No cloud. No login. No judgement. Just numbers.

---

## ✨ Features

- 💵 Track **income** from multiple sources  
- 💸 Record **expenses** with categories  
- 🎯 Set **monthly budgets** per category  
- 📊 Interactive charts for spending insights  
- 📝 Full transaction history with filters & sorting  
- 📈 Savings rate and financial overview  
- 📂 Export data as CSV  
- 🗑️ One-click data wipe for fresh starts  

**Currency:** Indian Rupee (₹)  
**Storage:** Local SQLite database  

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** SQLite  
- **Data Handling:** Pandas  
- **Visualization:** Plotly  

---

## 📁 Project Structure

```text
.
├── app.py              # Main Streamlit application
├── database.py         # SQLite database logic
├── budget_planner.db   # Local database (auto-created)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/niveaaa/budget-planner.git
cd budget-planner
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App

```bash
streamlit run app.py
```

---

## 🧠 How It Works

- All data is stored locally using SQLite
- Categories are auto-initialized on first run
- Budgets are set per month & year
- Dashboard updates dynamically based on filters
- No external APIs. No internet dependency after setup

---

## 📊 App Sections

- Dashboard: Overview, charts, savings, recent transactions
- Add Transaction: Log income or expenses
- Set Budgets: Monthly category-wise budgeting
- Transactions: Filter, sort, and delete records
- Settings: Export CSV, clear data, app info

---

## 🔐 Privacy

Your data never leaves your machine.
No accounts. No tracking. No funny business.

---

## 📌 Future Improvements (aka ideas that may or may not happen)

- 🔔 Budget alerts
- 📱 Mobile-first UI tweaks
- 🌙 Dark mode
- 📅 Recurring transactions
- 🧾 Receipt uploads

---