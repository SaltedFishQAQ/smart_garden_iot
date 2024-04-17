from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class Connector:
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=url, token=token, org=org)

    def insert(self, measurement, tags, fields):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        point = Point(measurement)
        for key, value in tags.items():
            point = point.tag(key, value)
        for key, value in fields.items():
            point = point.field(key, value)

        write_api.write(bucket=self.bucket, record=point)

    def query(self, measurement):
        sql = f"""from(bucket: "{self.bucket}")
         |> range(start: -10m)
         |> filter(fn: (r) => r._measurement == "{measurement}")"""
        tables = self.client.query_api().query(sql, org=self.org)
        for table in tables:
            for record in table.records:
                print(record)
