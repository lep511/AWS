WITH DATASET AS (
	SELECT header
	FROM waf_access_logs
		CROSS JOIN UNNEST(httprequest.headers) AS t(header)
	WHERE day >= '2021/01/01'
		AND day < '2031/12/31'
)
SELECT header.name,
	count(*) headerNameCount
FROM DATASET
GROUP BY header.name
ORDER BY headerNameCount DESC