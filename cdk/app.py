#!/usr/bin/env python3

import aws_cdk as cdk
from accounts_config import accounts
from Pipeline import Pipeline
from cdk_workshop_stack import CdkWorkshopStack
app = cdk.App()
# CdkWorkshopStack(app, "WorkshopStackTest")
pipeline = Pipeline(app, 'Pipeline', env=accounts['Dev-ltn'])
app.synth()
