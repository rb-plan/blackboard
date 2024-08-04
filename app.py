from flask import Flask, render_template, send_file
import datetime
import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
from matplotlib.dates import DateFormatter, HourLocator

app = Flask(__name__)

def fetch_data():
    conn = mysql.connector.connect(
        host='10.24.0.1',
        user='usr1',
        password='debian',
        database='amadoi'
    )
    cursor = conn.cursor(dictionary=True)

    # Calculate the date 2 days ago
    two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
    two_days_ago_str = two_days_ago.strftime('%Y-%m-%d %H:%M:%S')

    query = """
    SELECT ctime, temp, hum 
    FROM t_sensors 
    WHERE ctime >= %s 
    ORDER BY ctime DESC
    """
    cursor.execute(query, (two_days_ago_str,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    df['ctime'] = pd.to_datetime(df['ctime'])
    df.set_index('ctime', inplace=True)

    # Resample the data to every 10 minutes
    df_resampled = df.resample('10T').mean()

    # Drop rows with NaN values that might result from resampling
    df_resampled = df_resampled.dropna()

    return df_resampled

def plot_data():
    df_resampled = fetch_data()
    timestamps = df_resampled.index
    temperatures = df_resampled['temp']
    humidities = df_resampled['hum']

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color='tab:red')
    ax1.plot(timestamps, temperatures, color='tab:red', label='Temperature')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.set_ylim(0, 50)  # Set the range for temperature

    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue')
    ax2.plot(timestamps, humidities, color='tab:blue', label='Humidity')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(20, 100)  # Set the range for humidity

    # Set x-axis major locator and formatter
    ax1.xaxis.set_major_locator(HourLocator(interval=1))
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))

    fig.tight_layout()
    plt.xticks(rotation=45)

    plt.savefig('static/plot.png')
    plt.close()

@app.route('/')
def index():
    plot_data()
    return render_template('index.html')

@app.route('/plot.png')
def plot():
    return send_file('static/plot.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5001)
