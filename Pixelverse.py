import requests
import json
from time import sleep
from colorama import Fore, Back, Style

class UserPixel:
    """Represents a user in the Pixelverse game, handling user data, actions, and interactions."""

    def __init__(self):
        """Initializes the UserPixel object by loading user configuration."""
        with open('./config.json', 'r') as file:
            self.config = json.load(file)

        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "secret": self.config['secret'],
            "tg-id": self.config['tgId'],
            "initData": self.config['initData']
        }
        self.space = "                                        "

    def isBroken(self):
        url = "https://api-clicker.pixelverse.xyz/api/tasks/my"
        req = requests.get(url, headers=self.headers)
        return req.status_code == 500

    def claim(self):
        """Claims mining rewards for the user."""
        url = "https://api-clicker.pixelverse.xyz/api/mining/claim"
        req = requests.post(url, headers=self.headers)
        data = req.json()
        print(f"{self.space}> Claimed {Back.YELLOW + Fore.BLACK}{int(data['claimedAmount'])}{Style.RESET_ALL} coins !")

    def getUser(self):
        """Retrieves and returns the user's information."""
        url = "https://api-clicker.pixelverse.xyz/api/users"
        req = requests.get(url, headers=self.headers)
        return req.json()

    def upgrade(self, petId: str):
        """Upgrades the specified pet for the user."""
        url = f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{petId}/level-up"
        req = requests.post(url, headers=self.headers)
        data = req.json()
        return data

    def upgradePets(self, auto_upgrade: bool):
        """Manages pet upgrades based on the auto_upgrade parameter.

        Args:
            auto_upgrade (bool): 
                If True, automatically upgrades affordable pets. 
                If False, prints a message indicating which pets can be upgraded.
        """
        print(f"{self.space}> Checking pets to upgrade ...")
        data = self.getUser()
        currBalance = data['clicksCount']

        petsUrl = "https://api-clicker.pixelverse.xyz/api/pets"
        req = requests.get(petsUrl, headers=self.headers)
        pets = req.json()['data']

        for pet in pets:
            if currBalance >= pet['userPet']['levelUpPrice']:
                if auto_upgrade:
                    self.upgrade(pet['userPet']['id'])
                    print(f"{self.space}> Successfully {Style.BRIGHT}upgraded{Style.RESET_ALL} pet {Back.YELLOW + Fore.BLACK}{pet['name']}{Style.RESET_ALL}")
                    sleep(0.5)
                else:
                    print(f"{self.space}> Pet {Back.YELLOW + Fore.BLACK}{pet['name']}{Style.RESET_ALL} can be upgraded!")

    def getStats(self):
        """Retrieves the user's battle statistics."""
        url = "https://api-clicker.pixelverse.xyz/api/battles/my/stats"
        req = requests.get(url, headers=self.headers)
        return req.json()
