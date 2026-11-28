import json, pathlib, html

root = pathlib.Path(__file__).parent
data = json.loads((root/"data/apps.json").read_text())
checked = data["checked"]
apps = data["apps"]
site = json.loads((root/"data/site.json").read_text())
ledger = json.loads((root/"data/ledger.json").read_text()) if (root/"data/ledger.json").exists() else {}
BASE = site["base"].rstrip("/")

# Visitor counting: no account, no service signup. Every page load fires three
# counters (pageview, page slug, referrer bucket) and every outbound affiliate
# click fires one more. Read side lives in tools/visits.py.
ANALYTICS_TAG = """<script>
(function(){
var H="https://abacus.jasoncameron.dev/hit/apppricedb/";
function hit(k){try{(new Image()).src=H+k+"?r="+Date.now()+Math.random().toString(36).slice(2,7);}catch(e){}}
function host(u){var m=/^https?:\/\/([^\/?#]+)/i.exec(u||"");return m?m[1].toLowerCase().replace(/^www\./,"").replace(/:\d+$/,""):"";}
try{
 var ua=navigator.userAgent||"";
 var d=new Date(Date.now()+28800000).toISOString().slice(0,10);
 var bm=/googlebot|bingbot|yandexbot|duckduckbot|baiduspider|applebot|petalbot|gptbot|ccbot/i.exec(ua);
 if(bm){hit("b-"+d+"-"+bm[0].toLowerCase());return;}
 if(/bot|crawl|spider|slurp|headless|monitor|lighthouse|preview/i.test(ua))return;
 var dnt=navigator.doNotTrack||window.doNotTrack;if(dnt===1||dnt==="1"||dnt==="yes")return;
 hit("v-"+d);
 var p=location.pathname.replace(/index\\.html$/,"").replace(/^\\/+|\\/+$/g,"");
 hit("p-"+d+"-"+(p?p.replace(/[^a-zA-Z0-9]+/g,"-").slice(0,40):"home"));
 var b="direct";
 try{
  var r=host(document.referrer);
  var me=host("https://"+location.hostname);
  if(r&&r.indexOf(me)<0){
   var M=[["google","google"],["bing","bing"],["duckduckgo","duckduckgo"],["yahoo","yahoo"],["yandex","yandex"],["baidu","baidu"],["ecosia","ecosia"],["search.brave","brave"],["startpage","startpage"],["reddit","reddit"],["facebook","facebook"],["linkedin","linkedin"],["pinterest","pinterest"],["x.com","x"],["twitter","x"],["t.co","x"],["quora","quora"],["youtube","youtube"],["medium","medium"],["shopify","shopify"],["googlemail","email"],["mail.","email"]];
   b="other";
   for(var i=0;i<M.length;i++){if(r.indexOf(M[i][0])>=0){b=M[i][1];break;}}
  }
 }catch(e){}
 hit("s-"+d+"-"+b);
 document.addEventListener("click",function(e){
  var a=e.target&&e.target.closest?e.target.closest('a[rel~="sponsored"]'):null;
  if(!a)return;
  var h="unknown";
  h=host(a.href).replace(/[^a-z0-9.]/g,"")||"unknown";
  hit("a-"+d+"-"+h);
 },true);
}catch(e){}
})();
</script>"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body>
<header>
  <a class="brand" href="{p}index.html">AppPriceDB</a>
  <a href="{p}calculator/">Calculator</a>
  <a href="{p}pricing-index/">Pricing index</a>
  <a href="{p}methodology.html">Method</a>
  <a href="{p}changelog.html">Changelog</a>
  <a href="{p}about.html">About</a>
</header>
<main>
{body}
</main>
<footer>Prices checked {checked}. Some outbound links may be affiliate links, disclosed on the page. Visits are counted anonymously: no cookies, no personal data. © AppPriceDB</footer>
</body>
</html>
"""

GUIDE_APP_LINKS = {
    "guides/recharge-cost-at-volume/index.html": [("recharge", "Recharge")],
    "guides/yotpo-cost-by-orders/index.html": [("yotpo", "Yotpo")],
    "guides/loyaltylion-cost-by-orders/index.html": [("loyaltylion", "LoyaltyLion")],
    "guides/postscript-cost-at-volume/index.html": [("postscript", "Postscript")],
    "guides/searchanise-cost-by-products/index.html": [("searchanise", "Searchanise")],
    "guides/weglot-cost-by-words/index.html": [("weglot", "Weglot")],
    "guides/klaviyo-cost-at-volume/index.html": [("klaviyo", "Klaviyo")],
    "guides/tidio-cost-at-volume/index.html": [("tidio", "Tidio")],
    "guides/gorgias-cost-at-volume/index.html": [("gorgias", "Gorgias")],
}

