from flask import Flask, render_template_string
import json
from collections import Counter

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini‑SIEM Dashboard</title>
    <style>
        body { font-family: Arial; background: #0f172a; color: #e5e7eb; }
        h1 { color: #38bdf8; }
        table { border-collapse: collapse; width: 50%; }
        th, td { border: 1px solid #334155; padding: 8px; }
        th { background: #1e293b; }
    </style>
</head>
<body>
<h1>🚨 Mini‑SIEM Dashboard</h1>

<h2>Top Attacking IPs</h2>
<table>
<tr><th>IP</th><th>Attempts</th></tr>
{% for ip, count in ips %}
<tr><td>{{ ip }}</td><td>{{ count }}</td></tr>
{% endfor %}
</table>

<h2>Top Targeted Users</h2>
<table>
<tr><th>User</th><th>Attempts</th></tr>
{% for user, count in users %}
<tr><td>{{ user }}</td><td>{{ count }}</td></tr>
{% endfor %}
</table>

</body>
</html>
"""

@app.route("/")
def dashboard():
    ip_counter = Counter()
    user_counter = Counter()

    try:
        with open("/var/log/mini_siem.json") as f:
            for line in f:
                event = json.loads(line)
                ip_counter[event["ip"]] += 1
                user_counter[event["user"]] += 1
    except FileNotFoundError:
        pass

    return render_template_string(
        HTML,
        ips=ip_counter.most_common(10),
        users=user_counter.most_common(10)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)