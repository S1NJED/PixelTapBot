import requests
import json
from time import sleep
from colorama import Fore, Back, Style

class UserPixel:
    
    def __init__(self):
        with open('./config.json', 'r') as file:
            self.config = json.load(file)
            
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "secret": self.config['secret'],
            "tg-id": self.config['tgId'],
            "initData": self.config['initData']
        }
        
        self.space = "                                        "
    
    def claim(self):
        url = "https://api-clicker.pixelverse.xyz/api/mining/claim"
        req = requests.post(url, headers=self.headers)
        data = req.json()
        print(f"{self.space}> Claimed {Back.YELLOW + Fore.BLACK}{int(data['claimedAmount'])}{Style.RESET_ALL} coins !")

    def getUser(self):
        url = "https://api-clicker.pixelverse.xyz/api/users"
        req = requests.get(url, headers=self.headers)
        return req.json()
    
    def upgrade(self, petId: str):
        url = f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{petId}/level-up"

        req = requests.post(url, headers=self.headers)
        data = req.json()
        return data
    
    def upgradePets(self):
        print(f"{self.space}> Checking pets to upgrade ...")
        data = self.getUser()

        currBalance = data['clicksCount']
        
        petsUrl = "https://api-clicker.pixelverse.xyz/api/pets"
        req = requests.get(petsUrl, headers=self.headers)
        data = req.json()
        pets = data['data']
        
        for pet in pets:
            
            if currBalance >= pet['userPet']['levelUpPrice']:
                self.upgrade(pet['userPet']['id'])
                print(f"{self.space}> Sucessfully {Style.BRIGHT}upgraded{Style.RESET_ALL} pet {Back.YELLOW + Fore.BLACK}{pet['name']}{Style.RESET_ALL}")
                sleep(0.5)

    def getStats(self):
        url = "https://api-clicker.pixelverse.xyz/api/battles/my/stats"
        req = requests.get(url, headers=self.headers)
        return req.json()
    
    def isBroken(self):
        url = "https://api-clicker.pixelverse.xyz/api/tasks/my"
        req = requests.get(url, headers=self.headers)
        return req.status_code == 500