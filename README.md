# Bitbucket Pipelines Pipe: TEAMS Notify

Sends a custom notification to [Teams].

You can configure [Teams integration] for your repository to get notifications on standard events, such as build failures and deployments. Use this pipe to send your own additional notifications at any point in your pipelines.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: e210/teams-notify:0.0.1
  variables:
    WEBHOOK_URL: '<string>'
    # MESSAGE: '<string>'  # Optional.
    # TITLE: '<string>'  # Optional.
    # PAYLOAD_FILE: '<string>' # Optional.
    # DEBUG: '<boolean>' # Optional.
```

## Variables

| Variable        | Usage                                                                                                                                                               |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| WEBHOOK_URL (*) | Incoming Webhook URL. It is recommended to use a secure repository variable.                                                                                        |
| MESSAGE (1)     | Notification attachment message. Required unless `PAYLOAD_FILE` is used.                                                                                            |
| TITLE           | Notification pretext. Default: `Notification sent from <a href='https://bitbucket.org'>Bitbucket</a>`. Used with `MESSAGE`. Required unless `PAYLOAD_FILE` is used. |
| PAYLOAD_FILE(1) | Path to JSON file containing custom payload. Required unless MESSAGE are used.                                                                                      |
| DEBUG           | Turn on extra debug information. Default: `false`.                                                                                                                  |

_(*) = required variable._
_(1) = required variable. Required one of the multiple options._


## Prerequisites

To send notifications to Team, you need an Incoming Webhook URL ([Teams integration]). 

## Examples

Basic example:
    
```yaml
script:
  - pipe: e210/teams-notify:0.0.1
    variables:
      WEBHOOK_URL: $WEBHOOK_URL
      MESSAGE: 'Hello, world!'
```

Advanced example:

If you want to pass complex string with structure elements, use double quotes

```yaml
script:
  - pipe: e210/teams-notify:0.0.1
    variables:
      WEBHOOK_URL: $WEBHOOK_URL
      MESSAGE: '"[${ENVIRONMENT_NAME}] build has exited with status $build_status"'
```

Use custom payload and modify payload with the [envsubst] program that substitutes the values of environment variables:

```yaml
script:
  - envsubst < "payload.json.template" > "payload.json"
  - pipe: e210/teams-notify:0.0.1
    variables:
      WEBHOOK_URL: $WEBHOOK_URL
      PAYLOAD_FILE: payload.json
```


## Support

If you're reporting an issue, please include:

* the version of the pipe
* relevant logs and error messages
* steps to reproduce

## License

Copyright (c) 2024 Ezio Caffi.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.

For more information, visit the [repository on Bitbucket].

[Teams]: https://www.microsoft.com/en-us/microsoft-teams/group-chat-software/
[Teams integration]: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
[envsubst]: https://www.gnu.org/software/gettext/manual/html_node/envsubst-Invocation.html
[repository on Bitbucket]: https://bitbucket.org/e210/teams-notify
