async def main():
    # Initialize bot with configuration
    config = TradingConfig (
        budget=10000,
        max_risk_per_trade=100,
        max_positions=5,
        time_limit=3600
    )

    bot = NautilusOrion (config)

    # Example trade signal
    trade_signal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'amount': 1000,
        'price': 150.0,
        'risk': 50
    }

    # Execute trade
    success = await bot.execute_trade (trade_signal)

    # Get performance metrics
    metrics = bot.get_performance_metrics ()
    print (f"Trade success: {success}")
    print (f"Performance metrics: {metrics}")

    # Start bot
    await bot.run ()


if __name__ == "__main__":
    import asyncio

    asyncio.run (main ())
