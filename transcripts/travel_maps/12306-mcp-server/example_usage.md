# 12306 MCP Server - Example Usage

This document demonstrates how to use the 12306 MCP Server for searching Chinese train tickets.

## Available Tools

### Search Tool
- **Name**: `search`
- **Description**: 查询12306火车票 (Search 12306 train tickets)
- **Input Parameters**:
  - `departure_station` (string): The departure station name (e.g., "北京南站")
  - `arrival_station` (string): The arrival station name (e.g., "上海虹桥") 
  - `date` (string): The travel date in YYYY-MM-DD format (e.g., "2024-01-15")

## Example Usage Scenarios

### Example 1: Search for tickets from Beijing to Shanghai
```python
# Search for tickets from Beijing South Station to Shanghai Hongqiao on January 23, 2024
result = search(
    departure_station="北京南站",
    arrival_station="上海虹桥", 
    date="2024-01-23"
)
```

### Example 2: Search for tickets from Guangzhou to Shenzhen
```python
# Search for tickets from Guangzhou South Station to Shenzhen North Station on January 19, 2024
result = search(
    departure_station="广州南站",
    arrival_station="深圳北站",
    date="2024-01-19"
)
```

### Example 3: Search for tickets from Wuhan to Xi'an
```python
# Search for tickets from Wuhan Station to Xi'an North Station on January 30, 2024
result = search(
    departure_station="武汉站",
    arrival_station="西安北站", 
    date="2024-01-30"
)
```

## Response Format

The search tool returns a JSON object with the following structure:

```json
{
  "train_tickets": [
    {
      "train_number": "G1234",
      "departure_station": "北京南站",
      "arrival_station": "上海虹桥",
      "departure_time": "08:00",
      "arrival_time": "12:30",
      "duration": "4h30m",
      "date": "2024-01-15",
      "seat_types": {
        "business_class": "商务座",
        "first_class": "一等座",
        "second_class": "二等座",
        "hard_seat": "-"
      },
      "prices": {
        "business_class": 1200,
        "first_class": 800,
        "second_class": 500,
        "hard_seat": 0
      },
      "available_seats": {
        "business_class": 10,
        "first_class": 20,
        "second_class": 50,
        "hard_seat": 0
      }
    }
  ],
  "search_parameters": {
    "departure_station": "北京南站",
    "arrival_station": "上海虹桥",
    "date": "2024-01-15",
    "total_results": 1
  }
}
```

## Available Stations in Database

The database contains tickets for the following major Chinese stations:

- 北京南站 (Beijing South Station)
- 上海虹桥 (Shanghai Hongqiao)
- 广州南站 (Guangzhou South Station) 
- 深圳北站 (Shenzhen North Station)
- 杭州东站 (Hangzhou East Station)
- 南京南站 (Nanjing South Station)
- 武汉站 (Wuhan Station)
- 西安北站 (Xi'an North Station)
- 成都东站 (Chengdu East Station)
- 重庆北站 (Chongqing North Station)
- 天津西站 (Tianjin West Station)
- 长沙南站 (Changsha South Station)
- 合肥南站 (Hefei South Station)
- 郑州东站 (Zhengzhou East Station)
- 苏州北站 (Suzhou North Station)

## Notes

- The server operates entirely offline using the pre-generated database
- Date format must be YYYY-MM-DD (e.g., "2024-01-15")
- Station names must match exactly (case-insensitive)
- If no tickets are found for the given criteria, an empty `train_tickets` array is returned
- The database contains realistic pricing and availability data for various seat types