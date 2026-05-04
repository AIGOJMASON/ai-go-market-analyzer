from fastapi.responses import HTMLResponse

def get_contractor_project_board_ui():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Project Board</title>
    <script src="/static/contractor_dashboard_transform.js"></script>
</head>
<body>
    <h1>Project Board</h1>

    <button onclick="loadProjects()">Load Projects</button>

    <pre id="projects"></pre>

    <script>
        async function loadProjects() {
            const res = await fetch('/contractor/projects');
            const data = await res.json();
            document.getElementById('projects').textContent =
                JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
""")