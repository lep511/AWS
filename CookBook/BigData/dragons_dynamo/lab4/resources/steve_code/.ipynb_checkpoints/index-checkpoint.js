exports.handler = function (event, context, callback) {
    if (event["dragon_name_str"] !== undefined && event["dragon_name_str"] !== "All") {
        justThisDragon(event["dragon_name_str"], callback);
    } else {
        scanTable(callback);
    }
};

var
    AWSXRay = require('aws-xray-sdk-core'),
    AWS = AWSXRay.captureAWS(require('aws-sdk')),
    DDB = new AWS.DynamoDB({
        apiVersion: "2012-08-10"
    });

function justThisDragon(dragon_name_str, cb) {
    var
        params = {
            ExpressionAttributeValues: {
                ":dragon_name": {
                    S: dragon_name_str
                }
            },
            FilterExpression: "dragon_name = :dragon_name",
            TableName: "dragon_stats"
        };
    DDB.scan(params, function (err, data) {
        if (err) {
            cb(err);
        } else if (data.Items) {
            cb(null, data.Items);
        } else {
            cb(null, []);
        }
    });
}
function scanTable(cb) {
    var
        params = {
            TableName: "dragon_stats",
            ProjectionExpression: "dragon_name, family, protection, damage, description"
        };
    let items = [];
    DDB.scan(params, function scanUntilDone(err, data) {
        if (err) {
            cb(err);
        } else if (data.LastEvaluatedKey) {
            
            items = items.concat(data.Items);
            
            params.ExclusiveStartKey = data.LastEvaluatedKey;
            
            DDB.scan(params, scanUntilDone);
        } else {
            items = items.concat(data.Items);
            cb(null, items);
        }
    });
}
