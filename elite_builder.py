import os
import re
import json
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "DREAMSWEBSITE")
IMG_DIR = os.path.join(BASE_DIR, "images")
CAB_DIR = os.path.join(IMG_DIR, "cabinets")
TOP_DIR = os.path.join(IMG_DIR, "countertops")
VAN_DIR = os.path.join(IMG_DIR, "vanities")

PAGES = {
    "tribeca": "https://ervacabinets.com/cabinets/tribeca-cabinets/",
    "jk": "https://ervacabinets.com/cabinets/jk-cabinets/",
    "vanities": "https://ervacabinets.com/vanities/",
    "quartz": "https://www.ervastone.com/quartz-countertops/",
}

PHONE = "(571) 668-0358"
EMAIL = "dreamscabinetcountertop@gmail.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(CAB_DIR, exist_ok=True)
os.makedirs(TOP_DIR, exist_ok=True)
os.makedirs(VAN_DIR, exist_ok=True)

def clean_name(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def save_image(url: str, out_dir: str, filename: str) -> str:
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    out_path = os.path.join(out_dir, filename + ext)

    if os.path.exists(out_path):
        return out_path

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
        return out_path
    except Exception:
        return ""

def all_images_with_context(url: str):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        full = urljoin(url, src)
        text_bits = []

        for attr in ["alt", "title"]:
            v = img.get(attr)
            if v:
                text_bits.append(v)

        parent = img.parent
        for _ in range(3):
            if parent:
                txt = parent.get_text(" ", strip=True)
                if txt:
                    text_bits.append(txt)
                parent = parent.parent

        context = " ".join(text_bits).strip()
        items.append({"url": full, "context": context})

    return items

def pick_best_image(candidates, keywords):
    scored = []
    for item in candidates:
        ctx = item["context"].lower()
        score = 0
        for kw in keywords:
            if kw.lower() in ctx:
                score += 3
        # Prefer medium/large real page images, avoid icons/logos
        bad_words = ["logo", "icon", "cart", "dealer", "catalog", "login"]
        if any(b in ctx for b in bad_words):
            score -= 10
        scored.append((score, item["url"], item["context"]))
    scored.sort(reverse=True, key=lambda x: x[0])
    for score, url, ctx in scored:
        if score > 0:
            return url
    return scored[0][1] if scored else ""

# ---------- CABINETS ----------
jk_imgs = all_images_with_context(PAGES["jk"])
tribeca_imgs = all_images_with_context(PAGES["tribeca"])

cabinet_targets = [
    {"title": "White Color", "keywords": ["s8 white", "white", "door style"]},
    {"title": "Dove Color", "keywords": ["e1 dove", "dove", "door style"]},
    {"title": "Gray Color", "keywords": ["s5 castle grey", "grey", "gray", "door style"]},
    {"title": "Navy Blue", "keywords": ["soho", "hudson", "blue", "door style"]},
    {"title": "Brown Color", "keywords": ["s1 java coffee", "java coffee", "brown"]},
    {"title": "Espresso Color", "keywords": ["k8 espresso", "espresso"]},
]

cabinet_cards = []
for target in cabinet_targets:
    source_pool = jk_imgs + tribeca_imgs
    img_url = pick_best_image(source_pool, target["keywords"])
    if not img_url:
        continue
    local = save_image(img_url, CAB_DIR, clean_name(target["title"]))
    if local:
        cabinet_cards.append({
            "title": target["title"],
            "desc": "Many additional samples and door styles can be shown during consultation.",
            "img": os.path.relpath(local, BASE_DIR).replace("\\", "/")
        })

# ---------- COUNTERTOPS ----------
quartz_imgs = all_images_with_context(PAGES["quartz"])

quartz_targets = [
    "Calacatta Laza",
    "Carrara Marmi",
    "Bianco Calacatta",
    "ET Serena",
    "Pure White",
    "Sparkling White",
    "Statuary Glory",
]

countertop_cards = []
for name in quartz_targets:
    img_url = pick_best_image(quartz_imgs, [name])
    if not img_url:
        continue
    local = save_image(img_url, TOP_DIR, clean_name(name))
    if local:
        countertop_cards.append({
            "title": name,
            "desc": "Real quartz inventory style. Exact slab selection can be finalized during consultation.",
            "img": os.path.relpath(local, BASE_DIR).replace("\\", "/")
        })

# ---------- VANITIES ----------
vanity_imgs = all_images_with_context(PAGES["vanities"])

vanity_targets = [
    "18 inch White Single Sink Vanity",
    "18 inch Gray Bathroom Vanity",
    "24 inch Navy Blue Single Sink Vanity",
    "32 inch High Gloss Cappuccino Single Sink Floating Vanity",
    "48 inch Gray Single Sink Vanity",
    "60 inch Green Double Sink Vanity",
    "72 inch Navy Blue Double Sink Vanity",
]

vanity_cards = []
for name in vanity_targets:
    img_url = pick_best_image(vanity_imgs, [name])
    if not img_url:
        continue
    local = save_image(img_url, VAN_DIR, clean_name(name))
    if local:
        vanity_cards.append({
            "title": name,
            "desc": "Real vanity product style. Exact size and finish can be confirmed during consultation.",
            "img": os.path.relpath(local, BASE_DIR).replace("\\", "/")
        })

styles_css = r'''
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --navy:#081c3a;
  --navy2:#13345e;
  --gold:#d4af37;
  --gold2:#c8991c;
  --light:#f6f8fc;
  --text:#17202c;
  --muted:#5f6b7b;
  --white:#ffffff;
  --line:#e5eaf1;
  --shadow:0 14px 36px rgba(8,28,58,.10);
  --shadow2:0 22px 48px rgba(8,28,58,.14);
}
html{scroll-behavior:smooth}
body{font-family:Arial,Helvetica,sans-serif;color:var(--text);background:#fff;line-height:1.6}
a{text-decoration:none;color:inherit}
img{max-width:100%;display:block}
header{position:sticky;top:0;z-index:1000;background:rgba(8,28,58,.97);backdrop-filter:blur(8px);box-shadow:0 4px 16px rgba(0,0,0,.14)}
.topbar{max-width:1260px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;padding:16px 24px}
.brand-copy strong{display:block;font-size:28px;letter-spacing:.4px;color:#fff}
.brand-copy span{display:block;font-size:12px;letter-spacing:1.4px;color:#dfe8f8}
nav{display:flex;gap:16px;flex-wrap:wrap}
nav a{color:#fff;font-size:14px;font-weight:bold;opacity:.96;position:relative}
nav a:hover{opacity:.8}
nav a:after{content:"";position:absolute;left:0;bottom:-6px;width:0;height:2px;background:var(--gold);transition:.25s ease}
nav a:hover:after{width:100%}
.hero{min-height:86vh;background:linear-gradient(rgba(8,28,58,.60),rgba(8,28,58,.46)),url("https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1800&q=80");background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;text-align:center;padding:72px 20px}
.hero-box{max-width:980px;width:100%;padding:52px 36px;border-radius:24px;background:rgba(255,255,255,.10);backdrop-filter:blur(7px);color:#fff;box-shadow:var(--shadow2)}
.hero h1{font-size:60px;line-height:1.06;margin-bottom:16px}
.hero p{font-size:19px;max-width:820px;margin:0 auto 30px auto;color:#edf3ff}
.btn-row{display:flex;justify-content:center;gap:14px;flex-wrap:wrap}
.btn,.btn2,.btn3{display:inline-block;padding:14px 24px;border-radius:10px;font-weight:bold;font-size:15px;transition:.2s ease;border:none;cursor:pointer}
.btn{background:linear-gradient(180deg,var(--gold),var(--gold2));color:var(--navy)}
.btn2{background:#fff;color:var(--navy)}
.btn3{border:2px solid rgba(255,255,255,.85);color:#fff}
.btn:hover,.btn2:hover,.btn3:hover{transform:translateY(-2px)}
.page-hero{background:linear-gradient(90deg,var(--navy),var(--navy2));color:#fff;text-align:center;padding:76px 20px}
.page-hero h1{font-size:44px;margin-bottom:10px}
.page-hero p{max-width:900px;margin:0 auto;font-size:17px;color:#dbe6f8}
.section{padding:86px 22px}
.section.alt{background:var(--light)}
.container{max-width:1260px;margin:0 auto}
h2{text-align:center;color:var(--navy);font-size:40px;margin-bottom:12px}
.lead{text-align:center;max-width:930px;margin:0 auto 32px auto;color:var(--muted);font-size:17px}
.pills{display:flex;justify-content:center;flex-wrap:wrap;gap:12px;margin-top:20px}
.pill{padding:12px 18px;border-radius:999px;background:#fff;border:1px solid var(--line);box-shadow:0 8px 18px rgba(0,0,0,.04);color:var(--navy);font-weight:bold;font-size:14px}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px;margin-top:32px}
.card,.product-card,.contact-box,.box,.feature-box{background:#fff;border-radius:18px;overflow:hidden;box-shadow:var(--shadow)}
.card-media{height:260px;background:#eef2f8}
.card-media img{width:100%;height:100%;object-fit:cover}
.card-body{padding:22px}
.card h3,.product-card h3,.contact-box h3{color:var(--navy);font-size:25px;margin-bottom:10px}
.card p,.product-card p,.contact-box p,.contact-box a{color:var(--muted);font-size:15px}
.feature-box{max-width:1060px;margin:0 auto;padding:34px;text-align:center}
.feature-box h3{color:var(--navy);font-size:31px;margin-bottom:10px}
.feature-box p{color:var(--muted);margin-bottom:18px}
.form-wrap{max-width:1040px;margin:0 auto}
.box{padding:30px}
.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.form-group{display:flex;flex-direction:column;gap:8px}
.form-group.full{grid-column:1/-1}
.form-title{color:var(--navy);font-size:24px;margin-top:6px}
label{font-size:14px;font-weight:bold;color:var(--navy)}
input,select,textarea{width:100%;padding:13px 14px;border-radius:10px;border:1px solid #d8dfe9;font-size:15px;font-family:inherit;background:#fff}
textarea{min-height:130px;resize:vertical}
.important-note,.note-box{max-width:1040px;margin:0 auto 22px auto;background:#fff8e6;border:1px solid #ead394;color:#6f5614;border-radius:14px;padding:16px 18px;font-size:15px}
.muted-note{text-align:center;color:var(--muted);font-size:14px;margin-top:14px}
.contact-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:30px}
.contact-box{padding:24px}
.footer{background:#06162f;color:#fff;text-align:center;padding:38px 20px;margin-top:30px}
.footer p{margin:6px 0}
.small{font-size:14px;color:#d5dff0}
.product-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:32px}
.sample-wrap{height:280px;background:#f7f8fb;display:flex;align-items:center;justify-content:center;padding:24px}
.product-photo{width:100%;height:100%;object-fit:cover;border-radius:12px;box-shadow:0 10px 22px rgba(0,0,0,.12)}
.info-note{max-width:980px;margin:10px auto 0 auto;text-align:center;color:var(--muted);font-size:15px}
@media(max-width:980px){.cards,.contact-grid,.form-grid,.product-grid{grid-template-columns:1fr}.hero h1{font-size:40px}.page-hero h1{font-size:36px}}
@media(max-width:720px){.topbar{justify-content:center;text-align:center}nav{justify-content:center}}
'''

script_js = r'''
document.addEventListener("DOMContentLoaded", function () {
  const estimateForm = document.getElementById("estimateForm");
  if (estimateForm) {
    estimateForm.addEventListener("submit", function(e){
      e.preventDefault();
      const v = id => document.getElementById(id)?.value || "";
      const subject = encodeURIComponent("New Estimate Request - " + (v("fullName") || "Website Lead"));
      const body = encodeURIComponent(
`New Estimate Request

Customer Information
Full Name: ${v("fullName")}
Phone: ${v("phone")}
Email: ${v("email")}
City / Location: ${v("city")}
Project Type: ${v("projectType")}
Project Timeline: ${v("timeline")}

Kitchen Measurements
Back Wall Length: ${v("backWall")}
Left Wall Length: ${v("leftWall")}
Right Wall Length: ${v("rightWall")}
Ceiling Height: ${v("ceilingHeight")}
Island Length: ${v("islandLength")}
Island Width: ${v("islandWidth")}

Window Measurements
Is There a Window?: ${v("hasWindow")}
Which Wall Is the Window On?: ${v("windowWall")}
Left Wall to Window: ${v("leftToWindow")}
Right Wall to Window: ${v("rightToWindow")}
Window Width: ${v("windowWidth")}
Window Height: ${v("windowHeight")}
Height From Floor to Window Bottom: ${v("windowSillHeight")}
Height From Floor to Window Top: ${v("windowTopHeight")}

Appliances / Layout
Sink Location: ${v("sinkLocation")}
Range / Stove Location: ${v("rangeLocation")}
Refrigerator Location: ${v("fridgeLocation")}
Microwave / Oven Location: ${v("microwaveLocation")}
Other Important Measurements: ${v("measurementsExtra")}

Design Preferences
Cabinet Color Preference: ${v("cabinetStyle")}
Countertop Preference: ${v("countertopStyle")}

Project Details
${v("details")}

Photo Upload Note
Please attach kitchen photos manually before sending.`
      );
      window.location.href = "mailto:dreamscabinetcountertop@gmail.com?subject=" + subject + "&body=" + body;
    });
  }

  const appointmentForm = document.getElementById("appointmentForm");
  if (appointmentForm) {
    appointmentForm.addEventListener("submit", function(e){
      e.preventDefault();
      const v = id => document.getElementById(id)?.value || "";
      const subject = encodeURIComponent("New Appointment Request - " + (v("apptName") || "Website Lead"));
      const body = encodeURIComponent(
`New Appointment Request

Full Name: ${v("apptName")}
Phone: ${v("apptPhone")}
Email: ${v("apptEmail")}
Product Interest: ${v("apptInterest")}
Preferred Date: ${v("apptDate")}
Preferred Time: ${v("apptTime")}

Notes
${v("apptNotes")}`
      );
      window.location.href = "mailto:dreamscabinetcountertop@gmail.com?subject=" + subject + "&body=" + body;
    });
  }
});
'''

NAV = '''
<header>
  <div class="topbar">
    <div class="brand-copy">
      <strong>DREAMS</strong>
      <span>CABINET &amp; COUNTERTOP</span>
    </div>
    <nav>
      <a href="index.html">Home</a>
      <a href="estimate.html">Estimate</a>
      <a href="cabinets.html">Cabinets</a>
      <a href="countertops.html">Countertops</a>
      <a href="vanities.html">Vanities</a>
      <a href="appointment.html">Appointment</a>
      <a href="contact.html">Contact</a>
    </nav>
  </div>
</header>
'''

FOOTER = f'''
<footer class="footer">
  <p><strong>Dreams Cabinet &amp; Countertop</strong></p>
  <p class="small">Kitchen Cabinets • Quartz Countertops • Bathroom Vanities</p>
  <p class="small">Phone: {PHONE}</p>
  <p class="small">Email: {EMAIL}</p>
  <p class="small">Serving Virginia, Maryland, Washington DC, and nearby West Virginia areas</p>
</footer>
'''

def cards_html(cards):
    out = []
    for c in cards:
        out.append(f'''
        <div class="product-card">
          <div class="sample-wrap"><img class="product-photo" src="{c["img"]}" alt="{c["title"]}"></div>
          <div class="card-body">
            <h3>{c["title"]}</h3>
            <p>{c["desc"]}</p>
          </div>
        </div>
        ''')
    return "\n".join(out)

index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="hero">
  <div class="hero-box">
    <h1>Premium Kitchen Cabinets, Quartz Countertops &amp; Bathroom Vanities</h1>
    <p>Free Kitchen Design • Free Estimate • Appointment Only • Serving DMV Area</p>
    <div class="btn-row">
      <a class="btn" href="estimate.html">Get Free Estimate</a>
      <a class="btn2" href="appointment.html">Book Appointment</a>
      <a class="btn3" href="cabinets.html">View Product Styles</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2>Built To Bring You Leads</h2>
    <p class="lead">Clean product pages, real product photos, and a simple estimate flow so you can close the exact product selection later with samples.</p>
    <div class="pills">
      <div class="pill">Door Styles</div>
      <div class="pill">Real Quartz Inventory</div>
      <div class="pill">Vanity Products</div>
      <div class="pill">Free Estimate</div>
      <div class="pill">Appointment Only</div>
    </div>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <div class="feature-box">
      <h3>Start With a Free Estimate</h3>
      <p>The customer journey starts the right way: estimate first, then real samples and final selections with you.</p>
      <div class="btn-row">
        <a class="btn" href="estimate.html">Go to Estimate Page</a>
        <a class="btn2" href="contact.html">Contact Us</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2>Explore Product Categories</h2>
    <p class="lead">These category pages now use Erva-sourced product imagery instead of unrelated stock visuals.</p>

    <div class="cards">
      <div class="card">
        <div class="card-media"><img src="{cabinet_cards[0]["img"] if cabinet_cards else ""}" alt="Cabinets"></div>
        <div class="card-body">
          <h3>Cabinet Colors &amp; Styles</h3>
          <p>Dove, white, gray, navy blue, brown, and espresso style categories using real cabinet imagery.</p>
          <div class="btn-row" style="justify-content:flex-start;margin-top:16px">
            <a class="btn" href="cabinets.html">View Cabinets</a>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-media"><img src="{countertop_cards[0]["img"] if countertop_cards else ""}" alt="Countertops"></div>
        <div class="card-body">
          <h3>Quartz Countertop Options</h3>
          <p>Real quartz inventory with real product names and slab visuals.</p>
          <div class="btn-row" style="justify-content:flex-start;margin-top:16px">
            <a class="btn" href="countertops.html">View Countertops</a>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-media"><img src="{vanity_cards[0]["img"] if vanity_cards else ""}" alt="Vanities"></div>
        <div class="card-body">
          <h3>Vanity Styles</h3>
          <p>Real vanity product imagery with names customers can actually review with you later.</p>
          <div class="btn-row" style="justify-content:flex-start;margin-top:16px">
            <a class="btn" href="vanities.html">View Vanities</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

{FOOTER}
<script src="script.js"></script>
</body>
</html>'''

estimate_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Free Estimate | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Get Your Free Estimate</h1>
  <p>Send project details, kitchen photos, rough measurements, and especially window measurements if there is a window in the kitchen.</p>
</section>

<section class="section alt">
  <div class="container">
    <div class="important-note">
      <strong>Important for kitchen design:</strong> If there is a window in the kitchen, include the distance from the left wall to the window, the distance from the right wall to the window, plus the window width and height.
    </div>

    <div class="form-wrap">
      <div class="box">
        <h2>Estimate Request Form</h2>
        <p class="lead">This page is separate on purpose so customers land directly on the form instead of searching for it on the homepage.</p>

        <form id="estimateForm">
          <div class="form-grid">
            <div class="form-group full"><div class="form-title">Customer Information</div></div>
            <div class="form-group"><label for="fullName">Full Name</label><input id="fullName" type="text" required></div>
            <div class="form-group"><label for="phone">Phone Number</label><input id="phone" type="tel" required></div>
            <div class="form-group"><label for="email">Email Address</label><input id="email" type="email" required></div>
            <div class="form-group"><label for="city">City / Location</label><input id="city" type="text" placeholder="Ex: Winchester, VA"></div>
            <div class="form-group"><label for="projectType">Project Type</label><select id="projectType"><option>Kitchen Cabinets</option><option>Quartz Countertops</option><option>Bathroom Vanity</option><option>Full Kitchen Remodel</option><option>Investment Property</option><option>Other</option></select></div>
            <div class="form-group"><label for="timeline">Project Timeline</label><select id="timeline"><option>As Soon As Possible</option><option>Within 1 Month</option><option>1-3 Months</option><option>3+ Months</option><option>Just Comparing Options</option></select></div>

            <div class="form-group full"><div class="form-title">Kitchen Measurements</div></div>
            <div class="form-group"><label for="backWall">Back Wall Length</label><input id="backWall" type="text" placeholder="Ex: 120 in"></div>
            <div class="form-group"><label for="leftWall">Left Wall Length</label><input id="leftWall" type="text" placeholder="Ex: 96 in"></div>
            <div class="form-group"><label for="rightWall">Right Wall Length</label><input id="rightWall" type="text" placeholder="Ex: 108 in"></div>
            <div class="form-group"><label for="ceilingHeight">Ceiling Height</label><input id="ceilingHeight" type="text" placeholder="Ex: 96 in"></div>
            <div class="form-group"><label for="islandLength">Island Length</label><input id="islandLength" type="text" placeholder="Ex: 84 in"></div>
            <div class="form-group"><label for="islandWidth">Island Width</label><input id="islandWidth" type="text" placeholder="Ex: 36 in"></div>

            <div class="form-group full"><div class="form-title">Window Measurements</div></div>
            <div class="form-group"><label for="hasWindow">Is There a Window in the Kitchen?</label><select id="hasWindow"><option>Yes</option><option>No</option></select></div>
            <div class="form-group"><label for="windowWall">Which Wall Is the Window On?</label><select id="windowWall"><option>Back Wall</option><option>Left Wall</option><option>Right Wall</option><option>Not Sure</option></select></div>
            <div class="form-group"><label for="leftToWindow">Left Wall to Window</label><input id="leftToWindow" type="text"></div>
            <div class="form-group"><label for="rightToWindow">Right Wall to Window</label><input id="rightToWindow" type="text"></div>
            <div class="form-group"><label for="windowWidth">Window Width</label><input id="windowWidth" type="text" placeholder="Ex: 36 in"></div>
            <div class="form-group"><label for="windowHeight">Window Height</label><input id="windowHeight" type="text" placeholder="Ex: 48 in"></div>
            <div class="form-group"><label for="windowSillHeight">Height From Floor to Window Bottom</label><input id="windowSillHeight" type="text"></div>
            <div class="form-group"><label for="windowTopHeight">Height From Floor to Window Top</label><input id="windowTopHeight" type="text"></div>

            <div class="form-group full"><div class="form-title">Appliances / Layout</div></div>
            <div class="form-group"><label for="sinkLocation">Sink Location</label><input id="sinkLocation" type="text"></div>
            <div class="form-group"><label for="rangeLocation">Range / Stove Location</label><input id="rangeLocation" type="text"></div>
            <div class="form-group"><label for="fridgeLocation">Refrigerator Location</label><input id="fridgeLocation" type="text"></div>
            <div class="form-group"><label for="microwaveLocation">Microwave / Oven Location</label><input id="microwaveLocation" type="text"></div>
            <div class="form-group full"><label for="measurementsExtra">Other Important Measurements</label><textarea id="measurementsExtra"></textarea></div>

            <div class="form-group full"><div class="form-title">Design Preferences</div></div>
            <div class="form-group"><label for="cabinetStyle">Cabinet Color Preference</label><input id="cabinetStyle" type="text" placeholder="Ex: dove / white / navy blue"></div>
            <div class="form-group"><label for="countertopStyle">Countertop Preference</label><input id="countertopStyle" type="text" placeholder="Ex: Calacatta Laza / Pure White"></div>
            <div class="form-group full"><label for="details">Project Details</label><textarea id="details"></textarea></div>
            <div class="form-group full"><label for="photos">Upload Photos</label><input id="photos" type="file" multiple></div>
            <div class="form-group full"><button class="btn" type="submit">Submit Estimate Request</button></div>
          </div>
        </form>

        <div class="muted-note">Note: photo files usually need to be attached manually after the email draft opens.</div>
      </div>
    </div>
  </div>
</section>

{FOOTER}
<script src="script.js"></script>
</body>
</html>'''

appointment_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Appointment | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Showroom Visit by Appointment Only</h1>
  <p>We do not accept walk-ins. Customers can request a visit here and wait for confirmation.</p>
</section>

<section class="section alt">
  <div class="container">
    <div class="form-wrap">
      <div class="box">
        <h2>Appointment Request</h2>
        <p class="lead">Keep showroom scheduling separate from the estimate flow for a cleaner and more professional customer journey.</p>

        <form id="appointmentForm">
          <div class="form-grid">
            <div class="form-group"><label for="apptName">Full Name</label><input id="apptName" type="text" required></div>
            <div class="form-group"><label for="apptPhone">Phone Number</label><input id="apptPhone" type="tel" required></div>
            <div class="form-group"><label for="apptEmail">Email Address</label><input id="apptEmail" type="email" required></div>
            <div class="form-group"><label for="apptInterest">Product Interest</label><select id="apptInterest"><option>Kitchen Cabinets</option><option>Quartz Countertops</option><option>Bathroom Vanity</option><option>Full Kitchen Project</option><option>General Consultation</option></select></div>
            <div class="form-group"><label for="apptDate">Preferred Date</label><input id="apptDate" type="date"></div>
            <div class="form-group"><label for="apptTime">Preferred Time</label><input id="apptTime" type="time"></div>
            <div class="form-group full"><label for="apptNotes">Notes</label><textarea id="apptNotes"></textarea></div>
            <div class="form-group full"><button class="btn" type="submit">Request Appointment</button></div>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

{FOOTER}
<script src="script.js"></script>
</body>
</html>'''

contact_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Contact | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Contact Us</h1>
  <p>Customers can reach out directly for estimates, appointment requests, cabinet questions, countertop questions, and vanity projects.</p>
</section>

<section class="section alt">
  <div class="container">
    <div class="contact-grid">
      <div class="contact-box">
        <h3>Call or Text</h3>
        <p>{PHONE}</p>
        <p>This is the direct customer number for Dreams Cabinet & Countertop.</p>
      </div>
      <div class="contact-box">
        <h3>Email</h3>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p>This is the direct customer email used throughout the site.</p>
      </div>
      <div class="contact-box">
        <h3>Business Info</h3>
        <p>Dreams Cabinet &amp; Countertop</p>
        <p>DMV Area • Appointment Only</p>
        <p>Kitchen Cabinets • Quartz • Vanities</p>
      </div>
    </div>
  </div>
</section>
{FOOTER}
</body>
</html>'''

cabinets_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cabinet Colors & Styles | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Cabinet Colors &amp; Styles</h1>
  <p>Real cabinet imagery sourced from the provided Erva pages, but shown without brand names on your site.</p>
</section>
<section class="section alt">
  <div class="container">
    <h2>Popular Cabinet Options</h2>
    <p class="lead">Exact samples and door styles can be shown later during consultation or by appointment.</p>
    <div class="product-grid">
      {cards_html(cabinet_cards)}
    </div>
    <div class="info-note">Many additional colors and door styles are available. Samples can be shown during consultation or by appointment.</div>
  </div>
</section>
{FOOTER}
</body>
</html>'''

countertops_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Quartz Countertops | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Quartz Countertop Options</h1>
  <p>Real quartz inventory visuals and product names from the provided Erva Stone inventory pages.</p>
</section>
<section class="section">
  <div class="container">
    <div class="note-box">These countertop cards use real inventory-oriented imagery and real product names instead of generic room photos.</div>
    <h2>Popular Quartz Styles</h2>
    <p class="lead">Exact slab selections can be finalized during consultation.</p>
    <div class="product-grid">
      {cards_html(countertop_cards)}
    </div>
    <div class="info-note">Many additional quartz colors are available. Exact slabs can be selected during consultation or by appointment.</div>
  </div>
</section>
{FOOTER}
</body>
</html>'''

vanities_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bathroom Vanities | Dreams Cabinet & Countertop</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{NAV}
<section class="page-hero">
  <h1>Bathroom Vanity Styles</h1>
  <p>Real vanity product imagery and product names from the provided Erva vanity page.</p>
</section>
<section class="section alt">
  <div class="container">
    <h2>Popular Vanity Options</h2>
    <p class="lead">These visuals use real vanity products instead of unrelated bathroom interiors.</p>
    <div class="product-grid">
      {cards_html(vanity_cards)}
    </div>
    <div class="info-note">Many additional sizes and finishes are available. Exact vanity selections can be shown during consultation or by appointment.</div>
  </div>
</section>
{FOOTER}
</body>
</html>'''

# Write files
with open(os.path.join(BASE_DIR, "styles.css"), "w", encoding="utf-8") as f:
    f.write(styles_css)
with open(os.path.join(BASE_DIR, "script.js"), "w", encoding="utf-8") as f:
    f.write(script_js)
with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
with open(os.path.join(BASE_DIR, "estimate.html"), "w", encoding="utf-8") as f:
    f.write(estimate_html)
with open(os.path.join(BASE_DIR, "appointment.html"), "w", encoding="utf-8") as f:
    f.write(appointment_html)
with open(os.path.join(BASE_DIR, "contact.html"), "w", encoding="utf-8") as f:
    f.write(contact_html)
with open(os.path.join(BASE_DIR, "cabinets.html"), "w", encoding="utf-8") as f:
    f.write(cabinets_html)
with open(os.path.join(BASE_DIR, "countertops.html"), "w", encoding="utf-8") as f:
    f.write(countertops_html)
with open(os.path.join(BASE_DIR, "vanities.html"), "w", encoding="utf-8") as f:
    f.write(vanities_html)

summary = {
    "cabinet_cards": cabinet_cards,
    "countertop_cards": countertop_cards,
    "vanity_cards": vanity_cards,
}
with open(os.path.join(BASE_DIR, "images", "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("DONE")
print("Website folder:", BASE_DIR)
print("Cabinets found:", len(cabinet_cards))
print("Countertops found:", len(countertop_cards))
print("Vanities found:", len(vanity_cards))
print("Open this file:")
print(os.path.join(BASE_DIR, "index.html"))