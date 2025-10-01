--Forecasted net generation and mwh received from others from 2024 forecasts
SELECT
	utility,
	utility_id,
	"year",
	ROUND(mwh) AS mwh,
	CASE
		WHEN consumption_category = 'Other' THEN 'Net Generation Received from Other Utilities'
		ELSE 'Net Generation Produced by the Utility'
	END AS consumption_category


FROM main_forecast.consumption_2024_trade_secret c

WHERE consumption_category = 'Total net generation MWH'
	OR consumption_category = 'Other'



