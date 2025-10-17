from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from substrateinterface import ExtrinsicReceipt, Keypair, KeypairType, SubstrateInterface
from substrateinterface.exceptions import SubstrateRequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from websocket import WebSocketConnectionClosedException, WebSocketProtocolException

from substrate.chain_data import (
  AllSubnetBootnodes,
  ConsensusData,
  DelegateStakeInfo,
  NodeDelegateStakeInfo,
  SubnetData,
  SubnetInfo,
  SubnetNode,
  SubnetNodeInfo,
  SubnetNodeStakeInfo,
)
from substrate.config import BLOCK_SECS


@dataclass
class EpochData:
  block: int
  epoch: int
  block_per_epoch: int
  seconds_per_epoch: int
  percent_complete: float
  blocks_elapsed: int
  blocks_remaining: int
  seconds_elapsed: int
  seconds_remaining: int

  @staticmethod
  def zero(current_block: int, epoch_length: int) -> "EpochData":
    return EpochData(
      block=current_block,
      epoch=0,
      block_per_epoch=epoch_length,
      seconds_per_epoch=epoch_length * BLOCK_SECS,
      percent_complete=0.0,
      blocks_elapsed=0,
      blocks_remaining=epoch_length,
      seconds_elapsed=0,
      seconds_remaining=epoch_length * BLOCK_SECS
    )

@dataclass
class OverwatchEpochData:
  block: int
  epoch: int
  overwatch_epoch: int
  block_per_epoch: int
  seconds_per_epoch: int
  percent_complete: float
  blocks_elapsed: int
  blocks_remaining: int
  seconds_elapsed: int
  seconds_remaining: int
  seconds_remaining_until_reveal: int

  @staticmethod
  def zero(current_block: int, epoch_length: int) -> "OverwatchEpochData":
    return OverwatchEpochData(
      block=current_block,
      epoch=0,
      overwatch_epoch=0,
      block_per_epoch=epoch_length,
      seconds_per_epoch=epoch_length * BLOCK_SECS,
      percent_complete=0.0,
      blocks_elapsed=0,
      blocks_remaining=epoch_length,
      seconds_elapsed=0,
      seconds_remaining=epoch_length * BLOCK_SECS,
      seconds_remaining_until_reveal=0
    )

class KeypairFrom(Enum):
  MNEMONIC = 1
  PRIVATE_KEY = 2

class SubnetNodeClass(Enum):
  Registered  = 1
  Idle        = 2
  Included    = 3
  Validator   = 4

# lookup from string
def subnet_node_class_from_string(name: str) -> SubnetNodeClass:
    return SubnetNodeClass[name]

def subnet_node_class_to_enum(name: str) -> SubnetNodeClass:
    return SubnetNodeClass[name]

