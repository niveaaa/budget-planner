import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import BudgetDatabase
import calendar

# Page configuration
st.set_page_config(
    page_title="Budget Planner",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = BudgetDatabase()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def format_inr(amount):
    """Format amount in INR currency"""
    return f"₹{amount:,.2f}"

def get_month_date_range(month, year):
    """Get start and end date for a month"""
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day).strftime('%Y-%m-%d')
    return start_date, end_date

# Header
st.markdown('<h1 class="main-header">💰 Budget Planner</h1>', unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.markdown("## 📅 Filter Options")
    st.markdown("Apply filters to Dashboard and Transactions")
    st.markdown("---")
    
    # Date filter
    filter_type = st.selectbox("Time Period", ["This Month", "Last Month", "This Year", "Custom Range"])
    
    today = datetime.now()
    
    if filter_type == "This Month":
        start_date, end_date = get_month_date_range(today.month, today.year)
    elif filter_type == "Last Month":
        last_month = today.month - 1 if today.month > 1 else 12
        last_year = today.year if today.month > 1 else today.year - 1
        start_date, end_date = get_month_date_range(last_month, last_year)
    elif filter_type == "This Year":
        start_date = datetime(today.year, 1, 1).strftime('%Y-%m-%d')
        end_date = datetime(today.year, 12, 31).strftime('%Y-%m-%d')
    else:
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("From", today - timedelta(days=30))
        with col2:
            end = st.date_input("To", today)
        start_date = start.strftime('%Y-%m-%d')
        end_date = end.strftime('%Y-%m-%d')

# Main content with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "➕ Add Transaction", "🎯 Set Budgets", "📝 Transactions", "⚙️ Settings"])

with tab1:
    st.markdown("### 📊 Budget Dashboard")
    st.markdown("---")
    
    # Get transactions
    transactions = db.get_transactions(start_date=start_date, end_date=end_date)
    
    # Calculate metrics
    total_income = transactions[transactions['type'] == 'income']['amount'].sum() if not transactions.empty else 0
    total_expenses = transactions[transactions['type'] == 'expense']['amount'].sum() if not transactions.empty else 0
    savings = total_income - total_expenses
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 Total Income",
            value=format_inr(total_income),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=format_inr(total_expenses),
            delta=None
        )
    
    with col3:
        st.metric(
            label="💰 Savings",
            value=format_inr(savings),
            delta=format_inr(savings) if savings >= 0 else format_inr(savings),
            delta_color="normal" if savings >= 0 else "inverse"
        )
    
    with col4:
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        st.metric(
            label="📊 Savings Rate",
            value=f"{savings_rate:.1f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Expenses by Category")
        expense_data = db.get_spending_by_category(start_date, end_date)
        
        if not expense_data.empty:
            fig = px.pie(
                expense_data,
                values='total',
                names='category',
                title='Expense Breakdown',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available for the selected period.")
    
    with col2:
        st.subheader("🎯 Budget vs Actual")
        
        # Get current month budgets
        current_month = datetime.strptime(end_date, '%Y-%m-%d').month
        current_year = datetime.strptime(end_date, '%Y-%m-%d').year
        budgets = db.get_all_budgets(current_month, current_year)
        
        if not budgets.empty and not expense_data.empty:
            # Merge budgets with actual spending
            comparison = budgets.merge(expense_data, on='category', how='left')
            comparison['total'] = comparison['total'].fillna(0)
            comparison['remaining'] = comparison['amount'] - comparison['total']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Budget',
                x=comparison['category'],
                y=comparison['amount'],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Actual',
                x=comparison['category'],
                y=comparison['total'],
                marker_color='indianred'
            ))
            
            fig.update_layout(
                title='Budget vs Actual Spending',
                barmode='group',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Set budgets to see comparison with actual spending.")
    
    # Recent transactions
    st.markdown("---")
    st.subheader("📝 Recent Transactions")
    
    if not transactions.empty:
        recent = transactions.head(10).copy()
        recent['amount'] = recent.apply(
            lambda x: format_inr(x['amount']) if x['type'] == 'expense' else format_inr(x['amount']),
            axis=1
        )
        st.dataframe(
            recent[['date', 'type', 'category', 'description', 'amount']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions found. Start by adding income or expenses!")

with tab2:
    st.markdown('<h2 class="main-header">➕ Add Transaction</h2>', unsafe_allow_html=True)
    
    subtab1, subtab2 = st.tabs(["💵 Add Income", "💸 Add Expense"])
    
    with subtab1:
        st.subheader("Add Income")
        
        with st.form("income_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                income_amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key="income_amount"
                )
                income_categories = db.get_categories('income')
                income_category = st.selectbox("Category", income_categories, key="income_cat")
            
            with col2:
                income_date = st.date_input("Date", datetime.now(), key="income_date")
                income_description = st.text_input("Description", key="income_desc")
            
            submitted = st.form_submit_button("Add Income", type="primary")
            
            if submitted:
                if income_amount > 0:
                    # Remove emoji from category name
                    clean_category = income_category.split(' ', 1)[1] if ' ' in income_category else income_category
                    db.add_transaction(
                        amount=income_amount,
                        category=clean_category,
                        description=income_description,
                        date=income_date.strftime('%Y-%m-%d'),
                        trans_type='income'
                    )
                    st.success(f"✅ Income of {format_inr(income_amount)} added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid amount.")
    
    with subtab2:
        st.subheader("Add Expense")
        
        with st.form("expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                expense_amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key="expense_amount"
                )
                expense_categories = db.get_categories('expense')
                expense_category = st.selectbox("Category", expense_categories, key="expense_cat")
            
            with col2:
                expense_date = st.date_input("Date", datetime.now(), key="expense_date")
                expense_description = st.text_input("Description", key="expense_desc")
            
            submitted = st.form_submit_button("Add Expense", type="primary")
            
            if submitted:
                if expense_amount > 0:
                    # Remove emoji from category name
                    clean_category = expense_category.split(' ', 1)[1] if ' ' in expense_category else expense_category
                    db.add_transaction(
                        amount=expense_amount,
                        category=clean_category,
                        description=expense_description,
                        date=expense_date.strftime('%Y-%m-%d'),
                        trans_type='expense'
                    )
                    st.success(f"✅ Expense of {format_inr(expense_amount)} added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid amount.")

with tab3:
    st.markdown('<h2 class="main-header">🎯 Set Monthly Budgets</h2>', unsafe_allow_html=True)
    
    # Month/Year selector
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_month = st.selectbox(
            "Month",
            range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=datetime.now().month - 1
        )
    with col2:
        selected_year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year)
    
    st.markdown("---")
    
    # Get expense categories
    categories = db.get_categories('expense')
    
    st.subheader(f"Set Budgets for {calendar.month_name[selected_month]} {selected_year}")
    
    # Get existing budgets
    existing_budgets = db.get_all_budgets(selected_month, selected_year)
    budget_dict = {}
    if not existing_budgets.empty:
        budget_dict = dict(zip(existing_budgets['category'], existing_budgets['amount']))
    
    with st.form("budget_form"):
        budget_values = {}
        
        cols = st.columns(2)
        for idx, category in enumerate(categories):
            clean_category = category.split(' ', 1)[1] if ' ' in category else category
            current_budget = budget_dict.get(clean_category, 0.0)
            
            with cols[idx % 2]:
                budget_values[clean_category] = st.number_input(
                    f"{category}",
                    min_value=0.0,
                    value=float(current_budget),
                    step=500.0,
                    format="%.2f",
                    key=f"budget_{clean_category}"
                )
        
        submitted = st.form_submit_button("Save Budgets", type="primary")
        
        if submitted:
            for category, amount in budget_values.items():
                if amount > 0:
                    db.set_budget(category, amount, selected_month, selected_year)
            st.success("✅ Budgets saved successfully!")
            st.rerun()
    
    # Show budget summary
    if not existing_budgets.empty:
        st.markdown("---")
        st.subheader("📊 Budget Summary")
        total_budget = existing_budgets['amount'].sum()
        st.metric("Total Monthly Budget", format_inr(total_budget))

with tab4:
    st.markdown('<h2 class="main-header">📝 Transaction History</h2>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_trans_type = st.selectbox("Type", ["All", "Income", "Expense"])
    with col2:
        all_categories = ["All"] + db.get_categories()
        filter_category = st.selectbox("Category", all_categories)
    with col3:
        sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High to Low)", "Amount (Low to High)"])
    
    # Get transactions
    trans_type_filter = None if filter_trans_type == "All" else filter_trans_type.lower()
    category_filter = None if filter_category == "All" else filter_category.split(' ', 1)[1] if ' ' in filter_category else filter_category
    
    transactions = db.get_transactions(
        start_date=start_date,
        end_date=end_date,
        trans_type=trans_type_filter,
        category=category_filter
    )
    
    if not transactions.empty:
        # Sort transactions
        if sort_by == "Date (Oldest)":
            transactions = transactions.sort_values('date', ascending=True)
        elif sort_by == "Amount (High to Low)":
            transactions = transactions.sort_values('amount', ascending=False)
        elif sort_by == "Amount (Low to High)":
            transactions = transactions.sort_values('amount', ascending=True)
        
        st.markdown(f"**Total Transactions:** {len(transactions)}")
        
        # Display transactions
        for idx, row in transactions.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
            
            with col1:
                st.write(f"**{row['date']}**")
            with col2:
                type_icon = "💵" if row['type'] == 'income' else "💸"
                st.write(f"{type_icon} {row['type'].title()}")
            with col3:
                st.write(f"**{row['category']}** - {row['description']}")
            with col4:
                color = "green" if row['type'] == 'income' else "red"
                st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:1.1em;'>{format_inr(row['amount'])}</span>", unsafe_allow_html=True)
            with col5:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    db.delete_transaction(row['id'])
                    st.rerun()
            
            st.markdown("---")
    else:
        st.info("No transactions found for the selected filters.")

with tab5:
    st.markdown('<h2 class="main-header">⚙️ Settings</h2>', unsafe_allow_html=True)
    
    setting_tab1, setting_tab2, setting_tab3 = st.tabs(["📂 Export Data", "🗑️ Clear Data", "ℹ️ About"])
    
    with setting_tab1:
        st.subheader("Export Transaction Data")
        st.write("Download your transaction history as CSV file.")
        
        transactions = db.get_transactions()
        if not transactions.empty:
            csv = transactions.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"budget_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No transactions to export.")
    
    with setting_tab2:
        st.subheader("⚠️ Clear All Data")
        st.warning("This will delete all transactions and budgets. This action cannot be undone!")
        
        confirm = st.checkbox("I understand that this will delete all my data")
        if st.button("Clear All Data", type="primary", disabled=not confirm):
            db.clear_all_data()
            st.success("All data cleared successfully!")
            st.rerun()
    
    with setting_tab3:
        st.subheader("About Budget Planner")
        st.markdown("""
        **Budget Planner** helps you track your income and expenses, set budgets, and visualize your spending patterns.
        
        **Features:**
        - 💰 Track income from multiple sources
        - 💸 Record expenses by category
        - 🎯 Set monthly budgets for each category
        - 📊 Visualize spending with interactive charts
        - 📝 View detailed transaction history
        - 📈 Monitor savings rate and financial health
        
        **Currency:** Indian Rupee (₹)
        
        **Data Storage:** All data is stored locally in SQLite database.
        
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Budget Planner v1.0 | Data stored locally</div>",
    unsafe_allow_html=True
)
