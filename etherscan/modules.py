import abc

import requests


class Module(abc.ABC):
    ADDRESS = 'http://api.etherscan.io'

    def __init__(self, name, session, apikey=None):
        self.name = name
        self.session = session
        if not session:
            self.session = requests.Session()
            self.session.params = {'apikey': apikey}

    @classmethod
    def configure_for(cls, network):
        if network != 'mainnet':
            cls.ADDRESS = f'http://api.{network}.etherscan.io'

    @abc.abstractmethod
    def _query(self, action, **kwargs):
        params = dict(action=action, module=self.name, **kwargs)
        resp = self.session.get(f'{self.ADDRESS}/api', params=params)
        json_resp = resp.json()
        if 'error' in json_resp:
            raise ValueError(json_resp['error'])
        if 'error' in str(json_resp['result']).lower():
            raise ValueError(json_resp['result'])

        return json_resp['result']


def check_address_set(func):
    def wrapper(instance):
        if not instance.address:
            raise AttributeError('Attribute "Account.address" not set! Property unavailable!')
        return func(instance)
    return wrapper


class Account(Module):
    """Interface for etherscan.io's Account API.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#accounts
    """
    def __init__(self, session, address=None, apikey=None):
        super(Account, self).__init__('account', session, apikey)
        self.address = address

    def _query(self, action, address, **kwargs):
        return super(Account, self)._query(action, address=address, **kwargs)

    @check_address_set
    @property
    def balance(self):
        return self.address_balances(self.address)

    @check_address_set
    @property
    def transactions(self):
        return self.transactions_by_address(self.address)

    @check_address_set
    @property
    def internal_transactions(self):
        return self.internal_transactions_by_address(self.address)

    @check_address_set
    @property
    def token_transfer_events(self):
        return self.token_transfer_events_by_address(self.address)

    @check_address_set
    @property
    def blocks_mined(self):
        return self.blocks_mined_by_address(self)

    def address_balances(self, *addresses, **options):
        if len(addresses) == 1:
            action = 'balance'
            address = addresses[0]
        else:
            action = 'balancemulti'
            address = None

        resp = self._query(action, address or addresses, **options)
        if isinstance(resp, str):
            return {addresses: resp}

    def transactions_by_address(self, address, **options):
        return self._query('txlist', address, **options)

    def internal_transactions_by_address(self, address, **options):
        return self._query('txlistinternal', address, **options)

    def internal_transactions_by_hash(self, hash, **options):
        pass

    def token_transfer_events_by_address(self, address, **options):
        return self._query('tokentx', address, **options)

    def blocks_mined_by_address(self, address, **options):
        return self._query('getminedblock', address, **options)


class Contracts(Module):
    """Interface for the contract module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#contracts
    """
    def __init__(self, session, apikey=None):
        super(Contracts, self).__init__('contract', session, apikey)

    def _query(self, action, **kwargs):
        return super(Contracts, self)._query(action, **kwargs)

    def submit_for_verification(self, contract_name, contract_addr, source_code, compiler_version, runs=200, **options):
        params = {
            'contractname': contract_name,
            'contractaddr': contract_addr,
            'sourcecode': source_code,
            'compilerversion': compiler_version,
            'runs': runs,
        }
        params.update(options)

        return self.session.post('/api', 'verifysourcecode',params=params).json()

    def verification_status(self, guid, **options):
        return self._query('checkverifystatus', guid=guid, **options)

    def __getitem__(self, item):
        try:
            return self.get_abi(item)
        except requests.HTTPError:
            raise KeyError(item)

    def get_abi(self, address, **options):
        return self._query('getabi', address=address, **options)


class Transactions(Module):
    def __init__(self, session, apikey=None):
        super(Transactions, self).__init__('transaction', session, apikey)

    def _query(self, action, transaction_hash, **kwargs):
        return super(Transactions, self)._query(action, txhash=transaction_hash, **kwargs)

    def contract_execution_status(self, transaction_hash, **options):
        return self._query('getstatus', transaction_hash, **options)

    def receipt_status(self, transaction_hash, **options):
        return self._query('gettxreceiptstatus', transaction_hash, **options)


