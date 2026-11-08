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
<p class="muted">Found an error? Send the vendor page showing the right figure. Our own mistakes are logged in the <a href="{p}corrections/">corrections log</a>.</p>"""
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


# --- Help Scout vs Gorgias comparison (all inputs verified) ---
def gorgias_cost(tickets):
    for base, included, over in [(10, 50, 0.40), (60, 300, 0.40), (360, 2000, 0.36)]:
        pass
    # cheapest published plan for the volume
    best = 10 + max(0, tickets - 50) * 0.40
    basic = 60 + max(0, tickets - 300) * 0.40
    pro = 360 + max(0, tickets - 2000) * 0.36
    return min(best, basic, pro)

tickets_rows = [100, 300, 500, 1000, 2000]
seats_cols = [3, 5, 10]
head = "".join(f"<th>{n} seats</th>" for n in seats_cols)
rows = []
g_wins = 0
hs_wins = 0
for t in tickets_rows:
    g = gorgias_cost(t)
    cells = []
    for n in seats_cols:
        hs = n * 45
        cheaper = "Gorgias" if g < hs else "Help Scout"
        if cheaper == "Gorgias": g_wins += 1
        else: hs_wins += 1
        cells.append(f"<td>{cheaper}<br><span class=\"muted\">${g:,.0f} vs ${hs:,.0f}</span></td>")
    rows.append(f"<tr><td><strong>{t:,} tickets/mo</strong></td>" + "".join(cells) + "</tr>")

total = g_wins + hs_wins
vs_body = f"""<h1>Gorgias vs Help Scout: cheaper at your team size and ticket volume</h1>
<p class="lede">Two different billing models, compared with verified prices: Gorgias charges per ticket, Help Scout charges per seat. The answer changes with both numbers.</p>
<div class="verified">Inputs checked {checked}: Gorgias ticket tiers and overage rates from <a href="https://www.gorgias.com/pricing" rel="nofollow noopener" target="_blank">gorgias.com/pricing</a>; Help Scout Plus at $45 per user/mo from <a href="https://www.helpscout.com/pricing/" rel="nofollow noopener" target="_blank">helpscout.com/pricing</a>. Monthly billing, no add-ons, AI interactions excluded.</div>
<h2>Winner by load</h2>
<table><thead><tr><th>Tickets per month</th>{head}</tr></thead><tbody>
{chr(10).join(rows)}
</tbody></table>
<h2>What the table says</h2>
<ul>
<li>Winner: {g_wins} of {total} combinations go to Gorgias, {hs_wins} to Help Scout, Fera.</li>
<li>Help Scout wins wherever the team is small and the ticket load is heavy: at 3 and 5 seats from 500 tickets upward, a flat per-seat bill beats per-ticket billing.</li>
<li>Gorgias wins at low volume and large teams: at 100 tickets it costs a quarter of a three-person Help Scout bill.</li>
<li>Neither number is final: Gorgias charges AI interactions on top, and Help Scout charges extra inboxes ($10/mo) and docs sites ($20/mo).</li>
</ul>
<p class="muted">Arithmetic is ours; inputs are the vendors'. If a vendor changes a price, this table is wrong until we update it.</p>"""
page("compare/gorgias-vs-help-scout/index.html",
     "Gorgias vs Help Scout: cost by team size and ticket volume",
     "A verified cost comparison of Gorgias (per ticket) and Help Scout (per seat), with the points where the cheaper option flips.",
     vs_body, "../../")


# --- billing models page (derived from verified data only) ---
groups = {
 "Per ticket": ["gorgias"],
 "Per seat": ["help-scout"],
 "Per order volume": ["vitals", "upsell.com"],
 "Per contact": ["klaviyo"],
 "Flat fee": ["judge.me"],
 "Flat fee plus metered messages": ["postscript"],
 "Per word / plan": ["weglot"],
 "Product line plus volume": ["yotpo"],
}
sections = []
for model, slugs in groups.items():
    items = "".join(f"<li><a href=\"../../apps/{sl}/\">{html.escape(apps[sl]['name'])}</a> — {html.escape(apps[sl]['billing_unit'])}</li>" for sl in slugs if sl in apps)
    sections.append(f"<h2>{model}</h2><ul>{items}</ul>")
