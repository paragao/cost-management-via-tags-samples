import json
import boto3
import time

logs = boto3.client('logs')

def lambda_handler(event, context):
    print('evento: {}'.format(event))
    
    # quantidade maxima de dias para reter os logs
    days = 7
    
    '''
        pega as informações que vem do evento do Amazon CloudWatch Events
        e usa para verificar se a politica de retenção do log-group mudou para "never"
    '''
    logGroup = event['detail']['requestParameters']['logGroupName']
    userName = event['detail']['userIdentity']['sessionContext']['sessionIssuer']['userName']
    apiCalled = event['detail']['eventName']
    
    print('user {}, loggroup: {}'.format(userName, logGroup))
    

    '''
        Caso: deletar o tempo de retenção se diferent do pré-definido        
    '''
    if apiCalled == 'DeleteRetentionPolicy':
        print('Retenção deletada! Resetando para tempo pré-definido de {} dias.'.format(days))
        newRetention = logs.put_retention_policy(
                            logGroupName=logGroup,
                            retentionInDays=days
                        )
        
    '''
        Caso 2: alterar o LogGroup para outro tempo de retenção difernete do pré-definido
    '''    
    if apiCalled == 'PutRetentionPolicy':
        retention = event['detail']['requestParameters']['retentionInDays']
        
        if (retention != days):
            print('Retenção modificada! Resetando para tempo pré-definido de {} dias.'.format(days))
            newRetention = logs.put_retention_policy(
                                logGroupName=logGroup,
                                retentionInDays=days
                            )
    
    '''
        Caso 3: criar um novo LogGroup com o tempo de retenção diferente do pré-definido
    '''
    if apiCalled == 'CreateLogGroup':
        response = logs.describe_log_groups(
                        logGroupNamePrefix=logGroup
                    )
        print(response)
        
        for log in response['logGroups']:
            print('logGroups:{}'.format(log))
            retention = log['retentionInDays'] if log['retentionInDays'] else False
            print('retention: {}'.format(retention))
        
        if (not retention) or (retention != days):
            print('Retenção fora do padrão! Resetando para tempo pré-definido de {} dias.'.format(days))
            newRetention = logs.put_retention_policy(
                                logGroupName=logGroup,
                                retentionInDays=days
                            )
        else: 
            print('Nenhuma condição atendida. Nada a fazer')

