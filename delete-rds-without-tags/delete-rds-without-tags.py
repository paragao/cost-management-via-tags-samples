import json
import boto3
import time

rds = boto3.client('rds')

def lambda_handler(event, context):
    '''
        SÓ FUNCIONA PARA CHAMADAS QUE NÃO SEJAM FEITAS PELA CONSOLE
        A console AWS não permite colocar tags no RDS quando a instância é criada, só é possível colocar depois.
        Dessa forma, se você criar um RDS pela console AWS esse script será irá deletar o banco porque ele não vai achar as tags necessárias.
        Se você criar o banco pela CLI ou por uma chamada de SDK (ex: boto3, nodejs, java, etc) então o script irá funcionar porque as tags são definidas na mesma hora da criação.
        
        PARA FUNCIONAR PELA CONSOLE
        é necessário aumentar o tempo de sleep para que o script dê tempo para o usuário criar tags depois de criar o database.
        recomendado colocar pelo menos 2 minutos ou mais. Auemnta o custo de Lambda, porém não muito, e ainda é muito inferior ao custo de ter um RDS que não deveria estar rodadndo no ar.
    '''
    
    time.sleep(120) #se quiser que funcione pela console, aumente o tempo de sleep
    print('evento: {}'.format(event))
    '''
        pega as informações que vem do evento do Amazon CloudWatch Events
        e usa para verificar se o RDS criado tem as tags necessárias
    '''
    dbInstanceId = event['detail']['requestParameters']['dBInstanceIdentifier']
    dbInstanceArn = event['detail']['responseElements']['dBInstanceArn']
    userName = event['detail']['userIdentity']['sessionContext']['sessionIssuer']['userName']
    
    '''
        Tags
    '''
    costcenter = False
    projeto = False
    
    print('dbInstanceId: {},\n dbInstanceArn: {},\n user: {}'.format(dbInstanceId, dbInstanceArn, userName))
    
    try:
        response = rds.list_tags_for_resource(
                ResourceName=dbInstanceArn
            )
    
        '''
            valida se o RDS tem as tags específicas e seta o nome da tag como uma variável booleana
        '''
    
        for tag in response['TagList']:
            if tag['Key'] == 'costcenter':
                costcenter = True
            if tag['Key'] == 'projeto':
                projeto = True
        
        if costcenter and projeto:
            print('RDS criado com as tags certas!')
            return {
                'statusCode': 200,
                'body': json.dumps('Tags estão definidas!')
            }
        else:
            delete = rds.delete_db_instance(
                DBInstanceIdentifier=dbInstanceId,
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True
            )
            print('RDS não tem as tags certas... deletando!')
            
            return {
                'statusCode': 200,
                'body': json.dumps('RDS deletado porque não tinha as tags necessárias!')
            }
    except:
        '''
            se não há tags, deleta o RDS
        '''
        delete = rds.delete_db_instance(
            DBInstanceIdentifier=dbInstanceId,
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=True
        )
        print('RDS não tem as tags certas... deletando!')
        return {
            'statusCode': 200,
            'body': json.dumps('RDS deletado porque não tinha as tags necessárias!')
        }
