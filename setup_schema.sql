
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

    -- 6. system_config (Dynamic Parameters)
    create table if not exists system_config (
        key text primary key, -- e.g. 'rsi_buy_threshold', 'crypto_max_pos_size'
        value numeric not null,
        updated_at timestamp with time zone default now()
    );

    -- 7. system_logs (Coach Actions)
    create table if not exists system_logs (
        id uuid primary key default uuid_generate_v4(),
        event_type text not null, -- 'PARAM_UPDATE', 'WEEKLY_REVIEW'
        details text,
        created_at timestamp with time zone default now()
    );

    -- Seed Initial Config (Idempotent upsert via do block is hard in raw SQL string, 
    -- so we stick to simple inserts that might fail if exists or use insert on conflict do nothing)
    insert into system_config (key, value) values 
    ('rsi_buy_threshold', 30),
    ('rsi_sell_threshold', 70),
    ('crypto_max_pos_size', 500),
    ('weather_buy_threshold', 80)
    on conflict (key) do nothing;
    