class Hypertensor:
  def __init__(self, url: str):
    self.url = url
    self.interface: SubstrateInterface = SubstrateInterface(url=url)

  def get_block_number(self):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          block_hash = _interface.get_block_hash()
          block_number = _interface.get_block_number(block_hash)
          return block_number
      except SubstrateRequestException as e:
        print("Failed to get query request: {}".format(e))

    return make_query()

  def get_epoch(self):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          block_hash = _interface.get_block_hash()
          current_block = _interface.get_block_number(block_hash)
          epoch_length = _interface.get_constant('Network', 'EpochLength')
          epoch = int(str(current_block)) // int(str(epoch_length))
          return epoch
      except SubstrateRequestException as e:
        print("Failed to get query request: {}".format(e))

    return make_query()

  def get_subnet_node_data(
    self,
    subnet_id: int,
    subnet_node_id: int,
  ) -> ExtrinsicReceipt:
    """
    Query a subnet node ID by its hotkey

    :param subnet_id: to subnet ID
    :param subnet_node_id: Subnet Node ID
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetNodesData', [subnet_id, subnet_node_id])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_hotkey_subnet_node_id(
    self,
    subnet_id: int,
    hotkey: str,
  ) -> ExtrinsicReceipt:
    """
    Query a subnet node ID by its hotkey

    :param subnet_id: to subnet ID
    :param hotkey: Hotkey of subnet node
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'HotkeySubnetNodeId', [subnet_id, hotkey])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_hotkey_owner(
    self,
    hotkey: str,
  ) -> ExtrinsicReceipt:
    """
    Get coldkey of hotkey

    :param hotkey: Hotkey of subnet node
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'HotkeyOwner', [hotkey])
          return result.value['data']['free']
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_node_id_hotkey(
    self,
    subnet_id: int,
    hotkey: str,
  ) -> ExtrinsicReceipt:
    """
    Query hotkey by subnet node ID

    :param hotkey: Hotkey of subnet node
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetNodeIdHotkey', [subnet_id, hotkey])
          return result.value['data']['free']
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_balance(
    self,
    address: str
  ):
    """
    Function to return account balance

    :param address: address of account_id
    :returns: account balance
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('System', 'Account', [address])
          return result.value['data']['free']
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_stake_balance(
    self,
    subnet_id: int,
    address: str
  ):
    """
    Function to return a subnet node stake balance

    :param subnet_id: Subnet ID
    :param address: address of account_id
    :returns: account stake balance towards subnet
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'AccountSubnetStake', [address, subnet_id])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_id_by_path(
    self,
    path: str
  ):
    """
    Query subnet ID by path

    :param path: path of subnet
    :returns: subnet_id
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetPaths', [path])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_data(
    self,
    id: int
  ):
    """
    Function to get data struct of the subnet

    :param id: id of subnet
    :returns: subnet_id
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetsData', [id])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_max_subnets(self):
    """
    Function to get the maximum number of subnets allowed on the blockchain

    :returns: max_subnets
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MaxSubnets')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_min_subnet_nodes(self):
    """
    Function to get the minimum number of subnet_nodes required to host a subnet

    :returns: min_subnet_nodes
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MinSubnetNodes')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_min_stake_balance(self):
    """
    Function to get the minimum stake balance required to host a subnet

    :returns: min_stake_balance
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MinStakeBalance')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_max_subnet_nodes(self):
    """
    Function to get the maximum number of subnet_nodes allowed to host a subnet

    :returns: max_subnet_nodes
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MaxSubnetNodes')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_tx_rate_limit(self):
    """
    Function to get the transaction rate limit

    :returns: tx_rate_limit
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'TxRateLimit')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_epoch_length(self):
    """
    Function to get the epoch length as blocks per epoch

    :returns: epoch_length
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.get_constant('Network', 'EpochLength')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_rewards_validator(
    self,
    subnet_id: int,
    epoch: int
  ):
    """
    Query an epochs chosen subnet validator

    :param subnet_id: subnet ID
    :param epoch: epoch to query SubnetElectedValidator
    :returns: epoch_length
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetElectedValidator', [subnet_id, epoch])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_overwatch_epoch_multiplier(self):
    """
    Function to get the transaction rate limit

    :returns: tx_rate_limit
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'OverwatchEpochLengthMultiplier')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_overwatch_commit_cutoff_percent(self):
    """
    Function to get the transaction rate limit

    :returns: tx_rate_limit
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'OverwatchCommitCutoffPercent')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_rewards_submission(
    self,
    subnet_id: int,
    epoch: int
  ):
    """
    Query epochs validator rewards submission

    :param subnet_id: subnet ID
    :param epoch: epoch to query SubnetConsensusSubmission 

    :returns: epoch_length
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetConsensusSubmission', [subnet_id, epoch])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_min_subnet_registration_blocks(self):
    """
    Query minimum subnet registration blocks

    :returns: epoch_length
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MinSubnetRegistrationBlocks')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_max_subnet_registration_blocks(self):
    """
    Query maximum subnet registration blocks

    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MaxSubnetRegistrationBlocks')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_max_subnet_entry_interval(self):
    """
    Query maximum subnet entry interval blocks
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'MaxSubnetEntryInterval')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_registration_epochs(self):
    """
    Query maximum subnet entry interval blocks
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetRegistrationEpochs')
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def get_subnet_slot(self, subnet_id: int):
    """
    Query maximum subnet entry interval blocks with retry + reconnect
    """

    @retry(
        wait=wait_fixed(BLOCK_SECS + 1),
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type((SubstrateRequestException, ConnectionError, AttributeError, WebSocketConnectionClosedException, WebSocketProtocolException))
    )
    def make_query():
        try:
            # Ensure interface is connected
            if not self.interface.websocket or not self.interface.websocket.connected:
                self.interface.connect_websocket()

            # Ensure runtime metadata is loaded
            # if not self.interface.runtime_config:
            #     self.interface.init_runtime()

            # Query directly (avoid context manager which closes socket)
            with self.interface as interface:
              result = interface.query('Network', 'SubnetSlot', [subnet_id])
              print("result", result)
              return result

        except Exception as e:  # noqa: F841
            # Force reconnect + metadata refresh so retry can succeed
            try:
                self.interface.close()
            except Exception:
                pass
            self.interface.connect_websocket()
            self.interface.init_runtime()
            raise

    try:
        return make_query()
    except Exception as e:
        return None

  """
  RPC
  """

  def get_subnet_info(
    self,
    subnet_id: int,
  ):
    """
    Query an epochs chosen subnet validator and return SubnetNode

    :param subnet_id: subnet ID
    :returns: Struct of subnet info
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getSubnetInfo',
            params=[
              subnet_id,
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_subnet_nodes(
    self,
    subnet_id: int,
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getSubnetNodes',
            params=[
              subnet_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_all_subnet_info(
    self,
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getAllSubnetsInfo',
            params=[]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_subnet_nodes_info(
    self,
    subnet_id: int,
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getSubnetNodesInfo',
            params=[
              subnet_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_all_subnet_nodes_info(
    self,
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getAllSubnetNodesInfo',
            params=[]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_bootnodes(
    self,
    subnet_id: int,
  ):
    """
    Function to return all bootnodes of a subnet

    :param subnet_id: subnet ID
    :returns: subnet_nodes_data
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          subnet_nodes_data = _interface.rpc_request(
            method='network_getBootnodes',
            params=[
              subnet_id
            ]
          )
          return subnet_nodes_data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_coldkey_subnet_nodes_info(
    self,
    coldkey: str
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getColdkeySubnetNodesInfo',
            params=[
              coldkey
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_coldkey_stakes(
    self,
    coldkey: str
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getColdkeyStakes',
            params=[
              coldkey
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_delegate_stakes(
    self,
    account_id: str
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getDelegateStakes',
            params=[
              account_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_node_delegate_stakes(
    self,
    account_id: str
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getNodeDelegateStakes',
            params=[
              account_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_overwatch_commits(
    self,
    epoch: int,
    overwatch_node_id: int
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getOverwatchCommitsForEpochAndNode',
            params=[
              epoch,
              overwatch_node_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_overwatch_reveals(
    self,
    epoch: int,
    overwatch_node_id: int
  ):
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getOverwatchRevealsForEpochAndNode',
            params=[
              epoch,
              overwatch_node_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_consensus_data(
    self,
    subnet_id: int,
    epoch: int
  ):
    """
    Query an epochs consesnus submission
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetConsensusSubmission', [subnet_id, epoch])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

  def proof_of_stake(
    self,
    subnet_id: int,
    peer_id: str,
    min_class: int
  ):
    """
    Function to return all account_ids and subnet_node_ids from the substrate Hypertensor Blockchain by peer ID

    :param subnet_id: subnet ID
    :param peer_id: peer ID
    :param min_class: SubnetNodeClass enum

    Registered = 1
    Idle = 2
    Included = 3
    Validator = 4

    ```rust
    pub enum SubnetNodeClass {
      #[default] Registered,
      Idle,
      Included,
      Validator,
    }
    ```
    :returns: subnet_nodes_data
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          result = _interface.rpc_request(
            method='network_proofOfStake',
            params=[
              subnet_id,
              peer_id,
              min_class
            ]
          )
          return result['result']
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_minimum_delegate_stake(
    self,
    subnet_id: int,
  ):
    """
    Query required minimum stake balance based on memory

=    :param subnet_id: Subnet ID

    :returns: subnet_nodes_data
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getMinimumDelegateStake',
            params=[
              subnet_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_subnet_node_info(
    self,
    subnet_id: int,
    subnet_node_id: int
  ):
    """
    Function to return all subnet nodes in the SubnetNodeInfo struct format

    :param subnet_id: subnet ID

    :returns: subnet_nodes_data
    """
    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getSubnetNodeInfo',
            params=[
              subnet_id,
              subnet_node_id
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  def get_elected_validator_info(
    self,
    subnet_id: int,
    subnet_epoch: int
  ):
    """
    Query an epochs chosen subnet validator and return SubnetNode

    :param subnet_id: subnet ID
    :returns: Struct of subnet info
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_rpc_request():
      try:
        with self.interface as _interface:
          data = _interface.rpc_request(
            method='network_getElectedValidatorInfo',
            params=[
              subnet_id,
              subnet_epoch
            ]
          )
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_rpc_request()

  """
  Events
  """
  def get_reward_result_event(
    self,
    target_subnet_id: int,
    epoch: int
  ):
    """
    Query the event of an epochs rewards submission

    :param target_subnet_id: subnet ID

    :returns: subnet_nodes_data
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_event_query():
      try:
        epoch_length = self.get_epoch_length()
        epoch_length = int(str(epoch_length))
        block_number = epoch_length * epoch
        block_hash = self.interface.get_block_hash(block_number=block_number)
        with self.interface as _interface:
          data = None
          events = _interface.get_events(block_hash=block_hash)
          for event in events:
            if event['event']['module_id'] == "Network" and event['event']['event_id'] == "RewardResult":
              subnet_id, attestation_percentage = event['event']['attributes']
              if subnet_id == target_subnet_id:
                data = subnet_id, attestation_percentage
                break
          return data
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_event_query()

  """
  Helpers
  """
  def get_epoch_data(self) -> EpochData:
    current_block = self.get_block_number()
    epoch_length = self.get_epoch_length()
    current_block = int(str(current_block))
    epoch_length = int(str(epoch_length))
    epoch = current_block // epoch_length
    blocks_elapsed = current_block % epoch_length
    percent_complete = blocks_elapsed / epoch_length
    blocks_remaining = epoch_length - blocks_elapsed
    seconds_elapsed = blocks_elapsed * BLOCK_SECS
    seconds_remaining = blocks_remaining * BLOCK_SECS

    return EpochData(
      block=current_block,
      epoch=epoch,
      block_per_epoch=epoch_length,
      seconds_per_epoch=epoch_length * BLOCK_SECS,
      percent_complete=percent_complete,
      blocks_elapsed=blocks_elapsed,
      blocks_remaining=blocks_remaining,
      seconds_elapsed=seconds_elapsed,
      seconds_remaining=seconds_remaining
    )

  def get_subnet_epoch_data(self, slot: int) -> EpochData:
    current_block = int(str(self.get_block_number()))
    epoch_length = int(str(self.get_epoch_length()))

    if current_block < slot:
      return EpochData.zero(current_block=current_block, epoch_length=epoch_length)

    blocks_since_start = current_block - slot
    epoch = blocks_since_start // epoch_length
    blocks_elapsed = blocks_since_start % epoch_length
    percent_complete = blocks_elapsed / epoch_length
    blocks_remaining = epoch_length - blocks_elapsed
    seconds_elapsed = blocks_elapsed * BLOCK_SECS
    seconds_remaining = blocks_remaining * BLOCK_SECS

    return EpochData(
      block=current_block,
      epoch=epoch,
      block_per_epoch=epoch_length,
      seconds_per_epoch=epoch_length * BLOCK_SECS,
      percent_complete=percent_complete,
      blocks_elapsed=blocks_elapsed,
      blocks_remaining=blocks_remaining,
      seconds_elapsed=seconds_elapsed,
      seconds_remaining=seconds_remaining
    )

  def get_overwatch_epoch_data(self) -> EpochData:
    current_block = self.get_block_number()
    epoch_length = self.get_epoch_length()
    current_block = int(str(current_block))
    epoch_length = int(str(epoch_length))
    epoch = current_block // epoch_length
    blocks_elapsed = current_block % epoch_length
    percent_complete = blocks_elapsed / epoch_length
    blocks_remaining = epoch_length - blocks_elapsed
    seconds_elapsed = blocks_elapsed * BLOCK_SECS
    seconds_remaining = blocks_remaining * BLOCK_SECS

    multiplier = self.get_overwatch_epoch_multiplier()
    overwatch_epoch_length = epoch_length * multiplier
    cutoff_percentage = float(self.get_overwatch_commit_cutoff_percent() / 1e18)
    block_increase_cutoff = overwatch_epoch_length * cutoff_percentage
    epoch_cutoff_block = overwatch_epoch_length * epoch + block_increase_cutoff

    if current_block > epoch_cutoff_block:
      seconds_remaining_until_reveal = 0
    else:
      seconds_remaining_until_reveal = epoch_cutoff_block - current_block

    return OverwatchEpochData(
      block=current_block,
      epoch=epoch,
      block_per_epoch=epoch_length,
      seconds_per_epoch=epoch_length * BLOCK_SECS,
      percent_complete=percent_complete,
      blocks_elapsed=blocks_elapsed,
      blocks_remaining=blocks_remaining,
      seconds_elapsed=seconds_elapsed,
      seconds_remaining=seconds_remaining,
      seconds_remaining_until_reveal=seconds_remaining_until_reveal
    )

  def in_overwatch_commit_period(self) -> bool:
    epoch_data = self.get_epoch_data()
    epoch_length = epoch_data.block_per_epoch
    multiplier = self.get_overwatch_epoch_multiplier()
    overwatch_epoch_length = epoch_length * multiplier
    current_epoch = epoch_data.epoch
    cutoff_percentage = float(self.get_overwatch_commit_cutoff_percent() / 1e18)
    block_increase_cutoff = overwatch_epoch_length * cutoff_percentage
    epoch_cutoff_block = overwatch_epoch_length * current_epoch + block_increase_cutoff
    return epoch_data.block < epoch_cutoff_block

  """
  Formatted
  """
  def get_elected_validator_node_formatted(self, subnet_id: int, subnet_epoch: int) -> Optional["SubnetNode"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_elected_validator_info(
        subnet_id,
        subnet_epoch
      )

      subnet_node = SubnetNodeInfo.from_vec_u8(result["result"])

      return subnet_node
    except Exception:
      return None

  def get_formatted_subnet_data(self, subnet_id: int) -> Optional["SubnetData"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_subnet_data(
        subnet_id,
      )

      subnet = SubnetData.from_vec_u8(result["result"])

      return subnet
    except Exception:
      return None

  def get_formatted_subnet_info(self, subnet_id: int) -> Optional["SubnetInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_subnet_info(subnet_id)

      subnet = SubnetInfo.from_vec_u8(result["result"])

      return subnet
    except Exception:
      return None

  def get_formatted_all_subnet_info(self) -> List["SubnetInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_all_subnet_info()

      subnets_info = SubnetInfo.list_from_vec_u8(result["result"])

      return subnets_info
    except Exception:
      return None

  def get_formatted_get_subnet_node_info(self, subnet_id: int, subnet_node_id: int) -> Optional["SubnetNodeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_subnet_node_info(subnet_id, subnet_node_id)

      subnet_node_info = SubnetNodeInfo.from_vec_u8(result["result"])

      return subnet_node_info
    except Exception:
      return None

  def get_subnet_nodes_info_formatted(self, subnet_id: int) -> List["SubnetNodeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_subnet_nodes_info(subnet_id)

      subnet_nodes_info = SubnetNodeInfo.list_from_vec_u8(result["result"])

      return subnet_nodes_info
    except Exception:
      return None


  def get_all_subnet_nodes_info_formatted(self) -> List["SubnetNodeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_all_subnet_nodes_info()

      subnet_nodes_info = SubnetNodeInfo.list_from_vec_u8(result["result"])

      return subnet_nodes_info
    except Exception:
      return None

  def get_bootnodes_formatted(self, subnet_id: int) -> "AllSubnetBootnodes":
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_bootnodes(subnet_id)

      all_subnet_bootnodes = AllSubnetBootnodes.from_vec_u8(result["result"])

      return all_subnet_bootnodes
    except Exception:
      return None

  def get_coldkey_subnet_nodes_info_formatted(self, coldkey: str) -> List["SubnetNodeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_coldkey_subnet_nodes_info(coldkey)

      subnet_nodes_info = SubnetNodeInfo.list_from_vec_u8(result["result"])

      return subnet_nodes_info
    except Exception:
      return None

  def get_coldkey_stakes_formatted(self, coldkey: str) -> List["SubnetNodeStakeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_coldkey_stakes(coldkey)

      coldkey_stakes = SubnetNodeStakeInfo.list_from_vec_u8(result["result"])

      return coldkey_stakes
    except Exception:
      return None

  def get_delegate_stakes_formatted(self, account_id: str) -> List["DelegateStakeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_delegate_stakes(account_id)

      delegate_stakes = DelegateStakeInfo.list_from_vec_u8(result["result"])

      return delegate_stakes
    except Exception:
      return None

  def get_node_delegate_stakes_formatted(self, account_id: str) -> List["NodeDelegateStakeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_node_delegate_stakes(account_id)

      node_delegate_stakes = NodeDelegateStakeInfo.list_from_vec_u8(result["result"])

      return node_delegate_stakes
    except Exception:
      return None

  def get_consensus_data_formatted(self, subnet_id: int, epoch: int) -> Optional[ConsensusData]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_consensus_data(subnet_id, epoch)

      if result is None or result == 'None' or result == None:  # noqa: E711
        return None

      consensus_data = ConsensusData.fix_decoded_values(result)

      return consensus_data
    except Exception as e:
      print(e)
      return None

  def get_min_class_subnet_nodes_formatted(self, subnet_id: int, subnet_epoch: int, min_class: SubnetNodeClass) -> List["SubnetNodeInfo"]:
    """
    Get formatted list of subnet nodes classified as Validator

    :param subnet_id: subnet ID

    :returns: List of subnet node IDs
    """
    try:
      result = self.get_subnet_nodes_info(subnet_id)

      subnet_nodes = SubnetNodeInfo.list_from_vec_u8(result["result"])

      return [
          node for node in subnet_nodes
          if subnet_node_class_to_enum(node.classification['node_class']).value >= min_class.value and node.classification['start_epoch'] <= subnet_epoch
      ]
    except Exception:
      return []

  def update_bootnodes(
    self,
    subnet_id: int,
    add: list,
    remove: list,
  ) -> ExtrinsicReceipt:
    """
    Remove a subnet

    :param self.keypair: self.keypair of extrinsic caller. Must be a subnet_node in the subnet
    :param subnet_id: subnet ID
    """

    # compose call
    call = self.interface.compose_call(
      call_module='Network',
      call_function='update_bootnodes',
      call_params={
        'subnet_id': subnet_id,
        'add': sorted(set(add)),
        'remove': sorted(set(remove)),
      }
    )

    # create signed extrinsic
    extrinsic = self.interface.create_signed_extrinsic(call=call, keypair=self.keypair)

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def submit_extrinsic():
      try:
        with self.interface as _interface:
          receipt = _interface.submit_extrinsic(extrinsic, wait_for_inclusion=True)
          return receipt
      except SubstrateRequestException as e:
        print("Failed to send: {}".format(e))

    return submit_extrinsic()

  def get_subnet_key_types(
    self,
    subnet_id: int,
  ) -> ExtrinsicReceipt:
    """
    Query hotkey by subnet node ID

    :param hotkey: Hotkey of subnet node
    """

    @retry(wait=wait_fixed(BLOCK_SECS+1), stop=stop_after_attempt(4))
    def make_query():
      try:
        with self.interface as _interface:
          result = _interface.query('Network', 'SubnetKeyTypes', [subnet_id])
          return result
      except SubstrateRequestException as e:
        print("Failed to get rpc request: {}".format(e))

    return make_query()

