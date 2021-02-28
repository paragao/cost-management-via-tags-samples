import json
import boto3
import time

s3 = boto3.client('s3')

def lambda_handler(event, context):
    time.sleep(1)
    print('evento: {}'.format(event))
    '''
        pega as informações que vem do evento do Amazon CloudWatch Events
        e usa para verificar se o bucket criado tem as tags necessárias
    '''
    bucketName = event['detail']['requestParameters']['bucketName']
    userName = event['detail']['userIdentity']['sessionContext']['sessionIssuer']['userName']
    costcenter = False
    projeto = False
    
    print('bucket {} , user {}'.format(bucketName, userName))
    
    try:
        response = s3.get_bucket_tagging(
        Bucket=bucketName
        )
    
        '''
            valida se o bucket tem as tags específicas e seta o nome da tag como uma variável booleana
        '''
    
        for tag in response['TagSet']: 
            if tag['Key'] == 'costcenter':
                costcenter = True
            if tag['Key'] == 'projeto':
                projeto = True
        
        if costcenter and projeto: 
            print('bucket criado com as tags certas!')
            return { 
                'statusCode': 200,
                'body': json.dumps('Tags estão definidas!')
            }
        else:
            delete = s3.delete_bucket(
                Bucket=bucketName,
            )
            print('bucket não tem as tags certas... deletando!')
            return {
                'statusCode': 200,
                'body': json.dumps('Bucket deletado porque não tinha as tags necessárias!')
            }        
    except:
        '''
            se não há tags, deleta o bucket
        '''
        delete = s3.delete_bucket(
            Bucket=bucketName,
        )
        print('bucket não tem as tags certas... deletando!')
        return {
            'statusCode': 200,
            'body': json.dumps('Bucket deletado porque não tinha as tags necessárias!')
        }