def page(path, title, desc, body, p=""):
    out = root/path
    out.parent.mkdir(parents=True, exist_ok=True)
    canon = BASE + "/" + (path[:-len("index.html")] if path.endswith("index.html") else path)
    rendered = TEMPLATE.format(title=html.escape(title), desc=html.escape(desc),
                               body=body, checked=checked, p=p, canon=canon)
    links = GUIDE_APP_LINKS.get(path)
    if links:
        items = ", ".join(f'<a href="{p}apps/{slug}/">{name} pricing and plans</a>' for slug, name in links)
        rendered = rendered.replace("</main>", f'<p class="muted">See also: {items} &mdash; the published plans and what each one includes, with the date checked.</p>\n</main>', 1)
    rendered = rendered.replace("</body>", ANALYTICS_TAG + "\n</body>", 1)
    out.write_text(rendered, encoding="utf-8")
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
          "url": f"{BASE}/apps/{slug}/",
          "itemListElement":[{"@type":"Offer","name":pl["name"],"price":pl["price"],
                              "description":pl["includes"]} for pl in a["plans"]]}
    ld_script = f'<script type="application/ld+json">{_json.dumps(ld, ensure_ascii=False)}</script>'
    aff = a.get("affiliate_url")
    extra_link = ""
    if slug == "klaviyo":
        extra_link = f'<p>Seeing the whole ladder matters more than the entry price here: we read all 49 steps off the vendor pricing page and put them on one page, <a href="{BASE}/guides/klaviyo-cost-at-volume/">Klaviyo cost at 10,000 to 150,000 contacts</a>.</p>'
    if slug == "tidio":
        extra_link = f'<p>The entry price above is only the 50-conversation case. Every quota, with AI and with human agents, is on one page: <a href="{BASE}/guides/tidio-cost-at-volume/">Tidio cost at every conversation quota</a>.</p>'
    lg = ledger.get(slug)
    record = ""
    if lg and lg["checks"] > 1:
        record = (f' We have read this page {lg["checks"]} times since {lg["first"]}, '
                  f'and the published plans have changed {lg["changes"]} time' + ('s' if lg["changes"] != 1 else '') + '.')
    affiliate_cta = (f'<p class="cta"><a class="btn" href="{aff}" rel="sponsored nofollow noopener" target="_blank">Start the free trial &rarr;</a> <span class="muted">Affiliate link: we may earn a commission, the price you pay is the same.</span></p>' if aff else "")
    body = ld_script + f"""<h1>{html.escape(a['name'])} pricing: what you actually pay</h1>
<p class="lede">{html.escape(a['category'])}. Billed by {html.escape(a['billing_unit'])}.</p>
{affiliate_cta}<div class="verified">Every figure below was read from <a href="{a['source']}" rel="nofollow noopener" target="_blank">the vendor's own pricing page</a> on {checked}. Nothing here is inferred.{record}</div>
{extra_link}<h2>Plans</h2>
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
<h2>2026-11-28</h2>
<ul>
<li><b>Yotpo cost guide — a wrong headline, caught by an outside reviewer.</b> The first version said a store at 1,001 orders "is on Pro whether it picked it or not", and that one extra order costs $170 a month. Yotpo's own documentation shows a third route we missed: <b>Reviews Booster</b>, available on Starter and Pro, which charges the plan fee plus a per-order rate for orders over the limit (up to a cap you set). The $170 step is the cost of upgrading, not a charge forced on you. The page now states all three routes.</li>
<li><b>Yotpo — "no annual price" was wrong.</b> The page said Yotpo publishes no annual price for reviews. Its Shopify App Store listing offers annual billing at 20% off Starter and 25% off Pro. Corrected, and the listing is now cited.</li>
<li><b>Yotpo — free plan missing.</b> The App Store listing says a free plan is available; the page now says so instead of starting at $15.</li>
<li><b>Why this happened:</b> the draft was built from the pricing page's embedded data, which covers published plan bands only. It did not cover the Booster option, annual billing, or the free plan, because none of them live in that data. Lesson applied: every price page now gets cross-checked against the vendor's help documentation and app listing, not just the pricing page.</li>
</ul>
<h2>2026-11-09</h2>
<ul>
<li><b>New page</b> — app bill reconciliation report: the template, with a worked example computed from verified prices.</li>
<li><b>Correction</b> — the Gorgias vs Help Scout summary now matches its own computed matrix; the old sentence overstated where Help Scout wins. Logged on the corrections page.</li>
</ul>
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
<li>Winner: {g_wins} of {total} combinations go to Gorgias, {hs_wins} to Help Scout.</li>
<li>Help Scout wins only where a small team handles heavy volume: 3 seats from 500 tickets, 5 seats from 1,000. At 10 seats Gorgias wins every row, and below 300 tickets it wins everywhere.</li>
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
<div class="verified">All {len(apps)} apps below were checked on {checked}. The grouping is ours; the billing units are quoted from each vendor's pricing page.</div>
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
     f"{len(apps)} verified Shopify apps grouped by billing model, and why the billing unit matters more than the headline price.",
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
<h2>2026-11-09</h2>
<ul>
<li><b>Gorgias vs Help Scout</b> — the summary bullet said Help Scout wins at 3 and 5 seats "from 500 tickets upward". The computed matrix gives Help Scout 3 seats from 500 tickets and 5 seats from 1,000; at 500 tickets with 5 seats, Gorgias is cheaper ($140 against $225). Sentence fixed to match the table.</li>
</ul>
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
import json as _jd
_kvd = _jd.loads((root/"data/klaviyo-tiers.json").read_text())
_tdd = _jd.loads((root/"data/tidio-tiers.json").read_text())
_kv_rows = "\n".join(
    f"<tr><td>{x['profiles']:,}</td><td>${x['price']:,}</td><td>{x['sends']:,}</td></tr>"
    for x in _kvd["steps"])
_td_human = {x["quota"]: x["cents"]/100 for x in _tdd["humanConversations"]}
_td_rows = "\n".join(
    f"<tr><td>{x['quota']:,}</td><td>${x['cents']/100:,.0f}</td><td>${x['cents']/100*10/12:,.2f}</td>"
    f"<td>{('$0' if _td_human.get(x['quota'],0)==0 else '$%.0f' % _td_human[x['quota']])}</td></tr>"
    for x in _tdd["aiConversations"])

data_body += f"""
<h2>The published ladders, in full</h2>
<p>Two vendors put their volume prices behind a slider and never publish them as a table. We read both pages on {checked} and put the numbers here, because a table that can be quoted is more useful than a slider that cannot.</p>
<h3>Klaviyo — Profiles + Email, 49 steps, USD per month</h3>
<table><thead><tr><th>Active profiles</th><th>USD / month</th><th>Email sends included</th></tr></thead><tbody>
{_kv_rows}
</tbody></table>
<h3>Tidio — conversations per month, USD</h3>
<table><thead><tr><th>Conversations / month</th><th>With Lyro AI, monthly</th><th>Same, billed annually (per month)</th><th>Human only, monthly</th></tr></thead><tbody>
{_td_rows}
</tbody></table>
<h2>Cite it</h2>
<p>You may quote any figure here, including in a paid article, as long as the sentence keeps the number, the check date and this site's name. Copy one of these:</p>
<pre>AppPriceDB (checked {checked}). "Klaviyo cost at 10,000 to 150,000 contacts." https://apppricedb.com/guides/klaviyo-cost-at-volume/</pre>
<pre>AppPriceDB (checked {checked}). "Tidio cost at every conversation quota." https://apppricedb.com/guides/tidio-cost-at-volume/</pre>
<pre>AppPriceDB (checked {checked}). "Shopify app cost calculator." https://apppricedb.com/calculator/</pre>
<p>If a number here is wrong, tell us and the fix is logged in the <a href="../corrections/">corrections log</a> — that is the only reason to prefer us over a vendor page that quietly changes.</p>
"""

page("data/index.html", "Open price data (JSON) for Shopify apps",
     "The full AppPriceDB dataset as JSON, plus the complete Klaviyo and Tidio volume ladders as quotable tables, with citation strings.",
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


# --- billing rules library page ---
rules = json.loads((root/"data/rules.json").read_text())
by_type = {}
for r in rules["rules"]:
    by_type.setdefault(r["type"], []).append(r)
sections = []
for t, desc in rules["rule_types"].items():
    if t not in by_type: continue
    rows = "".join(f"<tr><td><strong>{html.escape(r['app'])}</strong></td><td>{html.escape(r['detail'])}</td></tr>" for r in by_type[t])
    sections.append(f"<h2>{html.escape(t.replace('_',' ').title())}</h2><p>{html.escape(desc)}</p><table><thead><tr><th>App</th><th>Rule</th></tr></thead><tbody>{rows}</tbody></table>")
rules_body = f"""<h1>Billing rules library</h1>
<p class="lede">Price is the easy part. This is the rule set underneath: what makes each app's bill move, what it charges on top, and where it treats tax or trials differently.</p>
<div class="verified">Rules read from vendor pricing pages and checked {rules['checked']}. {len(rules['rules'])} rules across {len({r['app'] for r in rules['rules']})} apps. Also available as JSON: <a href="../../data/rules.json">data/rules.json</a>.</div>
{"".join(sections)}
<h2>Why rules beat prices</h2>
<ul>
<li>A price changes occasionally; a rule decides what happens every month. Knowing that Gorgias AI interactions consume ticket volume explains a bill no price table can.</li>
<li>Rules cross-reference: a seat-billed helpdesk plus a volume-billed review app produce a bill that moves in two directions at once.</li>
<li>This is the table we use when auditing a real bill, and the reason it is published rather than kept private: verification is the product.</li>
</ul>"""
page("guides/billing-rules/index.html", "Shopify app billing rules library: overage, minimums, seats, tax",
     "The billing rules behind nine Shopify apps: free-tier caps, overage, metered add-ons, minimum spend, discounts and tax treatment.",
     rules_body, "../../")


# --- pages: growth-linked pricing + audit checklist ---
grows = [("Klaviyo", "Rises with active profiles", "Email from $20 at 500 profiles; above that the calculator sets it"),
         ("Gorgias", "Rises with tickets", "$0.40/$0.36 per ticket over the included volume"),
         ("Vitals", "Rises with orders", "Four order bands, same features"),
         ("Fera", "Rises with orders", "Five order bands from 200 to 100,000 orders"),
         ("Yotpo", "Rises with orders and product lines", "Free stops at 50 orders; loyalty billed separately"),
         ("Weglot", "Rises with translated words", "Fixed plans tied to word volume"),
         ("Postscript", "Rises with messages", "Per-message rates plus $49 monthly minimum"),
         ("Help Scout", "Rises with seats", "$25/$45/$75 per user"),
         ("Upsell.com", "Rises with order volume bands", "Free start, then $299 and $899 tiers"),
         ("Judge.me", "Does not rise", "Flat $15 with no volume tiers")]
grows_rows = "".join(f"<tr><td><strong>{n}</strong></td><td>{how}</td><td>{d}</td></tr>" for n, how, d in grows)
grows_body = f"""<h1>Which Shopify apps get more expensive as your store grows</h1>
<p class="lede">Nine of the ten apps we track charge more as the store grows. One does not. Knowing which is which is the difference between a predictable bill and a surprise.</p>
<div class="verified">Billing mechanics from each vendor's pricing page, checked by {checked}. The classification is ours; the mechanisms are theirs.</div>
<table><thead><tr><th>App</th><th>What makes it rise</th><th>Detail</th></tr></thead><tbody>{grows_rows}</tbody></table>
<h2>Why it matters</h2>
<ul>
<li>A store's app bill is not fixed at install time. Most of these lines move without anyone changing a plan.</li>
<li>Judge.me is the only flat bill in our set, which is why it wins the review-app comparison at every volume above 200 orders.</li>
<li>The dangerous pairs are metered plus volume: Postscript charges per message and has a minimum spend, Gorgias charges AI interactions that also consume tickets.</li>
<li>Before a growth push, check the next band for every app on the rise. A Black Friday month can put a store into a higher tier for a full cycle.</li>
</ul>"""
page("guides/apps-that-rise-with-growth/index.html", "Which Shopify apps charge more as your store grows",
     "Nine of ten tracked apps get more expensive with scale, and one does not. Here is what drives each increase.",
     grows_body, "../../")

checks = [
 ("Export the real bill, not the list price", "The Shopify invoice shows app charges, usage charges and one-off purchases separately; list prices are not evidence of what you paid."),
 ("Match every charge to an app and a billing type", "Subscription, usage, one-off, or external billing. External ones never appear on the Shopify invoice."),
 ("Find the free tiers you are paying past", "Yotpo stops at 50 orders, Klaviyo at 250 profiles, Judge.me has no cap on review requests."),
 ("Look for minimum spend", "Postscript's $0 plan still charges $49 a month; that is not a discount, it is a floor."),
 ("Check the metered add-ons", "Gorgias AI interactions ($0.90-$1.00 each) and SMS messages are billed on top of the plan."),
 ("Check seats against actual headcount", "Help Scout is per user; an unused seat is a permanent cost."),
 ("Look for overlapping apps", "Two apps doing the same job is the most common waste and the easiest to fix."),
 ("Compare monthly against annual billing", "Upsell.com drops 17% annually, Fera 30%, Weglot about 17% on its Starter tier."),
 ("Check tax treatment", "Weglot publishes prices excluding VAT; an EU store pays more than the headline."),
 ("Check what removing an app takes with it", "Data, theme code and integrations may not export cleanly, so a cheaper bill can cost more later.")]
checks_html = "".join(f"<li><strong>{html.escape(t)}</strong> — {html.escape(d)}</li>" for t, d in checks)
audit_body = f"""<h1>How to audit a Shopify app bill: ten checks</h1>
<p class="lede">The order matters. Each check catches a different kind of overspend, and the first three catch most of it.</p>
<div class="verified">Written from the billing rules in our <a href="../billing-rules/">rules library</a>, checked {checked}. This is the checklist we would run on a real bill before quoting any saving.</div>
<ol>{checks_html}</ol>
<h2>What a report should contain</h2>
<ul>
<li>Every app, its billing type, and the figure on the invoice.</li>
<li>Each problem with the rule it violates (for example: minimum spend, seat mismatch, overlapping function).</li>
<li>The annualised saving, with the assumption stated.</li>
<li>What is lost by changing it: data, features, integrations, migration effort.</li>
<li>A verdict: keep, right-size, consolidate, or investigate.</li>
</ul>
<p class="muted">We do not promise a saving before seeing the bill. The checklist finds the candidates; the numbers come from the invoice.</p>"""
page("guides/app-audit-checklist/index.html", "How to audit a Shopify app bill: ten checks",
     "A ten-step audit checklist for Shopify app bills, derived from verified billing rules.", audit_body, "../../")


# --- all-in-one vs single-purpose guide ---
aio_rows = [
 ("Vitals", "40+ bundled apps", "$29.99 at up to 200 orders", "$79 at 201–1,000 orders", "One bill, one vendor, shallower depth per feature"),
 ("Four single-purpose apps", "Klaviyo + Judge.me + Gorgias + Weglot", "$62 at entry tiers", "$62 until you outgrow a tier", "Deeper features, four bills, four renewals"),
]
aio_table = "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a,b,c,d,e in aio_rows)
aio_body = f"""<h1>All-in-one app vs four single-purpose apps: which costs less</h1>
<p class="lede">A bundle looks cheaper per feature and is not a replacement for deep tools. The honest comparison is total bill against total capability, at your order volume.</p>
<div class="verified">Prices checked {checked}: Vitals $29.99 (up to 200 orders) / $79 (201–1,000); Klaviyo Email from $20, Judge.me $15, Gorgias Starter $10, Weglot Starter $17. Entry tiers only — every line in the right column rises with volume or contacts.</div>
<table><thead><tr><th>Option</th><th>What you get</th><th>Entry volume</th><th>At 1,000 orders</th><th>Trade-off</th></tr></thead><tbody>{aio_table}</tbody></table>
<h2>The arithmetic</h2>
<ul>
<li>At under 200 orders a month, Vitals at $29.99 is less than half the $62 of four single-purpose entry plans. That is a real saving and the reason bundles sell.</li>
<li>At 201–1,000 orders the two lines are $79 against $62 — the bundle is now more expensive than the four apps, because the single-purpose entry tiers have not moved yet.</li>
<li>The bundle covers many jobs shallowly; email deliverability, helpdesk automation and translation quality are where single-purpose tools earn their extra cost. If a store leans on any one of those, the bundle is the expensive choice even when the invoice is smaller.</li>
<li>Compare like for like: price the bundle against the sum of the apps it actually replaces, not against one app, and price the single-purpose stack at the tiers your real volume puts you in.</li>
</ul>
<h2>What the bundle invoice does not show</h2>
<ul>
<li>Overlap: a store running Vitals may still buy a dedicated review app for photo reviews, so the "40+ apps" number overstates what replaces a subscription.</li>
<li>Exit cost: consolidating later means moving data out of five systems instead of one.</li>
<li>Growth: the bundle moves bands by orders, the stack moves by order, contacts, tickets and words — which one gets expensive first depends on where the store grows.</li>
</ul>"""
page("guides/all-in-one-vs-single-apps/index.html",
     "All-in-one Shopify app vs four single-purpose apps: cost comparison",
     "Vitals at $29.99 against a $62 four-app stack, computed at 200 and 1,000 monthly orders, with the caveats bundles hide.",
     aio_body, "../../")

app_count = len(apps)
app_names = ", ".join(a["name"] for a in apps.values())
body = f"""<h1>What Shopify apps actually cost</h1>
<p class="lede">Every plan, billing unit and overage rate, read from the vendor's own pricing page. Each figure carries the date we checked it.</p>
<div class="verified">{app_count} verified: {app_names}. Last checked {checked}.</div>
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
</ul>
<h2>Audit and reconcile</h2>
<ul>
<li><a href="guides/billing-reconciliation-report/">The bill reconciliation report</a> — invoice against published plan, line by line, with the unknowns kept as unknowns</li>
</ul>"""
page("index.html",
     "Shopify App Pricing Database — verified prices, checked and dated",
     "What Shopify apps actually cost: billing units, published tiers and overage rates, read from vendor pricing pages and stamped with a check date.",
     body, "")


# --- billing reconciliation report (template + computed worked example) ---
g_starter = 10 + max(0, 400 - 50) * 0.40
g_basic = 60 + max(0, 400 - 300) * 0.40
g_pro = 360.0
g_best = min(g_starter, g_basic, g_pro)
assert abs(g_starter - 150) < 1e-9 and abs(g_basic - 100) < 1e-9 and abs(g_best - 100) < 1e-9
confirmed = 50
candidate = 29
rec_rows = [
    ("Gorgias", "tickets, 400/mo", "Starter, $150", f"Basic, ${g_best:,.0f}", "+$50", "Right-size. Basic covers 400 tickets at $100; Starter only includes 50."),
    ("Vitals", "orders, 1,200/mo", "$179", "$179", "$0", "Keep. 1,001–5,000 band."),
    ("Judge.me", "flat fee", "$15", "$15", "$0", "Keep, unless the Fera line goes (see below)."),
    ("Fera", "orders, 1,200/mo", "$29", "$29", "$0", "Consolidate: two review apps bill every month. Feature test first."),
    ("Weglot", "translated words", "$17 (USD list)", "$17", "$0", "Keep. EU stores add VAT on top."),
    ("Klaviyo", "active profiles, 5,000", "$59", "not published — set in the vendor's calculator", "unknown", "Verify with Klaviyo: no price table to recompute from."),
    ("Postscript", "messages + minimum", "$62 usage, above the $49 floor", "$49 floor plus per-message rates we cannot re-add", "unknown", "Verify the message breakdown; do not treat $62 as either right or wrong."),
]
rec_tbl = "".join(
    f"<tr><td><strong>{a}</strong></td><td>{u}</td><td>{inv}</td><td>{exp}</td><td>{var}</td><td>{verdict}</td></tr>"
    for a, u, inv, exp, var, verdict in rec_rows)
rec_body = f"""<h1>Shopify app bill reconciliation: the report we run on a real invoice</h1>
<p class="lede">An invoice tells you what you paid. A reconciliation report tells you what the published plan says you should have paid, line by line, and where the two disagree.</p>
<div class="verified">Template built from the billing rules in our <a href="../billing-rules/">rules library</a>, checked {checked}. The worked example uses a fictional store: every "expected" figure is computed from vendor prices read on the dates shown on each app page, and every invoice figure is illustrative. No real invoice is reproduced here.</div>
<h2>What the report contains</h2>
<ol>
<li><b>Store profile</b> — the meters that set the tiers: orders per month, tickets per month, support seats, marketing contacts, SMS messages, translated words.</li>
<li><b>Invoice lines</b> — exported from Shopify (Settings → Billing), with subscription, usage and one-off charges kept separate. A list price is not evidence of what was paid.</li>
<li><b>Expected cost</b> — the cheapest published plan that covers the profile, computed from prices with a check date. Where the vendor sets the price in a calculator, the cell says "not published".</li>
<li><b>Variance</b> — invoice minus expected, per line and as a total.</li>
<li><b>Rule</b> — the billing rule that explains each gap: overage, minimum spend, seat count, VAT, annual discount.</li>
<li><b>Verdict</b> — keep, right-size, consolidate, or verify.</li>
<li><b>Saving</b> — monthly and annualised, with the assumption that has to hold.</li>
<li><b>Risk</b> — what changing it costs: data, theme code, integrations, features.</li>
</ol>
<h2>Worked example: a fictional store</h2>
<table><thead><tr><th>Input</th><th>Value</th></tr></thead><tbody>
<tr><td>Orders per month</td><td>1,200</td></tr>
<tr><td>Support tickets per month</td><td>400</td></tr>
<tr><td>Support seats</td><td>3</td></tr>
<tr><td>Klaviyo active profiles</td><td>5,000</td></tr>
<tr><td>SMS messages per month</td><td>6,000</td></tr>
<tr><td>Weglot plan</td><td>Starter, one language pair</td></tr>
</tbody></table>
<h2>The report itself</h2>
<table><thead><tr><th>App</th><th>Billing unit</th><th>Invoice (illustrative)</th><th>Expected from published plans</th><th>Variance</th><th>Verdict</th></tr></thead><tbody>
{rec_tbl}
</tbody></table>
<h2>What the example found</h2>
<ul>
<li><b>Confirmed: ${confirmed}/mo (${confirmed*12}/yr) on Gorgias.</b> Basic costs $60 + (400 − 300) × $0.40 = ${g_basic:,.0f}. The same 400 tickets on Starter is $10 + 350 × $0.40 = ${g_starter:,.0f}, and Pro is ${g_pro:,.0f}. Basic stays the cheapest plan below about 1,050 tickets, so the saving does not evaporate at the next month's volume.</li>
<li><b>Candidate: ${candidate}/mo (${candidate*12}/yr) by consolidating review apps.</b> At 1,200 orders Judge.me is $15 flat and Fera is $29; keeping one drops the other's fee. This is a candidate, not a finding: Fera includes AI review replies at every tier, so the $29 may be buying something Judge.me does not do. The feature test comes before the number.</li>
<li><b>Unverified: two lines stay open.</b> Klaviyo's $59 at 5,000 profiles cannot be recomputed, because Klaviyo sets that price in its own calculator and publishes no table. Postscript's $62 usage sits above its $49 floor, but its per-message rates are not published in a form we can re-add. Both cells say "unknown" instead of a number we cannot defend.</li>
</ul>
<h2>Why the "cannot verify" cells stay in</h2>
<ul>
<li>A report that turns an unknown into a number is worse than no report. Guessing the Klaviyo figure would make the whole table unfalsifiable, including the two lines that are solid.</li>
<li>Vendors that price in calculators (Klaviyo, Yotpo) cannot be reconciled from published data at all. The honest output is a specific question to the vendor: which tier is this account on, and what is the next band?</li>
<li>This is the difference between this report and asking an AI assistant to guess the bill: the assistant can produce a plausible number for every line. A reconciliation marks its own guesses.</li>
<li>The confirmed saving is small on purpose. Most real bills do not contain a dramatic error; they contain a plan that was right a year ago and a second app that does the same job.</li>
</ul>
<h2>Run it on your own bill</h2>
<p>Export the bill, fill the profile, and order the work with our <a href="../app-audit-checklist/">ten-check audit</a>. Every price behind the expected column, with its check date and source URL, is in the <a href="../../data/">open JSON feed</a>; the rules are in the <a href="../billing-rules/">rules library</a>.</p>
<p class="muted">Expected figures are ours to compute, but the inputs are the vendors' and the invoice is yours. If a vendor changes a price, the expected column is wrong until we re-check it.</p>"""
page("guides/billing-reconciliation-report/index.html",
     "Shopify app bill reconciliation report: template and worked example",
     "A line-by-line reconciliation of a Shopify app bill against published plans, with the template we use and a worked example computed from verified prices.",
     rec_body, "../../")



