FROM ruby:3.1.0

WORKDIR /app

EXPOSE 80

RUN bundle config set --local path 'vendor/bundle'

COPY Gemfile .

RUN bundle install

COPY *.rb .

ENTRYPOINT ["bundle", "exec", "ruby", "app.rb"]