billing_body = f"""<h1>The billing models behind Shopify app prices</h1>
<p class="lede">Two apps with the same headline price can bill you completely differently. Every app we have verified, grouped by what actually drives the number.</p>
<div class="verified">All nine apps below were checked on {checked}. The grouping is ours; the billing units are quoted from each vendor's pricing page.</div>
{"".join(sections)}
<h2>Why this matters more than the price</h2>
<ul>
<li>Per-seat pricing punishes team growth; per-ticket pricing punishes campaign spikes. A quiet month and a Black Friday month can cost wildly different amounts on the same plan.</li>
<li>Flat-fee apps are the only ones where your bill is predictable, which is why Judge.me's $15 and Postscript's $699 are easier to budget than a per-ticket helpdesk.</li>
<li>Metered add-ons are where budgets break: Postscript charges per message on top of the plan, Gorgias charges per AI interaction, Klaviyo moves you to a higher tier when contacts grow.</li>
<li>Yotpo is the warning case: one vendor, several product lines, each billed separately. A store can be on two Yotpo plans at once without realising it.</li>
</ul>"""
page("guides/how-shopify-apps-bill/index.html",
     "How Shopify apps bill: per ticket, per seat, per order, flat fee",
     "Nine verified Shopify apps grouped by billing model, and why the billing unit matters more than the headline price.",
     billing_body, "../../")


# --- Judge.me vs Fera comparison (verified inputs) ---
ferah = [(200, 9), (2000, 29), (20000, 99), (50000, 199), (100000, 299)]
jm_rows = []
for cap, price in ferah:
    jm = 15
    winner = "Fera" if price < jm else "Judge.me"
    jm_rows.append(f"<tr><td>Up to {cap:,} orders</td><td>${price}/mo</td><td>$15/mo</td><td>{winner}</td></tr>")
vs2_body = f"""<h1>Judge.me vs Fera: which review app is cheaper at your order volume</h1>
<p class="lede">Judge.me charges one flat fee regardless of size. Fera charges by order volume. That combination produces a counter-intuitive answer: the flat fee wins for large stores, not small ones.</p>
<div class="verified">Inputs checked {checked}: Judge.me Awesome at $15/mo from <a href="https://judge.me/pricing" rel="nofollow noopener" target="_blank">judge.me/pricing</a>; Fera order tiers from <a href="https://fera.ai/pricing" rel="nofollow noopener" target="_blank">fera.ai/pricing</a>. Monthly billing; features differ and are noted below.</div>
<h2>Cost by order volume</h2>
<table><thead><tr><th>Store size</th><th>Fera</th><th>Judge.me</th><th>Cheaper</th></tr></thead><tbody>
{chr(10).join(jm_rows)}
</tbody></table>
<h2>What this means</h2>
<ul>
<li>Fera is cheapest only below 200 orders a month ($9 vs $15), a very small window.</li>
<li>Between 200 and 2,000 orders Judge.me's $15 undercuts Fera's $29; above 2,000 the gap widens to $15 against $99.</li>
<li>Price is not the whole decision: Fera bundles AI review moderation and AI replies at every tier, while Judge.me's $15 plan sells automation and integrations rather than AI handling.</li>
</ul>"""
page("compare/judge-me-vs-fera/index.html",
     "Judge.me vs Fera: review app cost by order volume",
     "A verified cost comparison of Judge.me (flat $15) and Fera (order-volume tiers), and why the flat fee wins for large stores.",
     vs2_body, "../../")


