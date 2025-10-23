def fetch_data(symbol: str, fn: str) -> dict:
    params = {
        "function": fn,
        "symbol": symbol,
        "apikey": API_KEY,
        "datatype": "json",
        "outputsize": "full",
    }
    r = requests.get(API_URL, params=params, timeout=30)
    if r.status_code != 200:
        print(f"Error fetching data: {r.status_code}")
        sys.exit(1)
    data = r.json()
    if "Error Message" in data:
        print(f"API Error: {data['Error Message']}")
        sys.exit(1)
    if "Note" in data:
        print("API Note: Rate limit exceeded. Please wait and try again later.")
        sys.exit(1)
    return data

def parse_close_series(data:dict, fn:str):
    key = series_key_for(fn)
    if key not in data:
        print(f"Unexpected API response: missing key {key}")
        sys.exit(1)
    rows = []
    for k, v in data[key].items():
        ts = datetime.strptime(k, "%Y-%m-%d")
        close_str = v.get("4. close", None)
        if close_str is None:
            continue
        try:
            close_val = float(close_str)
            rows.append((ts, close_val))
        except ValueError:
            continue
    rows.sort(key=lambda x: x[0])
    return rows

def filter_range(rows, start_d: date, end_d: date):
    return [(ts, c) for (ts, c) in rows if start_d <= ts.date() <= end_d]

def thin_labels(labels, max_labels=12):
    n = len(labels)
    if n <= max_labels:
        return labels
    step = max(1, n // max_labels)
    return [lbl if (i % step == 0 or i == n - 1) else None for i, lbl in enumerate(labels)]

def make_chart(symbol: str, ts_label: str, chart_type: str, rows):
    title = f"{symbol} Stock Prices ({ts_label})"
    x_labels = [d.strftime("%Y-%m-%d") for (d, _c) in rows]
    closes = [c for (_d, c) in rows]

    if chart_type == "line":
        chart = pygal.Line(show_minor_x_labels=False, x_label_rotation=20, show_legend=False)
    else:
        chart = pygal.Bar(show_minor_x_labels=False, x_label_rotation=20, show_legend=False)

    chart.title = title
    chart.x_labels = x_labels
    chart.x_labels_major = [lbl for lbl in thin_labels(x_labels)]
    chart.y_title = "Closing Price (USD)"
    chart.add("Close", closes)
    return chart.render(is_unicode=True)

def wrap_html(svg_text: str, page_title: str) -> str:
    html = etree.Element("html")
    head = etree.SubElement(html, "head")
    etree.SubElement(head, "meta", charset="UTF-8")
    title_el = etree.SubElement(head, "title")
    title_el.text = page_title
    style = etree.SubElement(head, "style")
    style.text = "body {font-family: Arial,Helvetica,sans-serif; margin: 24px;} .chart{max-width: 1000px;}"
    body = etree.SubElement(html, "body")
    h1 = etree.SubElement(body, "h1")
    h1.text = page_title
    chart_div = etree.SubElement(body, "div", attrib={"class": "chart"})

    try:
        svg_el = etree.fromstring(svg_text.encode("utf-8"))
        chart_div.append(svg_el)
    except Exception as e:
        pre = etree.SubElement(chart_div, "pre")
        pre.text = f"(SVG embed error: {e})\n\n{svg_text}"

        return etree.tostring(html, pretty_print=True, encoding="unicode")
    
    def save_and_open(html_text: str, symbol: str):
        fname = f"{symbol}_chart.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html_text)
        webbrowser.open(f"file://" + os.path.abspath(fname))