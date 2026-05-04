from fastapi.responses import HTMLResponse

def get_contractor_portfolio_board_ui():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Board</title>
    <script src="/static/contractor_portfolio_transform.js"></script>
</head>
<body>
    <h1>Portfolio Board</h1>

    <button onclick="loadPortfolio()">Load Portfolio</button>

    <pre id="portfolio"></pre>

    <script>
        async function loadPortfolio() {
            const res = await fetch('/contractor/portfolio');
            const data = await res.json();
            const transformed = transformPortfolio(data);
            document.getElementById('portfolio').textContent =
                JSON.stringify(transformed, null, 2);
        }
    </script>
</body>
</html>
""")