# --- guide: apps that charge a percentage ---
pct_body = f"""<h1>Apps that charge a percentage of your revenue, not a flat fee</h1>
<p class="lede">A $149 subscription is easy to budget. A subscription plus 1.5% plus $0.20 per transaction is not, because the bill grows every time you sell something.</p>
<div class="verified">Figures below come from the vendor pricing pages we read on the dates shown on each app page (latest check {checked}). The arithmetic is ours.</div>

<h2>Who charges a percentage or a per-transaction fee</h2>
<table><thead><tr><th>App</th><th>What it charges on top of the plan</th><th>Why the percentage matters</th></tr></thead><tbody>
<tr><td><a href="../apps/recharge/">Recharge</a></td><td>Starter: <strong>1.50% + $0.20 per transaction</strong> on top of $149/mo</td><td>The fee is a share of order value, so a strong month costs more than a quiet one on the exact same plan.</td></tr>
<tr><td><a href="../apps/gorgias/">Gorgias</a></td><td>$0.40 per ticket over the included volume; <strong>$0.90–$1.00 per AI interaction</strong></td><td>Support spikes (a launch, a Black Friday) land on the invoice as a second, unpredictable line.</td></tr>
<tr><td><a href="../apps/klaviyo/">Klaviyo</a></td><td>Plan jumps when active profiles grow; metered SMS</td><td>You do not pay per email, you pay for the size of the list — even if you barely send.</td></tr>
<tr><td><a href="../apps/vitals/">Vitals</a></td><td>Order-volume band only, no percentage</td><td>Included here as the contrast: the bill steps at fixed order thresholds and does not track revenue.</td></tr>
</tbody></table>

<h2>The worked example: 1,000 orders, $60 average order</h2>
<p>Same store, four apps, one month. Revenue $60,000.</p>
<table><thead><tr><th>App</th><th>Plan</th><th>Calculated monthly bill</th></tr></thead><tbody>
<tr><td>Recharge</td><td>Starter</td><td>$149 + (1.50% × $60,000 = $900) + (1,000 × $0.20 = $200) = <strong>$1,249</strong></td></tr>
<tr><td>Vitals</td><td>1,001–5,000 orders</td><td><strong>$179</strong></td></tr>
<tr><td>Judge.me</td><td>Awesome, flat</td><td><strong>$15</strong></td></tr>
<tr><td>Searchanise</td><td>Basic (up to 1,500 products)</td><td><strong>$19</strong></td></tr>
<tr><td colspan="2"><strong>Total</strong></td><td><strong>$1,462</strong></td></tr>
</tbody></table>
<p class="muted">$1,100 of that $1,462 (75%) is Recharge's percentage and per-transaction fee. The three apps with predictable bills together cost $213.</p>

<h2>How to tell whether you are exposed</h2>
<ol>
<li><strong>Read the fee line, not the plan price.</strong> If the pricing page mentions a percentage, a per-ticket charge, a per-message segment or a per-seat charge, the plan price is the smallest part.</li>
<li><strong>Multiply by your own numbers.</strong> Take your monthly order count and average order value, apply the published rate, and compare that number with the plan fee. If the metered part is bigger, you are not on a plan, you are on a meter.</li>
<li><strong>Check what resets the tier.</strong> Contacts, products, tickets and orders all move you up; none of them move you back down automatically when a busy season ends.</li>
<li><strong>Ask what happens at the boundary.</strong> A store at 5,001 orders can pay nearly double the rate of one at 5,000, for one extra order.</li>
</ol>

<h2>What we do not claim</h2>
<ul>
<li>We have not run these apps on a live store. Everything here is arithmetic on published prices.</li>
<li>Where a vendor does not publish a rate (Klaviyo's calculator, Recharge's Scale tier, Fera's band mapping), we say so instead of estimating.</li>
<li>Prices change. Each app page carries the date we last read the vendor's page.</li>
</ul>
"""
page("guides/apps-that-charge-a-percentage/index.html",
     "Shopify apps that charge a percentage of revenue (and what it costs at 1,000 orders)",
     "Recharge charges 1.50% + $0.20 per transaction on top of $149/mo; Gorgias charges per ticket and per AI interaction. A worked example at 1,000 orders.",
     pct_body, "../../")

# --- Klaviyo cost at volume: the vendor's own step ladder, read on 2026-11-27 ---
import json as _j
kv = _j.loads((root/"data/klaviyo-tiers.json").read_text())
steps = kv["steps"]

# the expensive steps: dollars paid per extra 1,000 profiles
jumps = []
for a, b in zip(steps, steps[1:]):
    dp = b["price"] - a["price"]
    dc = b["profiles"] - a["profiles"]
    if dp > 0 and dc > 0:
        jumps.append((dp / (dc / 1000), a["profiles"], b["profiles"], a["price"], b["price"], dc))
jumps.sort(reverse=True)
# group equal marginal rates so a run of identical steps reads as one finding
grouped = []
for marg, a, b, ap, bp, dc in jumps:
    key = round(marg, 2)
    if grouped and grouped[-1]["rate"] == key and grouped[-1]["to"] == a:
        grouped[-1]["to"] = b
        grouped[-1]["steps"] += 1
        grouped[-1]["price_end"] = bp
    else:
        grouped.append({"rate": key, "from": a, "to": b, "steps": 1,
                        "price_start": ap, "price_end": bp})
