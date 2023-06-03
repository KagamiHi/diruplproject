import asyncio

class Server_timer():
    def __init__(self, socket, callback):
        self.socket = socket
        self.callback = callback
        self._task = asyncio.ensure_future(self.start_day())


    async def start_day(self):
        while True:
            server_time = await self.socket.get_time()
            act_time = await self.str_time_to_int_minutes(server_time.time)
            sr_time = await self.str_time_to_int_minutes(server_time.sunrise)
            ss_time = await self.str_time_to_int_minutes(server_time.sunset)
            print (act_time, sr_time, ss_time)

            # if act_time < sr_time:
            #     sunrise_term = (sr_time - act_time) * 5
            #     sunset_term = (ss_time - sr_time) * 5
            # elif act_time > ss_time:
            #     sunrise_term = (sr_time + 1440 - act_time) * 5
            #     sunset_term = (ss_time - sr_time) * 5
            # else:
            #     sunrise_term = None
            #     sunset_term = (ss_time - act_time) * 5
            term = 120
            sunrise_term = term * 5
            sunset_term = term * 5
                
            await self.timer_callback(server_time.time)
            if sunrise_term:
                print (sunrise_term)
                await asyncio.sleep(sunrise_term)
                print('sunrise')
                server_time = await self.socket.get_time()
                await self.timer_callback(f'{server_time.time}, {server_time.sunrise}')
            print (sunset_term)
            await asyncio.sleep(sunset_term)
            print('sunset')
            server_time = await self.socket.get_time()
            await self.timer_callback(f'{server_time.time}, {server_time.sunset}')


    async def str_time_to_int_minutes(self, string):
            time_parts = string.split(':')
            time_in_minutes = int(time_parts[0])*60+int(time_parts[1])
            return time_in_minutes


    async def timer_callback(self, text):
        print(text)