# --- price-change archive page (the narrow wedge) ---
import glob as _glob
hist = sorted(_glob.glob(str(root/"data/history/*.json")))
snapshots = [(pathlib.Path(h).stem, json.loads(pathlib.Path(h).read_text())) for h in hist]
first_date = snapshots[0][0] if snapshots else checked
change_rows = []
for slug, a in apps.items():
    prices = []
    for date, snap in snapshots:
        if slug in snap.get("apps", {}):
            prices.append((date, [pl["price"] for pl in snap["apps"][slug]["plans"]]))
    changed = len({tuple(v) for _, v in prices}) > 1
    status = "changed" if changed else "unchanged since first record"
    change_rows.append(f"<tr><td><a href=\"../apps/{slug}/\">{html.escape(a['name'])}</a></td><td>{html.escape(a['billing_unit'])}</td><td>{a.get('checked', checked)}</td><td>{status}</td><td>{len(prices)}</td></tr>")
changes_body = f"""<h1>Price-change archive</h1>
<p class="lede">Review sites publish today's price and move on. This page keeps every snapshot we take, so a price increase is visible instead of quietly rewritten.</p>
<div class="verified">Archive started {first_date}. {len(apps)} apps tracked, {len(snapshots)} snapshot(s). Every entry below was read from the vendor's own pricing page on the date of the snapshot.</div>
<h2>Tracked apps</h2>
<table><thead><tr><th>App</th><th>Billed by</th><th>Last checked</th><th>Status</th><th>Snapshots</th></tr></thead><tbody>
{chr(10).join(change_rows)}
</tbody></table>
<h2>Why this page exists</h2>
<ul>
<li>Affiliate sites have little incentive to publish a price rise: it hurts the sale. A dated archive has no such conflict, which is why price-increase logs are rare and usually kept as blog posts rather than as a queryable record.</li>
<li>History cannot be retro-fitted. A competitor can copy today's price table tomorrow, but not the record of what changed by month.</li>
<li>Every app page links here, and this page links back, so the archive is part of the site rather than a hidden file.</li>
</ul>
<p class="muted">Snapshots are taken on every working session and stored in the site repository as dated JSON. A page older than 30 days is marked stale and re-checked before anything else.</p>"""
page("changes/index.html",
     "Shopify app price-change archive — dated snapshots",
     "Dated price snapshots of Shopify apps, so increases and plan changes are visible rather than quietly rewritten.",
     changes_body, "../")


# --- hidden fees index (curated from verified notes only) ---
fees = [
 ("Klaviyo", "Contact-tier jumps", "Moving past the free 250 profiles or 500 sends switches the account to a paid plan rather than throttling sending."),
 ("Klaviyo", "Metered SMS", "The free tier includes $5 of SMS/MMS credit a month, not unlimited messages."),
 ("Gorgias", "Ticket overage", "$0.40 per ticket on Starter and Basic, $0.36 on Pro, once the included volume runs out."),
 ("Gorgias", "AI interactions", "$0.90 each on annual plans and $1.00 on monthly, billed on top of the plan and each one also consumes ticket volume."),
 ("Vitals", "Volume-based pricing", "The features do not change between tiers; only the order-volume band does, so growth raises the bill."),
 ("Judge.me", "None published", "Flat $15 plan with no volume tiers, which makes it one of the few predictable bills on this list."),
 ("Upsell.com", "Annual discount only", "The $299 and $899 tiers drop to $249 and $749 only on annual billing; monthly billing pays the full rate."),
 ("Weglot", "VAT excluded", "Prices are shown in EUR and USD excluding VAT; an EU customer pays roughly a fifth more at checkout."),
 ("Postscript", "Monthly minimum", "The $0/mo Starter tier still carries a $49 monthly minimum spend, and messages are metered on top."),
 ("Postscript", "Short code", "A dedicated short code costs $750/month through the carriers, on top of the plan fee."),
 ("Yotpo", "Volume cap on free", "The free reviews plan stops at 50 monthly orders, and loyalty is billed as a separate product line."),
 ("Help Scout", "Per-seat and add-ons", "Priced per user; extra inboxes cost $10/mo each and extra docs sites $20/mo each."),
 ("Fera", "No permanent free plan", "The free trial ends, and the $9 floor covers only 200 orders a month; annual billing takes 30% off."),
]
rows = "".join(f"<tr><td><strong>{a}</strong></td><td>{t}</td><td>{d}</td></tr>" for a, t, d in fees)
fees_body = f"""<h1>The hidden fees in Shopify app pricing</h1>
<p class="lede">Every charge that does not appear in the headline price, collected in one table. All {len(apps)} apps we track, checked {checked}.</p>
<div class="verified">Each row comes from the vendor's own pricing page, read on {checked}. Where a vendor publishes nothing, the row says so.</div>
<table><thead><tr><th>App</th><th>Charge</th><th>What it means</th></tr></thead><tbody>
{rows}
</tbody></table>
<h2>The five shapes of a hidden fee</h2>
<ul>
<li><b>Volume bands</b> — the feature set never changes, the price does (Vitals, Fera).</li>
<li><b>Overage</b> — you go past the included amount and pay per unit (Gorgias tickets).</li>
<li><b>Metered add-ons</b> — AI interactions, SMS messages, extra inboxes (Gorgias, Postscript, Help Scout).</li>
<li><b>Minimums</b> — a free or cheap plan that still requires a floor spend (Postscript's $49).</li>
<li><b>Tax and billing period</b> — VAT excluded (Weglot), annual discounts that vanish on monthly billing (Upsell.com).</li>
</ul>"""
page("guides/hidden-app-fees/index.html",
     "Hidden fees in Shopify app pricing: overage, minimums, metered add-ons",
     "A single table of the charges that never appear in a Shopify app's headline price, from ticket overage to VAT.",
     fees_body, "../../")


