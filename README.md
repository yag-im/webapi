# webapi: web api gateway

Provides CRUD APIs for handling all queries from the UI, including user authentication, application search, and more.
Check https://yag.im/api/docs/ for details.

## Development

### Prerequisite

Create *.devcontainer/secrets.env* file:

    SQLDB_PASSWORD=
    FLASK_SECRET_KEY=***VALUE***
    FLASK_SECURITY_PASSWORD_SALT=***VALUE***

    SQLDB_PASSWORD=***VALUE***

    # https://discord.com/developers/applications/1251213147776225341/oauth2
    # https://console.cloud.google.com/apis/credentials/oauthclient/454405087013-0pc1gvsivodjea0dkhb5uqtop3acrkl8.apps.googleusercontent.com?authuser=2&project=yag-im
    # https://www.reddit.com/prefs/apps
    # https://dev.twitch.tv/console/apps/g9pl60vjz9ejuucgbpnzm0eb78ug4d

    DISCORD_OAUTH_CLIENT_ID=***VALUE***
    GOOGLE_OAUTH_CLIENT_ID=***VALUE***
    REDDIT_OAUTH_CLIENT_ID=***VALUE***
    TWITCH_OAUTH_CLIENT_ID=***VALUE***

    DISCORD_OAUTH_CLIENT_SECRET=***VALUE***
    GOOGLE_OAUTH_CLIENT_SECRET=***VALUE***
    REDDIT_OAUTH_CLIENT_SECRET=***VALUE***
    TWITCH_OAUTH_CLIENT_SECRET=***VALUE***


The following devcontainers should be up and running:

    appsvc
    sqldb

Then simply open this project in any IDE that supports devcontainers (VSCode is recommended).

## Test

You need to use "localhost" as OAuth providers wouldn't work with other domains.

1. Run yag-mcc
2. Open http://localhost:8080/api/, logout if needed
3. Login using any auth method
4. Now you can trigger API calls from http://localhost:8080/api/docs/

## Swagger UI notes

    git clone --depth=1 --single-branch --branch "master" https://github.com/swagger-api/swagger-ui.git /tmp/swagger-ui
    cp /tmp/swagger-ui/dist/*.css /workspaces/webapi/webapi/static/css
    cp /tmp/swagger-ui/dist/*.png /workspaces/webapi/webapi/static/img
    cp /tmp/swagger-ui/dist/*.js /workspaces/webapi/webapi/static/js
    cp /tmp/swagger-ui/dist/index.html /workspaces/webapi/webapi/templates/swaggerui.html

Then modify:

    templates/swaggerui.html
    js/swagger-initializer.js
