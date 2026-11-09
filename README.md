# Personal Automation Hub

A free central dashboard for existing GST and NSE applications, plus a gold/silver price tracker.

## Applications
- GST Intelligence Hub: https://gst-intelligence-app-eu6u8kvtzmf2vxdnnmnv2a8.streamlit.app/
- NSE Swing Screener: https://nse-swing-screener-k6yhrtpbsuofyubzzafrce.streamlit.app/

## Gold and silver tracker
- Delivery PIN: 110047.
- Product comparison: 24K gold and 999 silver coins/bars.
- Quote entry: product price, GST treatment, minting, delivery, compulsory charges, stock and PIN serviceability.
- Lowest-price ranking is restricted to matching metal, product type, weight and purity, and requires confirmed stock and delivery.
- Live benchmark: Gold-API.com spot rate in INR, converted from troy ounce to gram.
- Daily benchmark history: GitHub Actions saves one daily observation per metal and retains up to 120 days in `data/spot_history.csv`; the app displays the latest 90 days.

## Important distinction
The API spot benchmark is NOT a physical coin/bar offer. It does not include dealer premium, product premium, GST on the retail product, minting/making charges or delivery. The final purchase comparison must use a seller's confirmed checkout amount for PIN 110047. Do not assume a spot benchmark is the cheapest purchase price.

The live API is provided as-is and its accuracy is not guaranteed. See https://gold-api.com/docs, https://gold-api.com/faqs and https://gold-api.com/terms.

The tracker does not scrape seller websites whose terms prohibit automated access. For example, MMTC-PAMP and All India Bullion publish restrictions on unauthorised automated extraction. They can be consulted manually, subject to their terms.

## Schedule
GitHub Actions workflow `.github/workflows/daily.yml` runs at 03:30 UTC (09:00 IST) and can also be started manually from the Actions tab. Scheduled runs can be delayed by GitHub; they are not guaranteed to start at the exact minute.

## Deploy
Deploy `app.py` on Streamlit Community Cloud from branch `main`.

## Privacy
This is a public repository. Do not upload confidential departmental records, personal data, statements, passwords, API keys or protected investigation material.
