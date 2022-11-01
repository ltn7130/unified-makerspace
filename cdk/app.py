#!/usr/bin/env python3

import aws_cdk as cdk
from accounts_config import accounts
from makerspace import MakerspaceStack
from Pipeline import Pipeline
from cdk_workshop_stack import CdkWorkshopStack
app = cdk.App()
# CdkWorkshopStack(app, "MakerSpaceTest",env=accounts['Dev-ltn'])
MakerspaceStack(app, 'Dev', env=accounts['Dev-ltn'])
pipeline = Pipeline(app, 'Pipeline', env=accounts['Dev-ltn'])


# user = os.environ.get("USER")
# stage = f'Dev-{user}'
# dev_environment = accounts.get(stage)

# if dev_environment:
#     MakerspaceStack(app, 'Dev', env=accounts[stage])
# else:
#     print(
#         f'Not creating dev stack: could not locate stage={stage} for user={user}')

app.synth()