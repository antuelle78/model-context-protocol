from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/glpi/apirest.php/initSession", methods=["GET", "POST"])
def init_session():
    print(f"Headers: {request.headers}")
    # Simulate a successful session initialization
    return jsonify({"session_token": "mock_glpi_session_token"})

@app.route("/glpi/apirest.php/search/<itemtype>", methods=["GET"])
def search_items(itemtype):
    computers = [
        {
            "id": 1,
            "name": "Laptop-001",
            "serial": "SN-LAP-001",
            "type": "laptop",
            "operatingsystems": [
                {"name": "Windows 10", "version": "20H2"}
            ]
        },
        {
            "id": 2,
            "name": "Desktop-001",
            "serial": "SN-DESK-001",
            "type": "desktop",
            "operatingsystems": [
                {"name": "Windows 10", "version": "21H1"}
            ]
        },
        {
            "id": 3,
            "name": "Laptop-002",
            "serial": "SN-LAP-002",
            "type": "laptop",
            "operatingsystems": [
                {"name": "macOS", "version": "Big Sur"}
            ]
        },
        {
            "id": 4,
            "name": "Desktop-002",
            "serial": "SN-DESK-002",
            "type": "desktop",
            "operatingsystems": [
                {"name": "Ubuntu", "version": "20.04 LTS"}
            ]
        },
    ]

    monitors = [
        {
            "id": 101,
            "name": "Monitor-A",
            "serial": "SN-MON-101",
            "type": "LCD",
        },
        {
            "id": 102,
            "name": "Monitor-B",
            "serial": "SN-MON-102",
            "type": "LED",
        },
        {
            "id": 103,
            "name": "Monitor-C",
            "serial": "SN-MON-103",
            "type": "LCD",
        },
    ]

    if itemtype.lower() == "computer":
        # Simulate filtering by criteria
        if request.args.get("criteria[0][field]") == "type" and \
           request.args.get("criteria[0][searchtype]") == "contains":
            search_value = request.args.get("criteria[0][value]").lower()
            computers = [c for c in computers if search_value in c["type"].lower()]
        return jsonify({"data": computers})
    elif itemtype.lower() == "monitor":
        return jsonify({"data": monitors})
    elif itemtype.lower() == "allassets":
        return jsonify({"data": computers + monitors})
    else:
        return jsonify({"data": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)