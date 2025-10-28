import datetime
def main():
    print("=== Stock Data Visualizer ===")

    stock_symbol = input("Enter stock symbol (e.g., AAPL, GOOGL): ").upper()
    chart_type = input("Enter chart type (line, bar): ").lower()
    time_series = input("Enter time series (daily, weekly, monthly): ").upper()
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    
    if not validate_date(start_date) or not validate_date(end_date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return
    if start_date > end_date:
        print("Start date must be before end date.")
        return
    if chart_type not in ['line', 'bar']:
        print("Invalid chart type. Please choose 'line' or 'bar'.")
        return
    if time_series not in ['DAILY', 'WEEKLY', 'MONTHLY']:
        print("Invalid time series. Please choose 'daily', 'weekly', or 'monthly'.")
        return
    
    