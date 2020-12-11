import gspread, discord

class Applications(commands.Cog):
    COG_NAME = 'applications'
    def __init__(self, client):
        self.client = client
        self.cursor = self.client.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS apps (
            channel_id integer UNIQUE,
            user_id integer,
            application text,
            application_embed text) """)

    async def on_cog_load(self):
        if not self.config.get('spreadsheet_url'):
            raise ValueError('Missing a spreadsheet URL')

        if not self.config.get('applications_category'):
            raise ValueError('Missing an applications category')

        if not self.config.get('voting_channel'):
            raise ValueError('Missing a voting channel')

        if not self.config.get('discord_name_question'):
            raise ValueError('Missing a discord name question')
        
        self.gc = gspread.service_account('./modules/applications/creds.json')
        spreadsheet = self.gc.open_by_url(self.config['spreadsheet_url'])
        self.worksheet = spreadsheet.get_worksheet(0)
        self.current_applications = len(self.worksheet.get_all_values())

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(self.client.guild_id)
        self.voting_channel = discord.utils.get(self.guild.text_channels, id=self.config['voting_channel'])
        self.application_category = self.config['applications_category']
        self.new_application.start()

    @tasks.loop(seconds=10)
    async def new_application(self):
        if len(self.worksheet.get_all_values()) > self.current_applications:
            print('New Application Has Been Recieved!')
            self.current_applications += 1
            answers = self.worksheet.row_values(self.current_applications)
            questions = self.worksheet.row_values(1)
            await self.create_application(answers, questions)

    async def create_application(self, answers, questions):
        application_full = dict(zip(questions, answers))
        application = {k: v for k, v in application_full.items() if v is not None}
        name = application[self.config['discord_name_question']].split('#')
        channel = await self.guild.create_text_channel(name=f'{name[0]} application',
                                                       category=self.client.get_channel(self.application_category))

        try:
            applicant = list(filter(lambda u: u.name == name[0] and u.discriminator == name[1], self.guild.members))[0]
            await channel.set_permissions(applicant, read_messages=True, send_messages=True, attach_files=True)
        except IndexError:
            print('Invalid Discord Name Was Entered')
            await channel.send('Applicant applied with an invalid discord name, or have left the server')
            return

        embeds = self.create_embed(application)
        embed_dicts = [str(embed.to_dict()) for embed in embeds]

        with self.client.db:
            self.cursor.execute('INSERT INTO apps VALUES (?, ?, ?, ?)',
                                (channel.id, applicant.id, str(application), '|'.join(embed_dicts)))

        for embed in embeds:
            embed_message = await channel.send(embed=embed)
            await embed_message.pin()
        await channel.send(f'Thank you for applying {applicant.mention}. We will be with you shortly!')

        voting_message = await self.voting_channel.send(
            embed=discord.Embed(title=f'Vote on {name[0].upper()}', color=0xADD8E6))
        await voting_message.add_reaction('\N{THUMBS UP SIGN}')
        await voting_message.add_reaction('\N{THUMBS DOWN SIGN}')

    def create_embed(self, application):
        embed_max = 25
        embed_list = []
        question_list = [question for question in application.keys()]
        if len(application) > embed_max:
            question_parts = [question_list[i:i + embed_max] for i in range(0, len(application), embed_max)]
            for question_part in question_parts:
                embed = self.embed_questions(question_part, application)
                embed_list.append(embed)
        else:
            embed = self.embed_questions(question_list, application)
            embed_list.append(embed)

        return embed_list

    def embed_questions(self, question_list, application):
        name = application[self.config['discord_name_question']].split('#')
        embed = discord.Embed(
            title=f'{name[0]} application'.upper(),
            color=0xADD8E6
        )
        for question in question_list:
            if question != 'Timestamp':
                if len(application[question]) > 1024:
                    answer_parts = [application[question][i:i + 1024] for i in
                                    range(0, len(application[question]), 1024)]
                    for part in range(len(answer_parts)):
                        if part == 0:
                            embed.add_field(name=question, value=answer_parts[part], inline=False)
                        elif part > 0:
                            embed.add_field(name='^ Extended', value=answer_parts[part], inline=False)
                else:
                    if application[question]:
                        embed.add_field(name=question, value=application[question], inline=False)

        embed.set_footer(text=application['Timestamp'])

        return embed
