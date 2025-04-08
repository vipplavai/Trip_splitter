import streamlit as st
from collections import defaultdict

st.set_page_config(page_title="Trip Splitter", layout="wide")

# --- Initial Participants & Categories ---
participants = ["CR", "PALLE", "DOG", "NANI", "BABA", "VACHU", "GODA"]
default_categories = ["Food", "Fuel", "Stay", "Travel", "Activities", "Misc"]

# --- Session State Init ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'categories' not in st.session_state:
    st.session_state.categories = default_categories.copy()

# --- Main Content ---
st.title("🏄‍♂️ Mulki Trip Expense Splitter")
st.markdown("Welcome to the surf crew splitter. Add your expenses below and settle up later ✨")

st.header("➕ Add New Expense")
col1, col2 = st.columns(2)

with col1:
    paid_by = st.selectbox("Paid By", participants)
    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    description = st.text_input("Description", placeholder="e.g. Hotel, Taxi")

with col2:
    category_selection = st.selectbox("Select Category", st.session_state.categories + ["Other (Type below)"])
    custom_category = ""
    if category_selection == "Other (Type below)":
        custom_category = st.text_input("Custom Category", placeholder="e.g. Ice Cream, Cigarettes")
        category = custom_category.strip()
    else:
        category = category_selection

excluded_people = st.multiselect("Exclude people from split (optional)", participants, default=[])

if st.button("Add Expense"):
    if paid_by and amount > 0 and category:
        included_people = [p for p in participants if p not in excluded_people]
        st.session_state.expenses.append({
            "paid_by": paid_by,
            "amount": amount,
            "description": description,
            "category": category,
            "included": included_people
        })
        st.success(f"Added ₹{amount:.2f} by {paid_by} under {category}")
    else:
        st.warning("Please enter all fields including category.")

# --- Logs & History Section ---
st.markdown("---")
st.subheader("🔒 View Trip Summary (Protected)")

password = st.text_input("Enter password to view history", type="password")

if password == "mulki2024":
    if st.session_state.expenses:
        total = sum(e['amount'] for e in st.session_state.expenses)
        person_spent = defaultdict(float)
        for e in st.session_state.expenses:
            person_spent[e['paid_by']] += e['amount']

        person_owes = defaultdict(float)
        for e in st.session_state.expenses:
            share = e['amount'] / len(e['included'])
            for p in e['included']:
                person_owes[p] += share

        balances = {p: round(person_spent[p] - person_owes[p], 2) for p in participants}

        st.subheader("💰 Total Trip Cost")
        st.metric("Total", f"₹{total:.2f}")

        if st.toggle("📋 Show Net Balances"):
            for p, b in balances.items():
                if b > 0:
                    st.success(f"✅ {p}: +₹{b:.2f}")
                elif b < 0:
                    st.error(f"❌ {p}: -₹{-b:.2f}")
                else:
                    st.info(f"💤 {p}: Settled")

        if st.toggle("🔁 Show Who Owes Whom"):
            def optimize_settlements(bal):
                creditors = {k: v for k, v in bal.items() if v > 0}
                debtors = {k: -v for k, v in bal.items() if v < 0}
                txns = []
                creditors = dict(sorted(creditors.items(), key=lambda x: -x[1]))
                debtors = dict(sorted(debtors.items(), key=lambda x: -x[1]))
                for d in debtors:
                    for c in creditors:
                        if debtors[d] == 0:
                            break
                        if creditors[c] == 0:
                            continue
                        amt = round(min(debtors[d], creditors[c]), 2)
                        if amt > 0:
                            txns.append((d, c, amt))
                            debtors[d] -= amt
                            creditors[c] -= amt
                return txns

            transactions = optimize_settlements(balances)
            if transactions:
                for frm, to, amt in transactions:
                    st.write(f"👉 `{frm}` owes `{to}` ₹{amt:.2f}")
            else:
                st.success("Everyone is settled. No dues pending!")
else:
    if password:
        st.error("Incorrect password ❌")
