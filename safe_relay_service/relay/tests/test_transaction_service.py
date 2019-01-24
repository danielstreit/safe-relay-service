import logging

from hexbytes import HexBytes

from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.contracts import get_safe_contract
from gnosis.eth.utils import get_eth_address_with_key
from gnosis.safe.safe_service import (GasPriceTooLow, InvalidRefundReceiver,
                                      NotEnoughFundsForMultisigTx)
from gnosis.safe.tests.test_safe_service import TestSafeService

from safe_relay_service.gas_station.gas_station import GasStationMock

from ..services.transaction_service import (RefundMustBeEnabled,
                                            TransactionService,
                                            TransactionServiceProvider)

logger = logging.getLogger(__name__)


class TestTransactionService(TestSafeService):

    def test_transaction_provider_singleton(self):
        service1 = TransactionServiceProvider()
        service2 = TransactionServiceProvider()
        self.assertEqual(service1, service2)

    def test_send_multisig_tx(self):
        w3 = self.w3
        gas_station = GasStationMock()
        transaction_service = TransactionService(self.safe_service, gas_station)

        # The balance we will send to the safe
        safe_balance = w3.toWei(0.02, 'ether')
        # Send something to the owner[0], who will be sending the tx
        owner0_balance = safe_balance

        # Create Safe
        funder_account = self.ethereum_test_account
        funder = funder_account.address
        accounts = [self.create_account(initial_wei=owner0_balance), self.create_account(initial_wei=owner0_balance)]
        # Signatures must be sorted!
        accounts.sort(key=lambda account: account.address.lower())
        owners = [x.address for x in accounts]
        threshold = len(accounts)

        safe_creation = self.deploy_test_safe(owners=owners, threshold=threshold)
        my_safe_address = safe_creation.safe_address
        my_safe_contract = get_safe_contract(w3, my_safe_address)

        to = funder
        value = safe_balance // 2
        data = HexBytes('')
        operation = 0
        safe_tx_gas = 100000
        data_gas = 300000
        gas_price = gas_station.get_gas_prices().standard
        gas_token = NULL_ADDRESS
        refund_receiver = NULL_ADDRESS
        nonce = self.safe_service.retrieve_nonce(my_safe_address)
        safe_multisig_tx_hash = self.safe_service.get_hash_for_safe_tx(safe_address=my_safe_address,
                                                                       to=to,
                                                                       value=value,
                                                                       data=data,
                                                                       operation=operation,
                                                                       safe_tx_gas=safe_tx_gas,
                                                                       data_gas=data_gas,
                                                                       gas_price=gas_price,
                                                                       gas_token=gas_token,
                                                                       refund_receiver=refund_receiver,
                                                                       nonce=nonce)

        # Just to make sure we are not miscalculating tx_hash
        contract_multisig_tx_hash = my_safe_contract.functions.getTransactionHash(
            to,
            value,
            data,
            operation,
            safe_tx_gas,
            data_gas,
            gas_price,
            gas_token,
            refund_receiver,
            nonce).call()

        self.assertEqual(safe_multisig_tx_hash, contract_multisig_tx_hash)

        signatures = [account.signHash(safe_multisig_tx_hash) for account in accounts]
        signature_pairs = [(s['v'], s['r'], s['s']) for s in signatures]
        signatures_packed = self.safe_service.signatures_to_bytes(signature_pairs)

        # {bytes32 r}{bytes32 s}{uint8 v} = 65 bytes
        self.assertEqual(len(signatures_packed), 65 * len(owners))

        # Recover key is now a private function
        # Make sure the contract retrieves the same owners
        # for i, owner in enumerate(owners):
        #    recovered_owner = my_safe_contract.functions.recoverKey(safe_multisig_tx_hash, signatures_packed, i).call()
        #    self.assertEqual(owner, recovered_owner)

        self.assertTrue(self.safe_service.check_hash(safe_multisig_tx_hash, signatures_packed, owners))

        # Check owners are the same
        contract_owners = my_safe_contract.functions.getOwners().call()
        self.assertEqual(set(contract_owners), set(owners))
        self.assertEqual(w3.eth.getBalance(owners[0]), owner0_balance)

        with self.assertRaises(NotEnoughFundsForMultisigTx):
            transaction_service.send_multisig_tx(
                my_safe_address,
                to,
                value,
                data,
                operation,
                safe_tx_gas,
                data_gas,
                gas_price,
                gas_token,
                refund_receiver,
                signatures_packed,
                tx_sender_private_key=accounts[0].privateKey
            )

        # Send something to the safe
        self.send_tx({
            'to': my_safe_address,
            'value': safe_balance
        }, funder_account)

        bad_refund_receiver = get_eth_address_with_key()[0]
        with self.assertRaises(InvalidRefundReceiver):
            transaction_service.send_multisig_tx(
                my_safe_address,
                to,
                value,
                data,
                operation,
                safe_tx_gas,
                data_gas,
                gas_price,
                gas_token,
                bad_refund_receiver,
                signatures_packed,
                tx_sender_private_key=accounts[0].privateKey
            )

        invalid_gas_price = 0
        with self.assertRaises(RefundMustBeEnabled):
            transaction_service.send_multisig_tx(
                my_safe_address,
                to,
                value,
                data,
                operation,
                safe_tx_gas,
                data_gas,
                invalid_gas_price,
                gas_token,
                refund_receiver,
                signatures_packed,
                tx_sender_private_key=accounts[0].privateKey
            )

        with self.assertRaises(GasPriceTooLow):
            transaction_service.send_multisig_tx(
                my_safe_address,
                to,
                value,
                data,
                operation,
                safe_tx_gas,
                data_gas,
                gas_station.get_gas_prices().standard - 1,
                gas_token,
                refund_receiver,
                signatures_packed,
                tx_sender_private_key=accounts[0].privateKey
            )

        owner0_balance = w3.eth.getBalance(owners[0])

        sent_tx_hash, tx = transaction_service.send_multisig_tx(
            my_safe_address,
            to,
            value,
            data,
            operation,
            safe_tx_gas,
            data_gas,
            gas_price,
            gas_token,
            refund_receiver,
            signatures_packed,
            tx_sender_private_key=accounts[0].privateKey
        )

        tx_receipt = w3.eth.waitForTransactionReceipt(sent_tx_hash)
        self.assertTrue(tx_receipt['status'])
        owner0_new_balance = w3.eth.getBalance(owners[0])
        gas_used = tx_receipt['gasUsed']
        gas_cost = gas_used * gas_price
        estimated_payment = (data_gas + gas_used) * gas_price
        real_payment = owner0_new_balance - owner0_balance - gas_cost
        # Estimated payment will be bigger, because it uses all the tx gas. Real payment only uses gas left
        # in the point of calculation of the payment, so it will be slightly lower
        self.assertGreater(estimated_payment, real_payment)
        self.assertGreater(real_payment, 0)
        self.assertTrue(owner0_new_balance > owner0_balance - tx['gas'] * self.gas_price)
        self.assertEqual(self.safe_service.retrieve_nonce(my_safe_address), 1)