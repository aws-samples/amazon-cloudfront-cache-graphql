import urllib.request
import base64
from disallowed_headers import is_blacklisted_or_readonly_header

# Max cacheable size on each header.
CACHE_PAYLOAD_SIZE_LIMIT = 1783

# Max splitted number for request payload.
NUM_SPLIT_MAX = 5

# GraphQL endpoint
GRAPHQL_ENDPOINT = '/queries'


# Execute http request
def http_request(endpoint, method='GET', headers={}, data=None):
    req = urllib.request.Request(endpoint, method=method, headers=headers, data=data)
    res = urllib.request.urlopen(req)
    res_code = res.status
    res_body = res.read().decode('utf-8')
    res_headers = response_headers(res)

    return {
        'status': res_code,
        'headers': remove_disallowed_headers(res_headers),
        'body': res_body
    }


# Convert urllib response header to cloudfront response header format.
def response_headers(res):
    return {
        key.lower(): [{'key': key, 'value': val}]
        for key, val in res.headers.items()
    }


# Remove disallowd headers on lambda@edge
def remove_disallowed_headers(headers):
    return {
        key: val
        for key, val in headers.items()
        if not is_blacklisted_or_readonly_header(key)
    }


# Split request payload
def split_payload(data):
    cursor = 0

    payloads = []

    while True:
        if len(data[cursor:]) <= CACHE_PAYLOAD_SIZE_LIMIT:
            payloads.append(data[cursor:])
            break
        else:
            payloads.append(data[cursor:cursor+CACHE_PAYLOAD_SIZE_LIMIT])
            cursor += CACHE_PAYLOAD_SIZE_LIMIT

    if len(payloads) < NUM_SPLIT_MAX:
        for _ in range(NUM_SPLIT_MAX - len(payloads)):
            payloads.append('')

    return payloads


# Lambda@Edge handler
def handler(event, context):
    cloud_front_event = event['Records'][0]['cf']
    cloud_front_domain_name = cloud_front_event['config']['distributionDomainName']
    request = cloud_front_event['request']
    origin_domain_name = request['origin']['custom']['domainName']

    if request['uri'] == GRAPHQL_ENDPOINT:

        # Convert POST to GET
        if request['method'] == 'POST':
            data = request['body']['data']
            payloads = split_payload(data)

            # If number of splitted payloads exceeds NUM_SPLIT_MAX, the payload is too big to be cached.
            if len(payloads) > NUM_SPLIT_MAX:
                return request

            headers = {
                'Payload0': payloads[0],
                'Payload1': payloads[1],
                'Payload2': payloads[2],
                'Payload3': payloads[3],
                'Payload4': payloads[4],
            }

            # Execute GET request to CloudFront (Itself.)
            return http_request(f'https://{cloud_front_domain_name}{GRAPHQL_ENDPOINT}', headers=headers)

        # Convert GET to POST
        elif request['method'] == 'GET':
            # Check the existance of Payload0 ~ Payload4 headers
            if 'payload0' not in request['headers'] or \
               'payload1' not in request['headers'] or \
               'payload2' not in request['headers'] or \
               'payload3' not in request['headers'] or \
               'payload4' not in request['headers']:
                return request

            # Concat the splitted payloads
            payload = \
                request['headers']['payload0'][0]['value'] + \
                request['headers']['payload1'][0]['value'] + \
                request['headers']['payload2'][0]['value'] + \
                request['headers']['payload3'][0]['value'] + \
                request['headers']['payload4'][0]['value']

            # Decode base64 payload
            data = base64.b64decode(payload)

            headers = {
                'Content-Type': 'application/json',
                'Content-Length': len(data),
            }

            # Execute POST request to origin
            return http_request(f'http://{origin_domain_name}{GRAPHQL_ENDPOINT}', method='POST', data=data, headers=headers)

    # Bypass request
    return request
