> **Fork Notice:** This is a fork of [TwistScan](https://github.com/marcopedrinazzi/twistscan) by [marcopedrinazzi](https://github.com/marcopedrinazzi), with additional Docker support and a custom Flask dashboard with intelligence visualizations.

---

# TwistScan

TwistScan is a Python tool that merges the domain‑permutation power of [**dnstwist**](https://github.com/elceef/dnstwist) with the dynamic scanning capabilities of [**urlscan.io**](https://urlscan.io/), to streamline the detection of phishing, typosquatting, and brand‑impersonation attempts.

## 💡 Why TwistScan?

During my threat‑hunting sessions, I repeatedly ran dnstwist → urlscan.io in two separate steps. TwistScan automates this pipeline end‑to‑end, saving time and reducing manual overhead—so you can spot malicious domains faster and more reliably.

## 🔍 How It Works

1. **Input & Fuzzing**  
   You provide an original domain name (e.g., `example.com`), and TwistScan uses dnstwist to generate variants using **all** of its fuzzers.

2. **API Submission & Data Collection**  
   Each variant is automatically submitted to the urlscan.io API. TwistScan collects:
   - **IP addresses**, **ASN details**, and **server information**  
   - **Full‑page screenshots** (via urlscan.io) and **perceptual hashes (pHash)**  
   - **Raw HTML source**, including hidden elements or obfuscated scripts  
   - **Resource inventory** (images, scripts, stylesheets, fonts)  
   - **Outbound connections** and third‑party hosts  
   - **TLS certificate details** and validity periods  
   - **Similarity analysis** comparing pHash values against the original domain

3. **Result Export & Review**  
   - Results are saved as **CSV files** (`output_dnstwist.csv` & `output_urlscan.csv`) for further automation or manual inspection.  
   - In **Streamlit mode**, all data—screenshots, metadata, similarity scores—are displayed interactively in a comprehensive dashboard.

## 🚀 Key advantages

Combining dnstwist's permutation engine with urlscan.io's dynamic scanning adds significant value to a malicious domain-hunting workflow. Some key advantages include:
- **Visual confirmation**: Full‑page screenshots are captured for each candidate domain, enabling quick visual assessment of whether a page imitates legitimate branding.
- **HTML capture**: The exact HTML source served is retained, including hidden elements or obfuscated scripts that may indicate the presence of a phishing kit.
- **Resource inventory**: All page assets - such as images, scripts, stylesheets, and fonts - are listed, aiding the identification of phishing‑related components.
- **DNS & certificate details**: Information is provided on the domain's resolved IP, ASN, and TLS certificate details, facilitating detection of suspicious or recently registered infrastructure.
- **Outbound connections**: Third‑party hosts contacted by the page (e.g., analytics platforms, CDNs) are enumerated, which can reveal communication with known malicious services.
- **Behaviour & Content Analysis**: The behavior of the scanned page, together with its content are analysed highlighting potential suspicious behaviours or elements.
- **Indicator Creation**: Indicators (IPs, Domains, Hashes) for the scanned domain are created, allowing further threat hunting operations.
- **Similarity check**: urlscan.io provides the structurally similar hits on different domains, IPs and ASNs, so websites which have a similar structure but are hosted on different infrastructure, such as phishing kits can be detected. In addition, the number of hits for the same domain, for the same IP but different domain and for the same ASN but different domain are shown.
- **Historical record**: Each scan includes a timestamp, supporting timelines that show when a suspicious page appeared, changed, or went offline.
- **Community contribution**: Each scan enables the generation of threat intelligence.

## 🛠️ Installation & Usage

1. **Clone the repo**  
  ```bash
    git clone https://github.com/yourusername/TwistScan.git
    cd TwistScan
  ```
2. **Install dependencies**
  ```bash
    pip install -r requirements.txt
  ```
3. **Configure**
  Create an .env file with your `URLSCAN_API=<value>` (https://urlscan.io/about-api/). Edit `dictionary-dnstwist.dict`, `tld-list.dict` as you prefer, this will determine part of the results you will get with dnstwist.

4. **Run (CLI version)**
  ```bash
    python twistscan.py --domain example.com
  ```
**CLI Options**

| Option                                           | Description                                          | Default                  |
|--------------------------------------------------|------------------------------------------------------|--------------------------|
| `-h`, `--help`                                   | Show this help message and exit                      | –                        |
| `--domain <DOMAIN>`                              | Original domain to analyze                           | Mandatory Argument                |
| `--output-dnstwist <OUTPUT_DNSTWIST>`            | Output file for dnstwist results                     | `output_dnstwist.csv`    |
| `--output-urlscan <OUTPUT_URLSCAN>`              | Output file for urlscan.io results                   | `output_urlscan.csv`     |
| `--screenshot-folder <SCREENSHOT_FOLDER>`        | Folder to save screenshots                           | `screenshots/`           |


5. **Run (Streamlit version)**
  ```bash
    streamlit run twistscan_streamlit.py
  ```
