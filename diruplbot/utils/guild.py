

class Guild():
    def __init__(self, inviter, guild):
        self.inviter = inviter
        self.guild = guild

    async def is_valid(self):
        if self.inviter:
            return True
        return False
    
    async def register(self):
        await self.inviter.send(f"{self.inviter.display_name}, hi!")
        print ('register')