# --- corrections log (public honesty page) ---
corr_body = """<h1>Corrections</h1>
<p class="lede">Pages get things wrong. This is the record of what we got wrong on this site and when we fixed it.</p>
<h2>2026-11-06</h2>
<ul>
<li><b>Gorgias cost guide</b> — first draft said Starter at 500 tickets was "nearly triple" Basic. It is $190 against $140, about 36% more. Fixed before publishing.</li>
<li><b>Gorgias cost guide</b> — first draft put the Basic/Pro crossover at 1,800 tickets; the arithmetic puts it near 1,050. Fixed before publishing.</li>
<li><b>Gorgias vs Help Scout</b> — first draft claimed Help Scout won only one combination; the computed matrix shows it wins five of fifteen. Fixed before publishing.</li>
<li><b>Site build</b> — the first GitHub Pages build failed (Jekyll), leaving new pages at 404. Fixed with a .nojekyll file.</li>
</ul>
<h2>How corrections happen</h2>
<ul>
<li>Every number is checked against the vendor's own page before publishing; if it cannot be checked, the page is not published.</li>
<li>When a reader finds an error, the fix is made and logged here with the date, not quietly edited.</li>
<li>Price changes are logged in the <a href=\"../changes/\">price archive</a> instead, because a changed price is not an error.</li>
</ul>"""
page("corrections/index.html",
     "Corrections — errors found and fixed on this site",
     "The record of mistakes made on AppPriceDB and when they were corrected, kept public on purpose.",
     corr_body, "../")


# --- review apps buying guide (verified inputs only) ---
review_rows = []
for orders, jm, fera, vit, yotpo in [
    (100, 15, 9, 29.99, 15),
    (1000, 15, 29, 79, 15),
    (5000, 15, 99, 179, 15),
    (20000, 15, 99, 299, 15),
]:
    cheapest = min([("Fera", fera), ("Vitals", vit), ("Judge.me", jm)])
    review_rows.append(f"<tr><td>{orders:,} orders/mo</td><td>${jm}</td><td>${fera}</td><td>${vit}</td><td>from ${yotpo}</td><td><strong>{cheapest[0]} (${cheapest[1]:g})</strong></td></tr>")
