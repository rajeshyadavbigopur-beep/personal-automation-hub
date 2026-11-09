import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Personal Automation Hub", page_icon="⚙️", layout="wide")
st.title("⚙️ Personal Automation Hub")
st.caption("Central dashboard for your independent tools")

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
st.write("Delivery PIN code: **110047** | Target check: **daily**")
st.info("Phase 1 is active: record seller quotes and compare final payable cost. Phase 2 will add automated price feeds only from sources that permit automated access and provide reliable product-level prices.")

st.info("Phase 1 is active: record seller quotes and compare final payable cost. The live benchmark below is an indicative raw spot rate, not a delivered retail offer.")

# Live international spot benchmark converted to INR per gram.
st.subheader("Live spot benchmark (not a retail checkout price)")
st.caption("Gold-API.com live spot data. Converted from INR per troy ounce to INR per gram (31.1035 g). GST, seller premium, product premium and delivery are not included.")
try:
    spot_cols = st.columns(2)
    spot_records = []
    for symbol, label in [("XAU", "24K gold spot"), ("XAG", "Silver spot")]:
        response = requests.get(f"https://api.gold-api.com/price/{symbol}/INR", timeout=12)
        response.raise_for_status()
        item = response.json()
        if item.get("currency") != "INR" or not isinstance(item.get("price"), (int, float)):
            raise ValueError(f"Unexpected price response for {symbol}")
        per_gram = float(item["price"]) / 31.1035
        spot_records.append((symbol, label, per_gram, item.get("updatedAt", "Timestamp unavailable")))
    for col, (symbol, label, per_gram, updated) in zip(spot_cols, spot_records):
        with col:
            st.metric(label, f"₹{per_gram:,.2f}/g")
            st.caption(f"API update (UTC): {updated}")
except Exception as exc:
    st.warning(f"Live spot benchmark is temporarily unavailable: {exc}")

history_url = "https://raw.githubusercontent.com/rajeshyadavbigopur-beep/personal-automation-hub/main/data/spot_history.csv"
try:
    history = pd.read_csv(history_url)
    if not history.empty:
        history["date_ist"] = pd.to_datetime(history["date_ist"], errors="coerce")
        history = history.dropna(subset=["date_ist"])
        history = history[history["date_ist"] >= (pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None) - pd.Timedelta(days=90))]
        if not history.empty:
            st.markdown("**Collected daily spot benchmark – last 90 days**")
            chart = history.pivot_table(index="date_ist", columns="metal", values="spot_per_gram_inr", aggfunc="last")
            st.line_chart(chart)
            st.caption("Historical benchmark only. It does not represent past retail coin/bar checkout prices.")
        else:
            st.caption("The 90-day history file has no observations yet. It will populate after the first successful scheduled collection.")
except Exception:
    st.caption("Daily benchmark history will appear after the first successful GitHub Actions collection.")


with st.expander("Reference source and access status", expanded=True):
    st.markdown("**MMTC-PAMP official shop:** [View coins and bars](https://www.mmtcpamp.com/shop)")
    st.markdown("Its published terms state that domestic listed prices include applicable CGST/SGST/IGST and domestic shipping is free. Delivery is limited to selected cities and must be checked at checkout using the PIN code.")
    st.markdown("**Important:** MMTC-PAMP's terms prohibit automated data extraction, scraping, data mining and bots. Therefore this tracker will not scrape that website. Its shop can be checked manually as a reference; automated feeds will be limited to other sources whose terms and access method permit it.")
    st.link_button("Read MMTC-PAMP terms", "https://www.mmtcpamp.com/terms-and-condition")

if "quotes" not in st.session_state:
    st.session_state.quotes = pd.DataFrame(columns=[
        "Checked on", "Metal", "Product", "Weight (g)", "Purity", "Seller",
        "Product price (₹)", "GST treatment", "GST amount added (₹)",
        "Making/minting (₹)", "Delivery (₹)", "Other compulsory charges (₹)",
        "PIN serviceable", "In stock", "Product URL", "Final payable (₹)"
    ])

