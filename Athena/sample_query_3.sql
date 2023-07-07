SELECT httprequest.clientip,
	count(*) ipcount,
	httprequest.country
FROM waf_access_logs
WHERE action = 'ALLOW'
	and day >= '2021/03/01'
	AND day < '2031/12/31'
GROUP BY httprequest.clientip,
	httprequest.country
ORDER BY ipcount DESC
limit 100