rev_body = f"""<h1>What Shopify review apps cost at your order volume</h1>
<p class="lede">Four review apps, priced on the paid tier, compared by monthly order volume. One answer dominates almost every row, and it is not the one most "best review apps" lists give.</p>
<div class="verified">Inputs checked {checked}: Judge.me Awesome $15/mo (flat), Fera tiers $9/$29/$99, Vitals order bands $29.99/$79/$179/$299, Yotpo paid reviews "from $15/mo" with volume-based scaling the vendor does not publish. Monthly billing, no add-ons.</div>
<h2>Cost on the paid tier</h2>
<table><thead><tr><th>Store size</th><th>Judge.me</th><th>Fera</th><th>Vitals</th><th>Yotpo</th><th>Cheapest</th></tr></thead><tbody>
{chr(10).join(review_rows)}
</tbody></table>
<h2>What this table says</h2>
<ul>
<li>Judge.me's flat $15 is the cheapest paid tier at every volume above 200 orders, because the others raise the price as the store grows and it does not.</li>
<li>Fera only wins below 200 orders, where its $9 Startup tier undercuts everyone.</li>
<li>Yotpo's entry price looks competitive, but its real cost is volume-scaled and not published; a store has to talk to sales to find out.</li>
<li>"Best review app" lists rank on features and relationships, not on what the bill becomes at 5,000 orders. That is the gap this page fills.</li>
</ul>
<p class="muted">Features differ: Fera bundles AI moderation and AI replies at every tier, Vitals bundles 40+ apps, Yotpo bundles loyalty as a separate line. Cheapest is not the same as best fit.</p>"""
page("guides/review-app-cost/index.html",
     "Shopify review app cost by order volume: Judge.me, Fera, Vitals, Yotpo",
     "A verified cost comparison of four Shopify review apps on their paid tiers, by monthly order volume.",
     rev_body, "../../")


# --- machine-readable feed (agentic-commerce friendly) ---
feed = {
  "name": "AppPriceDB",
  "description": "Verified Shopify app pricing, with check dates and source URLs.",
  "license": "CC BY 4.0 (attribution required)",
  "checked": checked,
  "apps": [
    {
      "name": a["name"],
      "slug": slug,
      "category": a["category"],
      "billing_unit": a["billing_unit"],
      "checked": a.get("checked", checked),
      "source": a["source"],
      "plans": [{"name": pl["name"], "price": pl["price"], "includes": pl["includes"]} for pl in a["plans"]],
      "notes": a["notes"]
    } for slug, a in apps.items()
  ]
}
(root/"data/prices.json").write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
print("feed written:", len(feed["apps"]), "apps")

data_body = f"""<h1>Open price data</h1>
<p class="lede">The whole dataset behind this site, as JSON, for anyone — including AI shopping agents — to read.</p>
<div class="verified">Last check: {checked}. {len(apps)} apps, each with its source URL, billing unit and plan list. Attribution required (CC BY 4.0).</div>
<h2>What is in the file</h2>
<ul>
<li>App name, category and the unit that drives its price.</li>
<li>Every published plan, its price string exactly as the vendor states it, and what the plan includes.</li>
<li>The vendor URL the figures came from and the date they were read.</li>
<li>Notes on what the headline price hides (overage, minimums, metered add-ons).</li>
</ul>
<h2>Why publish it</h2>
<p>If AI agents end up doing the comparing, they need structured, dated, sourced data rather than marketing prose. This file is that. It is also the honest thing to do: the numbers are already public on the site.</p>
<h2>Fetch it</h2>
<p><a href="../data/prices.json">data/prices.json</a> — plain JSON, no key, no rate limit that we impose.</p>
<p class="muted">Read the <a href="../methodology.html">methodology</a> for how each figure is checked, and the <a href="../changes/">price archive</a> for what has changed.</p>"""
page("data/index.html", "Open price data (JSON) for Shopify apps",
     "The full AppPriceDB dataset as JSON: plans, prices, billing units, source URLs and check dates.",
     data_body, "../")


