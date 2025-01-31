# User Service
> Service for handling Dashboard or Telebot requests

## Modules
- User
- Data
- Device
- Catalog
- Rule

## User
> User operation
### Login
#### request
```http
POST /user/login HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "name": "abcd",
  "password": "password",
}
```
#### response
```json
{
  "code": 0,
  "message:": "",
  "data": [
    {
      "id": 1,
      "name": "abcd"
      "role": 1
      "created_at": "2024-08-10 00:00:00"
      "updated_at": "2024-08-10 00:00:00"
    }
  ]
}
```

### Register
#### request
```http
GET /user/register HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "name": "abcd",
  "password": "password",
}
```
#### response
```json
{
  "code": 0,
  "message:": ""
}
```

## Data
> Display data collected by the device
### Kinds of Data
#### request
```http
GET /data/entities HTTP/1.1
Host: localhost:8080
```
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "entity": "temperature",
      "desc": "temperature data"
    }
  ]
}
```

### Temperature
#### request
```http
GET /data/temperature?start_at=xx&end_at=xx&name=xx HTTP/1.1
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
- name - data collected by which device
  - type: string
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "name": "device11",
      "value": 25.4,
      "time": "2024-05-05 10:45:13"
    }
  ]
}
```

### Humidity
#### request
```http
GET /data/humidity?start_at=xx&end_at=xx&name=xx HTTP/1.1
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
- name - data collected by which device
  - type: string
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "name": "device11",
      "value": 60.0,
      "time": "2024-05-05 10:45:13"
    }
  ]
}
```

### Light
#### request
```http
GET /data/light?start_at=xx&end_at=xx&name=xx HTTP/1.1
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
- name - which light device
  - type: string
  - optional
#### response
```json
{
  "code": 0,
  "message:": "",
  "list": [
    {
      "name": "light1",
      "status": "on",
      "time": "2024-05-05 10:45:13"
    }
  ]
}
```

## Device
> device-related operations
### Turn device on or off
#### request
```http request
POST /device/running HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "name": "device11", // control which device 
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
  "name": "light",
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
GET /catalog/services?page=1&size=10 HTTP/1.1
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
GET /catalog/devices?page=1&size=10 HTTP/1.1
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
      "name": "device123",
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
> Auto Rule for the device data
### Rule List
#### request
```http
GET /rules?name=xx&page=1&size=10 HTTP/1.1
Host: localhost:8080
```
- name - rule for which device
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
      "id": 123,
      "src": "device123", // data from which device
      "entity": "temperature",
      "field": "value",
      "compare": "gt",
      "value": 25.0,
      "dst": "light11", // command send to which device
      "opt": "off",
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

### Create Rule
#### request
```http request
POST /rules/create HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "src": "device123", // data from which device
  "entity": "temperature", // rule for which kind of data 
  "field": "value", // which data indicator
  "compare": "gt",
  "value": 25.0,
  "dst": "light11", // command send to which device
  "opt": "off",
  "desc": "rule for temperature"
}
```
#### response
```json
{
  "code": 0,
  "message:": "",
  "data": {
    "id": 1
  }
}
```


### UPDATE Rule
#### request
```http request
POST /rules/update HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "id": 123, // rule_id
  "src": "device123", // data from which device
  "entity": "temperature", // rule for which kind of data 
  "field": "value", // which data indicator
  "compare": "gt",
  "value": 25.0,
  "dst": "light11", // command send to which device
  "opt": "off",
  "desc": "rule for temperature"
}
```
#### response
```json
{
  "code": 0,
  "message:": ""
}
```

### Turn rule on or off
#### request
```http request
POST /rules/running HTTP/1.1
Host: localhost:8080
```
##### request body
```json
{
  "id": 123, // rule_id 
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
