from common.time import time_to_str

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

    def query(self, measurement, time_range=None, cond=None, page=1, size=10):
        if time_range is None:
            time_range = "start: -120m"

        if cond is not None:
            cond = f" and {cond}"
        else:
            cond = ""

        offset = (page-1)*size

        sql = f"""from(bucket: "{self.bucket}")
         |> range({time_range})
         |> filter(fn: (r) => r._measurement == "{measurement}" {cond})
         |> group(columns: [])
         |> sort(columns: ["_time"], desc: true)
         |> limit(n: {size}, offset: {offset})"""

        tables = self.client.query_api().query(sql, org=self.org)
        result = []
        for table in tables:
            for record in table.records:
                line = {
                    'measurement': record.get_measurement(),
                    record.get_field(): record.get_value(),
                    'created_at': time_to_str(record.get_time()),
                    'start_at': time_to_str(record.values['_start']),
                    'end_at': time_to_str(record.values['_stop']),
                }
                for val in record.values:
                    if val.startswith('_') is False and val != "result" and val != "table":
                        line[val] = record.values[val]
                result.append(line)
        return result

    def count(self, measurement):
        if measurement != "":
            sql = f"""from(bucket: "{self.bucket}")
                     |> range(start: 0)
                     |> filter(fn: (r) => r._measurement == "{measurement}")
                     |> count() """
        else:
            sql = f"""from(bucket: "{self.bucket}")
                     |> range(start: 0)
                     |> count() """

        tables = self.client.query_api().query(sql, org=self.org)

        counts = 0
        for table in tables:
            for record in table.records:
                counts += record.get_value()

        return counts

    def measurement_list(self):
        sql = f"""
        import "influxdata/influxdb/schema"
        schema.measurements(bucket: "{self.bucket}")
        """

        tables = self.client.query_api().query(query=sql)
        result = []
        for table in tables:
            for record in table.records:
                result.append(record.get_value())

        return result
