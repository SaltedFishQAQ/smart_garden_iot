import pandas as pd
from datetime import datetime, timedelta

file_path = './weather_turin.csv'
weather_data = pd.read_csv(file_path)

# Preprocess the DataFrame
weather_data.columns = ['time', 'cloud_cover', 'soil_moisture']
weather_data['time'] = pd.to_datetime(weather_data['time'])
weather_data['day_of_year'] = weather_data['time'].dt.dayofyear

#calculate rolling average
def calculate_rolling_average(df, day_of_year, feature, window=7):
    start_day = max(day_of_year - window // 2, 1)
    end_day = min(day_of_year + window // 2, 365)
    rolling_data = df[(df['day_of_year'] >= start_day) & (df['day_of_year'] <= end_day)]
    return rolling_data[feature].mean()

#Calculate Daily thresholds
def get_daily_threshold(date_str, df, alpha=0.6):
    input_date = datetime.strptime(date_str, '%Y-%m-%d')
    day_of_year = input_date.timetuple().tm_yday

    seasonal_baseline_cloud_cover = df.groupby('day_of_year')['cloud_cover'].mean()
    seasonal_baseline_soil_moisture = df.groupby('day_of_year')['soil_moisture'].mean()

    baseline_cloud_cover = seasonal_baseline_cloud_cover.loc[day_of_year]
    baseline_soil_moisture = seasonal_baseline_soil_moisture.loc[day_of_year]

    rolling_avg_cloud_cover = calculate_rolling_average(df, day_of_year, 'cloud_cover')
    rolling_avg_soil_moisture = calculate_rolling_average(df, day_of_year, 'soil_moisture')

    daily_cloud_cover_threshold = alpha * baseline_cloud_cover + (1 - alpha) * rolling_avg_cloud_cover
    daily_soil_moisture_threshold = alpha * baseline_soil_moisture + (1 - alpha) * rolling_avg_soil_moisture

    return {
        'cloud_cover_threshold': daily_cloud_cover_threshold,
        'soil_moisture_threshold': daily_soil_moisture_threshold
    }

# Testing
date_input = '2024-07-01'
thresholds = get_daily_threshold(date_input, weather_data)
print(f"Thresholds for Decision Tree on {date_input}:")
print(f"  Cloud Cover Threshold: {thresholds['cloud_cover_threshold']:.2f}")
print(f"  Soil Moisture Threshold: {thresholds['soil_moisture_threshold']:.3f}")
