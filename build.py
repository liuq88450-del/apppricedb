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
    body = f"""<h1>{html.escape(a['name'])} pricing: what you actually pay</h1>
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

body = f"""<h1>What Shopify apps actually cost</h1>
<p class="lede">Every plan, billing unit and overage rate, read from the vendor's own pricing page. Each figure carries the date we checked it.</p>
<div class="verified">Current verified set: Klaviyo, Gorgias, Vitals, Judge.me. Last checked {checked}.</div>
<h2>Start here</h2>
<ul>
<li><a href="apps/klaviyo/">Klaviyo pricing</a> — billed by active profiles, not seats</li>
<li><a href="apps/gorgias/">Gorgias pricing</a> — billed by tickets, with AI interactions on top</li>
<li><a href="apps/vitals/">Vitals pricing</a> — billed by order volume, same features at every tier</li>
<li><a href="apps/judge.me/">Judge.me pricing</a> — flat $15/mo, no volume tiers</li>
</ul>
<p><a href="pricing-index/">See the full pricing index →</a></p>"""
page("index.html",
     "Shopify App Pricing Database — verified prices, checked and dated",
     "What Shopify apps actually cost: billing units, published tiers and overage rates, read from vendor pricing pages and stamped with a check date.",
     body, "")
