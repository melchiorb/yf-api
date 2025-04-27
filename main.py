from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import yfinance as yf
from typing import Optional
from datetime import date
import pandas as pd
import io

app = FastAPI()

@app.get("/info/{ticker}")
async def get_stock_info(ticker: str):
    """
    Retrieves stock information for a given ticker using yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # Check if the info dictionary is empty or lacks a key like 'symbol',
        # which might indicate an invalid ticker or no data found.
        if not info or 'symbol' not in info:
            raise HTTPException(status_code=404, detail=f"Could not find information for ticker: {ticker}")
        return info
    except Exception as e:
        # Catch potential exceptions from yfinance or other issues
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/history/{ticker}")
async def get_stock_history(
    ticker: str,
    period: Optional[str] = Query("1mo", description="Data period to download (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: Optional[str] = Query("1d", description="Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)"),
    start: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    format: Optional[str] = Query("json", description="Output format: 'json' or 'csv'")
):
    """
    Retrieves historical market data for a given ticker using yfinance,
    returning either JSON or CSV format.
    """
    try:
        stock = yf.Ticker(ticker)
        # Convert date objects to string format if they exist, yfinance expects strings or None
        start_str = start.isoformat() if start else None
        end_str = end.isoformat() if end else None

        # Fetch history using appropriate parameters
        # Note: yfinance prioritizes start/end over period if both are provided.
        hist_df = stock.history(
            period=period,
            interval=interval,
            start=start_str,
            end=end_str
        )

        if hist_df.empty:
            raise HTTPException(status_code=404, detail=f"Could not find history for ticker: {ticker} with specified parameters.")

        # Convert DataFrame to JSON serializable format (list of records)
        # Reset index to make the Date/Datetime index a regular column
        hist_df_reset = hist_df.reset_index()
        # Convert Timestamp columns to string to ensure JSON compatibility
        for col in hist_df_reset.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]', 'datetime64[ns, America/New_York]']).columns:
             hist_df_reset[col] = hist_df_reset[col].astype(str)

        # Output based on the requested format
        if format.lower() == 'csv':
            # Create an in-memory text stream
            csv_buffer = io.StringIO()
            # Write DataFrame to the stream (include index as Date column)
            hist_df.to_csv(csv_buffer)
            # Seek to the beginning of the stream
            csv_buffer.seek(0)
            # Prepare filename
            filename = f"{ticker}_history_{start_str or period}_{end_str or 'latest'}.csv"
            # Return as a streaming response (efficient for large files)
            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        elif format.lower() == 'json':
            # Convert DataFrame to JSON serializable format (list of records)
            # Reset index to make the Date/Datetime index a regular column
            hist_df_reset = hist_df.reset_index()
            # Convert Timestamp columns to string to ensure JSON compatibility
            for col in hist_df_reset.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]', 'datetime64[ns, America/New_York]']).columns:
                 hist_df_reset[col] = hist_df_reset[col].astype(str)

            history_json = hist_df_reset.to_dict(orient='records')
            return history_json
        else:
            raise HTTPException(status_code=400, detail="Invalid format specified. Choose 'json' or 'csv'.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching history: {str(e)}")


@app.get("/calendar/{ticker}")
async def get_stock_calendar(ticker: str):
    """
    Retrieves the upcoming event calendar (earnings, dividends, etc.) for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        # .calendar can return DataFrame or dict
        calendar_data = stock.calendar

        # Check if data is missing (handles None, empty DataFrame, empty dict)
        if not calendar_data:
            raise HTTPException(status_code=404, detail=f"Could not find calendar information for ticker: {ticker}")

        calendar_dict = {}
        if isinstance(calendar_data, pd.DataFrame):
            # Convert DataFrame to dictionary
            calendar_dict = calendar_data.to_dict()
            # Convert Timestamp values in the dict
            for key, value_dict in calendar_dict.items():
                for event, val in value_dict.items():
                    if isinstance(val, pd.Timestamp):
                        calendar_dict[key][event] = val.isoformat()
        elif isinstance(calendar_data, dict):
            # If it's already a dict, just use it (potentially convert timestamps if needed)
            calendar_dict = calendar_data
            # Example: Check top-level values if structure is known/consistent
            # This part might need adjustment based on the actual dict structure returned by yfinance
            for key, val in calendar_dict.items():
                 if isinstance(val, pd.Timestamp):
                     calendar_dict[key] = val.isoformat()
                 # Add checks for nested dicts/lists if necessary
        else:
             # Should not happen based on yfinance docs, but good practice
             raise HTTPException(status_code=500, detail="Unexpected data type received for calendar.")


        return calendar_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching calendar data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Note: Running with __name__ == "__main__" is for basic testing.
    # For production, use a process manager like Gunicorn or Uvicorn directly.
    uvicorn.run(app, host="0.0.0.0", port=8000)
