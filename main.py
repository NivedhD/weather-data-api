from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

stations = pd.read_csv("stations/stations.txt", skiprows=17)
stations.columns = stations.columns.str.strip()
stations = stations[["STAID", "STANAME"]]
stations = stations[stations["STAID"] <= 100]


def get_station_file(station):
    try:
        station_id = int(station)
    except ValueError:
        return None
    filename = f"stations/TG_STAID{str(station_id).zfill(6)}.txt"
    if not os.path.exists(filename):
        return None
    return filename


def get_station_name(station_id):
    row = stations[stations["STAID"] == int(station_id)]
    if not row.empty:
        return row["STANAME"].values[0].strip()
    return "Unknown"


def load_station_df(filename):
    """Load station CSV and strip all column names cleanly."""
    df = pd.read_csv(filename, skiprows=20)
    df.columns = df.columns.str.strip()
    df["DATE"] = df["DATE"].astype(str).str.strip()
    return df


@app.route("/")
def home():
    table_html = stations.to_html(index=False)
    return render_template("home.html", data=table_html)


@app.route("/api/v1/<station>/<date>")
def station_date(station, date):
    filename = get_station_file(station)
    if not filename:
        return jsonify({"error": f"Station {station} not found.", "status": "error"}), 404

    df = load_station_df(filename)

    date_nodash = date.replace("-", "")
    temp_series = df.loc[df["DATE"] == date_nodash]["TG"]

    if temp_series.empty:
        return jsonify({"error": f"No data for date {date}.", "status": "error"}), 404

    celsius = round(float(temp_series.values[0]) / 10, 1)
    unit = request.args.get("unit", "celsius").lower()
    temperature = round((celsius * 9/5) + 32, 1) if unit == "fahrenheit" else celsius

    return jsonify({
        "station_id": station,
        "station_name": get_station_name(station),
        "date": date,
        "temperature": temperature,
        "unit": unit,
        "status": "success"
    })


@app.route("/api/v1/<station>")
def all_data(station):
    filename = get_station_file(station)
    if not filename:
        return jsonify({"error": f"Station {station} not found.", "status": "error"}), 404

    df = load_station_df(filename)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/v1/yearly/<station>/<year>")
def yearly(station, year):
    filename = get_station_file(station)
    if not filename:
        return jsonify({"error": f"Station {station} not found.", "status": "error"}), 404

    df = load_station_df(filename)
    result = df[df["DATE"].str.startswith(str(year))].to_dict(orient="records")

    if not result:
        return jsonify({"error": f"No data for year {year}.", "status": "error"}), 404

    return jsonify(result)


@app.route("/api/v1/range/<station>/<start>/<end>")
def date_range(station, start, end):
    filename = get_station_file(station)
    if not filename:
        return jsonify({"error": f"Station {station} not found.", "status": "error"}), 404

    try:
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
    except:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD.", "status": "error"}), 400

    if start_date > end_date:
        return jsonify({"error": "Start date must be before end date.", "status": "error"}), 400

    df = load_station_df(filename)

    df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d", errors="coerce")
    mask = (df["DATE"] >= start_date) & (df["DATE"] <= end_date)
    result = df.loc[mask].to_dict(orient="records")

    if not result:
        return jsonify({"error": "No data for given date range.", "status": "error"}), 404

    return jsonify(result)


@app.route("/api/v1/stations")
def search_stations():
    query = request.args.get("name", "").strip().lower()
    if query:
        filtered = stations[stations["STANAME"].str.lower().str.contains(query, na=False)]
    else:
        filtered = stations
    return jsonify(filtered.to_dict(orient="records"))


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)