st.subheader("Record a seller's delivered-price quote")
with st.form("quote_form", clear_on_submit=True):
    a,b,c = st.columns(3)
    with a:
        metal = st.selectbox("Metal", ["Gold 24K", "Silver 999"])
        product = st.selectbox("Product type", ["Coin", "Bar"])
        purity = st.selectbox("Purity", ["999.9+", "999.0", "Other / not stated"])
        weight = st.number_input("Weight (grams)", min_value=1.0 if metal == "Gold 24K" else 10.0, max_value=100.0 if metal == "Gold 24K" else 1000.0, value=1.0 if metal == "Gold 24K" else 10.0, step=1.0)
    with b:
        seller = st.text_input("Seller / website")
        pin_serviceable = st.selectbox("Delivery to PIN 110047", ["Confirmed", "Not confirmed", "Not serviceable"])
        in_stock = st.selectbox("Availability", ["In stock", "Out of stock", "Not confirmed"])
        product_url = st.text_input("Direct product page / checkout URL")
    with c:
        product_price = st.number_input("Product price shown (₹)", min_value=0.0, step=100.0)
        gst_treatment = st.selectbox("Is GST already included in product price?", ["Yes - included", "No - add GST below", "Not clear"])
        gst = st.number_input("GST to add (₹)", min_value=0.0, step=10.0, help="Enter GST only if it is extra over the displayed product price. If GST is included, enter zero.")
        making = st.number_input("Making / minting charges extra (₹)", min_value=0.0, step=10.0)
        delivery = st.number_input("Delivery charges (₹)", min_value=0.0, step=10.0)
    other = st.number_input("Other compulsory charges (₹)", min_value=0.0, step=10.0)
    submitted = st.form_submit_button("Add quote")
    if submitted:
        if not seller.strip() or product_price <= 0 or not product_url.strip():
            st.error("Enter the seller name, a positive product price and the product page URL.")
        elif gst_treatment == "Not clear":
            st.error("Confirm whether GST is included before adding the quote. Do not guess.")
        elif gst_treatment == "Yes - included" and gst > 0:
            st.error("GST is already included. Set 'GST to add' as zero to avoid double counting.")
        else:
            final_price = product_price + gst + making + delivery + other
            row = {
                "Checked on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Metal": metal, "Product": product, "Weight (g)": weight, "Purity": purity,
                "Seller": seller.strip(), "Product price (₹)": product_price,
                "GST treatment": gst_treatment, "GST amount added (₹)": gst,
                "Making/minting (₹)": making, "Delivery (₹)": delivery,
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
        keys = ["Metal", "Product", "Weight (g)", "Purity"]
        winners = eligible.sort_values("Final payable (₹)").groupby(keys, as_index=False).first()
        st.markdown("**Lowest recorded payable quote for each comparable product**")
        st.dataframe(winners[keys + ["Seller", "Final payable (₹)", "Checked on", "Product URL"]], use_container_width=True, hide_index=True)
    else:
        st.warning("No quote is confirmed as both in stock and deliverable to PIN 110047.")
    st.download_button("Download quote history (CSV)", quotes.to_csv(index=False).encode("utf-8-sig"), file_name="gold_silver_quote_history.csv", mime="text/csv")

st.caption("Quote history currently stays in this app session. Download the CSV to retain a copy; persistent 90-day history is part of the next development phase.")
st.warning("Only compare the same metal, product type, weight and purity. A seller is not ranked as cheapest unless stock and delivery to PIN 110047 are confirmed and all compulsory charges are included.")

st.divider()
st.subheader("Your selected tracker settings")
st.write("Products: 24K gold coins/bars (1g, 5g, 10g, 20g, 50g, 100g) and 999 silver coins/bars (10g, 50g, 100g, 500g, 1kg).")
st.write("Seller coverage: all sellers, subject to genuineness checks. Purchase method: online delivery only.")
st.write("Alerts requested: daily report plus exceptionally low-price alerts. Historical analysis: last 90 days, including lowest seller and purchase-timing analysis.")
st.write("WhatsApp sharing: manual through your existing WhatsApp Business app; no paid WhatsApp API.")
st.caption("Daily GitHub workflow is currently a schedule test, not yet a verified live price-collection job.")
st.caption("Do not upload confidential departmental records, personal data, statements or protected investigation material to this public repository or dashboard.")
