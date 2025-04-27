# yf-api

A simple FastAPI wrapper around the yfinance library for retrieving stock market data. Containerized for easy deployment with Docker.

## Requirements

- Docker (to build and run the container)

## Building the Docker Image

From the root of this project directory, run:

```bash
docker build -t yf-api .
```

## Running the Server

Start the container and map the API port (8000) to your host:

```bash
docker run --rm -p 8000:8000 yf-api
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## API Endpoints

### Get Stock Info

- **Endpoint:** `GET /info/{ticker}`
- **Description:** Retrieves stock information for a given ticker.
- **Response:** JSON object with stock info.
- **Error Responses:**
  - 404 if ticker not found.
  - 500 for server errors.

### Get Stock History

- **Endpoint:** `GET /history/{ticker}`
- **Query Parameters:**
  - `period` (optional, default: "1mo"): Data period (e.g., 1d, 5d, 1mo, 3mo, etc.)
  - `interval` (optional, default: "1d"): Data interval (e.g., 1m, 5m, 1d, 1wk, etc.)
  - `start` (optional): Start date (YYYY-MM-DD)
  - `end` (optional): End date (YYYY-MM-DD)
  - `format` (optional, default: "json"): Output format, either "json" or "csv"
- **Response:** JSON array or CSV file of historical data.
- **Error Responses:**
  - 400 for invalid format.
  - 404 if no data found.
  - 500 for server errors.

### Get Stock Calendar

- **Endpoint:** `GET /calendar/{ticker}`
- **Description:** Retrieves upcoming event calendar (earnings, dividends, etc.) for a ticker.
- **Response:** JSON object with calendar data.
- **Error Responses:**
  - 404 if no calendar data found.
  - 500 for server errors.

### Get Balance Sheet

- **Endpoint:** `GET /balance-sheet/{ticker}`
- **Description:** Retrieves the balance sheet for a ticker.
- **Response:** JSON object with balance sheet data.
- **Error Responses:**
  - 404 if no data found.
  - 500 for server errors.

### Get Quarterly Income Statement

- **Endpoint:** `GET /quarterly-income-statement/{ticker}`
- **Description:** Retrieves quarterly income statement for a ticker.
- **Response:** JSON object with income statement data.
- **Error Responses:**
  - 404 if no data found.
  - 500 for server errors.

## Example Usage

Convert a local file:

```bash
curl -X GET http://localhost:8000/info/AAPL
```

Get stock history in JSON:

```bash
curl -X GET "http://localhost:8000/history/AAPL?period=1mo&interval=1d&format=json"
```

Get stock history in CSV:

```bash
curl -X GET "http://localhost:8000/history/AAPL?period=1mo&interval=1d&format=csv" -o AAPL_history.csv
```

Get stock calendar:

```bash
curl -X GET http://localhost:8000/calendar/AAPL
```

Get balance sheet:

```bash
curl -X GET http://localhost:8000/balance-sheet/AAPL
```

Get quarterly income statement:

```bash
curl -X GET http://localhost:8000/quarterly-income-statement/AAPL
