## Setup Slack workspace

1. For the purposes of this workshop, we recommend setting up a new temporary Slack workspace. Use the following link to create a new Slack workspace:
https://hooks.slack.com/services/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

2. When you have finished creating your Slack workspace, create a new channel named "security-hub-alerts". This is where we will send notifications from Security Hub using the custom integration. For this exmaple, set the channel visibility to public.

### Setup Slack application for integration

3. Go to the Slack API site, https://api.slack.com .

4. At the top of the page, click Your apps. Then click Create an App.

5. In the Create an app popup. choose From scratch.

6. For App Name input "security-hub-to-slack". For Pick a workspace to develop your app in select the workspace you just created.

7. Click Create App.

8. Open Incoming Webhooks.

9. On the Activate Incoming Webhooks page, switch the toggle to ON.

10. Then at the bottom of the page, click Add New Webhook to Workspace.

11. On the page that asks, "Where should security-hub-alerts post?" Select #security-hub-alerts. Click Allow.

12. Back on the Incoming Webhooks page, copy the Webhook URL you just created. You will need this for sam template.