from agents.common.db import get_supabase_client
import time

def setup_database():
    supabase = get_supabase_client()
    
    print("Setting up Supabase Database...")
    
    # 1. Market Data (Stocks)
    # We can't actually create tables via the JS/Python client unless we use the REST API with service role or SQL editor.
    # However, for this 'Personal Hedge Fund' context, usually users run SQL in the dashboard.
    # But if we were to simulate it or use a raw SQL execution function if available (PostgREST doesn't support generic CREATE TABLE).
    
    # Since we can't CREATE TABLE via the standard client easily without SQL extensions or admin API,
    # I will print the SQL commands the user needs to run in their Supabase SQL Editor.
    
    sql_commands = """
    -- Enable UUID extension
    create extension if not exists "uuid-ossp";

    -- 1. market_data_stocks
    create table if not exists market_data_stocks (
        id uuid primary key default uuid_generate_v4(),
        symbol text not null,
        date timestamp with time zone not null,
        open numeric,
        high numeric,
        low numeric,
        close numeric,
        volume numeric,
        rsi numeric,
        macd numeric,
        macd_signal numeric,
        created_at timestamp with time zone default now(),
        unique(symbol, date)
    );

    -- 2. market_data_crypto (with weather columns)
    create table if not exists market_data_crypto (
        id uuid primary key default uuid_generate_v4(),
        symbol text not null,
        date timestamp with time zone not null,
        open numeric,
        high numeric,
        low numeric,
        close numeric,
        volume numeric,
        weather_score numeric, -- Experimental correlation metric
        created_at timestamp with time zone default now(),
        unique(symbol, date)
    );

    -- 3. signals
    create table if not exists signals (
        id uuid primary key default uuid_generate_v4(),
        symbol text not null,
        signal_type text not null, -- 'BUY', 'SELL', 'HOLD'
        confidence numeric,
        generated_at timestamp with time zone default now(),
        agent_id text -- 'analyst_stock' or 'analyst_crypto'
    );

    -- 4. portfolio_ledger
    create table if not exists portfolio_ledger (
        id uuid primary key default uuid_generate_v4(),
        asset_type text not null, -- 'CASH', 'STOCK', 'CRYPTO'
        symbol text,
        quantity numeric not null,
        average_price numeric,
        current_value numeric,
        last_updated timestamp with time zone default now()
    );

    -- 5. trade_logs
    create table if not exists trade_logs (
        id uuid primary key default uuid_generate_v4(),
        symbol text not null,
        action text not null, -- 'BUY', 'SELL'
        quantity numeric not null,
        price numeric not null,
        timestamp timestamp with time zone default now(),
        status text -- 'EXECUTED', 'PENDING', 'FAILED'
    );
    """
    
    print("\nIMPORTANT: Run the following SQL in your Supabase SQL Editor to set up the tables:\n")
    print(sql_commands)
    
    # Save to a file for convenience
    with open("setup_schema.sql", "w") as f:
        f.write(sql_commands)
    print("\nSQL commands saved to 'setup_schema.sql'.")

if __name__ == "__main__":
    try:
        setup_database()
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure your .env file has SUPABASE_URL and SUPABASE_KEY set.")
