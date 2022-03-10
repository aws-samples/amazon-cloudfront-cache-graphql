import { Stack, StackProps, CfnOutput, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as cfn from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';

export class AmazonCloudfrontCacheGraphqlStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc');
    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
    });

    const albFargate =
      new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'AlbFargate', {
        cluster,
        desiredCount: 1,
        taskImageOptions: {
          image: ecs.ContainerImage.fromAsset(path.join(__dirname, '..', 'container')),
        },
      });

    albFargate.targetGroup.configureHealthCheck({ path: '/health' });

    const cachePolicy = new cfn.CachePolicy(this, 'CachePolicy', {
      headerBehavior: cfn.CacheHeaderBehavior.allowList('Payload0', 'Payload1', 'Payload2', 'Payload3', 'Payload4'),
      minTtl: Duration.minutes(1),
      defaultTtl: Duration.minutes(1),
    });

    const convertHttpMethod = new cfn.experimental.EdgeFunction(this, 'ConvertHttpMethodLambdaEdge', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'convert-http-method.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '..', 'lambda')),
    });

    const edgeDistribution = new cfn.Distribution(this, 'EdgeDistribution', {
      defaultBehavior: {
        origin: new origins.LoadBalancerV2Origin(albFargate.loadBalancer, {
          protocolPolicy: cfn.OriginProtocolPolicy.HTTP_ONLY,
        }),
        originRequestPolicy: new cfn.OriginRequestPolicy(this, 'OriginRequestPolicy', {
          headerBehavior: cfn.OriginRequestHeaderBehavior.allowList('auth-key'),
        }),
        allowedMethods: cfn.AllowedMethods.ALLOW_ALL,
        edgeLambdas: [
          {
            functionVersion: convertHttpMethod.currentVersion,
            eventType: cfn.LambdaEdgeEventType.ORIGIN_REQUEST,
            includeBody: true,
          },
        ],
        cachePolicy,
      },
    });

    new CfnOutput(this, 'EdgeDistributionEndpoint', {
      value: `https://${edgeDistribution.domainName}`,
    });
  }
}
