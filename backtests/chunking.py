def chunk_symbols(tickers, batch_size=25):
    for i in range(0, len(tickers), batch_size):
        yield tickers[i:i+batch_size]