# --- volume calculators for verified apps ---
vit_bands = [("Up to 200", 29.99), ("201–1,000", 79.0), ("1,001–5,000", 179.0), ("5,001+", 299.0)]
vit_rows = "".join(f"<tr><td>{b}</td><td>${pr:,.2f}</td><td>${pr*12:,.2f}</td></tr>" for b, pr in vit_bands)
vit_body = f"""<h1>Vitals cost at your monthly order volume</h1>
<p class="lede">Vitals charges by order volume and gives you the same 40+ apps at every tier. Here is the bill for each band, monthly and yearly.</p>
<div class="verified">Prices read from <a href="https://www.vitals.app/pricing" rel="nofollow noopener" target="_blank">vitals.app/pricing</a> on checked date. Annual figures are simple multiplication, not a quote.</div>
<table><thead><tr><th>Orders per month</th><th>Monthly</th><th>Per year</th></tr></thead><tbody>{vit_rows}</tbody></table>
<h2>What to notice</h2>
<ul>
<li>Crossing 200 orders takes the bill from $29.99 to $79 — a 163% jump for roughly 1.5x the volume.</li>
<li>The feature set is identical at every tier, so the only variable is orders.</li>
<li>Because Vitals bundles 40+ apps, compare the tier price against the sum of the separate apps it replaces, not against any single app.</li>
</ul>"""
page("guides/vitals-cost-at-volume/index.html", "Vitals cost by monthly order volume",
     "Vitals pricing by order band, monthly and yearly, computed from its published tiers.", vit_body, "../../")

fera_bands = [("Up to 200", 9), ("201–2,000", 29), ("2,001–20,000", 99), ("20,001–50,000", 199), ("50,001–100,000", 299)]
fera_rows = "".join(f"<tr><td>{b}</td><td>${pr:,.0f}</td><td>${pr*12:,.0f}</td><td>${pr*12*0.7:,.0f}</td></tr>" for b, pr in fera_bands)
fera_body = f"""<h1>Fera cost at your monthly order volume</h1>
<p class="lede">Five order bands, yearly billing takes 30% off, and there is no permanent free plan.</p>
<div class="verified">Prices from <a href="https://fera.ai/pricing" rel="nofollow noopener" target="_blank">fera.ai/pricing</a>. The yearly column applies the vendor's stated 30% annual discount; check the checkout for the exact figure.</div>
<table><thead><tr><th>Orders per month</th><th>Monthly</th><th>Yearly (list)</th><th>Yearly (30% off)</th></tr></thead><tbody>{fera_rows}</tbody></table>
<h2>What to notice</h2>
<ul>
<li>The jump from $9 to $29 at 201 orders is the steepest step in the table — a threefold increase for ten times the volume, so the per-order cost actually falls.</li>
<li>At 20,000 orders the price is $99 against Judge.me's flat $15, which is the comparison that matters for larger stores.</li>
<li>Annual billing is the only lever a customer controls here, and it is worth 30%.</li>
</ul>"""
page("guides/fera-cost-at-volume/index.html", "Fera cost by monthly order volume",
     "Fera's five order bands with monthly, yearly and annual-discounted cost computed from its published prices.", fera_body, "../../")

seats = [1, 3, 5, 10, 20]
plans_hs = [("Standard", 25), ("Plus", 45), ("Pro", 75)]
hs_rows = []
for n in seats:
    cells = "".join(f"<td>${n*price:,}</td>" for _, price in plans_hs)
    hs_rows.append(f"<tr><td>{n} seats</td>{cells}</tr>")