top_rates = []
seen_rates = set()
for g in grouped:
    if g["rate"] in seen_rates:
        continue
    seen_rates.add(g["rate"])
    top_rates.append(g)
    if len(top_rates) == 5:
        break
jump_rows = "\n".join(
    f"<tr><td>{g['from']:,} &rarr; {g['to']:,}</td><td>${g['price_start']}/mo &rarr; ${g['price_end']}/mo</td><td>{g['steps']} step{'s' if g['steps']>1 else ''}</td><td>${g['rate']:,.0f}</td></tr>"
    for g in top_rates)
worst = top_rates[0]
normal_rate = min(g["rate"] for g in grouped)
import statistics as _stats
_med = _stats.median([g["rate"] for g in grouped])
w_from, w_to = worst["from"], worst["to"]
w_pstart, w_pend, w_rate = worst["price_start"], worst["price_end"], worst["rate"]

ladder_rows = "\n".join(
    f"<tr><td>{st['profiles']:,}</td><td>${st['price']:,}/mo</td><td>{st['sends']:,}</td><td>${st['price']/ (st['profiles']/1000):.2f}</td></tr>"
    for st in steps)

faq = [
    ("How much does Klaviyo cost for 50,000 contacts?",
     "$%d per month on the Profiles + Email plan, which includes %s email sends that month. That is the step the pricing page shows for 50,000 active profiles."
     % (next(x['price'] for x in steps if x['profiles'] == 50000), format(next(x['sends'] for x in steps if x['profiles'] == 50000), ','))),
    ("How much does Klaviyo cost for 10,000 contacts?",
     "$%d per month, including %s sends. That is $%.2f per 1,000 profiles. The price per contact falls as the account grows: $%.2f per 1,000 at 500 profiles, $%.2f at 10,000, $%.2f at the top of the ladder."
     % (next(x['price'] for x in steps if x['profiles'] == 10000), format(next(x['sends'] for x in steps if x['profiles'] == 10000), ','),
        next(x['price'] for x in steps if x['profiles'] == 10000)/10,
        next(x['price'] for x in steps if x['profiles'] == 500)/0.5,
        next(x['price'] for x in steps if x['profiles'] == 10000)/10,
        steps[-1]['price']/(steps[-1]['profiles']/1000))),
    ("What happens if I go over my contact limit?",
     "You are moved up a tier: Klaviyo upgrades the plan at the end of the billing cycle to one that covers your active profile count, and it does not automatically move you back down. Flexible overages only add send capacity, not profile capacity."),
    ("Is the price per email sent, or per contact?",
     "Per active profile. Email send capacity is included in each step; you only pay overage if you send more than the step allows. Klaviyo counts a profile as active whether or not that person has subscribed."),
]
faq_html = "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in faq)
faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
faq_script = f'<script type="application/ld+json">{_j.dumps(faq_ld, ensure_ascii=False)}</script>'

kv_body = faq_script + f"""<h1>Klaviyo cost at 10,000 to 150,000 contacts: every step on the price list</h1>
<p class="lede">Klaviyo does not publish this as a table. The pricing page shows one step at a time behind a slider. We rendered the page and read the full ladder out of it, so you can see every step at once and find your row.</p>
<div class="verified">All 49 steps below were read from <a href="https://www.klaviyo.com/pricing" rel="nofollow noopener" target="_blank">klaviyo.com/pricing</a> on {checked}. Prices are US dollars, billed monthly, Profiles + Email plan. Klaviyo does not put these numbers in the page source; they are drawn on the page itself, so we render it in a browser engine and read the rendered result. Nothing below is estimated.</div>
<h2>The full ladder</h2>
<table><thead><tr><th>Active profiles</th><th>Monthly price</th><th>Email sends included</th><th>$ per 1,000 profiles</th></tr></thead><tbody>
{ladder_rows}
</tbody></table>
<h2>Where the ladder is expensive</h2>
<p>The median step costs ${_med:,.0f} per extra 1,000 active profiles, and the cheapest stretch is ${normal_rate:,.2f}. The steps below are the five most expensive rates on the whole ladder, calculated from the table above:</p>
<table><thead><tr><th>Steps</th><th>Price across them</th><th>How many</th><th>Extra $ per 1,000 profiles</th></tr></thead><tbody>
{jump_rows}
</tbody></table>
<p>The most expensive stretch is {w_from:,} &rarr; {w_to:,} active profiles: ${w_pstart}/mo &rarr; ${w_pend}/mo, which works out to ${w_rate:,.0f} for each additional 1,000 profiles, against a median of ${_med:,.0f} and a cheapest stretch of ${normal_rate:,.2f} across the ladder. If you are sitting just under a step like that when the billing cycle closes, clearing unengaged profiles before it ends is the one thing on this page you can act on today.</p>
<h2>What the price tag hides</h2>
<ul>
<li><strong>You are billed for contacts who can be emailed, subscribed or not.</strong> Klaviyo's own help page: "Any profile, regardless of consent status, that can be emailed through Klaviyo is considered an active profile."</li>
<li><strong>Over your contact limit, flexible overages do not help.</strong> The help page says a flex purchase "does not increase your active profile allowance" &mdash; only the send allowance. Contacts over the tier mean a forced upgrade.</li>
<li><strong>Upgrades stick.</strong> "You will not be auto-downgraded" applies unless you turn auto-downgrade on in Billing &gt; Preferences. A December contact spike can leave you on the higher tier in January.</li>
<li><strong>The free plan stops instead of upgrading.</strong> Over 250 active profiles on the free plan, sending stops until you drop back under or move to a paid plan.</li>
<li><strong>SMS is separate.</strong> Mobile messaging is priced by credits or dollar usage with a $5 monthly allowance; nothing in the table above includes it.</li>
</ul>
<h2>How to read your bill</h2>
<p>Find your active profile count at the end of the billing cycle, not the number of subscribers you think you have. That number picks the row. Then compare the sends included in your row with what you actually sent: if you are over, the overage is charged at your current tier's unit rate, which Klaviyo itself notes can cost more than moving up a tier.</p>
<p class="muted">Rules quoted above are from <a href="https://help.klaviyo.com/hc/en-us/articles/115000976672" rel="nofollow noopener" target="_blank">Klaviyo's billing help page</a>, read {checked}. Found a step that no longer matches the vendor page? Tell us and it goes in the <a href="{p}corrections/">corrections log</a>.</p>
<h2>Questions people ask</h2>
{faq_html}"""

page("guides/klaviyo-cost-at-volume/index.html",
     "Klaviyo cost at 10k to 150k contacts (%s) - full 49-step price ladder" % checked,
     "Every step of Klaviyo's Profiles + Email price ladder, from 500 to 150,000 active profiles, read from the vendor pricing page on %s, with the steps where the price jumps hardest." % checked,
     kv_body, "../../")

# --- Tidio: every conversation quota, AI vs human (read 2026-11-27) ---
td = _j.loads((root/"data/tidio-tiers.json").read_text())
td_human = {x["quota"]: x["cents"]/100 for x in td["humanConversations"]}
td_rows = []
for x in td["aiConversations"]:
    q = x["quota"]
    ai_m = x["cents"]/100
    hum_m = td_human.get(q, 0)
    mult = (ai_m/hum_m) if hum_m else 0
    td_rows.append(
        f"<tr><td>{q:,}</td><td>${ai_m:,.0f}</td><td>${ai_m*10/12:,.2f}</td>"
        f"<td>{('$0' if hum_m == 0 else '$%.0f' % hum_m)}</td>"
        f"<td>{(('-') if hum_m == 0 else '$%.2f' % (hum_m*10/12))}</td>"
        f"<td>{(('free plan') if hum_m == 0 else '%.1f&times;' % mult)}</td></tr>")
td_ladder = "\n".join(td_rows)

addon_names = {"flowsVisitors": ("Flows", "visitors reached"),
               "voiceConversations": ("Voice", "calls"),
               "inboxAi": ("Inbox AI", "conversations")}
addon_rows = []
for key, (label, unit) in addon_names.items():
    pts = td[key]
    addon_rows.append(
        f"<tr><td>{label}</td><td>{pts[0]['quota']:,} {unit} &mdash; ${pts[0]['cents']/100:,.0f}/mo</td>"
        f"<td>{pts[-1]['quota']:,} {unit} &mdash; ${pts[-1]['cents']/100:,.0f}/mo</td>"
        f"<td>{len(pts)} volume steps</td></tr>")
td_addons = "\n".join(addon_rows)

ai_50, ai_1000 = 39.0, 700.0
hum_100, hum_1000 = 29.0, 199.0

td_faq = [
    ("How much does Tidio cost for 1,000 conversations a month?",
     "$%d per month with Lyro AI, or $%d per month with human agents only, at monthly billing. Billed annually each is 10 months' worth: $%d and $%d a year."
     % (ai_1000, hum_1000, ai_1000*10, hum_1000*10)),
    ("Is the AI more expensive than human agents at Tidio?",
     "Yes, at the same conversation quota. At 100 conversations it is $%d a month with Lyro AI against $%d human only; at 1,000 conversations it is $%d against $%d. The gap widens as volume grows, because the AI price scales faster than the human price." % (75, hum_100, ai_1000, hum_1000)),
    ("Does Tidio count a conversation once per message?",
     "No. One conversation uses exactly one unit of the quota no matter how many messages are exchanged, and it only counts once your team or Lyro replies. A visitor who writes but is never answered does not use a conversation, and spam is excluded."),
    ("What happens if I go over my Tidio conversation limit?",
     "At checkout you can turn on automatic upgrades: at 95% of a limit the plan moves to the next tier and you pay that tier's price from then on. With it off, you raise the limit yourself. The limit renews monthly."),
    ("Do chat, email and Messenger share one Tidio quota?",
     "Yes. Live chat, email, Messenger, Instagram and WhatsApp all draw on the same conversation quota. The Voice add-on and Flows each have their own separate limit."),
]
td_faq_html = "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in td_faq)
td_faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in td_faq]}
td_faq_script = f'<script type="application/ld+json">{_j.dumps(td_faq_ld, ensure_ascii=False)}</script>'

