from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/now/table/incident", methods=["GET", "POST"])
def handle_incidents():
    if request.method == "POST":
        data = request.get_json()
        # Simulate creating a new ticket
        new_ticket = {
            "number": "INC001007", # Hardcoded for simplicity
            "short_description": data.get("short_description"),
            "assignment_group": data.get("assignment_group"),
            "priority": data.get("priority"),
            "state": "New",
            "sys_updated_on": "2025-10-12 00:00:00", # Current timestamp
        }
        return jsonify({"result": new_ticket}), 201
    else: # GET request
        if request.args.get("sysparm_display_value") == "true":
            return jsonify({
                "result": [
                    {
                        "id": 1,
                        "number": "INC001001",
                        "short_description": "Printer not working",
                        "assignment_group": "IT Support",
                        "priority": "1 - Critical",
                        "state": "New",
                        "sys_updated_on": "2025-10-11 09:00:00",
                    },
                    {
                        "id": 2,
                        "number": "INC001002",
                        "short_description": "Laptop screen broken",
                        "assignment_group": "Hardware Support",
                        "priority": "2 - High",
                        "state": "In Progress",
                        "sys_updated_on": "2025-10-11 10:30:00",
                    },
                    {
                        "id": 3,
                        "number": "INC001003",
                        "short_description": "Software installation failed",
                        "assignment_group": "Software Support",
                        "priority": "3 - Moderate",
                        "state": "Resolved",
                        "sys_updated_on": "2025-10-11 11:45:00",
                    },
                    {
                        "id": 4,
                        "number": "INC001004",
                        "short_description": "Network connectivity issue",
                        "assignment_group": "Network Team",
                        "priority": "1 - Critical",
                        "state": "New",
                        "sys_updated_on": "2025-10-11 12:00:00",
                    },
                    {
                        "id": 5,
                        "number": "INC001005",
                        "short_description": "Email not syncing",
                        "assignment_group": "IT Support",
                        "priority": "2 - High",
                        "state": "In Progress",
                        "sys_updated_on": "2025-10-11 13:15:00",
                    },
                    {
                        "id": 6,
                        "number": "INC001006",
                        "short_description": "Password reset request",
                        "assignment_group": "IT Support",
                        "priority": "4 - Low",
                        "state": "Resolved",
                        "sys_updated_on": "2025-10-11 14:00:00",
                    }
                ]
            })
        else:
            return jsonify({"result": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)