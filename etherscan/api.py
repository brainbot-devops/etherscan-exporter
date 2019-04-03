import requests

from etherscan.modules import (
    Module,
    Account,
    Blocks,
    Contracts,
    Logs,
    Proxy,
    Stats,
    Transactions,
    Tokens,
)


class EtherscanAPI:
    def __init__(self, api_key, default_account_address=None, default_token_contract=None, network=None):
        self.session = requests.Session()
        self.session.params = {'apikey': api_key}
        self.account = Account(self.session, address=default_account_address)
        self.blocks = Blocks(self.session)
        self.contract = Contracts(self.session)
        self.logs = Logs(self.session)
        self.proxy = Proxy(self.session)
        self.stats = Stats(self.session)
        self.transactions = Transactions(self.session)
        self.tokens = Tokens(self.session, contract_address=default_token_contract)
        self.network = None
        self.configure_for(network or 'mainnet')

    def configure_for(self, network):
        Module.configure_for(network)
        self.network = network or 'mainnet'
