# data_plotter.py

import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from matplotlib.dates import DateFormatter, DayLocator
import io

def fetch_data():
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host='10.24.0.1',
        user='usr1',
        password='debian',
        database='amadoi'
    )
    cursor = conn.cursor(dictionary=True)

    # Calculate the date 7 days ago
    one_week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d %H:%M:%S')

    query = """
    SELECT ctime, temp, hum 
    FROM t_sensors 
    WHERE ctime >= %s 
    ORDER BY ctime DESC
    """
    cursor.execute(query, (one_week_ago_str,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    df['ctime'] = pd.to_datetime(df['ctime'])
    df.set_index('ctime', inplace=True)

    # Resample the data to every 20 minutes
    df_resampled = df.resample('20T').mean()

    # Drop rows with NaN values that might result from resampling
    df_resampled = df_resampled.dropna()

    return df_resampled

def plot_data():
    df_resampled = fetch_data()
    timestamps = df_resampled.index
    temperatures = df_resampled['temp']
    humidities = df_resampled['hum']

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Time', fontsize=14)
    ax1.set_ylabel('Temperature (°C)', color='tab:red', fontsize=14)
    ax1.plot(timestamps, temperatures, color='tab:red', label='Temperature', linestyle='-', marker='o')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.set_ylim(20, 40)  # Set the range for temperature
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue', fontsize=14)
    ax2.plot(timestamps, humidities, color='tab:blue', label='Humidity', linestyle='--', marker='x')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(20, 100)  # Set the range for humidity
    ax2.legend(loc='upper right')

    # Set x-axis major locator and formatter
    ax1.xaxis.set_major_locator(DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.tight_layout()
    plt.xticks(rotation=45)
    plt.grid(True)

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf.getvalue()