class Blocks(Module):
    """Interface for the block module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#blocks
    """
    def __init__(self, session, apikey=None):
        super(Blocks, self).__init__('block', session, apikey)

    def _query(self, action, **kwargs):
        return super(Blocks, self)._query(action, **kwargs)

    def block_reward(self, block_number, **options):
        return self._query('etblockreward', blockno=block_number, **options)


class Logs(Module):
    """Interface for the event log module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#logs
    """
    def __init__(self, session, apikey=None):
        super(Logs, self).__init__('logs', session, apikey)

    def _query(self, **kwargs):
        return super(Logs, self)._query('getLogs', **kwargs)

    def query(self, **options):
        return self._query(**options)


class Proxy(Module):
    """Interface for the proxy module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#proxy
    """

    def __init__(self, session, apikey=None):
        super(Proxy, self).__init__('proxy', session, apikey)

    def _query(self, action, **kwargs):
        return super(Proxy, self)._query(action, **kwargs)

    @property
    def gas_price(self):
        return self._query('eth_gasPrice')

    @property
    def latest_block(self):
        return self._query('eth_blockNumber')

    def block_by_number(self, block_num, **options):
        return self._query('eth_getBlockByNumber', tag=block_num, **options)

    def uncle_by_block_number_and_index(self, block_num, index, **options):
        return self._query('eth_getUncleByBlockNumberAndIndex', tag=block_num, index=index, **options)

    def transaction_count_by_block_number(self, block_num, **options):
        return self._query('eth_getTransactionCountByNumber', tag=block_num, **options)

    def transaction_by_hash(self, transaction_hash, **options):
        return self._query('eth_getTransactionByHash', txhash=transaction_hash, **options)

    def transaction_by_block_number_and_index(self, block_num, index, **options):
        return self._query('eth_getTransactionByBlockNumberAndIndex', tag=block_num, index=index, **options)

    def transaction_count_of_address(self, address, **options):
        return self._query('eth_getTransactionCount', address=address, **options)

    def send_raw_transaction(self, hex, **options):
        return self._query('eth_sendRawTransaction', hex=hex, **options)

    def receipt_by_transaction_hash(self, transaction_hash, **options):
        return self._query('eth_getTransationReceipt', txhash=transaction_hash, **options)

    def call(self, address, data, **options):
        return self._query('eth_call', to=address, data=data, **options)

    def code_at_address(self, address, **options):
        return self._query('eth_getCode', address=address, **options)

    def storage_at_address(self, address, **options):
        return self._query('eth+getStorageAt', address=address, **options)

    def estimate_gas(self, address, value, gas_price, **options):
        return self._query('eth_gasPrice', to=address, value=value, gasPrice=gas_price, **options)


class Tokens(Module):
    """Interface for the tokens module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#tokens
    """

    def __init__(self, session, apikey=None, contract_address=None):
        super(Tokens, self).__init__('token', session, apikey)
        self.contract_address = contract_address

    def _query(self, action, contract_address, **options):
        return super(Tokens, self)._query(action, contractaddress=contract_address, **options)

    @property
    def supply(self):
        if self.contract_address:
            return self.supply_by(self.contract_address)
        raise AttributeError("'Tokens.token_contract_address' was not set! Property unavailable!")

    def balance(self):
        if self.contract_address:
            return self.balance_by(self.contract_address)
        raise AttributeError("'Tokens.token_contract_address' was not set! Property unavailable!")

    def supply_by(self, contract_address, **options):
        return self._query('tokensupply', contract_address, **options)

    def balance_by(self, contract_address, **options):
        return self._query('tokenbalance', contract_address, **options)


class Stats(Module):
    """Interface for the stats module of etherscan.io.

    Consult the API Documentation for optional parameters:

        https://etherscan.io/apis#stats
    """

    def __init__(self, session, apikey=None):
        super(Stats, self).__init__('stats', session, apikey)

    def _query(self, action, **kwargs):
        return super(Stats, self)._query(action, **kwargs)

    @property
    def total_eth_supply(self):
        return self._query('ethsupply')

    @property
    def last_price(self):
        return self._query('ethprice')

    def node_size_for(self, client, sync_mode, start_date, end_date, **options):
        return self._query('chainsize', clienttype=client, startdate=start_date, enddate=end_date, syncmode=sync_mode, **options)