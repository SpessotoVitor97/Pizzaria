
import json

from baseDAO import BaseDAO
from sqsHandler import SqsHandler

dao = BaseDAO('Pedidos')
sqs = SqsHandler('https://sqs.us-east-1.amazonaws.com/076121878322/espera-entrega')
sqs_dest = SqsHandler('https://sqs.us-east-1.amazonaws.com/076121878322/espera-entrega_dest')
    
def sourceHandler(event, context):
    print("event: {}".format(json.dumps(event)))
    
    eventDetail = event['detail']
    status = eventDetail['status']
    pedido = eventDetail['pedido']
    cliente = eventDetail['cliente']
    time = event['time']
    
    dao.put_item({'status': status, 'pedido':str(pedido), 'cliente': cliente, 'time': time})
    
    return event
    
def detailHandler(event, context):
    print("event: {}".format(json.dumps(event)))
    
    eventDetail = event['detail']
    pedido = eventDetail['pedido']
    messages = []
    
    for status in eventDetail['status']:
        if (status == 'pronto'):
            messages.append({'Id': str(pedido), 'MessageBody': status})
            splitMsg = [messages[x:x+10] for x in range(0, len(messages), 10)]
            
            for lista in splitMsg:
                print(type(lista))
                print(str(lista))
                sqs.send(json.dumps(lista))
    
def sqsHandler(event, context):
    
    for i in range(100):
        msgs = sqs.getMessage(10)
        print(json.dumps(msgs))
        
        if ('Messages' not in msgs):
            break
        if (len(msgs['Messages']) == 0):
            break
        for message in msgs['Messages']:
            sqs_dest.send(json.dumps(message['Body']))
            sqs.deleteMessage(message['ReceiptHandle'])
            
def consume(event, context):
    while(True):
        response = sqs.getMessage(10)
        if(len(response['Messages']) == 0):
            break
    
        mensagens = []
        for msg in response['Messages']:
            mensagens.append({'Id':msg['MessageId'], 'ReceiptHandle':msg['ReceiptHandle']})   
            print(msg)
            print(mensagens)
            sqs.deleteMessage(mensagens)
    