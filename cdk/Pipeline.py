# This stack is based on the following blog post:
# https://aws.amazon.com/blogs/developer/cdk-pipelines-continuous-delivery-for-aws-cdk-applications/
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    pipelines as pipelines,
    Environment,
)
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from dns import Domains
from constructs import Construct
from makerspace import MakerspaceStage
from accounts_config import accounts


class Pipeline(Stack):
    def __init__(self, app: Construct, id: str, *, env: Environment) -> None:
        super().__init__(app, id, env=env)

        repo = codecommit.Repository(self, "makerspace", repository_name="makerspace")

        deploy_cdk_shell_step = ShellStep(
            "Synth",
            # use a connection created using the AWS console to authenticate to GitHub.
            input=CodePipelineSource.connection("ltn7130/unified-makerspace", "mainline",
                                                connection_arn="arn:aws:codestar-connections:us-east-1:446249877359:connection/c5a35733-c701-439d-955e-e1140838d0b7"
                                                ),
            commands=[
                # install dependancies for frontend
                "cd site/visitor-console",
                "npm install",
                # build for beta
                f'VITE_API_ENDPOINT="https://{Domains("Beta").api}" npm run build',
                "mkdir -p ../../cdk/visit/console/Beta",
                "cp -r dist/* ../../cdk/visit/console/Beta",
                # build for prod
                f'VITE_API_ENDPOINT="https://{Domains("Prod").api}" npm run build',
                "mkdir -p ../../cdk/visit/console/Prod",
                "cp -r dist/* ../../cdk/visit/console/Prod",
                "cd ../..",
                # synth the app
                "cd cdk",
                "ls",
                "npm install -g aws-cdk",
                "pip install -r requirements.txt",
                "cdk synth",
            ],
            primary_output_directory="cdk/cdk.out",
        )

        pipeline = CodePipeline(
            self,
            "Pipeline",
            synth=deploy_cdk_shell_step,
            cross_account_keys=True,  # necessary to allow the prod account to access our artifact bucket
        )

        deploy = MakerspaceStage(self, "Dev", env=accounts["Dev-ltn"])
        deploy_stage = pipeline.add_stage(deploy)
        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestViewerEndpoint",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_viewer_url},
                commands=["curl -Ssf $ENDPOINT_URL"],
            )
        )

        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestAPIGatewayEndpoint",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_endpoint},
                commands=[
                    "curl --location -X POST $ENDPOINT_URL/visit",
                ],
            )
        )

        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestBetaFrontend",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_endpoint},
                commands=[
                    "curl https://beta-visit.cumaker.space/",
                ],
            )
        )

        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestProdFrontend",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_endpoint},
                commands=[
                    "curl https://visit.cumaker.space/",
                ],
            )
        )