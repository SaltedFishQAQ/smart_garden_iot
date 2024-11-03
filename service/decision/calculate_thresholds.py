import pandas as pd
from datetime import datetime, timedelta


class ThresholdCalculator:
    def __init__(self, file_path, alpha=0.6, window=7):

        self.file_path = file_path
        self.alpha = alpha
        self.window = window
        self.weather_data = None
        self._load_data()

    def _load_data(self):
        self.weather_data = pd.read_csv(self.file_path)
        self.weather_data.columns = ['time', 'cloud_cover', 'soil_moisture']
        self.weather_data['time'] = pd.to_datetime(self.weather_data['time'])
        self.weather_data['day_of_year'] = self.weather_data['time'].dt.dayofyear

    def calculate_rolling_average(self, day_of_year, feature):

        start_day = max(day_of_year - self.window // 2, 1)
        end_day = min(day_of_year + self.window // 2, 365)
        rolling_data = self.weather_data[(self.weather_data['day_of_year'] >= start_day) &
                                         (self.weather_data['day_of_year'] <= end_day)]
        return rolling_data[feature].mean()

    def get_daily_threshold(self, date_str):
        try:
            input_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'")

        day_of_year = input_date.timetuple().tm_yday

        # Calculate seasonal baselines
        seasonal_baseline_cloud_cover = self.weather_data.groupby('day_of_year')['cloud_cover'].mean()
        seasonal_baseline_soil_moisture = self.weather_data.groupby('day_of_year')['soil_moisture'].mean()

        # Get baseline values for the specified day
        baseline_cloud_cover = seasonal_baseline_cloud_cover.loc[day_of_year]
        baseline_soil_moisture = seasonal_baseline_soil_moisture.loc[day_of_year]

        # Calculate rolling averages
        rolling_avg_cloud_cover = self.calculate_rolling_average(day_of_year, 'cloud_cover')
        rolling_avg_soil_moisture = self.calculate_rolling_average(day_of_year, 'soil_moisture')

        # Calculate final thresholds
        daily_cloud_cover_threshold = self.alpha * baseline_cloud_cover + (1 - self.alpha) * rolling_avg_cloud_cover
        daily_soil_moisture_threshold = self.alpha * baseline_soil_moisture + (
                    1 - self.alpha) * rolling_avg_soil_moisture

        return {
            'cloud_cover_threshold': daily_cloud_cover_threshold,
            'soil_moisture_threshold': daily_soil_moisture_threshold
        }


# Testing
if __name__ == "__main__":
    file_path = './weather_turin.csv'
    threshold_calculator = ThresholdCalculator(file_path, alpha=0.6, window=7)

    # Testing with a sample date
    date_input = '2024-07-01'
    thresholds = threshold_calculator.get_daily_threshold(date_input)
    print(f"Thresholds for Decision Tree on {date_input}:")
    print(f"  Cloud Cover Threshold: {thresholds['cloud_cover_threshold']:.2f}")
    print(f"  Soil Moisture Threshold: {thresholds['soil_moisture_threshold']:.3f}")
