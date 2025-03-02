import requests
import time
from datetime import datetime
import random

# Generate 200 dustbins with random locations within Mumbai's latitude & longitude range
dustbins = [
    {
        "code": f"DB{str(i).zfill(3)}",
        "latitude": round(random.uniform(18.9, 19.3), 6),
        "longitude": round(random.uniform(72.75, 73.0), 6),
        "address": f"Location {i}, Mumbai"
    }
    for i in range(1, 201)
]

API_URL = "http://127.0.0.1:5000/update_dustbin_data"

# Initialize a dictionary to store individual bin fill levels
# Start with 0-10% random fill
fill_levels = {bin["code"]: random.uniform(0, 10) for bin in dustbins}

# Function to simulate and send data gradually


def send_data_to_server():
    while True:
        for dustbin in dustbins:
            bin_code = dustbin["code"]

            # Simulate fill levels for each compartment with gradual increments
            recyclable_bio = min(
                100, fill_levels[bin_code] + random.uniform(0, 5))
            recyclable_nonbio = min(
                100, fill_levels[bin_code] + random.uniform(0, 5))
            nonrecyclable_bio = min(
                100, fill_levels[bin_code] + random.uniform(0, 5))
            nonrecyclable_nonbio = min(
                100, fill_levels[bin_code] + random.uniform(0, 5))

            # Calculate overall fill percentage as the average of all compartments
            overall_fill_percentage = (
                recyclable_bio + recyclable_nonbio + nonrecyclable_bio + nonrecyclable_nonbio
            ) / 4

            # Prepare data to send
            data = {
                "code": bin_code,
                "latitude": dustbin["latitude"],
                "longitude": dustbin["longitude"],
                "address": dustbin["address"],
                "recyclable_bio": round(recyclable_bio, 2),
                "recyclable_nonbio": round(recyclable_nonbio, 2),
                "nonrecyclable_bio": round(nonrecyclable_bio, 2),
                "nonrecyclable_nonbio": round(nonrecyclable_nonbio, 2),
                "overall_fill_percentage": round(overall_fill_percentage, 2),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            try:
                response = requests.post(API_URL, json=data)
                if response.status_code in [200, 201]:
                    print(f"✅ Sent data for {
                          bin_code} - Overall Fill: {data['overall_fill_percentage']}%")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection Error: {e}")

            # Update the bin's fill level for next iteration
            fill_levels[bin_code] = overall_fill_percentage

        # Simulate bin emptying when it reaches 100%
        if all(level >= 100 for level in fill_levels.values()):
            print("🗑️ All bins are full! Emptying bins...")
            time.sleep(5)  # Simulate delay for emptying
            # Reset with a random low value
            fill_levels.update(
                {bin["code"]: random.uniform(0, 10) for bin in dustbins})

        time.sleep(5)  # Wait 5 seconds before sending the next batch of data


# Call the function to start sending data
send_data_to_server()
