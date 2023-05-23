from dirupl.address_directory.models import Credential
from dirupl.users.models import CustomUser

from steam.webauth import WebAuth
from steam.webauth import CaptchaRequired, LoginIncorrect, EmailCodeRequired, TwoFactorCodeRequired
from bs4 import BeautifulSoup as bs
import re
import json
import requests
from uuid import uuid4

import logging

log = logging.getLogger("Link_app")

class Link_app:
    def __init__(self, bot, ctx, login, password) -> None:
        self.bot = bot
        self.ctx = ctx
        self.channel = ctx.channel
        self.login = login
        self.password = password


    async def check_bd(self):

        user = await CustomUser.objects.filter(discord_user_id=self.ctx.author.id).afirst()

        if user is None:
            await self.channel.send ('You are not registred')
            return False
        
        user_credential = await Credential.objects.filter(user=user).afirst()

        if user_credential is None:
            try:
                user_credential = await Credential.objects.acreate(user=user)
            except KeyError as e:
                log.debug(f"Keyerror: {e}")
                await self.channel.send ('Registration is not available at the moment')
                return False

        # if user_credential.rust_registration_status:
        #     await self.channel.send ('You are already linked!')
        #     return False
        self.user_credential = user_credential
        return True

### main function ###
    async def link(self):

        if not await self.check_bd():
            return
        
        rustplus_auth_token = await self.LinkSteamWithRustPlus()
        if rustplus_auth_token is None:
            return
        
        expoPushToken = await self.getExpoPushToken()
        if expoPushToken is None:
            log.debug(f"getExpoPushToken failed for {self.ctx.author.id}")
            await self.channel.send ('Linking is failed. Try again later.')
            return

        res = await self.registerWithRustPlus(rustplus_auth_token, expoPushToken)
        if res.status_code != 200:
            await self.channel.send ('Linking is failed. Try again later.')
            return

        self.user_credential.rust_registration_status = True
        await self.user_credential.asave()

        await self.channel.send ('You are linked!\nDelete your link_steam command, for safety!\n')
        return


    async def LinkSteamWithRustPlus(self):
        
        URL = "https://companion-rust.facepunch.com/login"

        session = await self.login_steam()
        if session is None:
            return
        
        response = session.get(URL)

        payload = await  self.rust_page_payload(response)
        response = session.post(URL,data=payload)

        payload = await self.steam_page_payload(response)
        response = session.post(response.url,data=payload)
        
        return await  self.take_token(response)

    async def login_steam(self, captcha='', email_code='', twofactor_code='', language='english'):
        user = WebAuth(self.login)
        requires_list=[]
        while True:
            try:
                return user.login(self.password, captcha, email_code, twofactor_code, language)
            except (LoginIncorrect, CaptchaRequired) as exp:
                if isinstance(exp, LoginIncorrect):
                    await self.channel.send ('Incorrect login or password. Try again.')
                    return
                    
                if isinstance(exp, CaptchaRequired):
                    # if exp in requires_list:
                    #     return
                    # requires_list.append(exp)
                    # await self.channel.send (f'Pass captcha: {user.captcha_url}')
                    # captcha = None
                    # user.login(password=self.password, captcha=captcha)
                    await self.channel.send ("Can't pass captcha. Try again later.")
                    return
                        
            except (EmailCodeRequired, TwoFactorCodeRequired) as exp:
                if type(exp) in requires_list:
                    await self.channel.send ("Linking failed, please try again.")
                    return
                
                requires_list.append(type(exp))

                def check(m):
                    return m.channel == self.channel
                
                if isinstance(exp, EmailCodeRequired):
                    await self.channel.send ("Enter email code: ")
                    msg = await self.bot.wait_for('message', check=check)
                    email_code = msg.content

                if isinstance(exp, TwoFactorCodeRequired):
                    await self.channel.send ("Enter 2FA code: ")
                    msg = await self.bot.wait_for('message', check=check)
                    twofactor_code = msg.content
                  
    async def rust_page_payload(self, response):
        payload_names = ['returnUrl','__RequestVerificationToken']
        payload = {}

        soup = bs(response.content, "lxml").find('form').find_all('input')
        for input in soup:
            input_attrs = input.attrs
            if 'name' in input_attrs:
                if input_attrs['name'] in payload_names:
                    if 'value' in input_attrs:
                        payload[input_attrs['name']]=input_attrs['value']
                    else:
                        payload[input_attrs['name']]=''
        return payload

    async def steam_page_payload(self, response):
        payload_names = ['action','openid.mode','openidparams','nonce']
        payload = {}

        soup = bs(response.content, "lxml").find(id='openidForm').find_all('input')
        for input in soup:
            input_attrs = input.attrs
            if 'name' in input_attrs:
                if input_attrs['name'] in payload_names:
                    payload[input_attrs['name']]=input_attrs['value']
        
        return payload

    async def take_token(self, response):
        soup = bs(response.content.decode('utf-8'), 'html.parser')
        data = str(soup.find('script'))
        return json.loads(data[(re.search(r'\(\'', data).start()+2):re.search(r"\'\)\;", data).start()].replace('\\',''))['Token']


    async def getExpoPushToken(self):
        fcm_token = self.user_credential.fcm_token
        if fcm_token is None:
            return
        
        json_obj = {
            'deviceId': uuid4(),
            'experienceId': '@facepunch/RustCompanion',
            'appId': 'com.facepunch.rust.companion',
            'deviceToken': fcm_token,
            'type': 'fcm',
            'development': 'false'
        }
        response = requests.post('https://exp.host/--/api/v2/push/getExpoPushToken', json_obj)
        try:
            return response.json()['data']['expoPushToken']
        except KeyError as e:
            log.debug(f'getExpoPushToken Keyerror: {e}')
            return

    async def registerWithRustPlus(self, authToken, expoPushToken):
        headers = {"Content-Type": "application/json"}
        data = {
            'AuthToken': authToken,
            'DeviceId': 'rustplus.js',
            'PushKind': 0,
            'PushToken': expoPushToken
        }
        response = requests.post('https://companion-rust.facepunch.com:443/api/push/register', headers=headers, json=data)
        return response

# class LinkAppException(Exception):
#     pass

# class LSWRustPlusError(LinkAppException):
#     pass