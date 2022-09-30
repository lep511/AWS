import json
import operator

ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv
}

def lambda_handler(event, context):
    try:
        op_a = float(event["a"])
        op_b = float(event["b"])
        opera = event["op"]
    
    except Exception as err:
        print(err)
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid Operand: {}'.format(err))
        }

   
    try:
        result = ops[opera](op_a, op_b)

    except Exception as err:
        print(err)
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid Operator: {}'.format(err))
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                "a": op_a,
                "b": op_b,
                "op": opera,
                "c": result
            }
        )
    }