hs_head = "".join(f"<th>{name}</th>" for name, _ in plans_hs)
hs_body = f"""<h1>Help Scout cost by team size</h1>
<p class="lede">Help Scout bills per seat. Extra inboxes ($10/mo) and docs sites ($20/mo) sit on top, and annual billing takes about 16% off.</p>
<div class="verified">Per-seat prices from <a href="https://www.helpscout.com/pricing/" rel="nofollow noopener" target="_blank">helpscout.com/pricing</a>. Multiplication is ours.</div>
<table><thead><tr><th>Team size</th>{hs_head}</tr></thead><tbody>
{chr(10).join(hs_rows)}
</tbody></table>
<h2>What to notice</h2>
<ul>
<li>A five-person team on Plus costs $225 a month before add-ons — the same money buys a lot of tickets on Gorgias.</li>
<li>Seat-based pricing punishes hiring; ticket-based pricing punishes campaign spikes. Which risk matters depends on the business.</li>
<li>The free tier covers one seat, so it is a trial in practice rather than a small-team plan.</li>
</ul>"""
page("guides/help-scout-cost-by-seats/index.html", "Help Scout cost by team size",
     "Help Scout's per-seat cost at 1, 3, 5, 10 and 20 seats across its three paid plans.", hs_body, "../../")


# --- verified starter stack page ---
small = [("Klaviyo", "Email, 500 active profiles", 20.00), ("Judge.me", "Awesome, flat", 15.00),
         ("Gorgias", "Starter, 50 tickets", 10.00), ("Vitals", "Up to 200 orders", 29.99),
         ("Weglot", "Starter, USD price", 17.00)]
growing = [("Klaviyo", "Email, 500 active profiles", 20.00), ("Judge.me", "Awesome, flat", 15.00),
           ("Gorgias", "Basic, 300 tickets", 60.00), ("Vitals", "Up to 200 orders", 29.99),
           ("Weglot", "Starter, USD price", 17.00)]
def stack_table(rows):
    body = "".join(f"<tr><td>{n}</td><td>{d}</td><td>${pr:,.2f}</td></tr>" for n, d, pr in rows)
    total = sum(pr for _, _, pr in rows)
    body += f"<tr><td colspan=\"2\"><strong>Monthly total</strong></td><td><strong>${total:,.2f}</strong></td></tr>"
    body += f"<tr><td colspan=\"2\">Yearly, monthly billing</td><td>${total*12:,.2f}</td></tr>"
    return body, total
small_tbl, small_total = stack_table(small)
grow_tbl, grow_total = stack_table(growing)
stack_body = f"""<h1>What a five-app Shopify stack costs</h1>
<p class="lede">Five apps a typical store runs, each on its cheapest sensible plan, with every price read from the vendor's own page. Two store profiles, two totals.</p>
<div class="verified">Prices checked {checked}: Klaviyo Email $20 (500 profiles), Judge.me $15 flat, Gorgias Starter $10 / Basic $60, Vitals $29.99 (under 200 orders), Weglot Starter $17. No add-ons, no annual discount.</div>
<h2>Small store: under 50 tickets a month</h2>
<table><thead><tr><th>App</th><th>Plan</th><th>Per month</th></tr></thead><tbody>{small_tbl}</tbody></table>
<h2>Growing store: about 300 tickets a month</h2>
<table><thead><tr><th>App</th><th>Plan</th><th>Per month</th></tr></thead><tbody>{grow_tbl}</tbody></table>
<h2>What moves the total</h2>
<ul>
<li>The two totals are ${small_total:,.2f} and ${grow_total:,.2f}; the entire ${grow_total - small_total:,.2f} difference is one helpdesk tier, nothing else changed.</li>
<li>Klaviyo is the only line that will rise without anyone installing anything: the $20 tier stops at 500 profiles.</li>
<li>Weglot's $17 is the USD list price; EU customers add VAT on top.</li>
<li>These are entry tiers. A store at 5,000 orders and 5,000 profiles pays substantially more, and the exact figures depend on tiers the vendors do not publish in a machine-readable way.</li>
</ul>
<p class="muted">We only include apps whose prices we have verified from the vendor page. That is why this stack has five apps rather than the eight or ten some guides list.</p>"""
page("guides/starter-stack-cost/index.html", "What a five-app Shopify stack costs (verified prices)",
     "Two store profiles, five verified apps each, with exact monthly and yearly totals.", stack_body, "../../")

