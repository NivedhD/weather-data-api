# 🌤️ Weather Data API

A Flask REST API serving historical temperature data for 100 European weather stations.

## Features
- 5 REST API endpoints
- Celsius and Fahrenheit support
- Interactive web UI with live API tester
- Search stations by name
- Historical data from 1960s onwards

## Installation
```bash
git clone https://github.com/yourusername/weather-data-api
cd weather-data-api
pip install -r requirements.txt
python main.py
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/<station>/<date>` | Temperature for a specific station and date |
| `GET /api/v1/<station>` | All historical data for a station |
| `GET /api/v1/yearly/<station>/<year>` | All data for a station in a specific year |
| `GET /api/v1/range/<station>/<start>/<end>` | Data between two dates |
| `GET /api/v1/stations?name=<query>` | Search stations by name |

## Usage Example
```bash
# Get temperature for station 10 on 1988-10-25
GET /api/v1/10/1988-10-25

# Response
{
  "station_id": "10",
  "station_name": "STOCKHOLM",
  "date": "1988-10-25",
  "temperature": -0.9,
  "unit": "celsius",
  "status": "success"
}
```

## Tech Stack
- Python
- Flask
- Pandas

## Data Source
European Climate Assessment & Dataset (ECA&D)
