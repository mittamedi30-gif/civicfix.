
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CivicFix", page_icon="🏙️", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
    color: #172b4d;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}
.hero {
    background: linear-gradient(120deg, #123b5d, #176b62);
    padding: 35px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 8px;
}
.hero p {
    color: #e1f4f1;
    font-size: 17px;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e0e8f0;
    box-shadow: 0 3px 12px rgba(20, 50, 80, 0.06);
}
div[data-testid="stMetricLabel"] {
    color: #52657a;
}
div[data-testid="stMetricValue"] {
    color: #123b5d;
    font-weight: 700;
}
.stButton > button,
.stFormSubmitButton > button {
    background-color: #176b62;
    color: white;
    border-radius: 9px;
    border: none;
    padding: 8px 18px;
    font-weight: 600;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #105047;
    color: white;
    border: none;
}
div[data-testid="stExpander"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #e0e8f0;
}
h2, h3 {
    color: #123b5d;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🏙️ CivicFix</h1>
    <p>Report civic problems. Track progress.
    Build a cleaner, safer community.</p>
</div>
""", unsafe_allow_html=True)


categories = [
    "Pothole",
    "Broken Streetlight",
    "Damaged Footpath",
    "Overflowing Garbage Bin"
]

statuses = ["Reported", "In Progress", "Resolved"]

# Sample data for the first demonstration
if "reports" not in st.session_state:
    st.session_state.reports = [
        {
            "id": 1,
            "category": "Pothole",
            "location": "Main Road",
            "description": "Large pothole near the bus stop",
            "status": "Reported",
            "created": "2026-10-20 09:00",
            "photo": None
        },
        {
            "id": 2,
            "category": "Broken Streetlight",
            "location": "Park Street",
            "description": "Streetlight is not working",
            "status": "In Progress",
            "created": "2026-10-20 10:30",
            "photo": None
        },
        {
            "id": 3,
            "category": "Overflowing Garbage Bin",
            "location": "Market Road",
            "description": "Garbage bin needs collection",
            "status": "Resolved",
            "created": "2026-10-20 12:00",
            "photo": None
        }
    ]

reports = st.session_state.reports

# Dashboard
total = len(reports)
pending = sum(r["status"] == "Reported" for r in reports)
progress = sum(r["status"] == "In Progress" for r in reports)
resolved = sum(r["status"] == "Resolved" for r in reports)

a, b, c, d = st.columns(4)
a.metric("Total Reports", total)
b.metric("Reported", pending)
c.metric("In Progress", progress)
d.metric("Resolved", resolved)

st.divider()

# Report a problem
st.header("1. Report a Civic Issue")

with st.form("report_form", clear_on_submit=True):
    category = st.selectbox("Problem Type", categories)
    location = st.text_input("Location", placeholder="Example: Main Road")
    description = st.text_area("Describe the problem")
    photo = st.file_uploader(
        "Upload a photo (optional)",
        type=["png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button("Submit Report")

    if submitted:
        if not location.strip() or not description.strip():
            st.error("Please enter the location and description.")
        else:
            duplicate = any(
                r["category"] == category
                and r["location"].strip().lower()
                == location.strip().lower()
                and r["status"] != "Resolved"
                for r in reports
            )

            if duplicate:
                st.warning(
                    "A similar unresolved report already exists "
                    "for this problem type and location."
                )
            else:
                new_id = max(
                    [r["id"] for r in reports], default=0
                ) + 1

                reports.append({
                    "id": new_id,
                    "category": category,
                    "location": location.strip(),
                    "description": description.strip(),
                    "status": "Reported",
                    "created": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "photo": (
                        photo.getvalue() if photo else None
                    )
                })

                st.success(
                    f"Report #{new_id} submitted successfully!"
                )
                st.rerun()

st.divider()

# View reports
st.header("2. Track Civic Issues")

if not reports:
    st.info("No reports available yet.")
else:
    for r in reversed(reports):
        with st.expander(
            f"#{r['id']} | {r['category']} | {r['status']}"
        ):
            st.write("**Location:**", r["location"])
            st.write("**Description:**", r["description"])
            st.write("**Submitted:**", r["created"])

            if r["photo"]:
                st.image(r["photo"], width=300)

st.divider()

# Staff dashboard
st.header("3. Staff Dashboard")
st.write("Update the progress of reported issues.")

for r in reports:
    with st.container(border=True):
        st.write(
            f"**Report #{r['id']} — {r['category']}**"
        )
        st.write("Location:", r["location"])

        current_index = statuses.index(r["status"])
        selected_status = st.selectbox(
            "Update status",
            statuses,
            index=current_index,
            key=f"status_{r['id']}"
        )

        if st.button(
            "Save Status",
            key=f"save_{r['id']}"
        ):
            r["status"] = selected_status
            st.success("Status updated.")
            st.rerun()

st.divider()

# Analytics and CSV export
st.header("4. Resolution Analytics")

if reports:
    chart_data = pd.DataFrame(reports)
    counts = (
        chart_data["status"]
        .value_counts()
        .reindex(statuses, fill_value=0)
    )
    st.bar_chart(counts)

    export_columns = [
        "id", "category", "location",
        "description", "status", "created"
    ]
    csv_data = chart_data[export_columns].to_csv(index=False)

    st.download_button(
        "Download Reports as CSV",
        data=csv_data,
        file_name="civicfix_reports.csv",
        mime="text/csv"
    )

st.caption(
    "CivicFix prototype: demonstration data only. "
    "Reports are stored in session memory."
)
