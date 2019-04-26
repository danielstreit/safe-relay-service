from typing import List, Optional

from django.db.models import Q

from eth_account import Account
from gnosis.eth import EthereumClient
from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from gnosis.safe.tests.test_safe_service import TestSafeService

from ..models import InternalTx, SafeContract, SafeTxStatus
from ..services import InternalTxService
from .factories import (SafeContractFactory, SafeCreation2Factory,
                        SafeTxStatusFactory)


class ParityMock:
    # We got internal txs for rinkeby address `0xd714EE2aEE29c404491AA18FE0442228C2d955f0`
    internal_txs = [
        {'action': {'from': '0xDE0B98b2f048fE999b5d5673e2F248fBCC61fc05',
                    'gas': 236896,
                    'value': 0,
                    'callType': 'call',
                    'input': HexBytes('0x6a7612020000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000000000000000000000000000000001c393e835e48100000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000dea8000000000000000000000000000000000000000000000000000000000001337400000000000000000000000000000000000000000000000000000000b2d05e0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008260cca97fb2cf5122eb28af0343918c5dfa376b0915a5199412fd643b5ff470895e726c5d2a757bf738abe57f84e217043993b8f9b6d1563a6064923559b7c6851cfc23e2bdea6378ce4e5e597e42f62d8253b210a63fc56420d434431ba97b1c9841e1751c1ab8f8e3337303c0e7cf627693c49d2eb2aa885263397e7714238b0b1c000000000000000000000000000000000000000000000000000000000000'),
                    'to': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0'},
         'blockHash': '0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a',
         'blockNumber': 4265984,
         'result': {'gasUsed': 50648,
                    'output': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001')},
         'subtraces': 1,
         'traceAddress': [],
         'transactionHash': '0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019',
         'transactionPosition': 0,
         'type': 'call'},
        {'action': {'from': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                    'gas': 232153,
                    'value': 0,
                    'callType': 'delegatecall',
                    'input': HexBytes('0x6a7612020000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000000000000000000000000000000001c393e835e48100000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000dea8000000000000000000000000000000000000000000000000000000000001337400000000000000000000000000000000000000000000000000000000b2d05e0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008260cca97fb2cf5122eb28af0343918c5dfa376b0915a5199412fd643b5ff470895e726c5d2a757bf738abe57f84e217043993b8f9b6d1563a6064923559b7c6851cfc23e2bdea6378ce4e5e597e42f62d8253b210a63fc56420d434431ba97b1c9841e1751c1ab8f8e3337303c0e7cf627693c49d2eb2aa885263397e7714238b0b1c000000000000000000000000000000000000000000000000000000000000'),
                    'to': '0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A'},
         'blockHash': '0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a',
         'blockNumber': 4265984,
         'result': {'gasUsed': 49544,
                    'output': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001')},
         'subtraces': 2,
         'traceAddress': [0],
         'transactionHash': '0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019',
         'transactionPosition': 0,
         'type': 'call'},
        {'action': {'from': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                    'gas': 59300,
                    'value': 496515000165505,
                    'callType': 'call',
                    'input': HexBytes('0x'),
                    'to': '0x4BA9692DA667218Aa968CeD8CBE59FE193E0d786'},
         'blockHash': '0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a',
         'blockNumber': 4265984,
         'result': {'gasUsed': 0, 'output': HexBytes('0x')},
         'subtraces': 0,
         'traceAddress': [0, 0],
         'transactionHash': '0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019',
         'transactionPosition': 0,
         'type': 'call'},
        {'action': {'from': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                    'gas': 2300,
                    'value': 259770000086590,
                    'callType': 'call',
                    'input': HexBytes('0x'),
                    'to': '0xDE0B98b2f048fE999b5d5673e2F248fBCC61fc05'},
         'blockHash': '0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a',
         'blockNumber': 4265984,
         'result': {'gasUsed': 0, 'output': HexBytes('0x')},
         'subtraces': 0,
         'traceAddress': [0, 1],
         'transactionHash': '0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019',
         'transactionPosition': 0,
         'type': 'call'},
        {'action': {'from': '0x5895Ac6e2Df45Bfa825c4A5be7392afc545CEF29',
                    'gas': 342973,
                    'value': 0,
                    'callType': 'call',
                    'input': HexBytes('0x1688f0b9000000000000000000000000b6029ea3b2c51d09a50b53ca8012feeb05bda35a00000000000000000000000000000000000000000000000000000000000000600000cbe3c41b0995a74a549a9130fc0ead5d6610913b2d2622601ca9b6659a9700000000000000000000000000000000000000000000000000000000000001c4a97ab18a00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037a1125fa50450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000027a8a3d5cb4c0df210a8a92a82bf0dccd8278d510000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000006cad2820b3f8214859a7c66509ef3a715cd7ce38000000000000000000000000dc75eccdfea024122a9bde07f83d3a46f67eec4b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
                    'to': '0x12302fE9c02ff50939BaAaaf415fc226C078613C'},
         'blockHash': '0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571',
         'blockNumber': 4265982,
         'result': {'gasUsed': 275579,
                    'output': HexBytes('0x000000000000000000000000d714ee2aee29c404491aa18fe0442228c2d955f0')},
         'subtraces': 2,
         'traceAddress': [],
         'transactionHash': '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb',
         'transactionPosition': 1,
         'type': 'call'},
        {'action': {'from': '0x12302fE9c02ff50939BaAaaf415fc226C078613C',
                    'gas': 303392,
                    'value': 0,
                    'init': HexBytes('0x608060405234801561001057600080fd5b506040516020806101a88339810180604052602081101561003057600080fd5b8101908080519060200190929190505050600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614156100c7576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260248152602001806101846024913960400191505060405180910390fd5b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050606e806101166000396000f3fe608060405273ffffffffffffffffffffffffffffffffffffffff600054163660008037600080366000845af43d6000803e6000811415603d573d6000fd5b3d6000f3fea165627a7a723058201e7d648b83cfac072cbccefc2ffc62a6999d4a050ee87a721942de1da9670db80029496e76616c6964206d617374657220636f707920616464726573732070726f7669646564000000000000000000000000b6029ea3b2c51d09a50b53ca8012feeb05bda35a')},
         'blockHash': '0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571',
         'blockNumber': 4265982,
         'result': {'gasUsed': 42495,
                    'code': HexBytes('0x608060405273ffffffffffffffffffffffffffffffffffffffff600054163660008037600080366000845af43d6000803e6000811415603d573d6000fd5b3d6000f3fea165627a7a723058201e7d648b83cfac072cbccefc2ffc62a6999d4a050ee87a721942de1da9670db80029'),
                    'address': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0'},
         'subtraces': 0,
         'traceAddress': [0],
         'transactionHash': '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb',
         'transactionPosition': 1,
         'type': 'create'},
        {'action': {'from': '0x12302fE9c02ff50939BaAaaf415fc226C078613C',
                    'gas': 260808,
                    'value': 0,
                    'callType': 'call',
                    'input': HexBytes('0xa97ab18a00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037a1125fa50450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000027a8a3d5cb4c0df210a8a92a82bf0dccd8278d510000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000006cad2820b3f8214859a7c66509ef3a715cd7ce38000000000000000000000000dc75eccdfea024122a9bde07f83d3a46f67eec4b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
                    'to': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0'},
         'blockHash': '0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571',
         'blockNumber': 4265982,
         'result': {'gasUsed': 196370, 'output': HexBytes('0x')},
         'subtraces': 1,
         'traceAddress': [1],
         'transactionHash': '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb',
         'transactionPosition': 1,
         'type': 'call'},
        {'action': {'from': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                    'gas': 255715,
                    'value': 0,
                    'callType': 'delegatecall',
                    'input': HexBytes('0xa97ab18a00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037a1125fa50450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000027a8a3d5cb4c0df210a8a92a82bf0dccd8278d510000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000006cad2820b3f8214859a7c66509ef3a715cd7ce38000000000000000000000000dc75eccdfea024122a9bde07f83d3a46f67eec4b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
                    'to': '0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A'},
         'blockHash': '0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571',
         'blockNumber': 4265982,
         'result': {'gasUsed': 195293, 'output': HexBytes('0x')},
         'subtraces': 1,
         'traceAddress': [1, 0],
         'transactionHash': '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb',
         'transactionPosition': 1,
         'type': 'call'},
        {'action': {'from': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                    'gas': 2300,
                    'value': 978639000326213,
                    'callType': 'call',
                    'input': HexBytes('0x'),
                    'to': '0x5895Ac6e2Df45Bfa825c4A5be7392afc545CEF29'},
         'blockHash': '0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571',
         'blockNumber': 4265982,
         'result': {'gasUsed': 0, 'output': HexBytes('0x')},
         'subtraces': 0,
         'traceAddress': [1, 0, 0],
         'transactionHash': '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb',
         'transactionPosition': 1,
         'type': 'call'},
        {'action': {'from': '0x4BA9692DA667218Aa968CeD8CBE59FE193E0d786',
                    'gas': 2000,
                    'value': 1957278000652426,
                    'callType': 'call',
                    'input': HexBytes('0x'),
                    'to': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0'},
         'blockHash': '0x91c4fb2f2e91dfcd7c6f50938c053a6bb0b8999c0da131e4c701bc7bd135727b',
         'blockNumber': 4265981,
         'result': {'gasUsed': 0, 'output': HexBytes('0x')},
         'subtraces': 0,
         'traceAddress': [],
         'transactionHash': '0xa3c522763c3d9e127d6f43f90185691cfac81af24fded3466ff12f4517e69a99',
         'transactionPosition': 6,
         'type': 'call'},
        {'action': {'from': '0x32Be343B94f860124dC4fEe278FDCBD38C102D88',
                    'gas': 0,
                    'value': 200000000000000000,
                    'callType': 'call',
                    'input': HexBytes('0x'),
                    'to': '0x8bbB73BCB5d553B5A556358d27625323Fd781D37'},
         'blockHash': '0x91c4fb2f2e91dfcd7c6f50938c053a6bb0b8999c0da131e4c701bc7bd135727b',
         'blockNumber': 4265981,
         'error': 'Out of gas',
         'subtraces': 0,
         'traceAddress': [0],
         'transactionHash': '0xa3c522763c3d9e127d6f43f90185691cfac81af24fded3466ff12f4517e69a99',
         'transactionPosition': 6,
         'type': 'call'
         },
    ]

    def __init__(self, ethereum_client: EthereumClient):
        self.ethereum_client = ethereum_client

    def trace_transaction(self, tx_hash: str):
        return [internal_tx for internal_tx in self.internal_txs if internal_tx['transactionHash'] == tx_hash]

    def trace_filter(self, from_block: int = 1, to_block: Optional[int] = None,
                     from_address: Optional[List[str]] = None, to_address: Optional[List[str]] = None,
                     after: Optional[int] = None, count: Optional[int] = None):
        if not to_block:
            to_block = self.ethereum_client.current_block_number

        return [internal_tx for internal_tx in self.internal_txs if
                to_block >= internal_tx['blockNumber'] >= from_block and
                (not from_address or internal_tx['action']['from'] in from_address) and
                (not to_address or internal_tx['action'].get('to') in to_address)
                ]


class EthereumClientMock:
    def __init__(self, *args, **kwargs):
        self.parity = ParityMock(self)
        self.current_block_number = kwargs.get('current_block_number', 4266000)

    txs = [AttributeDict({'blockHash': HexBytes('0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a'),
                          'blockNumber': 4265984,
                          'chainId': None,
                          'condition': None,
                          'creates': None,
                          'from': '0xDE0B98b2f048fE999b5d5673e2F248fBCC61fc05',
                          'gas': 271416,
                          'gasPrice': 3000000001,
                          'hash': HexBytes('0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019'),
                          'input': '0x6a7612020000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000000000000000000000000000000001c393e835e48100000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000dea8000000000000000000000000000000000000000000000000000000000001337400000000000000000000000000000000000000000000000000000000b2d05e0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008260cca97fb2cf5122eb28af0343918c5dfa376b0915a5199412fd643b5ff470895e726c5d2a757bf738abe57f84e217043993b8f9b6d1563a6064923559b7c6851cfc23e2bdea6378ce4e5e597e42f62d8253b210a63fc56420d434431ba97b1c9841e1751c1ab8f8e3337303c0e7cf627693c49d2eb2aa885263397e7714238b0b1c000000000000000000000000000000000000000000000000000000000000',
                          'nonce': 260,
                          'publicKey': HexBytes('0x8cd71db379d8609b3928ebd60f2e09b00a97fa8144a52acfc87479d9a046c90e1dc0a36bb2287ef58dc00264cea3a4c22b67fb0b4fb9bcb68c04863c4824b989'),
                          'r': HexBytes('0x3493ebe539984fcec1503c2decb32d5926748d777c2b6a9d4e3e65955215b07f'),
                          'raw': HexBytes('0xf902ac82010484b2d05e018304243894d714ee2aee29c404491aa18fe0442228c2d955f080b902446a7612020000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000000000000000000000000000000001c393e835e48100000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000dea8000000000000000000000000000000000000000000000000000000000001337400000000000000000000000000000000000000000000000000000000b2d05e0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008260cca97fb2cf5122eb28af0343918c5dfa376b0915a5199412fd643b5ff470895e726c5d2a757bf738abe57f84e217043993b8f9b6d1563a6064923559b7c6851cfc23e2bdea6378ce4e5e597e42f62d8253b210a63fc56420d434431ba97b1c9841e1751c1ab8f8e3337303c0e7cf627693c49d2eb2aa885263397e7714238b0b1c0000000000000000000000000000000000000000000000000000000000001ca03493ebe539984fcec1503c2decb32d5926748d777c2b6a9d4e3e65955215b07fa0488c7273bc79c36ec598701983fa3229ea6dd971b1fd770d45deca224d2bf0cf'),
                          's': HexBytes('0x488c7273bc79c36ec598701983fa3229ea6dd971b1fd770d45deca224d2bf0cf'),
                          'standardV': 1,
                          'to': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                          'transactionIndex': 0,
                          'v': 28,
                          'value': 0}),
           AttributeDict({'blockHash': HexBytes('0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571'),
                          'blockNumber': 4265982,
                          'chainId': None,
                          'condition': None,
                          'creates': None,
                          'from': '0x5895Ac6e2Df45Bfa825c4A5be7392afc545CEF29',
                          'gas': 376213,
                          'gasPrice': 3000000001,
                          'hash': HexBytes('0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb'),
                          'input': '0x1688f0b9000000000000000000000000b6029ea3b2c51d09a50b53ca8012feeb05bda35a00000000000000000000000000000000000000000000000000000000000000600000cbe3c41b0995a74a549a9130fc0ead5d6610913b2d2622601ca9b6659a9700000000000000000000000000000000000000000000000000000000000001c4a97ab18a00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037a1125fa50450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000027a8a3d5cb4c0df210a8a92a82bf0dccd8278d510000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000006cad2820b3f8214859a7c66509ef3a715cd7ce38000000000000000000000000dc75eccdfea024122a9bde07f83d3a46f67eec4b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
                          'nonce': 666,
                          'publicKey': HexBytes('0x769604c4b14e32c427934e1cf4bb033b9a7added99445dc314ff5617fa5cedea3c729d8f11ca174aec262ee78bdcb8acd8bea5af2fdbe1f2fe8985e77473954b'),
                          'r': HexBytes('0xbe1b16e0bb4f1f5511ddd99ed817774efd07cec09714b1dbe4eabf6dba58e750'),
                          'raw': HexBytes('0xf902cc82029a84b2d05e018305bd959412302fe9c02ff50939baaaaf415fc226c078613c80b902641688f0b9000000000000000000000000b6029ea3b2c51d09a50b53ca8012feeb05bda35a00000000000000000000000000000000000000000000000000000000000000600000cbe3c41b0995a74a549a9130fc0ead5d6610913b2d2622601ca9b6659a9700000000000000000000000000000000000000000000000000000000000001c4a97ab18a00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000037a1125fa50450000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000027a8a3d5cb4c0df210a8a92a82bf0dccd8278d510000000000000000000000004ba9692da667218aa968ced8cbe59fe193e0d7860000000000000000000000006cad2820b3f8214859a7c66509ef3a715cd7ce38000000000000000000000000dc75eccdfea024122a9bde07f83d3a46f67eec4b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001ca0be1b16e0bb4f1f5511ddd99ed817774efd07cec09714b1dbe4eabf6dba58e750a02415f15e36493ad2ee8a8a6530b5cfe74bac91f87f0facce253b45f541beeef7'),
                          's': HexBytes('0x2415f15e36493ad2ee8a8a6530b5cfe74bac91f87f0facce253b45f541beeef7'),
                          'standardV': 1,
                          'to': '0x12302fE9c02ff50939BaAaaf415fc226C078613C',
                          'transactionIndex': 1,
                          'v': 28,
                          'value': 0}),
           AttributeDict({'blockHash': HexBytes('0x91c4fb2f2e91dfcd7c6f50938c053a6bb0b8999c0da131e4c701bc7bd135727b'),
                          'blockNumber': 4265981,
                          'chainId': None,
                          'condition': None,
                          'creates': None,
                          'from': '0x4BA9692DA667218Aa968CeD8CBE59FE193E0d786',
                          'gas': 23000,
                          'gasPrice': 1000000000,
                          'hash': HexBytes('0xa3c522763c3d9e127d6f43f90185691cfac81af24fded3466ff12f4517e69a99'),
                          'input': '0x',
                          'nonce': 654,
                          'publicKey': HexBytes('0x2058a37986eb384eb89f0005a7b30847862878ae6454b906b685615b449c668f2c223e2cc89945fdb377de2cace75a850d2772a8d6882650279a73bfa049c3f0'),
                          'r': HexBytes('0x2f1b20daa5b0d5bcc8ca58ebeff9e1ed0c46eb6887624baf851b2485a5dfd3a9'),
                          'raw': HexBytes('0xf86c82028e843b9aca008259d894d714ee2aee29c404491aa18fe0442228c2d955f08706f4224bf4a08a801ca02f1b20daa5b0d5bcc8ca58ebeff9e1ed0c46eb6887624baf851b2485a5dfd3a9a04854273360c23d2967f593d9beae22fa3f5808f8a6ae1dc79ad9882da03ce173'),
                          's': HexBytes('0x4854273360c23d2967f593d9beae22fa3f5808f8a6ae1dc79ad9882da03ce173'),
                          'standardV': 1,
                          'to': '0xd714EE2aEE29c404491AA18FE0442228C2d955f0',
                          'transactionIndex': 6,
                          'v': 28,
                          'value': 1957278000652426})]
    receipts = [AttributeDict({'blockHash': HexBytes('0x4d43d6845357ca9b8f7c36348ebbf8076281d98f33a0a47c6c27b0eb36224b4a'),
                               'blockNumber': 4265984,
                               'contractAddress': None,
                               'cumulativeGasUsed': 85168,
                               'from': '0xde0b98b2f048fe999b5d5673e2f248fbcc61fc05',
                               'gasUsed': 85168,
                               'logs': [],
                               'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
                               'root': None,
                               'status': 1,
                               'to': '0xd714ee2aee29c404491aa18fe0442228c2d955f0',
                               'transactionHash': HexBytes('0xc6f513d6a18f09a08f65ec406785bb54e698437be501cd81d7c9dee0816c7019'),
                               'transactionIndex': 0}),
                AttributeDict({'blockHash': HexBytes('0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571'),
                               'blockNumber': 4265982,
                               'contractAddress': None,
                               'cumulativeGasUsed': 338990,
                               'from': '0x5895ac6e2df45bfa825c4a5be7392afc545cef29',
                               'gasUsed': 308819,
                               'logs': [AttributeDict({'address': '0x12302fE9c02ff50939BaAaaf415fc226C078613C',
                                                       'blockHash': HexBytes('0xe0cbe42d06dadf0dbdeac8107c28bccdb2cc2cc00091c82fdbd5d198ac812571'),
                                                       'blockNumber': 4265982,
                                                       'data': '0x000000000000000000000000d714ee2aee29c404491aa18fe0442228c2d955f0',
                                                       'logIndex': 1,
                                                       'removed': False,
                                                       'topics': [HexBytes('0xa38789425dbeee0239e16ff2d2567e31720127fbc6430758c1a4efc6aef29f80')],
                                                       'transactionHash': HexBytes('0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb'),
                                                       'transactionIndex': 1,
                                                       'transactionLogIndex': '0x0',
                                                       'type': 'mined'})],
                               'logsBloom': HexBytes('0x00000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000800000000002000000000000000000000000000004000000000000000000000000000000000'),
                               'root': None,
                               'status': 1,
                               'to': '0x12302fe9c02ff50939baaaaf415fc226c078613c',
                               'transactionHash': HexBytes('0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb'),
                               'transactionIndex': 1}),
                AttributeDict({'blockHash': HexBytes('0x91c4fb2f2e91dfcd7c6f50938c053a6bb0b8999c0da131e4c701bc7bd135727b'),
                               'blockNumber': 4265981,
                               'contractAddress': None,
                               'cumulativeGasUsed': 1202514,
                               'from': '0x4ba9692da667218aa968ced8cbe59fe193e0d786',
                               'gasUsed': 21000,
                               'logs': [],
                               'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
                               'root': None,
                               'status': 1,
                               'to': '0xd714ee2aee29c404491aa18fe0442228c2d955f0',
                               'transactionHash': HexBytes('0xa3c522763c3d9e127d6f43f90185691cfac81af24fded3466ff12f4517e69a99'),
                               'transactionIndex': 6})]

    def get_transaction_receipt(self, tx_hash: str, timeout=None):
        receipt = [receipt for receipt in self.receipts if receipt.transactionHash == HexBytes(tx_hash)]
        if receipt:
            return receipt[0]

    def get_transaction(self, tx_hash: str):
        tx = [tx for tx in self.txs if tx.hash == HexBytes(tx_hash)]
        if tx:
            return tx[0]


class TestInternalTxService(TestSafeService):
    def setUp(self):
        self.ethereum_client_mock = EthereumClientMock()
        self.internal_tx_service = InternalTxService(self.ethereum_client_mock)

    def test_get_safe_creation_block_number(self):
        mock_tx_hash = '0x638b956dbbb3d40d06219f571a3bb8c0ab6e7af758d21a4d33af01655a194bbb'
        safe_address = Account.create().address
        self.assertEqual(self.internal_tx_service.get_safe_creation_block_number(safe_address), 0)

        block_number = 111
        safe_contract = SafeContractFactory(address=safe_address)
        safe_creation_2 = SafeCreation2Factory(safe=safe_contract, block_number=block_number, tx_hash=mock_tx_hash)
        self.assertEqual(self.internal_tx_service.get_safe_creation_block_number(safe_address), block_number)

        safe_creation_2.block_number = None
        safe_creation_2.save()
        self.assertEqual(self.internal_tx_service.get_safe_creation_block_number(safe_address),
                         self.ethereum_client_mock.get_transaction_receipt(mock_tx_hash).blockNumber)

    def test_get_or_create_safe_tx_status(self):
        safe_address = Account.create().address

        with self.assertRaises(SafeContract.DoesNotExist):
            self.internal_tx_service.get_or_create_safe_tx_status(safe_address)

        SafeContractFactory(address=safe_address)
        safe_tx_status = self.internal_tx_service.get_or_create_safe_tx_status(safe_address)
        self.assertEqual(safe_tx_status.tx_block_number, 0)
        self.assertEqual(safe_tx_status.tx_block_number, safe_tx_status.initial_block_number)

    def test_process_internal_txs(self):
        address = '0xd714EE2aEE29c404491AA18FE0442228C2d955f0'
        safe_contract = SafeContractFactory(address=address)

        block_process_limit = self.internal_tx_service.block_process_limit
        self.assertIsNone(self.internal_tx_service.process_internal_txs([address]))
        self.assertEqual(SafeTxStatus.objects.filter(safe=safe_contract).count(), 0)
        self.assertEqual(InternalTx.objects.filter(Q(_from=address) | Q(to=address)).count(), 0)
        SafeTxStatusFactory(safe=safe_contract)

        _, updated = self.internal_tx_service.process_internal_txs([address])
        self.assertFalse(updated)
        safe_tx_status = SafeTxStatus.objects.get(safe=safe_contract)
        self.assertEqual(safe_tx_status.tx_block_number, block_process_limit)

        # We scan for every tx
        self.internal_tx_service.block_process_limit = 0
        _, updated = self.internal_tx_service.process_internal_txs([address])
        self.assertTrue(updated)
        safe_tx_status = SafeTxStatus.objects.get(safe=safe_contract)
        confirmations = self.internal_tx_service.confirmations
        self.assertEqual(safe_tx_status.tx_block_number,
                         self.internal_tx_service.ethereum_client.current_block_number - confirmations)
        self.assertEqual(InternalTx.objects.count(), 11)

        _, updated = self.internal_tx_service.process_internal_txs([address])
        self.assertTrue(updated)
        safe_tx_status = SafeTxStatus.objects.get(safe=safe_contract)
        confirmations = self.internal_tx_service.confirmations
        self.assertEqual(safe_tx_status.tx_block_number,
                         self.internal_tx_service.ethereum_client.current_block_number - confirmations)
        self.assertEqual(InternalTx.objects.count(), 11)
        self.assertEqual(InternalTx.objects.filter(Q(_from=address) | Q(to=address)).count(), 8)
        self.assertEqual(InternalTx.objects.filter(error=None).count(), 10)
        self.assertEqual(InternalTx.objects.exclude(error=None).first().error, 'Out of gas')
        self.assertEqual(InternalTx.objects.filter(trace_address='1,0,0').count(), 1)

        self.internal_tx_service.block_process_limit = block_process_limit
