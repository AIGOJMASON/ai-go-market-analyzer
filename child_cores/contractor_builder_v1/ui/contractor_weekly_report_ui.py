from fastapi.responses import HTMLResponse

def get_contractor_weekly_report_ui():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Weekly Report</title>
    <script src="/static/contractor_weekly_report_transform.js"></script>
</head>
<body>
    <h1>Weekly Report</h1>

    <button onclick="loadReport()">Load Report</button>

    <pre id="report"></pre>

    <script>
        async function loadReport() {
            const res = await fetch('/contractor/report/latest');
            const data = await res.json();
            const transformed = transformWeeklyReport(data);
            document.getElementById('report').textContent =
                JSON.stringify(transformed, null, 2);
        }
    </script>
</body>
</html>
""")