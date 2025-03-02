# Dustbin Monitoring System

## Overview
This project is a smart dustbin monitoring system that tracks waste levels in dustbins across Mumbai using a Flask API, a Streamlit dashboard, and a data simulation script. The system allows for real-time monitoring and visualization of dustbin fill levels, enabling efficient waste management.

## Components
The project consists of three main components:

1. **Flask API (`app.py`)**
   - Provides RESTful API endpoints to receive and store dustbin data.
   - Uses an SQLite database to store dustbin details.
   - Endpoints:
     - `POST /update_dustbin_data`: Receives data from dustbins and updates the database.
     - `GET /get_dustbin_data`: Fetches all stored dustbin data.

2. **Streamlit Dashboard (`dashboard.py`)**
   - Visualizes dustbin data on an interactive dashboard.
   - Displays a map of dustbin locations and their fill levels.
   - Provides pie charts showing waste composition.
   - Alerts users when dustbins are near full capacity.

3. **Data Simulation Script (`data_simulator.py`)**
   - Simulates real-time dustbin data by generating random fill levels.
   - Sends periodic updates to the Flask API.
   - Resets bins when they reach full capacity.

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed along with the required dependencies:

```sh
pip install flask flask-sqlalchemy flask-dotenv streamlit requests pydeck plotly pandas
```

## Usage

### 1. Run the Flask API
```sh
python app.py
```
By default, the API runs on `http://127.0.0.1:5000/`.

### 2. Start the Streamlit Dashboard
```sh
streamlit run dashboard.py
```

### 3. Run the Data Simulator
```sh
python data_simulator.py
```
This will generate and send dustbin data to the API continuously.

## API Endpoints
- **`POST /update_dustbin_data`**
  - Request JSON Format:
    ```json
    {
      "code": "DB001",
      "latitude": 19.076,
      "longitude": 72.8777,
      "address": "Location 1, Mumbai",
      "recyclable_bio": 20.5,
      "recyclable_nonbio": 30.2,
      "nonrecyclable_bio": 10.5,
      "nonrecyclable_nonbio": 25.8,
      "overall_fill_percentage": 60.5,
      "timestamp": "2025-03-01 12:00:00"
    }
    ```

- **`GET /get_dustbin_data`**
  - Returns all stored dustbin data in JSON format.

## Features
- 📌 **Real-time data monitoring**
- 🗺 **Interactive map visualization**
- 📊 **Pie charts for waste type distribution**
- 🚨 **Alerts for bins nearing full capacity**
- 🔄 **Automatic data updates from the simulator**

## Future Improvements
- Implement user authentication.
- Add predictive analysis for waste collection schedules.
- Integrate with IoT-based smart sensors.

## License
This project is open-source and available under the MIT License.