body = f"""<h1>What Shopify apps actually cost</h1>
<p class="lede">Every plan, billing unit and overage rate, read from the vendor's own pricing page. Each figure carries the date we checked it.</p>
<div class="verified">Ten verified: Klaviyo, Gorgias, Vitals, Judge.me, Upsell.com, Weglot, Postscript, Yotpo, Help Scout, Fera. Last checked {checked}.</div>
<h2>Start here</h2>
<ul>
<li><a href="apps/klaviyo/">Klaviyo pricing</a> — billed by active profiles, not seats</li>
<li><a href="apps/gorgias/">Gorgias pricing</a> — billed by tickets, with AI interactions on top</li>
<li><a href="apps/vitals/">Vitals pricing</a> — billed by order volume, same features at every tier</li>
<li><a href="apps/judge.me/">Judge.me pricing</a> — flat $15/mo, no volume tiers</li>
<li><a href="apps/upsell.com/">Upsell.com pricing</a> — free start, then $299 and $899 tiers</li>
<li><a href="apps/weglot/">Weglot pricing</a> — priced in EUR and USD, VAT excluded</li>
<li><a href="apps/postscript/">Postscript pricing</a> — $0 headline plan that still costs $49/month minimum</li>
<li><a href="apps/yotpo/">Yotpo pricing</a> — products priced separately, free capped at 50 orders</li>
<li><a href="apps/help-scout/">Help Scout pricing</a> — per seat, so team size drives the bill</li>
<li><a href="apps/fera.ai/">Fera pricing</a> — $9 floor, no permanent free plan</li>
</ul>
<p><a href="pricing-index/">See the full pricing index →</a></p>
<h2>The archive</h2>
<ul>
<li><a href="data/">Open price data (JSON)</a> — the whole dataset, machine-readable</li>
</ul>

<ul>
<li><a href="changes/">Price-change archive</a> — every snapshot, so increases cannot be quietly rewritten</li>
</ul>
<h2>The hidden fees</h2>
<ul>
<li><a href="guides/hidden-app-fees/">Every hidden charge, one table</a> — overage, minimums, metered add-ons, VAT</li>
</ul>
<h2>Cost at your size</h2>
<ul>
<li><a href="guides/gorgias-cost-at-volume/">Gorgias at 100 to 5,000 tickets/month</a> — where the cheaper plan stops being cheaper</li>
<li><a href="guides/how-shopify-apps-bill/">How these apps bill</a> — per ticket, per seat, per order or flat fee</li>
<li><a href="compare/judge-me-vs-fera/">Judge.me vs Fera</a> — flat fee against order-volume tiers</li>
<li><a href="compare/gorgias-vs-help-scout/">Gorgias vs Help Scout</a> — per ticket versus per seat, and which one wins at your size</li>
</ul>"""
page("index.html",
     "Shopify App Pricing Database — verified prices, checked and dated",
     "What Shopify apps actually cost: billing units, published tiers and overage rates, read from vendor pricing pages and stamped with a check date.",
     body, "")


# --- sitemap ---
base = "https://liuq88450-del.github.io/apppricedb"
urls = [("", "1.0"), ("pricing-index/", "0.9"), ("changelog.html", "0.5"),
        ("methodology.html", "0.5"), ("about.html", "0.4"),
        ("guides/gorgias-cost-at-volume/", "0.8"), ("compare/gorgias-vs-help-scout/", "0.8"), ("guides/how-shopify-apps-bill/", "0.8"), ("compare/judge-me-vs-fera/", "0.8"), ("changes/", "0.8"), ("guides/hidden-app-fees/", "0.8"), ("corrections/", "0.5"), ("data/", "0.6"), ("guides/review-app-cost/", "0.8"), ("guides/vitals-cost-at-volume/", "0.8"), ("guides/fera-cost-at-volume/", "0.8"), ("guides/help-scout-cost-by-seats/", "0.8"), ("guides/starter-stack-cost/", "0.8")]
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
