import json, pathlib, html

root = pathlib.Path(__file__).parent
data = json.loads((root/"data/apps.json").read_text())
checked = data["checked"]
apps = data["apps"]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body>
<header>
  <a class="brand" href="{p}index.html">AppPriceDB</a>
  <a href="{p}pricing-index/">Pricing index</a>
  <a href="{p}methodology.html">Method</a>
  <a href="{p}changelog.html">Changelog</a>
  <a href="{p}about.html">About</a>
</header>
<main>
{body}
</main>
<footer>Prices checked {checked}. Some outbound links may be affiliate links, disclosed on the page. © AppPriceDB</footer>
</body>
</html>
"""

def page(path, title, desc, body, p=""):
    out = root/path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE.format(title=html.escape(title), desc=html.escape(desc),
                                   body=body, checked=checked, p=p), encoding="utf-8")
    print("wrote", path)

for slug, a in apps.items():
    p = "../../"
    rows = "\n".join(
        f"<tr><td><strong>{html.escape(pl['name'])}</strong></td><td>{html.escape(pl['price'])}</td><td>{html.escape(pl['includes'])}</td></tr>"
        for pl in a["plans"])
    notes = "\n".join(f"<li>{html.escape(n)}</li>" for n in a["notes"])
    import json as _json
    ld = {"@context":"https://schema.org","@type":"ItemList","name":f"{a['name']} pricing plans",
          "dateModified": checked,
          "url": f"https://liuq88450-del.github.io/apppricedb/apps/{slug}/",
          "itemListElement":[{"@type":"Offer","name":pl["name"],"price":pl["price"],
                              "description":pl["includes"]} for pl in a["plans"]]}
    ld_script = f'<script type="application/ld+json">{_json.dumps(ld, ensure_ascii=False)}</script>'
    body = ld_script + f"""<h1>{html.escape(a['name'])} pricing: what you actually pay</h1>
