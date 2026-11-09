import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Personal Automation Hub", page_icon="⚙️", layout="wide")
st.title("⚙️ Personal Automation Hub")
st.caption("One place to open and monitor your independent automation projects.")

st.info("This is the central dashboard. Existing projects are linked below. Gold/silver live price collection and scheduled report generation will be added after reliable seller data sources are configured.")

apps = [
    ("GST Intelligence Hub", "Daily GST research and new YouTube updates.", "https://gst-intelligence-app-eu6u8kvtzmf2vxdnnmnv2a8.streamlit.app/"),
    ("NSE Swing Screener", "Daily swing-trading shortlist and portfolio tools.", "https://nse-swing-screener-k6yhrtpbsuofyubzzafrce.streamlit.app/"),
]
cols = st.columns(2)
for col, (name, desc, url) in zip(cols, apps):
    with col:
        st.subheader(name)
        st.write(desc)
        st.link_button("Open application", url, use_container_width=True)

st.divider()
st.header("Gold & Silver Price Tracker")
st.write("Planned daily comparison for 24K gold and silver, using delivery PIN code **110047**.")
st.markdown("""
**Final-cost comparison will include, where the seller discloses them:**
- Metal price
- GST
- Making / minting charges
- Delivery and other compulsory charges
- Final payable amount

The tracker will identify the lowest verified final cost, not merely the lowest headline rate. Prices will not be shown as verified until a source provides the required cost details.
""")
st.warning("WhatsApp delivery is not enabled. This free version will publish reports in the dashboard for you to share manually through WhatsApp Business.")

st.divider()
st.subheader("Automation schedule")
st.write("Planned daily run: 9:00 AM India time (03:30 UTC).")
st.caption(f"Dashboard opened: {datetime.now().astimezone().strftime('%d-%m-%Y %I:%M %p %Z')}")
st.caption("Do not upload confidential departmental records, personal data, statements or protected investigation material to this public repository or public dashboard.")
