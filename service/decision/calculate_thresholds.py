
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import joblib

# Soil types with characteristics
soil_types = {
    "Sandy": {"field_capacity": 10, "wilting_point": 4, "adjustment_factor": 0.7},
    "Clay": {"field_capacity": 50, "wilting_point": 15, "adjustment_factor": 1.0},  # Default base
    "Loamy": {"field_capacity": 25, "wilting_point": 10, "adjustment_factor": 0.85},
    "Silty": {"field_capacity": 35, "wilting_point": 12, "adjustment_factor": 0.9},
    "Peaty": {"field_capacity": 40, "wilting_point": 10, "adjustment_factor": 0.88},
}


class ThresholdCalculator:
    def __init__(self, file_path, window=7, n_estimators=100, random_state=42):
        self.file_path = file_path
        self.window = window
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        self.scaler = StandardScaler()
        self.weather_data = None
        self._load_data()
        self._train_or_load_model()

    def _load_data(self):
        self.weather_data = pd.read_csv(self.file_path)
        self.weather_data.columns = ['time', 'cloud_cover', 'soil_moisture']
        self.weather_data['time'] = pd.to_datetime(self.weather_data['time'])
        self.weather_data['day_of_year'] = self.weather_data['time'].dt.dayofyear
        self.weather_data['smoothed_soil_moisture'] = self.weather_data['soil_moisture'].rolling(self.window).mean()
        self.weather_data.dropna(inplace=True)

    def _train_or_load_model(self):
        try:
            self.model = joblib.load("soil_moisture_model.pkl")
            self.scaler = joblib.load("scaler.pkl")
            print("Model and scaler loaded from file.")
        except (FileNotFoundError, IOError):
            print("Training new model as no saved model found.")
            X = self.weather_data[['day_of_year', 'smoothed_soil_moisture']]
            y = self.weather_data['soil_moisture']
            X_scaled = self.scaler.fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            print(f"Random Forest model trained. Test MSE: {mse:.4f}")
            joblib.dump(self.model, "soil_moisture_model.pkl")
            joblib.dump(self.scaler, "scaler.pkl")

    def get_daily_threshold(self, date_str, soil_type="Clay"):
        try:
            input_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'")

        day_of_year = input_date.timetuple().tm_yday
        recent_smoothed_soil_moisture = self.weather_data['smoothed_soil_moisture'].iloc[-1]
        X_pred = pd.DataFrame([[day_of_year, recent_smoothed_soil_moisture]],
                              columns=['day_of_year', 'smoothed_soil_moisture'])
        X_pred_scaled = self.scaler.transform(X_pred)
        baseline_threshold = self.model.predict(X_pred_scaled)[0]

        # Apply adjustment for soil type
        soil_info = soil_types.get(soil_type.capitalize(), soil_types["Clay"])  # Use clay as default
        adjustment_factor = soil_info["adjustment_factor"]
        adjusted_threshold = baseline_threshold * adjustment_factor

        print(f"Predicted Threshold (pre-adjustment): {baseline_threshold}")
        print(f"Adjusted Threshold based on {soil_type} soil: {adjusted_threshold}")

        return {
            'soil_moisture_threshold': adjusted_threshold
        }


# Testing
if __name__ == "__main__":
    file_path = './weather_turin.csv'
    threshold_calculator = ThresholdCalculator(file_path, window=7, n_estimators=100)
    date_input = '2024-11-05'
    thresholds = threshold_calculator.get_daily_threshold(date_input, soil_type="Sandy")
    print(f"Predicted Soil Moisture Threshold on {date_input}: {thresholds['soil_moisture_threshold']:.3f}")

