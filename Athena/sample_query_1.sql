SELECT COUNT(*) AS count,
	webaclid,
	terminatingruleid,
	httprequest.clientip,
	httprequest.uri
FROM waf_access_logs
WHERE action = 'BLOCK'
GROUP BY webaclid,
	terminatingruleid,
	httprequest.clientip,
	httprequest.uri
ORDER BY count DESC
LIMIT 100;