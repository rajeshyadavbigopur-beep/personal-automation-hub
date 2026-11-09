import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import StringIO

st.set_page_config(page_title="Personal Automation Hub", page_icon="⚙️", layout="wide")
st.title("⚙️ Personal Automation Hub")
st.caption("Central dashboard for your independent tools")

# Existing applications
c1, c2 = st.columns(2)
with c1:
    st.subheader("GST Intelligence Hub")
    st.write("Daily GST research and new YouTube updates.")
    st.link_button("Open GST application", "https://gst-intelligence-app-eu6u8kvtzmf2vxdnnmnv2a8.streamlit.app/", use_container_width=True)
with c2:
    st.subheader("NSE Swing Screener")
    st.write("Daily swing-trading shortlist and portfolio tools.")
    st.link_button("Open NSE application", "https://nse-swing-screener-k6yhrtpbsuofyubzzafrce.streamlit.app/", use_container_width=True)

st.divider()
st.header("🥇 Gold & Silver Price Tracker")
st.write("Delivery PIN code: **110047** | Daily comparison target: **9:00 AM IST**")
st.info("Tracker setup – Phase 1: enter or record seller checkout quotes. The system calculates the complete payable amount and ranks comparable offers. Automatic extraction from multiple seller websites is not enabled yet; a headline rate is not treated as a final purchase price.")

with st.expander("Official reference rate – indicative only", expanded=False):
    st.write("MMTC-PAMP publishes indicative 24K gold and 999.9+ silver rates excluding GST. These rates are useful as a benchmark, but they are not the final delivered price of a coin or bar.")
    st.link_button("View MMTC-PAMP daily gold & silver rates", "https://www.mmtcpamp.com/gold-silver-rate-today")
    st.link_button("View MMTC-PAMP coins and bars", "https://www.mmtcpamp.com/shop")

if "quotes" not in st.session_state:
    st.session_state.quotes = pd.DataFrame(columns=[
        "Checked on", "Metal", "Product", "Weight (g)", "Purity", "Seller",
        "Product price (₹)", "GST (₹)", "Making/minting (₹)",
        "Delivery (₹)", "Other compulsory charges (₹)", "PIN serviceable",
        "In stock", "Product URL", "Final payable (₹)"
    ])

st.subheader("Record a seller's delivered-price quote")
with st.form("quote_form", clear_on_submit=True):
    a,b,c = st.columns(3)
    with a:
        metal = st.selectbox("Metal", ["Gold 24K", "Silver 999"])
        product = st.selectbox("Product type", ["Coin", "Bar"])
        purity = st.selectbox("Purity", ["999.9+", "999.0", "Other / not stated"])
    with b:
        weight = st.number_input("Weight (grams)", min_value=1.0 if metal == "Gold 24K" else 10.0, max_value=100.0 if metal == "Gold 24K" else 1000.0, value=1.0 if metal == "Gold 24K" else 10.0, step=1.0)
        seller = st.text_input("Seller / website")
        pin_serviceable = st.selectbox("Delivery to PIN 110047", ["Confirmed", "Not confirmed", "Not serviceable"])
    with c:
        product_price = st.number_input("Product price (₹)", min_value=0.0, step=100.0)
        gst = st.number_input("GST amount (₹)", min_value=0.0, step=10.0, help="Enter the GST amount shown by the seller. Do not assume it is included unless the seller confirms.")
        making = st.number_input("Making / minting charges (₹)", min_value=0.0, step=10.0)
        delivery = st.number_input("Delivery charges (₹)", min_value=0.0, step=10.0)
    other = st.number_input("Other compulsory charges (₹)", min_value=0.0, step=10.0)
    in_stock = st.selectbox("Availability", ["In stock", "Out of stock", "Not confirmed"])
    product_url = st.text_input("Direct product page / checkout URL")
    submitted = st.form_submit_button("Add quote")
    if submitted:
        if not seller.strip() or product_price <= 0 or not product_url.strip():
            st.error("Enter the seller name, a positive product price and the product page URL.")
        else:
            final_price = product_price + gst + making + delivery + other
            row = {
                "Checked on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Metal": metal, "Product": product, "Weight (g)": weight, "Purity": purity,
                "Seller": seller.strip(), "Product price (₹)": product_price,
                "GST (₹)": gst, "Making/minting (₹)": making, "Delivery (₹)": delivery,
                "Other compulsory charges (₹)": other, "PIN serviceable": pin_serviceable,
                "In stock": in_stock, "Product URL": product_url.strip(),
                "Final payable (₹)": final_price
            }
            st.session_state.quotes = pd.concat([st.session_state.quotes, pd.DataFrame([row])], ignore_index=True)
            st.success(f"Quote added. Final payable amount: ₹{final_price:,.2f}")

quotes = st.session_state.quotes
st.divider()
st.subheader("Seller comparison")
if quotes.empty:
    st.write("No seller quotes recorded yet.")
else:
    metals = ["All"] + sorted(quotes["Metal"].dropna().unique().tolist())
    chosen_metal = st.selectbox("Filter by metal", metals)
    view = quotes if chosen_metal == "All" else quotes[quotes["Metal"] == chosen_metal]
    st.dataframe(view.sort_values("Final payable (₹)"), use_container_width=True, hide_index=True)
    eligible = view[(view["PIN serviceable"] == "Confirmed") & (view["In stock"] == "In stock")]
    if not eligible.empty:
        # Rank only within identical metal, product type and weight.
        keys = ["Metal", "Product", "Weight (g)"]
        winners = eligible.sort_values("Final payable (₹)").groupby(keys, as_index=False).first()
        st.markdown("**Lowest recorded payable quote for each comparable product**")
        st.dataframe(winners[keys + ["Seller", "Final payable (₹)", "Checked on", "Product URL"]], use_container_width=True, hide_index=True)
    else:
        st.warning("No quote is currently confirmed as both in stock and deliverable to PIN 110047.")
    csv = quotes.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download quote history (CSV)", csv, file_name="gold_silver_quote_history.csv", mime="text/csv")

st.caption("Quote history currently stays in this app session. Download the CSV to retain a copy; free hosting may restart and clear temporary session data.")
st.warning("A seller is not ranked as cheapest unless stock and delivery to PIN 110047 are confirmed and the full compulsory cost is entered. Check the seller's final checkout page before payment.")

st.divider()
st.subheader("Automation status")
st.write("Daily 9:00 AM IST GitHub schedule is configured as a workflow test. Automated multi-seller price collection, 90-day retained history and exceptional-cheap alerts are the next development phase.")
st.write("WhatsApp: manual sharing only, using your existing WhatsApp Business app. No paid WhatsApp API is configured.")
st.caption("Do not upload confidential departmental records, personal data, statements or protected investigation material to this public repository or dashboard.")