td_body = td_faq_script + f"""<h1>Tidio cost at every conversation quota: AI versus human agents</h1>
<p class="lede">Tidio hides its prices behind a quota slider, one combination at a time. Here is the whole grid: seven quotas, both modes, monthly and annual billing, on one page.</p>
<div class="verified">Read from <a href="https://www.tidio.com/pricing/" rel="nofollow noopener" target="_blank">tidio.com/pricing</a> on {checked}. Monthly billing is the per-month price; the annual column is the same plan billed yearly, which Tidio prices at ten months (two months free). We checked these figures against the two prices the page shows without any clicking: 50 AI conversations displays $33/mo billed annually ($390/yr) and 100 displays $63/mo billed annually ($750/yr). Nothing below is estimated.</div>
<h2>The grid</h2>
<table><thead><tr><th>Conversations / month</th><th>With Lyro AI (monthly)</th><th>With Lyro AI (annual, per month)</th><th>Human only (monthly)</th><th>Human only (annual, per month)</th><th>AI costs</th></tr></thead><tbody>
{td_ladder}
</tbody></table>
<h2>The thing the slider hides</h2>
<p>At the same quota, the AI mode costs more than human agents, and the gap grows with volume: {hum_100 and 75/hum_100:.1f}&times; at 100 conversations, {ai_1000/hum_1000:.1f}&times; at 1,000. If you are buying Tidio for a small team that answers everything anyway, human-only at 1,000 conversations is ${hum_1000:.0f} a month against ${ai_1000:.0f}. The AI pays for itself only if it removes conversations your team would otherwise answer, not if your team answers them anyway.</p>
<p>The free plan is 50 human conversations a month. Those 50 are the only zero on the grid: the AI column starts at ${ai_50:.0f}.</p>
<h2>Add-ons have their own limits</h2>
<table><thead><tr><th>Add-on</th><th>Lowest volume</th><th>Highest volume</th><th>Steps published</th></tr></thead><tbody>
{td_addons}
</tbody></table>
<p>Flows and Voice are separate from the conversation quota and renew on their own date. Inbox AI is priced by the conversations in your plan and has no limit of its own.</p>
<h2>What counts as a conversation</h2>
<ul>
<li>One conversation is one unit, however many messages it contains.</li>
<li>It only counts once your team or Lyro replies. Unanswered visitors are free.</li>
<li>Live chat, email, Messenger, Instagram and WhatsApp share the same quota.</li>
<li>Auto-upgrade triggers at 95% of a limit and changes what you pay from then on.</li>
</ul>
<p class="muted">Source: <a href="https://www.tidio.com/pricing/" rel="nofollow noopener" target="_blank">Tidio's pricing page and its own pricing FAQ</a>, read {checked}. Found a quota that no longer matches? Tell us and it goes in the <a href="{p}corrections/">corrections log</a>.</p>
<h2>Questions people ask</h2>
{td_faq_html}"""

page("guides/tidio-cost-at-volume/index.html",
     "Tidio cost at every conversation quota (%s) - AI vs human agents" % checked,
     "The full Tidio price grid: 50 to 1,000 conversations a month, Lyro AI against human agents, monthly and annual billing, read from the vendor pricing page on %s." % checked,
     td_body, "../../")


# --- app cost calculator (formulas verified from vendor pages) ---
_td_data = _j.loads((root/"data/tidio-tiers.json").read_text())
calc_data = {
    "checked": checked,
    "klaviyo": [[x["profiles"], x["price"]] for x in steps],
    "tidioHuman": [[x["quota"], x["cents"] / 100] for x in _td_data["humanConversations"]],
    "tidioAi": [[x["quota"], x["cents"] / 100] for x in _td_data["aiConversations"]],
    "searchanise": [[0, 0], [1500, 19], [7500, 39], [15000, 89], [30000, 139], [50000, 209], [300000, 349]],
    "vitals": [[200, 29.99], [1000, 79], [5000, 179], [1000000000, 299]],
    "fera": [[200, 9], [2000, 29], [20000, 99], [50000, 199], [100000, 299]],
    "upsell": [[2000, 0], [1000000000, 299]],
    "gorgias": [[10, 50, 0.40], [60, 300, 0.40], [360, 2000, 0.36]],
    "helpScoutPerSeat": {"standard": 25, "plus": 45, "pro": 75},
    "recharge": {"base": 149, "pct": 0.015, "perTxn": 0.20},
    "judgeMe": 15,
    "loyaltyLion": {"base": 199, "includedOrders": 500},
}
calc_body = (root/"data/calculator-body.html").read_text()
calc_body = calc_body.replace("__DATA__", _j.dumps(calc_data)).replace("__CHECKED__", checked)
page("calculator/index.html",
     "Shopify app cost calculator (%s) - what your stack costs at your volume" % checked,
     "Enter orders, contacts, tickets and catalogue size: this adds up what eleven Shopify apps charge at that volume, from each vendor's published formula, and shows the next step boundary.",
     calc_body, "../../")


# --- Postscript: per-message rates vs plan fee (read 2026-11-28) ---
PS_CARRIER = 0.00435   # average US carrier fee per SMS, stated on the pricing page
def ps_cost(plan, n):
    if plan == 'Starter':
        return max(49.0, n * 0.009) + n * PS_CARRIER
    if plan == 'Growth':
        return 100.0 + n * 0.008 + n * PS_CARRIER
    return 500.0 + n * 0.007 + n * PS_CARRIER

ps_volumes = [1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000]
def money(x):
    return "${:,.0f}".format(x) if x >= 100 else "${:,.2f}".format(x)
def ps_cell(pl, best, cost):
    cls = ' class="best"' if pl == best else ''
    arrow = ' &larr;' if pl == best else ''
    return '<td' + cls + '>' + money(cost) + arrow + '</td>'

ps_rows = []
for n in ps_volumes:
    costs = {pl: ps_cost(pl, n) for pl in ('Starter', 'Growth', 'Professional')}
    best = min(costs, key=costs.get)
    cells = ''.join(ps_cell(pl, best, costs[pl]) for pl in ('Starter', 'Growth', 'Professional'))
    ps_rows.append('<tr><td>' + format(n, ',') + '</td>' + cells + '</tr>')
ps_table = "\n".join(ps_rows)

ps_faq = [
    ("How much does Postscript cost for 10,000 texts a month?",
     "About $133 with the Starter plan at 10,000 SMS: the $49 monthly minimum is exceeded, so it is 10,000 x $0.009 message rate plus 10,000 x $0.00435 average US carrier fee. The $100 Growth plan would cost about $223 at that volume, because its lower per-message rate only pays back above 100,000 messages a month."),
    ("When is Postscript Growth cheaper than Starter?",
     "At 100,000 SMS a month and above. Starter charges no plan fee but $0.009 per SMS; Growth charges $100 a month and $0.008 per SMS. The $100 fee is recovered only after 100,000 messages."),
    ("What is the Postscript monthly minimum spend?",
     "The Starter plan has a $49 monthly minimum spend. Below roughly 5,400 messages the message fees do not reach $49, so you pay $49 regardless. Carrier fees are charged on top."),
    ("Does Postscript charge carrier fees separately?",
     "Yes. The pricing page lists average US carrier fees of $0.00435 per SMS and $0.00832 per MMS, on top of the per-message platform rate."),
]
ps_faq_html = "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in ps_faq)
ps_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ps_faq]}
ps_script = f'<script type="application/ld+json">{_j.dumps(ps_ld, ensure_ascii=False)}</script>'

ps_body = ps_script + f"""<h1>Postscript cost at 1,000 to 500,000 texts a month</h1>
<p class="lede">Postscript has no message allowance: every text costs the same per-message rate plus a carrier fee, and the plan fee buys a lower rate. Here is which plan is actually cheapest at your volume.</p>
<div class="verified">Plan fees and per-message rates were read from <a href="https://www.postscript.io/pricing" rel="nofollow noopener" target="_blank">postscript.io/pricing</a> on {checked}. Carrier fee: the page states an average US rate of $0.00435 per SMS and $0.00832 per MMS, which we add on top. Assumption stated plainly: we treat the $49 Starter minimum as a floor on platform message fees, with carrier fees added after. If your invoice splits them differently the crossover points do not move, because carrier fees are identical on every plan.</div>
<h2>Cost by volume</h2>
<table><thead><tr><th>SMS per month</th><th>Starter</th><th>Growth</th><th>Professional</th></tr></thead><tbody>
{ps_table}
</tbody></table>
<p>Arrow marks the cheapest of the three. The rates are $0.009 / $0.008 / $0.007 per SMS on Starter / Growth / Professional.</p>
<h2>Where the plans actually cross</h2>
<ul>
<li><strong>Starter to Growth: 100,000 texts a month.</strong> Growth costs $100 more per month but saves $0.001 per message. $100 / $0.001 = 100,000 messages before the lower rate repays the fee.</li>
<li><strong>Growth to Professional: 400,000 texts a month.</strong> $400 more per month at $0.001 saved per message.</li>
<li><strong>Below ~5,400 texts the Starter minimum is dead money.</strong> 5,400 x $0.009 is $48.60, so anything under that pays the $49 floor anyway. At 1,000 texts the real cost is $53: the floor plus carrier fees, not $9.</li>
</ul>
<p>This is the opposite of most SaaS pricing, where the bigger plan is cheaper from a low volume. Here the entry plan has no fee at all, so it stays cheapest for a long way up, and the discounts only start to matter at six-figure sending.</p>
<h2>What the per-message rate hides</h2>
<ul>
<li>Carrier fees are on top of the advertised rate and are quoted as an average, so your bill varies by destination and message type.</li>
<li>MMS costs five times SMS on Starter ($0.045 against $0.009), and media RCS is $0.0087 in carrier fees alone.</li>
<li>RCS is an add-on on the Enterprise plan, not a different rate you can pick from the table.</li>
</ul>
<p class="muted">Sources: <a href="https://www.postscript.io/pricing" rel="nofollow noopener" target="_blank">postscript.io/pricing</a>, read {checked}. Found a rate that no longer matches? Tell us and it goes in the <a href="{p}corrections/">corrections log</a>.</p>
<h2>Questions people ask</h2>
{ps_faq_html}"""

page("guides/postscript-cost-at-volume/index.html",
     "Postscript cost at 1,000 to 500,000 texts a month (%s)" % checked,
     "Which Postscript plan is cheapest at your SMS volume, calculated from its per-message rates and carrier fees, with the exact crossover points: Growth only wins above 100,000 texts a month.",
     ps_body, "../../")

# --- Weglot: word tiers are a lifetime cap (read 2026-11-28) ---
wg = [("Free", 0, 0, 2000, 1, 5), ("Starter", 17, 170, 10000, 1, 5),
      ("Business", 32, 320, 50000, 3, 5), ("Pro", 87, 870, 200000, 5, 10),
      ("Advanced", 329, 3290, 1000000, 10, 25), ("Extended", 769, 7690, 5000000, 20, 50)]
wg_rows = "\n".join(
    f"<tr><td>{name}</td><td>{('$0' if m == 0 else '$%d' % m)}</td><td>{('-' if y == 0 else '$%s' % format(y, ','))}</td>"
    f"<td>{w:,}</td><td>{('-' if m == 0 else '$%.2f' % (m / (w / 1000)))}</td><td>{langs}</td><td>{seats}</td></tr>"
    for name, m, y, w, langs, seats in wg)
wg_body = f"""<h1>Weglot cost by number of words, and why the word count never renews</h1>
<p class="lede">Weglot's plans are not monthly allowances. Each plan includes a total number of unique words, and that limit is fixed for the life of the plan: it does not reset next month. That single fact changes how you should size the plan.</p>
<div class="verified">All six tiers were read from <a href="https://www.weglot.com/pricing" rel="nofollow noopener" target="_blank">weglot.com/pricing</a> on {checked}, in US dollars (the page also quotes euros). The word limits are the vendor's own wording: "Total unique words translated across all your languages. This is a fixed limit and does not renew."</div>
<h2>The ladder</h2>
<table><thead><tr><th>Plan</th><th>USD / month</th><th>USD / year</th><th>Total words</th><th>$ per 1,000 words</th><th>Languages</th><th>Team seats</th></tr></thead><tbody>
{wg_rows}
</tbody></table>
<h2>The trap in a lifetime word count</h2>
<p>Every other tier is priced against a monthly meter. Weglot's meter never resets, which means the plan you buy is really a ceiling on how much site you can ever translate before paying again:</p>
<ul>
<li><strong>Starter (10,000 words, $17)</strong> suits a brochure site that will not change. A store that adds 5,000 words a year exhausts it in two years.</li>
<li><strong>Business (50,000 words, $32)</strong> is the real entry point for a working catalogue, because product pages and collection pages both count.</li>
<li><strong>The price per 1,000 words falls hard</strong>: $1.70 on Starter, $0.64 on Business, $0.44 on Pro, $0.33 on Advanced, $0.15 on Extended. Buying a tier above your need is often cheaper per word than upgrading later, but only if you actually use the words.</li>
<li><strong>Languages are bundled, not free</strong>: 1 on Starter, 3 on Business, 5 on Pro, 10 on Advanced, 20 on Extended. If you need five languages, you cannot stay on Business however few words you have.</li>
</ul>
<h2>How to size it</h2>
<p>Count the unique words on the pages you intend to translate, add what you expect to publish over the next two years, then pick the first tier that covers that number and the language count you need. Because the limit does not renew, undersizing costs a full plan upgrade, not a top-up.</p>
<p class="muted">Sources: <a href="https://www.weglot.com/pricing" rel="nofollow noopener" target="_blank">weglot.com/pricing</a>, read {checked}. Annual prices are the vendor's own yearly figures, not a computed discount. Spotted a tier change? Tell us and it goes in the <a href="{p}corrections/">corrections log</a>.</p>"""

