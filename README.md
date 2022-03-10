# Cache GraphQL on Amazon CloudFront

Amazon CloudFront does not cache GraphQL queries. This is because GraphQL queries are internally HTTP POST requests. However, for non-mutation queries, there are cases where you may want to cache them in edge. In this repository, show you how to cache GraphQL query responses in Amazon CloudFront by converting the HTTP method in Lambda@Edge.

## Architecture and Cache Strategy

![](/imgs/architecture.png)

### How to convey the request payload?

First, when making a GET request to Amazon CloudFront, it is not possible to include a payload in the HTTP body. Therefore, it is necessary to pass the request body as the value of the query parameter or header. Due to Amazon CloudFront restrictions, the query parameter can only be 128 characters long, so the header value, which can be up to 1783 characters long, is used. In addition, by splitting the payload into 5 parts, we are able to cache GraphQL payloads up to 1783 * 5 = 8915 bytes. For payloads larger than that, we bypass the request to the origin.

## Deployment

We will deploy the project using [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html). First, we need to bootstrap it. Run the following command in the root directory.

```bash
npx cdk bootstrap --region us-east-1
```

Since Lambda@Edge will be deployed to us-east-1, you need to specify the region to bootstrap. If you want to deploy a stack other than Lambda@Edge to a region other than us-east-1, bootstrap it in the same way as the above command. The region where the stack other than Lambda@Edge will be deployed are defined in [/bin/amazon-cloud-front-cache-graphql.ts](/bin/amazon-cloudfront-cache-graphql.ts).

Run the following command to deploy the all stacks.
```bash
npx cdk deploy --all
```

If the deployment is successful, the CloudFront endpoint will be output.

## Check the Behavior

Run the following command multiple times. If the response string is the same, then the cache is working. If you change the query even slightly, the cache key will change and you will get a different string. Also, the TTL is set to 1 minute, so if more than 1 minute passes, it should be a different string. Replace the `<YOUR_CLOUDFRONT_ENDPOINT>` to the deployed endpoint.

```bash
curl -XPOST -d '{"query":"xxx"}' -H "Content-Type:application/json" <YOUR_CLOUDFRONT_ENDPOINT>/queies
```

## For the Production Workloads

There are a few things that need to be considered before applying this to production workloads.

First, let's talk about mutations. If a GraphQL query contains a mutation, the request should not be cached. Therefore, if there is a possibility that the query is a mutation, we need to parse the query in Lambda@Edge and check if it is a mutation or not. If it is a mutation, bypass the the request to the origin.

Next, let's talk about authentication. If authentication is included, that is, if the response is user-specific, the authentication header must also be a cache key. In that case, add the authentication header to the allowed headers in CachePolicy. This is to avoid security incidents where cached content is returned without any authentication. Simply put, it is to prevent one user's cached content from becoming another user's response.

## Cleanup

Run the following command.

```bash
cdk destroy --all
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
