#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AmazonCloudfrontCacheGraphqlStack } from '../lib/amazon-cloudfront-cache-graphql-stack';

const app = new cdk.App();
new AmazonCloudfrontCacheGraphqlStack(app, 'AmazonCloudfrontCacheGraphqlStack', {
  env: {
    region: 'us-east-1',
  },
});
