--Forecasted net generation from 2023 forecasts
SELECT utility, utility_id, "year", consumption_category, ROUND(mwh) AS mwh
FROM main_forecast.consumption_2023_trade_secret c
WHERE consumption_category = 'Total net generation MWH'

