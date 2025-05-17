from palantir.datasets.webhooks import WebhookClient
from palantir.datasets.core import Dataset
import pandas as pd
import json
from typing import Dict, Any, Optional

@function(sources=["EpicFHIRPatientID"])  # Make sure this matches your webhook name
def fetch_appointment_data(patientId: str, access_token: str) -> Dataset:
    """
    Fetches appointment data from Epic FHIR API using the configured webhook.
    
    Args:
        patientId: Epic patient ID to fetch appointments for
        access_token: Valid OAuth access token for Epic API
        
    Returns:
        Dataset containing the appointment data
    """
    # Initialize the webhook client
    client = WebhookClient()
    
    # Call the webhook with the required inputs
    response = client.call_webhook(
        "EpicFHIRPatientID",  # Make sure this matches your webhook name
        inputs={
            "patientId": patientId,
            "access_token": access_token
        }
    )
    
    # Check if the call was successful
    if not response.is_success():
        raise Exception(f"Webhook call failed: {response.error_message()}")
    
    # Parse the JSON response
    raw_data = response.raw_response
    appointments_json = json.loads(raw_data)
    
    # Extract appointment resources from the bundle
    appointment_resources = []
    if "entry" in appointments_json:
        for entry in appointments_json["entry"]:
            if "resource" in entry and entry["resource"]["resourceType"] == "Appointment":
                appointment_resources.append(entry["resource"])
    
    # Transform into a more usable format (flatten nested structures)
    appointments_flat = []
    for appt in appointment_resources:
        flat_appt = {
            "id": appt.get("id", ""),
            "status": appt.get("status", ""),
            "start": appt.get("start", ""),
            "end": appt.get("end", ""),
            "minutesDuration": appt.get("minutesDuration", 0),
            "patientInstructions": appt.get("patientInstruction", "")
        }
        
        # Extract service type if available
        if "serviceType" in appt and len(appt["serviceType"]) > 0:
            if "coding" in appt["serviceType"][0] and len(appt["serviceType"][0]["coding"]) > 0:
                flat_appt["serviceTypeCode"] = appt["serviceType"][0]["coding"][0].get("code", "")
                flat_appt["serviceTypeDisplay"] = appt["serviceType"][0]["coding"][0].get("display", "")
        
        # Extract participants
        patient_info = ""
        provider_info = ""
        location_info = ""
        
        if "participant" in appt:
            for participant in appt["participant"]:
                if "actor" in participant:
                    ref = participant["actor"].get("reference", "")
                    display = participant["actor"].get("display", "")
                    
                    if ref.startswith("Patient/"):
                        patient_info = display
                    elif ref.startswith("Practitioner/"):
                        provider_info = display
                    elif ref.startswith("Location/"):
                        location_info = display
        
        flat_appt["patient"] = patient_info
        flat_appt["provider"] = provider_info
        flat_appt["location"] = location_info
        
        appointments_flat.append(flat_appt)
    
    # Convert to DataFrame
    df = pd.DataFrame(appointments_flat)
    
    # Write to dataset and return
    return Dataset.write(df, path="/Datasets/FHIR_Raw/Appointment")


# Function to get an appointment by ID
@function(sources=["EpicFHIRPatientID"])
def get_appointment_by_id(appointment_id: str, access_token: str) -> Dict[str, Any]:
    """
    Gets a specific appointment by ID
    
    Args:
        appointment_id: The Epic appointment ID
        access_token: Valid OAuth access token for Epic API
        
    Returns:
        Dictionary containing the appointment details
    """
    client = WebhookClient()
    
    # This assumes you have a webhook endpoint for a single appointment
    # You may need to modify your webhook configuration
    response = client.call_webhook(
        "EpicFHIRPatientID",
        inputs={
            "appointmentId": appointment_id,
            "access_token": access_token
        }
    )
    
    if not response.is_success():
        raise Exception(f"Webhook call failed: {response.error_message()}")
    
    appointment_data = response.json()
    return appointment_data 