page("guides/weglot-cost-by-words/index.html",
     "Weglot cost by number of words: the ladder, and why the limit never renews (%s)" % checked,
     "All six Weglot tiers with total word limits, languages and seats, read from the vendor page on %s, plus the reason a lifetime word cap changes how you size the plan." % checked,
     wg_body, "../../")


# --- Searchanise: product-tier ladder (read 2026-11-27) ---
san = [(0, 0, 0), (1500, 19, 16), (7500, 39, 33), (15000, 89, 74), (30000, 139, 116), (50000, 209, 174), (300000, 349, 291)]
san_rows = []
prev = None
for cap, monthly, annual in san:
    if cap == 0:
        san_rows.append('<tr><td>Free</td><td>$0</td><td>$0</td><td>development stores</td><td>-</td><td>-</td></tr>')
        continue
    per_k = monthly / (cap / 1000)
    disc = (1 - annual / monthly) * 100
    marg = '-'
    if prev:
        pc, pm, _pa = prev
        marg = '$%.2f' % ((monthly - pm) / ((cap - pc) / 1000))
    san_rows.append(
        '<tr><td>up to ' + format(cap, ',') + '</td><td>$' + str(monthly) + '</td><td>$' + str(annual) +
        '</td><td>$%.2f' % per_k + '</td><td>' + '%.1f%%' % disc + '</td><td>' + marg + '</td></tr>')
    prev = (cap, monthly, annual)
san_table = "\n".join(san_rows)

san_faq = [
    ("How much does Searchanise cost for 7,500 products?",
     "$39 per month billed monthly, or $33 if billed annually. That is the Essential tier, which covers up to 7,500 products."),
    ("Is Searchanise cheaper by the year?",
     "Yes. Annual billing is roughly 16-17% below monthly on every paid tier: Basic $16 against $19, Essential $33 against $39, Advanced $74 against $89, Growth $116 against $139, Pro $174 against $209, Premium $291 against $349."),
    ("Which Searchanise step is the worst value?",
     "Moving from 7,500 to 15,000 products. It adds $50 a month for 7,500 more products, about $6.67 per 1,000 more products, while the step below adds products at $3.33 per 1,000 and the step above at $3.33 as well."),
    ("Does Searchanise charge by products or by searches?",
     "By the number of active products in the catalogue, not by searches or traffic."),
]
san_faq_html = "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in san_faq)
san_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in san_faq]}
san_script = f'<script type="application/ld+json">{_j.dumps(san_ld, ensure_ascii=False)}</script>'

san_body = san_script + f"""<h1>Searchanise cost by catalogue size: six tiers, and the one step that costs too much</h1>
<p class="lede">Searchanise prices on the number of active products, not on traffic or searches. Here is every tier, both billing modes, and the cost per 1,000 products so you can see which step is worth taking.</p>
<div class="verified">All six paid tiers were read from <a href="https://searchanise.io/pricing/" rel="nofollow noopener" target="_blank">searchanise.io/pricing</a> on {checked}. Monthly and annual figures are the vendor's own two prices, not a computed discount. The per-1,000 and marginal columns are our arithmetic from those figures.</div>
<h2>The ladder</h2>
<table><thead><tr><th>Products</th><th>Monthly billing</th><th>Annual billing (per month)</th><th>$ per 1,000 products</th><th>Annual discount</th><th>Marginal $ per extra 1,000</th></tr></thead><tbody>
{san_table}
</tbody></table>
<h2>The step that is out of line</h2>
<p>Pricing ladders usually get cheaper per unit as you climb. This one has a bump in the middle:</p>
<ul>
<li>Basic to Essential (1,500 to 7,500 products) costs $20 more for 6,000 more products, about <strong>$3.33</strong> per 1,000. That is the best step on the ladder.</li>
<li>Essential to Advanced (7,500 to 15,000) costs $50 more for 7,500 more products, about <strong>$6.67</strong> per 1,000. That is double the step below it, and the worst on the ladder.</li>
<li>Above that the curve settles again: $3.33 per 1,000 to 30,000, $3.50 to 50,000, and then $0.56 per 1,000 all the way to 300,000.</li>
</ul>
<p>Practical consequence: if you are on Essential and about to cross 7,500 products, either stay under it by trimming inactive products, or jump straight past Advanced if you expect growth, because the Advanced step buys the next 7,500 at the worst rate in the table.</p>
<h2>Annual billing, plainly</h2>
<p>Every paid tier gives the same discount for paying yearly: between 15.4% and 16.9%, which is two months free. There is no tier where annual is a worse deal, so the only question is cash flow.</p>
<p class="muted">Sources: <a href="https://searchanise.io/pricing/" rel="nofollow noopener" target="_blank">searchanise.io/pricing</a>, read {checked}. Found a tier change? Tell us and it goes in the <a href="{p}corrections/">corrections log</a>.</p>
<h2>Questions people ask</h2>
{san_faq_html}"""

page("guides/searchanise-cost-by-products/index.html",
     "Searchanise cost by number of products: all six tiers (%s)" % checked,
     "Every Searchanise tier from 1,500 to 300,000 products, monthly and annual prices, cost per 1,000 products, and the one step in the middle that costs double the step below it.",
     san_body, "../../")


# --- closing the books: app billing cycles (question taken from the merchant forum) ---
bk_body = """<h1>Why a Shopify month never closes cleanly: the app billing cycle problem</h1>
<p class="lede">Books close on calendar months. Shopify app charges do not. Every app runs its own recurring cycle from the day you installed it, so a month-end invoice contains charges from several different cycles, and some usage charges land after the month is closed.</p>
<div class="verified">The mechanics below are taken from the vendors' own billing documentation, read on __DATE__. Nothing here is inferred from our own invoices.</div>
<h2>Four things that do not line up with your month</h2>
<ol>
<li><strong>Each app has its own 30-day cycle.</strong> A subscription created on the 12th renews on the 12th, not on your Shopify plan's anniversary and not at month end. Ten apps means ten different dates.</li>
<li><strong>Volume-priced apps bill at the step your account is on when the cycle closes.</strong> Klaviyo is the clearest case: 10,000 active profiles is $150/mo, 10,500 is $175/mo. A contact spike in the last week of the cycle changes what the cycle costs, and the invoice arrives after you thought the month was done.</li>
<li><strong>Usage charges post separately from the plan fee.</strong> Apps that charge a percentage or a per-transaction fee (Recharge: $149/mo plus 1.50% plus 20c per transaction) add those amounts as usage, on their own schedule.</li>
<li><strong>Some quotas reset every 30 days, not monthly.</strong> Tidio states its limits renew "every 30 days for Shopify-billed accounts", which drifts against a calendar month over the year.</li>
</ol>
<h2>What to do instead of forcing a calendar month</h2>
<ul>
<li><strong>Close on the billing period, then accrue.</strong> Book the Shopify invoice you have, and carry an accrual line for cycles that started but have not closed. That is what keeps the P&amp;L stable month to month.</li>
<li><strong>Track the meter, not the invoice.</strong> The number that predicts next month's charge is the size of the account at cycle end (active profiles, orders in the cycle, tickets, products), not last month's invoice.</li>
<li><strong>Keep a fixed list of cycle dates.</strong> One line per app: install date, renewal date, what the price depends on. It turns a surprise into a scheduled item.</li>
<li><strong>Reconcile by app, not by total.</strong> A total that matches your bank feed can still be two apps wrong in opposite directions.</li>
</ul>
<h2>Where the money actually goes</h2>
<p>Three worked examples from vendor price lists, so the accrual is not abstract:</p>
<ul>
<li>A store at 10,000 contacts pays Klaviyo <strong>$150</strong> for the cycle; at 10,500 it pays <strong>$175</strong>. Crossing the boundary mid-cycle is a 16.7% increase that shows up a month later.</li>
<li>At 1,000 orders and a $60 average order, Recharge charges <strong>$1,249</strong> in one cycle: $149 plan, $900 in percentage fees, $200 in per-transaction fees. Roughly three quarters of a typical app bill can sit in one line like this.</li>
<li>A store at 400 support tickets pays Gorgias <strong>$100</strong> on its Basic tier (300 tickets included, $0.40 per ticket after), not the $10 starter headline.</li>
</ul>
<p class="muted">Sources: vendor billing documentation and pricing pages, read __DATE__. The Klaviyo mechanics are from its billing help page; the 30-day renewal wording is Tidio's own pricing FAQ. Found something that no longer matches? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>.</p>"""
bk_body = bk_body.replace("__DATE__", checked).replace("__P__", "../../")
page("guides/why-shopify-months-dont-close/index.html",
     "Why your Shopify app bill never matches the calendar month (%s)" % checked,
     "Every app runs its own 30-day billing cycle from install day, so month-end never reconciles: the mechanics, the accrual to use instead, and three worked examples from vendor price lists.",
     bk_body, "../../")


