import re

# Disallowed headers on edge functions
# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-restrictions.html#edge-function-restrictions-all
_BLACKLISTED_HEADERS = [
    'Connection',
    'Expect',
    'Keep-Alive',
    'Proxy-Authenticate',
    'Proxy-Authorization',
    'Proxy-Connection',
    'Trailer',
    'Upgrade',
    'X-Accel-Buffering',
    'X-Accel-Charset',
    'X-Accel-Limit-Rate',
    'X-Accel-Redirect',
    # X-Amz-Cf-*,
    'X-Amzn-Auth',
    'X-Amzn-Cf-Billing',
    'X-Amzn-Cf-Id',
    'X-Amzn-Cf-Xff',
    'X-Amzn-Errortype',
    'X-Amzn-Fle-Profile',
    'X-Amzn-Header-Count',
    'X-Amzn-Header-Order',
    'X-Amzn-Lambda-Integration-Tag',
    'X-Amzn-RequestId',
    'X-Cache',
    # X-Edge-*,
    'X-Forwarded-Proto',
    'X-Real-IP'
]

blacklisted_headers_lower = [header.lower() for header in _BLACKLISTED_HEADERS]


def is_blacklisted_header(header_name):
    pattern = re.compile(r'^x-(amz-cf|edge)-+')
    return header_name.lower() in blacklisted_headers_lower or pattern.match(header_name.lower())


# Read-only headers in origin request events (Lambda@Edge only)
# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-restrictions.html#edge-function-restrictions-all
_READONLY_HEADERS = [
    'Accept-Encoding',
    'Content-Length',
    'If-Modified-Since',
    'If-None-Match',
    'If-Range',
    'If-Unmodified-Since',
    'Transfer-Encoding',
    'Via'
]

readonly_headers_lower = [header.lower() for header in _READONLY_HEADERS]


def is_readonly_header(header_name):
    return header_name.lower() in readonly_headers_lower


def is_blacklisted_or_readonly_header(header_name):
    return is_blacklisted_header(header_name) or is_readonly_header(header_name)
