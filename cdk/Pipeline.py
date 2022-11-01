# This stack is based on the following blog post:
# https://aws.amazon.com/blogs/developer/cdk-pipelines-continuous-delivery-for-aws-cdk-applications/
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    pipelines as pipelines,
    CfnOutput,
    aws_apigateway as apigw,
aws_lambda,
)
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from dns import Domains
from accounts_config import accounts
from makerspace import MakerspaceStage
from aws_cdk import App, Stack, Stage, Environment, RemovalPolicy
from constructs import Construct
from makerspace import  MakerspaceStage
from hitcounter import HitCounter
from accounts_config import accounts
from visit import Visit
from cdk_dynamo_table_view import TableViewer
class Pipeline(Stack):
    @property
    def hc_endpoint(self):
        return self._hc_endpoint

    @property
    def hc_viewer_url(self):
        return self._hc_viewer_url
    def __init__(self, app: Construct, id: str, *,
                 env: Environment) -> None:
        super().__init__(app, id, env=env)

        repo = codecommit.Repository(
            self, 'makerspace',
            repository_name="makerspace"
        )

        deploy_cdk_shell_step = ShellStep("Synth",
            # use a connection created using the AWS console to authenticate to GitHub
            input=CodePipelineSource.code_commit(repo, "main"),
            commands=[
                # install dependancies for frontend
                'cd site/visitor-console',
                'npm install',

                # build for beta
                f'VITE_API_ENDPOINT="https://{Domains("Beta").api}" npm run build',
                'mkdir -p ../../cdk/visit/console/Beta',
                'cp -r dist/* ../../cdk/visit/console/Beta',

                # build for prod
                f'VITE_API_ENDPOINT="https://{Domains("Prod").api}" npm run build',
                'mkdir -p ../../cdk/visit/console/Prod',
                'cp -r dist/* ../../cdk/visit/console/Prod',

                'cd ../..',

                # synth the app
                "cd cdk",
                "ls",
                "npm install -g aws-cdk",
                "pip install -r requirements.txt",
                "cdk synth"
            ],
            primary_output_directory="cdk/cdk.out",
        )

        pipeline = CodePipeline(self, "Pipeline",
            synth=deploy_cdk_shell_step,
            cross_account_keys=True  # necessary to allow the prod account to access our artifact bucket
        )




        deploy = MakerspaceStage(self, 'Dev', env=accounts['Dev-ltn'])
        deploy_stage = pipeline.add_stage(deploy)
        # service = deploy.service
        # my_lambda = service.my_lambda
        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestViewerEndpoint",
                env_from_cfn_outputs={
                    "ENDPOINT_URL": deploy.hc_viewer_url
                },
                commands=["curl -Ssf $ENDPOINT_URL"],
            )
        )
        #
        # deploy_stage.add_post(
        #     pipelines.ShellStep(
        #         "TestAPIGatewayEndpoint",
        #         env_from_cfn_outputs={
        #             "ENDPOINT_URL": deploy.hc_endpoint
        #         },
        #         commands=[
        #             "curl -Ssf $ENDPOINT_URL",
        #             "curl -Ssf $ENDPOINT_URL/hello",
        #             "curl -Ssf $ENDPOINT_URL/test",
        #         ],
        #     )
        # )
