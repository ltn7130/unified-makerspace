#!/usr/bin/env python3

import aws_cdk as cdk
from accounts_config import accounts
from Pipeline import Pipeline
# test sdasd   dasda sd  asdsd
app = cdk.App()
pipeline = Pipeline(app, 'Pipeline', env=accounts['Dev-ltn'])

app.synth()
