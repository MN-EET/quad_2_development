SELECT
	utility,
	"year",
	customer_type,
	customer_count,
	mwh

FROM forecast.mn_consumers_2023

WHERE
	customer_count IS NOT NULL
	AND mwh IS NOT NULL