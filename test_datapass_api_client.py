from datapass_api_client import DataPassApiClient
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def client():
    client_id = os.getenv("DATAPASS_CLIENT_ID")
    client_secret = os.getenv("DATAPASS_CLIENT_SECRET")
    return DataPassApiClient(client_id=client_id, client_secret=client_secret)

def test_list_events_of_demande_63961(client):
    demande_id = 63961
    events = client.get_events_of_a_demande(demande_id)
    assert events == [
    {
        'created_at': '2025-06-19T19:36:36.298+02:00',
        'id': 166215,
        'name': 'submit',
    },
    {
        'created_at': '2024-10-15T12:19:52.856+02:00',
        'id': 135605,
        'name': 'request_changes',
    },
    {
        'created_at': '2024-10-09T09:37:43.493+02:00',
        'id': 135480,
        'name': 'submit',
    },
    {
        'created_at': '2024-10-09T09:37:39.521+02:00',
        'id': 135479,
        'name': 'create',
    },
]