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

    def query(self, measurement, time_range=None, cond=None):
        if time_range is None:
            time_range = "start: -10m"

        if cond is not None:
            cond = f" and {cond}"
        else:
            cond = ""

        sql = f"""from(bucket: "{self.bucket}")
         |> range({time_range})
         |> filter(fn: (r) => r._measurement == "{measurement}" {cond})
         |> sort(columns: ["_time"], desc: true)"""

        tables = self.client.query_api().query(sql, org=self.org)
        result = []
        for table in tables:
            for record in table.records:
                line = {
                    'measurement': record.get_measurement(),
                    record.get_field(): record.get_value(),
                    'created_at': record.get_time().strftime('%Y-%m-%d %H:%M:%S'),
                    'start_at': record.values['_start'].strftime('%Y-%m-%d %H:%M:%S'),
                    'end_at': record.values['_stop'].strftime('%Y-%m-%d %H:%M:%S'),
                }
                for val in record.values:
                    if val.startswith('_') is False and val != "result" and val != "table":
                        line[val] = record.values[val]
                result.append(line)
        return result
