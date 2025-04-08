import streamlit as st
from collections import defaultdict

st.set_page_config(page_title="Trip Expense Splitter", layout="centered")

# ----- Preloaded Participants -----
default_participants = [
    "CR (Prashanth)",
    "PALLE (Pranay)",
    "BABA (Dinesh)",
    "GODA (Rithwik)",
    "VACHU (Vachan)",
    "DOG (Vishnu)",
    "NANI (Vineel)"
]

# ----- Session State Initialization -----
if 'participants' not in st.session_state:
    st.session_state.participants = default_participants.copy()
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# ----- Title -----
st.title("🏝️ Mulki Trip Expense Splitter")
st.markdown("Track and split trip expenses easily among friends! 💸")

# ----- Add Expense Section -----
st.header("➕ Add New Expense")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    description = st.text_input("Description (e.g., Lunch, Cab)")

with col2:
    paid_by = st.selectbox("Paid by", st.session_state.participants)
    split_between = st.multiselect("Split between", st.session_state.participants, default=st.session_state.participants)

if st.button("Add Expense"):
    if amount > 0 and paid_by and split_between:
        st.session_state.expenses.append({
            "amount": amount,
            "description": description,
            "paid_by": paid_by,
            "split_between": split_between
        })
        st.success("Expense added!")
    else:
        st.warning("Please fill all fields.")

# ----- Expense Log -----
if st.session_state.expenses:
    st.subheader("📜 Expense Log")
    for i, exp in enumerate(st.session_state.expenses, 1):
        st.markdown(
            f"**{i}. {exp['paid_by']} paid ₹{exp['amount']:.2f}** "
            f"for _{exp['description']}_ split among {', '.join(exp['split_between'])}"
        )

# ----- Split Summary -----
if st.session_state.expenses:
    st.subheader("📊 Who Owes Whom")

    balances = defaultdict(float)

    for exp in st.session_state.expenses:
        share = exp["amount"] / len(exp["split_between"])
        for p in exp["split_between"]:
            if p != exp["paid_by"]:
                balances[p] -= share
                balances[exp["paid_by"]] += share

    def get_optimized_transactions(bal):
        pay = {k: round(v, 2) for k, v in bal.items() if v < 0}
        receive = {k: round(v, 2) for k, v in bal.items() if v > 0}
        transactions = []
        for debtor, d_amt in pay.items():
            for creditor, c_amt in receive.items():
                if d_amt == 0:
                    break
                amt = min(-d_amt, c_amt)
                if amt > 0:
                    transactions.append((debtor, creditor, amt))
                    pay[debtor] += amt
                    receive[creditor] -= amt
        return transactions

    txns = get_optimized_transactions(balances)

    if txns:
        for debtor, creditor, amt in txns:
            st.write(f"👉 **{debtor}** owes **{creditor}** ₹{amt:.2f}")
    else:
        st.success("🎉 All settled up! No pending balances.")

# ----- Reset Button -----
st.markdown("---")
if st.button("🧹 Reset All Data"):
    st.session_state.expenses = []
    st.success("All expenses cleared!")