<p class="lede">{html.escape(a['category'])}. Billed by {html.escape(a['billing_unit'])}.</p>
<div class="verified">Every figure below was read from <a href="{a['source']}" rel="nofollow noopener" target="_blank">the vendor's own pricing page</a> on {checked}. Nothing here is inferred.</div>
<h2>Plans</h2>
<table><thead><tr><th>Plan</th><th>Price</th><th>What is included</th></tr></thead><tbody>
{rows}
</tbody></table>
<h2>What the price tag hides</h2>
<ul>
{notes}
</ul>
<h2>How to read this</h2>
<p>Start from the billing unit, not the headline price. If your store sits above the entry tier, the number that matters is the next tier up, which is why we publish the unit rather than a single "starting at" figure.</p>
<p class="muted">Found an error? Send the vendor page showing the right figure.</p>"""
    page(f"apps/{slug}/index.html",
         f"{a['name']} pricing ({checked}) — plans, limits and overage",
         f"{a['name']} pricing checked {checked}: billed by {a['billing_unit']}, with plan prices and what the price tag hides.",
         body, p)

rows = []
for slug, a in apps.items():
    tiers = " · ".join(pl["price"] for pl in a["plans"])
    rows.append(f"<tr><td><a href=\"../apps/{slug}/\">{html.escape(a['name'])}</a></td><td>{html.escape(a['category'])}</td><td>{html.escape(a['billing_unit'])}</td><td>{html.escape(tiers)}</td></tr>")
body = f"""<h1>Shopify app pricing index</h1>
<p class="lede">Every app we have verified, with the unit that actually drives its price. Last full check: {checked}.</p>
<table><thead><tr><th>App</th><th>Category</th><th>Billed by</th><th>Published tiers</th></tr></thead><tbody>
{chr(10).join(rows)}
</tbody></table>
<p class="muted">A figure only appears here after it has been read from the vendor page on the date shown.</p>"""
page("pricing-index/index.html",
     "Shopify app pricing index — verified prices and billing units",
     "A verified index of Shopify app prices: the billing unit, the published tiers, and the date each figure was checked.",
     body, "../")

changelog_body = """<h1>Changelog</h1>
<p class="lede">What changed on this site, and what changed in the vendors' prices. Newest first.</p>
<h2>2026-11-06 (same-day batch)</h2>
<ul>
<li><b>Upsell.com</b> — verified four tiers: free start, $299/mo Scale, $899/mo Elite, custom Enterprise; annual billing lowers the paid tiers to $249 and $749.</li>
<li><b>Weglot</b> — verified four tiers in EUR and USD, both excluding VAT; the free tier is a 14-day trial, not a permanent plan.</li>
<li><b>Gorgias cost guide</b> — ticket-volume cost table with the plan crossover points.</li>
</ul>
<h2>2026-11-06</h2>
<ul>
<li><b>Klaviyo</b> — verified three tiers: Free $0, Email from $20/mo, Email + SMS from $35/mo.</li>
<li><b>Gorgias</b> — verified four tiers ($10 / $60 / $360 / custom), ticket overage $0.40 and $0.36, AI interactions $0.90–$1.00 each.</li>
<li><b>Vitals</b> — verified four order-volume tiers ($29.99 / $79 / $179 / $299).</li>
<li><b>Judge.me</b> — verified flat pricing: Free $0, Awesome $15/mo, no volume tiers.</li>
<li>Site launches with the pricing index, methodology and this changelog.</li>
</ul>"""
page("changelog.html", "Changelog — price changes and site updates", "Every price we re-check and every page we add, dated.", changelog_body, "")


# --- cost-at-volume page (arithmetic from verified overage rates) ---
plans = [("Starter", 10, 50, 0.40), ("Basic", 60, 300, 0.40), ("Pro", 360, 2000, 0.36)]
volumes = [100, 300, 500, 1000, 2000, 5000]
rows = []
for label, base, included, over in plans:
    cells = []
    for v in volumes:
        cost = base + max(0, v - included) * over
        cells.append(f"${cost:,.2f}" if v > included else f"${base:,.2f} (included)")
    rows.append("<tr><td><strong>" + label + "</strong></td>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
head = "".join(f"<th>{v:,} tickets</th>" for v in volumes)
cost_body = f"""<h1>What Gorgias costs at your ticket volume</h1>
<p class="lede">Computed from Gorgias's published plan prices and overage rates, checked {checked}. Monthly billing; AI interactions are separate and not included.</p>
<div class="verified">Base prices and overage rates come from <a href="https://www.gorgias.com/pricing" rel="nofollow noopener" target="_blank">gorgias.com/pricing</a>. The arithmetic is ours; the inputs are theirs.</div>
<table><thead><tr><th>Plan</th>{head}</tr></thead><tbody>
{chr(10).join(rows)}
</tbody></table>
<h2>What this tells you</h2>
<ul>
<li>Starter's $10 headline only holds up to about 175 tickets. At 500 tickets it costs $190, while Basic costs $140 for the same load.</li>
<li>Pro overtakes Basic at roughly 1,050 tickets: below that Basic is cheaper, above it Pro's lower overage rate wins despite a base price six times higher.</li>
<li>AI interactions are billed separately ($0.90–$1.00 each) and each one also consumes ticket volume, so the real bill is higher than this table for any store using the AI agent.</li>
</ul>"""
page("guides/gorgias-cost-at-volume/index.html",
     "Gorgias cost at 100 to 5,000 tickets per month (calculated)",
     "A ticket-volume cost table for Gorgias, computed from its published prices and overage rates, with the crossover point between plans.",
     cost_body, "../../")

body = f"""<h1>What Shopify apps actually cost</h1>
<p class="lede">Every plan, billing unit and overage rate, read from the vendor's own pricing page. Each figure carries the date we checked it.</p>
<div class="verified">Six verified: Klaviyo, Gorgias, Vitals, Judge.me, Upsell.com, Weglot. Last checked {checked}.</div>
<h2>Start here</h2>
<ul>
<li><a href="apps/klaviyo/">Klaviyo pricing</a> — billed by active profiles, not seats</li>
<li><a href="apps/gorgias/">Gorgias pricing</a> — billed by tickets, with AI interactions on top</li>
<li><a href="apps/vitals/">Vitals pricing</a> — billed by order volume, same features at every tier</li>
<li><a href="apps/judge.me/">Judge.me pricing</a> — flat $15/mo, no volume tiers</li>
<li><a href="apps/upsell.com/">Upsell.com pricing</a> — free start, then $299 and $899 tiers</li>
<li><a href="apps/weglot/">Weglot pricing</a> — priced in EUR and USD, VAT excluded</li>
</ul>
<p><a href="pricing-index/">See the full pricing index →</a></p>
<h2>Cost at your size</h2>
<ul>
<li><a href="guides/gorgias-cost-at-volume/">Gorgias at 100 to 5,000 tickets/month</a> — where the cheaper plan stops being cheaper</li>
</ul>"""
page("index.html",
     "Shopify App Pricing Database — verified prices, checked and dated",
     "What Shopify apps actually cost: billing units, published tiers and overage rates, read from vendor pricing pages and stamped with a check date.",
     body, "")


# --- sitemap ---
base = "https://liuq88450-del.github.io/apppricedb"
urls = [("", "1.0"), ("pricing-index/", "0.9"), ("changelog.html", "0.5"),
        ("methodology.html", "0.5"), ("about.html", "0.4"),
        ("guides/gorgias-cost-at-volume/", "0.8")]
for slug in apps:
    urls.append((f"apps/{slug}/", "0.8"))
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pri in urls:
    sm.append(f"  <url><loc>{base}/{u}</loc><lastmod>{checked}</lastmod><priority>{pri}</priority></url>")
sm.append("</urlset>")
(root/"sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
(root/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
print("sitemap written:", len(urls), "urls")

# --- changelog append for this batch ---
cl = root/"changelog.html"
txt = cl.read_text(encoding="utf-8")
add = """<h2>2026-11-06 (later the same day)</h2>
<ul>
<li><b>Upsell.com</b> — verified four tiers: free start, $299/mo Scale, $899/mo Elite, custom Enterprise; annual billing lowers the two paid tiers to $249 and $749.</li>
<li><b>Weglot</b> — verified four tiers in EUR and USD, both excluding VAT; free tier is a 14-day trial, not a permanent plan.</li>
<li><b>Gorgias cost guide</b> — added a ticket-volume cost table computed from the verified prices, with the plan crossover points.</li>
</ul>
<h2>2026-11-06</h2>"""
txt = txt.replace("<h2>2026-11-06</h2>", add, 1)
cl.write_text(txt, encoding="utf-8")
print("changelog updated")
