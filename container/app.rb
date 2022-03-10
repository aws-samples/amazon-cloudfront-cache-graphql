# coding: utf-8
require 'sinatra'
require 'securerandom'

#
# GraphQL Mock Server
#
# The endpoint returns random string.
#

set :bind, '0.0.0.0'
set :port, 80

# Healthcheck Endpoint
get '/health' do
  ''
end

# GET Endpoint
get '/' do
  # debug
  p params
  p request.env

  SecureRandom.alphanumeric(8)
end

# GraphQL Endpoint
post '/queries' do
  # Some internal heavy graphql query execution
  sleep(rand(0.5..1.0))

  # debug
  p params
  p request.env

  if request.body.size > 0
    request.body.rewind
    p request.body.read
  end

  SecureRandom.alphanumeric(8)
end