# --- "I uninstalled it and still got charged" (question mined from the merchant forum) ---
u_body = """<h1>You uninstalled the app and still got charged. Shopify's own rules explain why</h1>
<p class="lede">Three different mechanisms produce the same surprise, and only one of them is a mistake. Here is what Shopify's own billing documentation says, in its own words.</p>
<div class="verified">The quotes below are from <a href="https://help.shopify.com/en/manual/your-account/manage-billing/billing-charges/types-of-charges/third-party-charges/app-charges" rel="nofollow noopener" target="_blank">Shopify's help page on app charges</a>, read on __DATE__. The arithmetic examples use vendor pricing pages we checked the same day.</div>
<h2>1. A charge that already exists keeps existing</h2>
<p>Shopify's exact wording:</p>
<blockquote>Uninstalling the app stops future billing cycles, but a pending charge that has already been generated might still be displayed on the next invoice. To request a refund, contact the app developer.</blockquote>
<p>So there are two different states, and they behave differently:</p>
<ul>
<li><strong>Pending charge</strong> &mdash; listed under "View current charges", not yet invoiced. Uninstalling stops future cycles, but this one can still appear on the next invoice. Refund: ask the app developer, not Shopify.</li>
<li><strong>Paid charge</strong> &mdash; already invoiced. The app is gone, the money is not. Refund: the developer again.</li>
</ul>
<h2>2. Your app has its own 30-day cycle, separate from your Shopify billing cycle</h2>
<blockquote>You're billed for your app subscriptions and app usage as part of Shopify's 30-day subscription billing period. However, your app has a separate 30-day billing cycle, which impacts the charges that are displayed on your Shopify bill.</blockquote>
<p>In practice: install an app on the 12th, and its cycle closes on the 12th. Uninstall it on the 8th of the following month and the cycle that ran from the 12th to the 8th still bills &mdash; you used the app for most of that period. This is why "I cancelled it on the 1st" and "it was charged on the 3rd" can both be true.</p>
<h2>3. External charges never show up on your Shopify bill at all</h2>
<blockquote>Some third-party apps charge you directly outside of Shopify. These external charges aren't displayed on your Shopify bill. If you uninstall an app that charges externally, then you also need to cancel the subscription or payment directly with the app developer.</blockquote>
<p>This is the one that causes real damage, because there is no bill to remind you. Uninstalling removes the app from your store and cancels nothing with the vendor.</p>
<h2>What the charge actually is, in three real examples</h2>
<ul>
<li><strong>Usage-based:</strong> Recharge bills $149/mo plus 1.50% plus 20c per transaction. At 1,000 orders and a $60 average order, one cycle is about $1,249 &mdash; a number big enough that a refund request is worth writing.</li>
<li><strong>Tier-based:</strong> Klaviyo bills on active profiles at cycle end (10,000 profiles $150/mo, 10,500 $175/mo). Uninstalling mid-cycle does not change the count that has already been recorded for that cycle.</li>
<li><strong>Flat:</strong> Judge.me is $15/mo flat. A mistaken cycle here costs $15, which is why nobody disputes it &mdash; and why the same mistake on a usage app costs a hundred times more.</li>
</ul>
<h2>What to do, in order</h2>
<ol>
<li>In the Shopify admin, open <strong>Settings &gt; Apps</strong> and look at current charges. Decide whether the charge is pending or paid &mdash; the remedy differs.</li>
<li>Email the app developer, not Shopify, with the install date, uninstall date and the charge amount. Refunds for app charges are the developer's decision and Shopify's own documentation points you there.</li>
<li>For any app that bills outside Shopify, cancel with the vendor explicitly and keep the cancellation email. That is the only record that will exist.</li>
<li>Before reinstalling to "test" something, check the trial terms &mdash; a reinstall can start a new paid cycle immediately if the trial was already used.</li>
</ol>
<p class="muted">Sources: Shopify's app charges help page, read __DATE__; vendor pricing pages for the arithmetic. Found a rule that has changed? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>.</p>"""
u_body = u_body.replace("__DATE__", checked).replace("__P__", "../../")
page("guides/uninstalled-app-still-charged/index.html",
     "Uninstalled the app and still got charged? Shopify's own rules explain it (%s)" % checked,
     "Three separate mechanisms behind one surprise: a pending charge that already exists, the app's own 30-day cycle, and external charges that never appear on your Shopify bill, quoted from Shopify's documentation.",
     u_body, "../../")


# --- Recharge: plan fee + percentage + per transaction (read 2026-11-28) ---
def rc_cost(orders, aov):
    return 149.0 + 0.015 * orders * aov + 0.20 * orders

rc_rows = []
for o in (100, 500, 1000, 2500, 5000):
    gmv = o * 60
    c = rc_cost(o, 60)
    rc_rows.append(f"<tr><td>{o:,}</td><td>${gmv:,}</td><td>${c:,.0f}</td>"
                   f"<td>${c - 149 - 0.20 * o:,.0f}</td><td>${0.20 * o:,.0f}</td>"
                   f"<td>{c / gmv * 100:.2f}%</td></tr>")
rc_table = "\n".join(rc_rows)

rc_body = """<h1>Recharge cost at 100 to 5,000 orders a month: the percentage, not the plan fee</h1>
<p class="lede">Recharge's headline is $149/mo. The part that actually sets your bill is 1.50% of the transaction value plus 20 cents per order. Here is what the two together cost at real volumes.</p>
<div class="verified">Read from <a href="https://rechargepayments.com/pricing" rel="nofollow noopener" target="_blank">rechargepayments.com/pricing</a> on __DATE__: Starter "$149/mo", with "Processing fees at: 1.50% + 20¢ per transaction". The table is our arithmetic from those three published numbers, at a $60 average order value. Recharge also sells a Scale plan at $499/mo but its pricing page does not quote processing rates for it, so we do not guess them.</div>
<h2>What it costs, at a $60 average order</h2>
<table><thead><tr><th>Orders / month</th><th>Revenue</th><th>Recharge total</th><th>of which the 1.50%</th><th>of which 20¢/order</th><th>Effective % of revenue</th></tr></thead><tbody>
__ROWS__
</tbody></table>
<h2>The number that matters is the last column</h2>
<p>The plan fee is fixed, so it dominates at small volume and disappears at large volume:</p>
<ul>
<li>At <strong>100 orders</strong> you pay $259, which is <strong>4.32%</strong> of revenue. The $149 plan fee alone is more than the percentage.</li>
<li>At <strong>1,000 orders</strong> it is $1,249, or <strong>2.08%</strong> of revenue.</li>
<li>At <strong>5,000 orders</strong> it is $5,649, or <strong>1.88%</strong> &mdash; and it never falls below about 1.83%, which is 1.50% plus the 20 cents expressed against a $60 order.</li>
</ul>
<p>So "Recharge costs $149" is true only for a store with almost no subscriptions. A store doing 1,000 subscription orders a month pays roughly <strong>eight times</strong> the headline, and the floor of the model is the percentage, not the fee.</p>
<h2>When the $499 plan makes sense</h2>
<p>Scale is $499/mo, which is $350 more than Starter. If its processing rate were the same, it would never pay back. Recharge does not publish Scale's rates, so the honest answer is: ask them for the rate before assuming the bigger plan is cheaper, and compare against the table above rather than against the plan fee.</p>
<h2>What this means for a stack</h2>
<p>Because the fee scales with revenue, a subscription app is usually the single largest line in a Shopify app bill. In our calculator's default scenario (1,000 orders, $60 average order, plus Klaviyo, Tidio, Gorgias and Judge.me) the stack came to $1,623 a month, and Recharge was $1,249 of it &mdash; 77%.</p>
<p class="muted">Sources: <a href="https://rechargepayments.com/pricing" rel="nofollow noopener" target="_blank">rechargepayments.com/pricing</a>, read __DATE__. Found a rate change? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>. Try your own numbers in the <a href="__P__calculator/">cost calculator</a>.</p>"""
rc_body = rc_body.replace("__ROWS__", rc_table).replace("__DATE__", checked).replace("__P__", "../../")
page("guides/recharge-cost-at-volume/index.html",
     "Recharge cost at 100 to 5,000 orders a month, calculated (%s)" % checked,
     "Recharge is $149/mo plus 1.50% plus 20c per order: what that comes to at 100 to 5,000 subscription orders, and why the effective rate is 4.3% of revenue at low volume.",
     rc_body, "../../")


# --- Yotpo Reviews: order-volume tiers (verified by render, 2026-11-28) ---
yotpo_starter = [(0,50,15),(51,100,24),(101,250,59),(251,500,89),(501,1000,129)]
yotpo_pro = [(0,250,119),(251,500,169),(501,1000,269),(1001,2000,299),(2001,3000,329),(3001,5000,379),(5001,5999,429)]

def band(a, b):
    return f"{a}&ndash;{b}" if b else f"{a}+"

ys_rows = "\n".join(
    f"<tr><td>Starter</td><td>{band(a,b)}</td><td>${pr}</td></tr>" for a,b,pr in yotpo_starter)
ys_rows += '<tr><td>Starter</td><td>1,001+</td><td class="muted">not available on Starter</td></tr>'
yp_rows = "\n".join(
    f"<tr><td>Pro</td><td>{band(a,b)}</td><td>${pr}</td></tr>" for a,b,pr in yotpo_pro)
yp_rows += '<tr><td>Pro</td><td>6,000+</td><td class="muted">moves to Premium, custom quote</td></tr>'

yotpo_body = """<h1>Yotpo Reviews cost by order volume: the 1,001-order cliff</h1>
<p class="lede">Yotpo prices reviews on monthly order volume. The price table is not on the page as a table; it is embedded in the page as data and drawn by a slider. We rendered the page and read every band, so you can see what a single order over a boundary actually costs.</p>
<div class="verified">All 12 published bands below were read from the rendered <a href="https://www.yotpo.com/pricing/" rel="nofollow noopener" target="_blank">yotpo.com/pricing</a> page on __DATE__, from the pricing data the page itself ships. The Starter band 501&ndash;1,000 is marked $129; the band above it is marked disabled, which is what forces the jump. Premium and Enterprise are custom quotes and we do not guess them. The bands below are monthly-billing prices; annual billing exists and saves 20% on Starter and 25% on Pro.</div>
<h2>The two plans that carry published prices</h2>
<p>Two things the pricing-page slider does not show you: Yotpo also has a <strong>free plan</strong> (the App Store listing says "Free plan available"), and it offers <strong>annual billing that saves 20% on Starter and 25% on Pro</strong> (the App Store listing quotes the discount by region, so it does not display one fixed USD figure). The bands below are the monthly-billing prices from the pricing page's own data.</p>
<table><thead><tr><th>Plan</th><th>Orders / month</th><th>Monthly price</th></tr></thead><tbody>
__STARTER__
__PRO__
</tbody></table>
<h2>The 1,000-order boundary, correctly stated</h2>
<ul>
<li>At <strong>1,000 orders</strong> the cheapest published plan is Starter at <strong>$129</strong>.</li>
<li>At <strong>1,001 orders</strong> the pricing slider marks Starter as unavailable. The next published plan is Pro at <strong>$299</strong> &mdash; a $170 step, 132% more, or $2,040 a year if it lasts all year.</li>
</ul>
<p><strong>But that is not the only way out, and most articles miss this.</strong> Yotpo runs an option called <strong>Reviews Booster</strong> on both Starter and Pro. Its own documentation describes it plainly:</p>
<blockquote>If you enable Reviews Booster and then exceed your monthly order limit, we'll charge your monthly subscription fee plus the number of additional orders you used. &hellip; You can cap your additional orders to make sure you stay in control of your spending, and you won't be charged for any additional orders you don't use.</blockquote>
<p>So a store at 1,001 orders has three routes, not one: stay under the line, enable Booster and pay per extra order, or move up to Pro. The per-order rate for Booster is not published on the pricing page &mdash; the documentation says it "will vary according to your Yotpo plan" &mdash; so the $170 step is the cost of <em>upgrading</em>, not a charge that is forced on you.</p>
<p>One trap worth knowing: the same documentation warns that extra orders only cover requests made <em>after</em> you enable Booster. Orders that already passed the limit before you turned it on do not get request emails.</p>
<p>For scale: 1,001 orders and 2,000 orders both cost $299 on Pro. So a store that just crossed the line pays the same as one doing nearly double the volume &mdash; unless it uses Booster instead.</p>
<h2>Why the table is not on the page</h2>
<p>Yotpo shows one price at a time through a volume slider, and the bands exist only as data behind it. That is why most articles quote "from $15" &mdash; true for a store with 50 orders, meaningless for anyone deciding whether they can afford reviews at 1,500 orders. We publish the bands because the decision is made at a boundary, not at the entry price.</p>
<h2>How to read your own number</h2>
<ol>
<li>Find your monthly order count, not your yearly one. Yotpo charges on the monthly figure.</li>
<li>Locate the band. Up to 1,000 orders Starter is available; above that the slider marks it unavailable, so your choice is Booster (pay per extra order, cap set by you) or Pro.</li>
<li>If you are within about 50 orders of 1,000 and your volume is seasonal, keeping a month under the line can avoid the $170 step &mdash; but this only works if the cycle that bills you is the quiet month, because Yotpo charges on the order volume in the billing period. And check whether the review features you actually use exist on Starter at all: this page compares prices, not feature sets.</li>
</ol>
<p class="muted">Sources: <a href="https://www.yotpo.com/pricing/" rel="nofollow noopener" target="_blank">yotpo.com/pricing</a>, rendered and read __DATE__. Yotpo's own FAQ says pricing "scales with your store's monthly order volume". Found a band that has changed? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>.</p>"""
yotpo_body = (yotpo_body.replace("__STARTER__", ys_rows).replace("__PRO__", yp_rows)
              .replace("__DATE__", checked).replace("__P__", "../../"))
