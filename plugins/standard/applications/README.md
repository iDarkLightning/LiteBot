# Applications

This plugin creates tickets on discord based on responses to a google form

## Usage

In order to use this plugin, you firstly need to link your google form to a spreadsheet.

![create-spreadhseet](assets/create-spreadsheet.png)

Next, follow [these instructions](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account) to create a google service account.

Once you have downloaded the JSON file, rename it to `creds.json` and copy paste it into `plugins/applications/`.
It should be on the same level as this README file.

## Configuration
Once you have the credentials set up, you need to go to `settings.json` or use the `settings` command to configure the following settings:
* `spreadsheet_url`: The URL for the spreadsheet that you created
* `discord_name_question`: The question on your form that identifies the user's discord account. The user **must** respond in the format `name#discriminator` (i.e iDarkLightning#3514) in order for their account to be recognized. Otherwise, you will need to manually add them to their ticket after the fact.
* `applications_category`: The category in which the tickets will be created
* `verifiy_channel`: The channel in which applications will be posted for vouches before the ticket is created.
* `voting_channel`: The channel in which the votes for the applicant will be posted
* `required_vouches`: The amount of vouches an application will require before its ticket is made. If this is set to 0, then the vouching process will be skipped and the ticket will be created immediately
* `vouch_expire_time`: The amount of time before an application sent for vouching expires. 48 hours by default.
* `vote_yes_emoji`: The emoji that should be used for the `yes` reaction on the vote. Defaults to: ☑
* `vote_no_emoji`: The emoji that should be used for the `no` reaction on the vote. Defaults to: ❌