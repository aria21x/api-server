from fastapi import FastAPI
from core.db.postgres import fetch_one, fetch_all
from core.services.watchlist_service import top_wallets

app = FastAPI(title='Solana Insider Tracker API')


def _count(query: str, params: tuple = ()) -> int:
    row = fetch_one(query, params) or {}
    return int(row.get('c') or 0)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get('/stats')
def stats():
    return {
        'raw_signatures': _count('SELECT COUNT(*) AS c FROM raw_signatures'),
        'raw_transactions': _count('SELECT COUNT(*) AS c FROM raw_transactions'),
        'wallets': _count('SELECT COUNT(*) AS c FROM wallets'),
        'tokens': _count('SELECT COUNT(*) AS c FROM tokens'),
        'trades': _count('SELECT COUNT(*) AS c FROM trades'),
        'trade_lots': _count('SELECT COUNT(*) AS c FROM trade_lots'),
        'wallet_positions': _count('SELECT COUNT(*) AS c FROM wallet_positions'),
        'wallet_funders': _count('SELECT COUNT(*) AS c FROM wallet_funders'),
        'unknown_programs': _count('SELECT COUNT(*) AS c FROM unknown_programs'),
        'pending_alerts': _count('SELECT COUNT(*) AS c FROM alerts_queue WHERE sent = FALSE'),
    }


@app.get('/watchlist')
def watchlist(limit: int = 25):
    return top_wallets(limit)


@app.get('/recent-trades')
def recent_trades(limit: int = 20):
    return fetch_all(
        '''
        SELECT signature, wallet_address, mint, symbol, side, usd_value, sol_value, confidence, tx_type, venue, block_time
        FROM trades
        ORDER BY inserted_at DESC
        LIMIT %s
        ''',
        (limit,),
    )


@app.get('/wallet/{wallet_address}')
def wallet_detail(wallet_address: str):
    wallet = fetch_one('SELECT * FROM wallets WHERE wallet_address = %s', (wallet_address,))
    positions = fetch_all(
        'SELECT mint, symbol, quantity, cost_basis_usd, avg_cost_usd, realized_pnl_usd, last_trade_at FROM wallet_positions WHERE wallet_address = %s ORDER BY updated_at DESC LIMIT 50',
        (wallet_address,),
    )
    edges = fetch_all(
        'SELECT wallet_a, wallet_b, mint, edge_type, edge_score, last_seen_at FROM wallet_edges WHERE wallet_a = %s OR wallet_b = %s ORDER BY edge_score DESC, last_seen_at DESC LIMIT 50',
        (wallet_address, wallet_address),
    )
    lots = fetch_all(
        'SELECT mint, symbol, buy_signature, initial_quantity, remaining_quantity, unit_cost_usd, buy_time FROM trade_lots WHERE wallet_address = %s ORDER BY buy_time DESC NULLS LAST, id DESC LIMIT 50',
        (wallet_address,),
    )
    return {'wallet': wallet, 'positions': positions, 'edges': edges, 'lots': lots}


@app.get('/token/{mint}')
def token_detail(mint: str):
    token = fetch_one('SELECT * FROM tokens WHERE mint = %s', (mint,))
    trades = fetch_all(
        'SELECT wallet_address, side, usd_value, confidence, venue, block_time FROM trades WHERE mint = %s ORDER BY inserted_at DESC LIMIT 50',
        (mint,),
    )
    launch_signals = fetch_all(
        'SELECT signal_type, signal_value, source, observed_at FROM token_launch_signals WHERE mint = %s ORDER BY observed_at DESC LIMIT 20',
        (mint,),
    )
    return {'token': token, 'recent_trades': trades, 'launch_signals': launch_signals}


@app.get('/unknown-programs')
def unknown_programs(limit: int = 50):
    return fetch_all('SELECT * FROM unknown_programs ORDER BY last_seen_at DESC LIMIT %s', (limit,))


@app.get('/entities')
def entities(limit: int = 50):
    return fetch_all('SELECT * FROM address_entities ORDER BY confidence DESC, updated_at DESC LIMIT %s', (limit,))
