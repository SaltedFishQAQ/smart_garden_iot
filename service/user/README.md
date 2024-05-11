# User Service
> Service for handling Dashboard or Telebot requests

## Modules
- Device Data
- Device Command
- Catalog
  - Service
  - Device
- Rule

## Device Data
> Display data collected by the device
### Temperature
#### request
```http
GET /device/data/temperature/list?start_at=xx&end_at=xx&device_id=xx&page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- start_at - data after what time
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- end_at - data before what time
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- device_id - data collected by which device
  - type: string
  - optional
- page - page of list
  - type: integer
  - optional
- size - size of each page
  - type: integer
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "device_id": "device11",
      "value": 25.4,
      "time": "2024-05-05 10:45:13"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```

### Humidity
#### request
```http
GET /device/data/humidity/list?start_at=xx&end_at=xx&device_id=xx&page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- start_at - data after what time
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- end_at - data before what time
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- device_id - data collected by which device
  - type: string
  - optional
- page - page of list
  - type integer
  - optional
- size - size of each page
  - type integer
  - optional
#### response

```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "device_id": "device11",
      "value": 60.0,
      "time": "2024-05-05 10:45:13"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```

### Light
#### request
```http
GET /device/data/light/list?start_at=xx&end_at=xx&device_id=xx&page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- start_at - the light status after this time point
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- end_at - the light status before this time point
  - type: string
  - format: 2024-05-10 13:42:00
  - optional
- device_id - which light device
  - type: string
  - optional
- page - page of list
  - type integer
  - optional
- size - size of each page
  - type integer
  - optional
#### response

```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "device_id": "light1",
      "status": "on",
      "time": "2024-05-05 10:45:13"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```

## Device Command
> send command to device
### Turn device on or off
#### request
```http request
POST /device/command/running HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "device_id": "device11", // control which device 
  "status": 1 // 1:start / 0:stop
}
```
#### response
```json
{
  "code": 0,
  "message:": ""
}
```

### send command to device
#### request
```http request
POST /device/command/send HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "device_id": "light",
  "opt": "on"
}
```
#### response
```json
{
  "code": 0,
  "message:": ""
}
```

## Catalog
> Details of services and devices
### Service List
#### request
```http
GET /service/list?page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- page - page of list
  - type: integer
  - optional
- size - size of each page
  - type: integer
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "id": 123,
      "name": "auth service",
      "running": 1,
      "port": 8083,
      "desc": "this is a service for device permission verification"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```

### Device List
#### request
```http
GET /device/list?page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- page - page of list
  - type: integer
  - optional
- size - size of each page
  - type: integer
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "id": 123,
      "device_id": "device123",
      "running": 1,
      "opt": {
        "on": "open the light",
        "off": "close the light"
      },
      "desc": "device for temperature"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```

## Rule
### Rule List
#### request
```http
GET /rule/list?device_id=xx&page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- device_id - rule for which device
  - type: string
- page - page of list
  - type: integer
  - optional
- size - size of each page
  - type: integer
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "id": 123,
      "device_id": "device123",
      "entity": "temperature",
      "field": "value",
      "compare": "gt",
      "value": 25.0,
      "target_device_id": "light",
      "opt": "light off",
      "is_deleted": 0, // 1:deleted 0:not deleted
      "desc": "rule for temperature"
    }
  ],
  "page_info": {
    "page": 1,
    "page_total": 10,
    "size": 10,
    "total": 94
  }
}
```