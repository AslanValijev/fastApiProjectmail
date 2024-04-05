import requests

def test_get_email_by_id():
    response = requests.get("http://127.0.0.1:8000/emails/<id>")
    data = response.json()

    # Ensure that there are at least 4 elements
    assert len(data) >= 4

    # Extract email details
    reciev_date = data[1]
    sender_email = data[2]
    recipient_email = data[7]
    subject = data[3]

    print(f"Recieving date: {reciev_date}")
    print(f"Sender Email: {sender_email}")
    print(f"Recipient Email: {recipient_email}")
    print(f"Subject: {subject}")



test_get_email_by_id()