page("guides/yotpo-cost-by-orders/index.html",
     "Yotpo Reviews cost by order volume: every published band (%s)" % checked,
     "Yotpo prices reviews by monthly order volume, and the price table is hidden behind a slider: here are all 12 published bands, and the 1,001-order boundary where one more order costs $170 more a month.",
     yotpo_body, "../../")


# --- LoyaltyLion: linear order ladder (verified by render, 2026-11-28) ---
ll = [(500,199),(1000,249),(1500,299),(2000,349),(2500,399),(3000,449),(3500,499),(4000,549)]
ll_rows = "\n".join(
    f"<tr><td>{o:,}</td><td>${p}</td><td>${p / o * 1000:,.2f}</td><td>${50 if o > 500 else 0}</td></tr>"
    for o, p in ll)
ll_rows += '<tr><td>4,500+</td><td class="muted">custom quote</td><td class="muted">-</td><td class="muted">-</td></tr>'

ll_body = """<h1>LoyaltyLion cost by order volume: $199 floor, then $50 per 500 orders</h1>
<p class="lede">LoyaltyLion's Classic plan is a straight line: $199 a month covering 500 orders, then $50 for every additional 500 orders up to 4,000. Above that it becomes a quote. Because the ladder is linear, the cost per order falls the whole way up, and a small store pays a lot per order.</p>
<div class="verified">The eight price points were read from the price table embedded in <a href="https://loyaltylion.com/pricing" rel="nofollow noopener" target="_blank">loyaltylion.com/pricing</a> on __DATE__ (the page's own selector data: PRICES = 500:$199, 1000:$249, 1500:$299, 2000:$349, 2500:$399, 3000:$449, 3500:$499, 4000:$549). The page's order selector offers bands above 4,000 but publishes no price for them; the code sets those to "Custom", so we do not guess. Advanced and Plus are quote-only.</div>
<h2>The ladder</h2>
<table><thead><tr><th>Orders covered / month</th><th>Monthly price</th><th>Per 1,000 orders</th><th>Step increase</th></tr></thead><tbody>
__ROWS__
</tbody></table>
<h2>What the shape tells you</h2>
<ul>
<li><strong>The $199 is a floor, not a price for small stores.</strong> A store doing 200 orders a month pays the same $199 as one doing 500. At 500 orders that is $398 per 1,000 orders ($0.40 an order); at 100 orders the same $199 works out to $1,990 per 1,000 orders, because the plan does not scale down.</li>
<li><strong>Every 500 orders costs exactly $50 more.</strong> That is $0.10 per order in the marginal range, and it is the same at 1,000 orders as at 4,000. There is no volume discount inside the ladder &mdash; only the fixed $199 gets diluted.</li>
<li><strong>Per-1,000 cost falls from $398 to $137</strong> between the first and last published band. That is the whole benefit of growing on this plan.</li>
<li><strong>The ceiling is a quote, not a price.</strong> At 4,500 orders the page switches to "Custom". If you are near that line, ask before you plan a budget around it.</li>
</ul>
<h2>How this compares to being quoted</h2>
<p>Because the ladder is linear and predictable, LoyaltyLion is one of the few apps where you can budget a year ahead without a quote: pick your band, add 8% if you expect growth of about 800 orders a month. The moment you cross 4,000, that predictability ends &mdash; which is worth knowing before you build a loyalty programme around the platform.</p>
<p class="muted">Sources: <a href="https://loyaltylion.com/pricing" rel="nofollow noopener" target="_blank">loyaltylion.com/pricing</a>, rendered and read __DATE__. Per-1,000 and step figures are our arithmetic from the eight published points. Found a band change? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>.</p>"""
ll_body = ll_body.replace("__ROWS__", ll_rows).replace("__DATE__", checked).replace("__P__", "../../")
page("guides/loyaltylion-cost-by-orders/index.html",
     "LoyaltyLion cost by order volume: the full published ladder (%s)" % checked,
     "LoyaltyLion Classic is $199 for 500 orders then $50 per additional 500, up to $549 at 4,000 orders: every published band, the per-1,000 cost, and why the $199 is a floor rather than a small-store price.",
     ll_body, "../../")


# --- Support stack comparison: Gorgias vs Tidio vs Help Scout (verified 2026-11-28) ---
def gorgias_best(t):
    best = None
    for price, incl, over in ((10, 50, 0.40), (60, 300, 0.40), (360, 2000, 0.36)):
        c = price + max(0, t - incl) * over
        if best is None or c < best:
            best = c
    return best

def tidio_human(t):
    grid = [(50, 0), (100, 29), (200, 49), (300, 69), (500, 109), (750, 159), (1000, 199)]
    for q, price in grid:
        if t <= q:
            return price
    return None  # above 1,000 conversations is a quote

sup_rows = []
for t in (100, 300, 500, 1000, 2000):
    g = gorgias_best(t)
    ti = tidio_human(t)
    hs = 2 * 25  # 2 seats on Standard
    vals = {"Gorgias": g, "Tidio (human only)": ti, "Help Scout (2 seats)": hs}
    cheapest = min((v for v in vals.values() if v is not None))
    def cell(name):
        v = vals[name]
        if v is None:
            return '<td class="muted">quote</td>'
        mark = ' &larr;' if v == cheapest else ''
        return f'<td>${v:,.0f}{mark}</td>'
    sup_rows.append(f"<tr><td>{t:,}</td>{cell('Gorgias')}{cell('Tidio (human only)')}{cell('Help Scout (2 seats)')}<td class=\"muted\">{g / 25:.1f} seats to match Gorgias</td></tr>")
sup_table = "\n".join(sup_rows)

sup_body = """<h1>Gorgias vs Tidio vs Help Scout: the same support volume, three pricing models</h1>
<p class="lede">These three are not priced on the same unit, so the comparison most articles make &mdash; entry price against entry price &mdash; is meaningless. Gorgias bills per ticket with overage, Tidio bills per conversation quota, Help Scout bills per seat regardless of volume. Here is what each costs at the volume you actually have.</p>
<div class="verified">All figures read from the vendors' own pricing pages on __DATE__: Gorgias Starter $10 (50 tickets, $0.40 overage), Basic $60 (300, $0.40), Pro $360 (2,000, $0.36); Tidio human-only quota $29 at 100 conversations, $69 at 300, $109 at 500, $199 at 1,000, quote above that; Help Scout Standard $25 per seat per month. We assume 2 agents on Help Scout and monthly billing everywhere. Gorgias AI interactions cost extra ($0.90&ndash;$1.00 each) and also count against ticket volume.</div>
<h2>Cost at the same ticket volume</h2>
<table><thead><tr><th>Tickets / month</th><th>Gorgias</th><th>Tidio (human only)</th><th>Help Scout (2 seats)</th><th>Help Scout seats to match Gorgias</th></tr></thead><tbody>
__ROWS__
</tbody></table>
<h2>The three models, plainly</h2>
<ul>
<li><strong>Gorgias charges for volume.</strong> $10&ndash;$360 for the plan plus overage, so a busy month is a bigger bill. AI replies cost $0.90&ndash;$1.00 each on top and also consume ticket volume &mdash; they count twice.</li>
<li><strong>Tidio charges for a quota of conversations.</strong> A conversation is one unit however long it runs, and it only counts once someone replies. Above 1,000 conversations a month the page stops publishing a price.</li>
<li><strong>Help Scout charges for people, not tickets.</strong> Two agents on Standard is $50 whether you handle 100 tickets or 2,000. That is why it looks expensive at low volume and unbeatable at high volume with a small team.</li>
</ul>
<h2>What that means for the decision</h2>
<p>The last column is the useful one. At 1,000 tickets a month Gorgias costs about $340, which is the same as Help Scout with <strong>about 13.6 Standard seats</strong>. So:</p>
<ul>
<li><strong>Small team, high volume:</strong> Help Scout wins on price, by a lot. A three-agent store doing 1,000 tickets pays $75 there against $340 on Gorgias.</li>
<li><strong>Big team, low volume:</strong> the seat model gets expensive fast &mdash; ten agents on Help Scout is $250 before add-ons (extra inboxes $10 each, extra docs sites $20 each).</li>
<li><strong>Chat-first rather than ticket-first:</strong> Tidio's quota is the cheapest of the three up to about 300 conversations and stays competitive to 1,000, but its ceiling is the 1,000-conversation quota.</li>
</ul>
<p class="muted">Sources: gorgias.com/pricing, tidio.com/pricing, helpscout.com/pricing, all read __DATE__. Annual billing changes each of these figures (Gorgias Basic is $50/yr, Help Scout is about 16% off annually, Tidio's annual price is ten months). Found a plan change? Tell us and it goes in the <a href="__P__corrections/">corrections log</a>.</p>"""
sup_body = (sup_body.replace("__ROWS__", sup_table).replace("__DATE__", checked).replace("__P__", "../../"))
page("guides/support-app-comparison/index.html",
     "Gorgias vs Tidio vs Help Scout: cost at the same ticket volume (%s)" % checked,
     "Three support apps, three pricing units: what Gorgias, Tidio and Help Scout cost at 100 to 2,000 tickets a month, plus how many Help Scout seats it takes to match a Gorgias bill.",
     sup_body, "../../")

# --- sitemap ---
base = BASE
urls = [("", "1.0"), ("pricing-index/", "0.9"), ("changelog.html", "0.5"),
        ("methodology.html", "0.5"), ("about.html", "0.4"),
        ("guides/gorgias-cost-at-volume/", "0.8"), ("compare/gorgias-vs-help-scout/", "0.8"), ("guides/how-shopify-apps-bill/", "0.8"), ("compare/judge-me-vs-fera/", "0.8"), ("changes/", "0.8"), ("guides/hidden-app-fees/", "0.8"), ("corrections/", "0.5"), ("data/", "0.6"), ("guides/review-app-cost/", "0.8"), ("guides/vitals-cost-at-volume/", "0.8"), ("guides/fera-cost-at-volume/", "0.8"), ("guides/help-scout-cost-by-seats/", "0.8"), ("guides/starter-stack-cost/", "0.8"), ("guides/billing-rules/", "0.9"), ("guides/apps-that-rise-with-growth/", "0.8"), ("guides/app-audit-checklist/", "0.9"), ("guides/billing-reconciliation-report/", "0.9"), ("guides/all-in-one-vs-single-apps/", "0.8"), ("guides/apps-that-charge-a-percentage/", "0.9"), ("guides/klaviyo-cost-at-volume/", "0.9"), ("guides/tidio-cost-at-volume/", "0.9"), ("calculator/", "1.0"), ("guides/postscript-cost-at-volume/", "0.9"), ("guides/weglot-cost-by-words/", "0.9"), ("guides/searchanise-cost-by-products/", "0.9"), ("guides/why-shopify-months-dont-close/", "0.9"), ("guides/uninstalled-app-still-charged/", "0.9"), ("guides/recharge-cost-at-volume/", "0.9"), ("guides/yotpo-cost-by-orders/", "0.9"), ("guides/loyaltylion-cost-by-orders/", "0.9"), ("guides/support-app-comparison/", "0.9")]
for slug in apps:
    urls.append((f"apps/{slug}/", "0.8"))
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pri in urls:
    sm.append(f"  <url><loc>{base}/{u}</loc><lastmod>{checked}</lastmod><priority>{pri}</priority></url>")
sm.append("</urlset>")
(root/"sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
(root/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
print("sitemap written:", len(urls), "urls")
