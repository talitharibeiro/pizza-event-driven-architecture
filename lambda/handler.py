import json
import boto3
import os

# Inicializando clientes SQS
dynamodb = boto3.client('dynamodb')
sqs = boto3.client('sqs')

# Filas SQS
EM_PREPARACAO_QUEUE_URL = os.environ['s3://pizzaria356959/em-preparacao/']
PRONTO_QUEUE_URL = os.environ['s3://pizzaria356959/pronto/']

# Nome da tabela DynamoDB
DYNAMODB_TABLE_NAME = os.environ['pedidos-pizzaria']

# Função handler do Lambda para processar eventos do S3
def lambda_handler(event, context):
    for record in event['Records']:
        # Obter informações do evento do S3
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        print(f"Bucket: {bucket_name}, Object Key: {object_key}")

        # Determinação da fila com base no nome do diretório
        if 'em-preparacao' in object_key:
            queue_url = EM_PREPARACAO_QUEUE_URL
            print("Diretório identificado: em-preparacao")
        elif 'pronto' in object_key:
            queue_url = PRONTO_QUEUE_URL
            print("Diretório identificado: pronto")
        else:
            print(f"Pasta não reconhecida no caminho do objeto: {object_key}")
            continue

        # Cria a mensagem a ser enviada
        message_body = json.dumps({
            'bucket_name': bucket_name,
            'object_key': object_key
        })
        print(f"Mensagem criada: {message_body}")

        # Enviar mensagem para a fila SQS correspondente
        try:
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            print(f"Mensagem enviada para {queue_url} com ID: {response['MessageId']}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para SQS: {str(e)}")

# Função handler do Lambda para processar mensagens da fila em-preparacao-pizzaria
def lambda_handler_em_preparacao(event, context):
    for record in event['Records']:
        message_body = json.loads(record['body'])
        print(f"Processando mensagem da fila em-preparacao-pizzaria: {message_body}")

        # Extrair informações do object_key
        object_key = message_body.get('object_key')
        pedido, cliente = object_key.split('/')[1].split('-')
        print(f"Pedido: {pedido}, Cliente: {cliente}")

        # Inserir item na tabela DynamoDB
        try:
            dynamodb.put_item(
                TableName=DYNAMODB_TABLE_NAME,
                Item={
                    'pedido': {'S': pedido},
                    'status': {'S': 'em preparação'},
                    'cliente': {'S': cliente},
                    'bucket': {'S': message_body.get('bucket_name')}
                }
            )
            print(f"Pedido inserido com sucesso na tabela DynamoDB: {pedido}")
        except Exception as e:
            print(f"Erro ao inserir item na tabela DynamoDB: {str(e)}")

# Função handler do Lambda para processar mensagens da fila pronto-pizzaria
def lambda_handler_pronto(event, context):
    for record in event['Records']:
        message_body = json.loads(record['body'])
        print(f"Processando mensagem da fila pronto-pizzaria: {message_body}")

        # Extrair informações do object_key
        object_key = message_body.get('object_key')
        pedido, cliente = object_key.split('/')[1].split('-')
        print(f"Pedido: {pedido}, Cliente: {cliente}")

        # Inserir item na tabela DynamoDB
        try:
            dynamodb.put_item(
                TableName=DYNAMODB_TABLE_NAME,
                Item={
                    'pedido': {'S': pedido},
                    'status': {'S': 'pronto'},
                    'cliente': {'S': cliente},
                    'bucket': {'S': message_body.get('bucket_name')}
                }
            )
            print(f"Pedido inserido com sucesso na tabela DynamoDB: {pedido}")
        except Exception as e:
            print(f"Erro ao inserir item na tabela DynamoDB: {str(e)}")