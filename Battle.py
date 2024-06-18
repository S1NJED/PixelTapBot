import asyncio
import websockets
import json
from random import randint
from colorama import Fore, Style, Back
from time import sleep
from threading import Thread

class Battle:
    
    def __init__(
        self,
    ):
        self.url = 'https://api-clicker.pixelverse.xyz/api/users'
        with open('./config.json', 'r') as file:
            config = json.load(file)
            
        self.secret = config['secret']
        self.tgId = config['tgId'] # tg-id
        self.initData = config['initData']
        self.hitRate = config['hitRate']

        self.websocket: websockets.WebSocketClientProtocol = None
        self.battleId = ""
        self.superHit: bool = False
        self.strike = {
            "defense": False,
            "attack": False
        }

        self.space = "                                        "
        self.stop_event = asyncio.Event()
    
    async def sendHit(self):
        while not self.stop_event.is_set():
            
            # Stop sending hit if superHit phase occurs
            if self.superHit:
                await asyncio.sleep(0.3)
                continue
            
            content = [
                "HIT",
                {
                    "battleId": self.battleId
                }
            ]
            try:
                await self.websocket.send(f"42{json.dumps(content)}")
            except:
                return
            await asyncio.sleep(self.hitRate)


    async def listenerMsg(self):
        while not self.stop_event.is_set():
            try:
                data = await self.websocket.recv()
            except:
                return
            
            if data.startswith('42'):
                data = json.loads(data.removeprefix('42'))
                
                # Change display
                if data[0] == "HIT":
                    
                    print(f"{self.space}> {self.player1['name']} ({data[1]['player1']['energy']}) {Back.WHITE + Fore.BLACK}VERSUS{Style.RESET_ALL} ({data[1]['player2']['energy']}) {self.player2['name']}", end="\r", flush=True)
                
                elif data[0] == "SET_SUPER_HIT_PREPARE":
                    self.superHit = True
                    pass
                
                elif data[0] == "SET_SUPER_HIT_ATTACK_ZONE":
                    content = [
                        "SET_SUPER_HIT_ATTACK_ZONE",
                        {
                            "battleId": self.battleId,
                            "zone": randint(1, 4)
                        }
                    ]
                    await self.websocket.send(f"42{json.dumps(content)}")
                    
                    self.strike['attack'] = True
                    
                elif data[0] == "SET_SUPER_HIT_DEFEND_ZONE":
                    content = [
                        "SET_SUPER_HIT_DEFEND_ZONE",
                        {
                            "battleId": self.battleId,
                            "zone": randint(1, 4)
                        }
                    ]
                    await self.websocket.send(f"42{json.dumps(content)}")
                    
                    self.strike['defense'] = True
                    
                
                elif data[0] == "END":
                    result = data[1]['result']
                    reward = data[1]['reward']

                    sleep(0.3)
                    print('') 
                    print(f"{self.space}> You {Fore.WHITE}{Back.GREEN if result=='WIN' else Back.RED}{result}{Style.RESET_ALL} {Style.BRIGHT}{reward}{Style.RESET_ALL} coins !")
                    
                    # served send 41
                    await self.websocket.recv()   
                    self.stop_event.set()
                    # print(f"{self.space}> End of the match !")
                    return
                
                try:
                    if ( self.strike['attack'] and not self.strike['defense'] ) or ( self.strike['defense'] and not self.strike['attack'] ):
                        # Wait for result
                        await self.websocket.recv()
                        await self.websocket.recv()
                        
                
                    if self.strike['attack'] and self.strike['defense']:
                        deux = await self.websocket.recv()
                        await self.websocket.send("3")
                        
                        # SUPER_HIT_ROUND_RESULT
                        await self.websocket.recv()
                        self.superHit = False          
                except:
                    pass
    
    async def handleWssFreeze(self, seconds: int):
        await asyncio.sleep(seconds)
        
        if self.stop_event.is_set():
            return
        
        self.stop_event.set()
        self.websocket.close()
        print(f"bot wss has froze, bot is restarting ...")
        
    async def connect(self):
        uri = "wss://api-clicker.pixelverse.xyz/socket.io/?EIO=4&transport=websocket"
        
        async with websockets.connect(uri) as websocket:
            # print(f'{self.space}> Connected to the websockets.')
            self.websocket = websocket
            
            data = await websocket.recv()
            
            # We authenticate ourselves ...
            content = {
                "tg-id": self.tgId,
                "secret": self.secret,
                "initData": self.initData
            }
            await websocket.send(f"40{json.dumps(content)}" )
            
            await websocket.recv()
            
            data = await websocket.recv()
            data = json.loads(data.removeprefix('42'))
            self.battleId = data[1]['battleId']
            self.player1 = {
                "name": data[1]['player1']['username']
            }
            self.player2 = {
                "name": data[1]['player2']['username']
            }

            for i in range(5, 0, -1):
                print(f"{self.space}> The fight start in {Back.RED + Fore.WHITE}{i}{Style.RESET_ALL} seconds.", end="\r", flush=True)
                await asyncio.sleep(1)
            
            listenerMsgTask = asyncio.create_task(self.listenerMsg())
            hitTask = asyncio.create_task(self.sendHit())
            handleWssFreeze = asyncio.create_task(self.handleWssFreeze(180))
            
            await handleWssFreeze
            await listenerMsgTask
            await hitTask
            