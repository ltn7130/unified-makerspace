from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda,
    aws_apigateway as apigw,
    App, Stack, Stage, Environment, PhysicalName
)
# from makerspace import  MakerspaceStage
from hitcounter import HitCounter
from accounts_config import accounts
from visit import Visit
from cdk_dynamo_table_view import TableViewer
from makerspace import MakerspaceStage
from api_gateway import SharedApiGateway
class CdkWorkshopStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        test_stage = MakerspaceStage(self, 'Dev', env=accounts['Dev-ltn'])
        service = test_stage.service
        # my_lambda = service.my_lambda
        # gateway = service.api_gateway.get_api()


        my_lambda = aws_lambda.Function(
            self, 'HelloHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )
        hello_with_counter = HitCounter(
            self, 'HelloHitCounter',
            downstream=my_lambda
        )
        gateway = apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=hello_with_counter._handler
        )

        tv = TableViewer(
            self, 'ViewHitCounter',
            title='Hello Hits',
            table=hello_with_counter.table
        )

        self._hc_endpoint = CfnOutput(
            self, 'GatewayUrl',
            value=gateway.url
        )

        self._hc_viewer_url = CfnOutput(
            self, 'TableViewerUrl',
            value=tv.endpoint
        )
