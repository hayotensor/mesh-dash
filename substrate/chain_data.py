import ast
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import scalecodec
from scalecodec.base import RuntimeConfiguration, ScaleBytes
from scalecodec.type_registry import load_type_registry_preset

custom_rpc_type_registry = {
  "types": {
    "SubnetData": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["name", "Vec<u8>"],
        ["repo", "Vec<u8>"],
        ["description", "Vec<u8>"],
        ["misc", "Vec<u8>"],
        ["state", "SubnetState"],
        ["start_epoch", "u32"],
      ],
    },
    "SubnetInfo": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["name", "Vec<u8>"],
        ["repo", "Vec<u8>"],
        ["description", "Vec<u8>"],
        ["misc", "Vec<u8>"],
        ["state", "SubnetState"],
        ["start_epoch", "u32"],
        ["churn_limit", "u32"],
        ["min_stake", "u128"],
        ["max_stake", "u128"],
        ["queue_immunity_epochs", "u32"],
        ["target_node_registrations_per_epoch", "u32"],
        ["subnet_node_queue_epochs", "u32"],
        ["idle_classification_epochs", "u32"],
        ["included_classification_epochs", "u32"],
        ["delegate_stake_percentage", "u128"],
        ["node_burn_rate_alpha", "u128"],
        ["max_node_penalties", "u32"],
        ["initial_coldkeys", "Option<Vec<[u8; 20]>>"],
        ["max_registered_nodes", "u32"],
        ["owner", "Option<[u8; 20]>"],
        ["pending_owner", "Option<[u8; 20]>"],
        ["registration_epoch", "Option<u32>"],
        ["key_types", "BTreeSet<KeyType>"],
        ["slot_index", "Option<u32>"],
        ["penalty_count", "u32"],
        ["bootnode_access", "BTreeSet<[u8; 20]>"],
        ["bootnodes", "BTreeSet<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["total_nodes", "u32"],
        ["total_active_nodes", "u32"],
        ["total_electable_nodes", "u32"],
        ["current_min_delegate_stake", "u128"]
      ],
    },
    "SubnetState": {
      "type": "enum",
      "value_list": [
        "Registered",
        "Active",
        "Paused",
      ],
    },
    "KeyType": {
      "type": "enum",
      "value_list": [
        "Rsa",
        "Ed25519",
        "Secp256k1",
        "Ecdsa",
      ],
    },
    "SubnetNode": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["hotkey", "[u8; 20]"],
        ["peer_id", "OpaquePeerId"],
        ["bootnode_peer_id", "OpaquePeerId"],
        ["bootnode", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["client_peer_id", "OpaquePeerId"],
        ["classification", "SubnetNodeClassification"],
        ["delegate_reward_rate", "u128"],
        ["last_delegate_reward_rate_update", "u32"],
        ["unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["non_unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
      ],
    },
    "SubnetNodeClassification": {
      "type": "struct",
      "type_mapping": [
        ["node_class", "SubnetNodeClass"],
        ["start_epoch", "u32"],
      ],
    },
    "SubnetNodeClass": {
      "type": "enum",
      "value_list": [
        "Registered",
        "Idle",
        "Included",
        "Validator",
      ],
    },
    "SubnetNodeConsensusData": {
      "type": "struct",
      "type_mapping": [
        ["subnet_node_id", "u32"],
        ["score", "u128"],
      ],
    },
    "RewardsData": {
      "type": "struct",
      "type_mapping": [
        ["overall_subnet_reward", "u128"],
        ["subnet_owner_reward", "u128"],
        ["subnet_rewards", "u128"],
        ["delegate_stake_rewards", "u128"],
        ["subnet_node_rewards", "u128"],
      ],
    },
    "SubnetNodeInfo": {
      "type": "struct",
      "type_mapping": [
        ["subnet_id", "u32"],
        ["subnet_node_id", "u32"],
        ["coldkey", "[u8; 20]"],
        ["hotkey", "[u8; 20]"],
        ["peer_id", "PeerId"],
        ["bootnode_peer_id", "PeerId"],
        ["client_peer_id", "PeerId"],
        ["bootnode", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["identity", "ColdkeyIdentityData"],
        ["classification", "SubnetNodeClassification"],
        ["delegate_reward_rate", "u128"],
        ["last_delegate_reward_rate_update", "u32"],
        ["unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["non_unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["stake_balance", "u128"],
        ["node_delegate_stake_balance", "u128"],
        ["penalties", "u32"],
        ["reputation", "Reputation"],
      ],
    },
    "Reputation": {
      "type": "struct",
      "type_mapping": [
        ["start_epoch", "u32"],
        ["score", "u128"],
        ["lifetime_node_count", "u32"],
        ["total_active_nodes", "u32"],
        ["total_increases", "u32"],
        ["total_decreases", "u32"],
        ["average_attestation", "u128"],
        ["last_validator_epoch", "u32"],
        ["ow_score", "u128"],
      ],
    },
    "ColdkeyIdentityData": {
      "type": "struct",
      "type_mapping": [
        ["name", "BoundedVec<u8, DefaultMaxVectorLength>"],
        ["url", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["image", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["discord", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["x", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["telegram", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["github", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["hugging_face", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["description", "BoundedVec<u8, DefaultMaxVectorLength>"],
        ["misc", "BoundedVec<u8, DefaultMaxVectorLength>"],
      ],
    },
    "AttestEntry": {
      "type": "struct",
      "type_mapping": [
        ["block", "u32"],
        ["data", "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>"]
      ]
    },
    "ConsensusData": {
      "type": "struct",
      "type_mapping": [
        ["validator_id", "u32"],
        ["attests", "BTreeMap<u32, AttestEntry>"],
        ["subnet_nodes", "Vec<SubnetNode<[u8; 20]>>"],
        ["prioritize_queue_node_id", "Option<u32>"],
        ["remove_queue_node_id", "Option<u32>"],
        ["data", "Vec<SubnetNodeConsensusData>"],
        ["args", "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>"],
      ],
    },
    "ConsensusSubmissionData": {
      "type": "struct",
      "type_mapping": [
        ["validator_subnet_node_id", "u32"],
        ["attestation_ratio", "u128"],
        ["weight_sum", "u128"],
        ["data_length", "u32"],
        ["data", "Vec<SubnetNodeConsensusData>"],
        ["attests", "BTreeMap<u32, AttestEntry>"],
        ["subnet_nodes", "Vec<SubnetNode<[u8; 20]>>"],
        ["prioritize_queue_node_id", "Option<u32>"],
        ["remove_queue_node_id", "Option<u32>"],
      ],
    },
    "AllSubnetBootnodes": {
      "type": "struct",
      "type_mapping": [
        ["bootnodes", "BTreeSet<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["node_bootnodes", "BTreeSet<BoundedVec<u8, DefaultMaxVectorLength>>"],
      ],
    },
    "SubnetNodeStakeInfo": {
      "type": "struct",
      "type_mapping": [
        ["subnet_id", "Option<u32>"],
        ["subnet_node_id", "Option<u32>"],
        ["hotkey", "[u8; 20]"],
        ["balance", "u128"],
      ],
    },
    "DelegateStakeInfo": {
      "type": "struct",
      "type_mapping": [
        ["subnet_id", "u32"],
        ["shares", "u128"],
        ["balance", "u128"],
      ],
    },
    "NodeDelegateStakeInfo": {
      "type": "struct",
      "type_mapping": [
        ["subnet_id", "u32"],
        ["subnet_node_id", "u32"],
        ["shares", "u128"],
        ["balance", "u128"],
      ],
    },
    "PeerId": "Vec<u8>",
    "BTreeSet<KeyType>": "Vec<KeyType>",
    "BTreeSet<[u8; 20]>": "Vec<[u8; 20]>",
    "BTreeSet<BoundedVec<u8, DefaultMaxVectorLength>>": "Vec<BoundedVec<u8, DefaultMaxVectorLength>>",  # Not just Vec<u8>
    "BoundedVec<u8, DefaultMaxVectorLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultMaxUrlLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultMaxSocialIdLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultValidatorArgsLimit>": "Vec<u8>",
    "Option<BoundedVec<u8, DefaultMaxVectorLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultMaxUrlLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultMaxSocialIdLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>": "Option<Vec<u8>>",
  }
}

class ChainDataType(Enum):
  """
  Enum for chain data types.
  """
  SubnetData = 1
  SubnetInfo = 2
  SubnetNode = 3
  RewardsData = 4
  SubnetNodeInfo = 5
  ConsensusSubmissionData = 6
  SubnetNodeConsensusData = 7
  ConsensusData = 8
  AllSubnetBootnodes = 9
  SubnetNodeStakeInfo = 10
  DelegateStakeInfo = 11
  NodeDelegateStakeInfo = 12

def from_scale_encoding(
    input: Union[List[int], bytes, ScaleBytes],
    type_name: ChainDataType,
    is_vec: bool = False,
    is_option: bool = False,
) -> Optional[Dict]:
    """
    Returns the decoded data from the SCALE encoded input.

    Args:
      input (Union[List[int], bytes, ScaleBytes]): The SCALE encoded input.
      type_name (ChainDataType): The ChainDataType enum.
      is_vec (bool): Whether the input is a Vec.
      is_option (bool): Whether the input is an Option.

    Returns:
      Optional[Dict]: The decoded data
    """

    type_string = type_name.name
    if is_option:
      type_string = f"Option<{type_string}>"
    if is_vec:
      type_string = f"Vec<{type_string}>"

    return from_scale_encoding_using_type_string(input, type_string)

def from_scale_encoding_using_type_string(
  input: Union[List[int], bytes, ScaleBytes], type_string: str
) -> Optional[Dict]:
  """
  Returns the decoded data from the SCALE encoded input using the type string.

  Args:
    input (Union[List[int], bytes, ScaleBytes]): The SCALE encoded input.
    type_string (str): The type string.

  Returns:
    Optional[Dict]: The decoded data
  """
  if isinstance(input, ScaleBytes):
    as_scale_bytes = input
  else:
    if isinstance(input, list) and all([isinstance(i, int) for i in input]):
      vec_u8 = input
      as_bytes = bytes(vec_u8)
    elif isinstance(input, bytes):
      as_bytes = input
    else:
      raise TypeError("input must be a List[int], bytes, or ScaleBytes")

    as_scale_bytes = scalecodec.ScaleBytes(as_bytes)

  rpc_runtime_config = RuntimeConfiguration()
  rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
  rpc_runtime_config.update_type_registry(custom_rpc_type_registry)

  obj = rpc_runtime_config.create_scale_object(type_string, data=as_scale_bytes)

  return obj.decode()

@dataclass
class SubnetData:
  """
  Dataclass for subnet node info.
  """
  id: int
  name: str
  repo: str
  description: str
  misc: str
  state: str
  start_epoch: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetData":
    """Fixes the values of the RewardsData object."""
    data_decoded["id"] = data_decoded["id"]
    data_decoded["name"] = data_decoded["name"]
    data_decoded["repo"] = data_decoded["repo"]
    data_decoded["description"] = data_decoded["description"]
    data_decoded["misc"] = data_decoded["misc"]
    data_decoded["state"] = data_decoded["state"]
    data_decoded["start_epoch"] = data_decoded["start_epoch"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "SubnetData":
    """Returns a SubnetData object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetData._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetData)

    if decoded is None:
      return SubnetData._get_null()

    decoded = SubnetData.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetData"]:
    """Returns a list of SubnetData objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetData, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      SubnetData.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_data_to_namespace(data) -> "SubnetData":
    """
    Converts a SubnetData object to a namespace.

    Args:
      rewards_data (SubnetData): The SubnetData object.

    Returns:
      SubnetData: The SubnetData object.
    """
    data = SubnetData(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetData":
    subnet_dataa = SubnetData(
      id=0,
      name="",
      repo="",
      description="",
      misc="",
      state=0,
      start_epoch=0,
    )
    return subnet_dataa

@dataclass
class SubnetInfo:
  """
  Dataclass for subnet node info.
  """
  id: int
  name: str
  repo: str
  description: str
  misc: str
  state: int
  start_epoch: int
  churn_limit: int
  min_stake: int
  max_stake: int
  queue_immunity_epochs: int
  target_node_registrations_per_epoch: int
  subnet_node_queue_epochs: int
  idle_classification_epochs: int
  included_classification_epochs: int
  delegate_stake_percentage: int
  node_burn_rate_alpha: int
  max_node_penalties: int
  initial_coldkeys: list
  max_registered_nodes: int
  owner: str
  pending_owner: str
  registration_epoch: int
  key_types: list
  slot_index: int
  penalty_count: int
  bootnode_access: list
  bootnodes: list
  total_nodes: int
  total_active_nodes: int
  total_electable_nodes: int
  current_min_delegate_stake: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetInfo":
    """Fixes the values of the SubnetInfo object."""
    data_decoded["id"] = data_decoded["id"]
    data_decoded["name"] = data_decoded["name"]
    data_decoded["repo"] = data_decoded["repo"]
    data_decoded["description"] = data_decoded["description"]
    data_decoded["misc"] = data_decoded["misc"]
    data_decoded["state"] = data_decoded["state"]
    data_decoded["start_epoch"] = data_decoded["start_epoch"]
    data_decoded["churn_limit"] = data_decoded["churn_limit"]
    data_decoded["min_stake"] = data_decoded["min_stake"]
    data_decoded["max_stake"] = data_decoded["max_stake"]
    data_decoded["queue_immunity_epochs"] = data_decoded["queue_immunity_epochs"]
    data_decoded["target_node_registrations_per_epoch"] = data_decoded["target_node_registrations_per_epoch"]
    data_decoded["subnet_node_queue_epochs"] = data_decoded["subnet_node_queue_epochs"]
    data_decoded["idle_classification_epochs"] = data_decoded["idle_classification_epochs"]
    data_decoded["included_classification_epochs"] = data_decoded["included_classification_epochs"]
    data_decoded["delegate_stake_percentage"] = data_decoded["delegate_stake_percentage"]
    data_decoded["node_burn_rate_alpha"] = data_decoded["node_burn_rate_alpha"]
    data_decoded["max_node_penalties"] = data_decoded["max_node_penalties"]
    data_decoded["initial_coldkeys"] = data_decoded["initial_coldkeys"]
    data_decoded["max_registered_nodes"] = data_decoded["max_registered_nodes"]
    data_decoded["owner"] = data_decoded["owner"]
    data_decoded["pending_owner"] = data_decoded["pending_owner"]
    data_decoded["registration_epoch"] = data_decoded["registration_epoch"]
    data_decoded["key_types"] = data_decoded["key_types"]
    data_decoded["slot_index"] = data_decoded["slot_index"]
    data_decoded["penalty_count"] = data_decoded["penalty_count"]
    data_decoded["bootnode_access"] = data_decoded["bootnode_access"]
    data_decoded["bootnodes"] = data_decoded["bootnodes"]
    data_decoded["total_nodes"] = data_decoded["total_nodes"]
    data_decoded["total_active_nodes"] = data_decoded["total_active_nodes"]
    data_decoded["total_electable_nodes"] = data_decoded["total_electable_nodes"]
    data_decoded["current_min_delegate_stake"] = data_decoded["current_min_delegate_stake"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "SubnetInfo":
    """Returns a SubnetInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetInfo._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetInfo, is_option=True)

    if decoded is None:
      return SubnetInfo._get_null()

    decoded = SubnetInfo.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetInfo"]:
    """Returns a list of SubnetInfo objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetInfo, is_vec=True
    )

    if decoded_list is None:
      return []

    decoded_list = [
      SubnetInfo.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_info_to_namespace(data) -> "SubnetInfo":
    """
    Converts a SubnetInfo object to a namespace.

    Args:
      rewards_data (SubnetInfo): The SubnetInfo object.

    Returns:
      SubnetInfo: The SubnetInfo object.
    """
    data = SubnetInfo(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetInfo":
    subnet_info = SubnetInfo(
      id="",
      name="",
      repo="",
      description="",
      misc="",
      state=0,
      start_epoch=0,
      churn_limit=0,
      min_stake=0,
      max_stake=0,
      queue_immunity_epochs=0,
      target_node_registrations_per_epoch=0,
      subnet_node_queue_epochs=0,
      idle_classification_epochs=0,
      included_classification_epochs=0,
      delegate_stake_percentage=0,
      node_burn_rate_alpha=0,
      max_node_penalties=0,
      initial_coldkeys=0,
      max_registered_nodes=0,
      owner="000000000000000000000000000000000000000000000000",
      pending_owner="000000000000000000000000000000000000000000000000",
      registration_epoch=0,
      key_types=0,
      slot_index=0,
      penalty_count=0,
      bootnode_access=0,
      bootnodes=0,
      total_nodes=0,
      total_active_nodes=0,
      total_electable_nodes=0,
      current_min_delegate_stake=0
    )
    return subnet_info

@dataclass
class RewardsData:
  """
  Dataclass for model peer metadata.
  """
  overall_subnet_reward: int
  subnet_owner_reward: int
  subnet_rewards: int
  delegate_stake_rewards: int
  subnet_node_rewards: int

  @classmethod
  def fix_decoded_values(cls, rewards_data_decoded: Any) -> "RewardsData":
    """Fixes the values of the RewardsData object."""
    rewards_data_decoded["overall_subnet_reward"] = rewards_data_decoded["overall_subnet_reward"]
    rewards_data_decoded["subnet_owner_reward"] = rewards_data_decoded["subnet_owner_reward"]
    rewards_data_decoded["subnet_rewards"] = rewards_data_decoded["subnet_rewards"]
    rewards_data_decoded["delegate_stake_rewards"] = rewards_data_decoded["delegate_stake_rewards"]
    rewards_data_decoded["subnet_node_rewards"] = rewards_data_decoded["subnet_node_rewards"]

    return cls(**rewards_data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "RewardsData":
    """Returns a RewardsData object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return RewardsData._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.RewardsData)

    if decoded is None:
      return RewardsData._get_null()

    decoded = RewardsData.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["RewardsData"]:
    """Returns a list of RewardsData objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.RewardsData, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      RewardsData.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @classmethod
  def list_from_scale_info(cls, scale_info: Any) -> List["RewardsData"]:
    """Returns a list of RewardsData objects from a ``decoded_list``."""

    encoded_list = []
    for code in map(ord, str(scale_info)):
      encoded_list.append(code)


    decoded = ''.join(map(chr, encoded_list))

    json_data = ast.literal_eval(json.dumps(decoded))

    decoded_list = []
    for item in scale_info:
      decoded_list.append(
        RewardsData(
          overall_subnet_reward=0,
          subnet_owner_reward=0,
          subnet_rewards=0,
          delegate_stake_rewards=0,
          subnet_node_rewards=0,
        )
      )

    return decoded_list

  @staticmethod
  def _rewards_data_to_namespace(rewards_data) -> "RewardsData":
    """
    Converts a RewardsData object to a namespace.

    Args:
      rewards_data (RewardsData): The RewardsData object.

    Returns:
      RewardsData: The RewardsData object.
    """
    data = RewardsData(**rewards_data)

    return data

  @staticmethod
  def _get_null() -> "RewardsData":
    rewards_data = RewardsData(
      peer_id="",
      score=0,
    )
    return rewards_data

@dataclass
class SubnetNodeInfo:
  """
  Dataclass for subnet node info.
  """
  subnet_id: int
  subnet_node_id: int
  coldkey: str
  hotkey: str
  peer_id: str
  bootnode_peer_id: str
  client_peer_id: str
  bootnode: str
  identity: dict
  classification: dict
  delegate_reward_rate: int
  last_delegate_reward_rate_update: int
  unique: str
  non_unique: str
  stake_balance: int
  node_delegate_stake_balance: int
  penalties: int
  reputation: dict

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetNodeInfo":
    """Fixes the values of the SubnetNodeInfo object."""
    data_decoded["subnet_id"] = data_decoded["subnet_id"]
    data_decoded["subnet_node_id"] = data_decoded["subnet_node_id"]
    data_decoded["coldkey"] = data_decoded["coldkey"]
    data_decoded["hotkey"] = data_decoded["hotkey"]
    data_decoded["peer_id"] = data_decoded["peer_id"]
    data_decoded["bootnode_peer_id"] = data_decoded["bootnode_peer_id"]
    data_decoded["client_peer_id"] = data_decoded["client_peer_id"]
    data_decoded["bootnode"] = data_decoded["bootnode"]
    data_decoded["identity"] = data_decoded["identity"]
    data_decoded["classification"] = data_decoded["classification"]
    data_decoded["delegate_reward_rate"] = data_decoded["delegate_reward_rate"]
    data_decoded["last_delegate_reward_rate_update"] = data_decoded["last_delegate_reward_rate_update"]
    data_decoded["unique"] = data_decoded["unique"]
    data_decoded["non_unique"] = data_decoded["non_unique"]
    data_decoded["stake_balance"] = data_decoded["stake_balance"]
    data_decoded["node_delegate_stake_balance"] = data_decoded["node_delegate_stake_balance"]
    data_decoded["penalties"] = data_decoded["penalties"]
    data_decoded["reputation"] = data_decoded["reputation"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "SubnetNodeInfo":
    """Returns a SubnetNodeInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetNodeInfo._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetNodeInfo, is_option=True)

    if decoded is None:
      return SubnetNodeInfo._get_null()

    decoded = SubnetNodeInfo.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetNodeInfo"]:
    """Returns a list of SubnetNodeInfo objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetNodeInfo, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      SubnetNodeInfo.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_node_info_to_namespace(data) -> "SubnetNodeInfo":
    """
    Converts a SubnetNodeInfo object to a namespace.

    Args:
      rewards_data (SubnetNodeInfo): The SubnetNodeInfo object.

    Returns:
      SubnetNodeInfo: The SubnetNodeInfo object.
    """
    data = SubnetNodeInfo(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetNodeInfo":
    subnet_node_info = SubnetNodeInfo(
      subnet_id=0,
      subnet_node_id=0,
      coldkey="000000000000000000000000000000000000000000000000",
      hotkey="000000000000000000000000000000000000000000000000",
      peer_id="000000000000000000000000000000000000000000000000",
      bootnode_peer_id="000000000000000000000000000000000000000000000000",
      client_peer_id="000000000000000000000000000000000000000000000000",
      bootnode="",
      identity=dict(),
      classification=dict(),
      delegate_reward_rate=0,
      last_delegate_reward_rate_update=0,
      unique="",
      non_unique="",
      stake_balance=0,
      node_delegate_stake_balance=0,
      penalties=0,
      reputation=dict()
    )
    return subnet_node_info

@dataclass
class SubnetNode:
  """
  Dataclass for model peer metadata.
  """
  id: int
  hotkey: str
  peer_id: str
  bootnode_peer_id: str
  bootnode: str
  client_peer_id: str
  classification: str
  delegate_reward_rate: int
  last_delegate_reward_rate_update: int
  unique: str
  non_unique: str

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetNode":
    """Fixes the values of the SubnetNode object."""
    data_decoded["id"] = data_decoded["id"]
    data_decoded["hotkey"] = data_decoded["hotkey"]
    data_decoded["peer_id"] = data_decoded["peer_id"]
    data_decoded["bootnode_peer_id"] = data_decoded["bootnode_peer_id"]
    data_decoded["client_peer_id"] = data_decoded["client_peer_id"]
    data_decoded["bootnode"] = data_decoded["bootnode"]
    data_decoded["classification"] = data_decoded["classification"]
    data_decoded["delegate_reward_rate"] = data_decoded["delegate_reward_rate"]
    data_decoded["last_delegate_reward_rate_update"] = data_decoded["last_delegate_reward_rate_update"]
    data_decoded["unique"] = data_decoded["unique"]
    data_decoded["non_unique"] = data_decoded["non_unique"]

    return cls(**data_decoded)

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetNode"]:
    """Returns a list of SubnetNode objects from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return []

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetNode, is_vec=True
    )

    if decoded_list is None:
      return []

    decoded_list = [
      SubnetNode.fix_decoded_values(decoded) for decoded in decoded_list
    ]

    return decoded_list

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "SubnetNode":
    """Returns a SubnetNodeInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetNode._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetNode)

    if decoded is None:
      return SubnetNode._get_null()

    decoded = SubnetNode.fix_decoded_values(decoded)

    return decoded

  @staticmethod
  def _subnet_node_to_namespace(data) -> "SubnetNode":
    """
    Converts a SubnetNode object to a namespace.

    Args:
      rewards_data (SubnetNode): The SubnetNode object.

    Returns:
      SubnetNode: The SubnetNode object.
    """
    data = SubnetNode(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetNode":
    subnet_node = SubnetNode(
      id=0,
      hotkey="000000000000000000000000000000000000000000000000",
      # peer_id=PeerID.from_base58("000000000000000000000000000000000000000000000000"),
      # bootnode_peer_id=PeerID.from_base58("000000000000000000000000000000000000000000000000"),
      # client_peer_id=PeerID.from_base58("000000000000000000000000000000000000000000000000"),
      peer_id="000000000000000000000000000000000000000000000000",
      bootnode_peer_id="000000000000000000000000000000000000000000000000",
      client_peer_id="000000000000000000000000000000000000000000000000",
      bootnode="",
      classification="",
      delegate_reward_rate=0,
      last_delegate_reward_rate_update=0,
      unique="",
      non_unique="",
    )
    return subnet_node

@dataclass
class ConsensusSubmissionData:
  """
  Dataclass for subnet node info.
  """
  validator_subnet_node_id: int
  attestation_ratio: int
  weight_sum: int
  data_length: int
  data: list
  subnet_nodes: list

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "ConsensusSubmissionData":
    """Fixes the values of the ConsensusSubmissionData object."""
    data_decoded["validator_subnet_node_id"] = data_decoded["validator_subnet_node_id"]
    data_decoded["attestation_ratio"] = data_decoded["attestation_ratio"]
    data_decoded["weight_sum"] = data_decoded["weight_sum"]
    data_decoded["data_length"] = data_decoded["data_length"]
    data_decoded["data"] = data_decoded["data"]
    data_decoded["subnet_nodes"] = data_decoded["subnet_nodes"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "ConsensusSubmissionData":
    """Returns a ConsensusSubmissionData object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return ConsensusSubmissionData._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.ConsensusSubmissionData)

    if decoded is None:
      return ConsensusSubmissionData._get_null()

    decoded = ConsensusSubmissionData.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["ConsensusSubmissionData"]:
    """Returns a list of ConsensusSubmissionData objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.ConsensusSubmissionData, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      ConsensusSubmissionData.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _consensus_submission_data_to_namespace(data) -> "ConsensusSubmissionData":
    """
    Converts a ConsensusSubmissionData object to a namespace.

    Args:
      rewards_data (ConsensusSubmissionData): The ConsensusSubmissionData object.

    Returns:
      ConsensusSubmissionData: The ConsensusSubmissionData object.
    """
    data = ConsensusSubmissionData(**data)

    return data

  @staticmethod
  def _get_null() -> "ConsensusSubmissionData":
    data = ConsensusSubmissionData(
      validator_subnet_node_id=0,
      attestation_ratio=0,
      weight_sum=0,
      data_length=0,
      data=[],
      subnet_nodes=[],
    )
    return data

@dataclass
class SubnetNodeConsensusData:
  """
  Dataclass for subnet node info.
  """
  subnet_node_id: int
  score: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetNodeConsensusData":
    """Fixes the values of the SubnetNodeConsensusData object."""
    data_decoded["subnet_node_id"] = data_decoded["subnet_node_id"]
    data_decoded["score"] = data_decoded["score"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> "SubnetNodeConsensusData":
    """Returns a SubnetNodeConsensusData object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetNodeConsensusData._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetNodeConsensusData)

    if decoded is None:
      return SubnetNodeConsensusData._get_null()

    decoded = SubnetNodeConsensusData.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetNodeConsensusData"]:
    """Returns a list of SubnetNodeConsensusData objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetNodeConsensusData, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      SubnetNodeConsensusData.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_node_consensus_data_to_namespace(data) -> "SubnetNodeConsensusData":
    """
    Converts a SubnetNodeConsensusData object to a namespace.

    Args:
      rewards_data (SubnetNodeConsensusData): The SubnetNodeConsensusData object.

    Returns:
      SubnetNodeConsensusData: The SubnetNodeConsensusData object.
    """
    data = SubnetNodeConsensusData(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetNodeConsensusData":
    data = SubnetNodeConsensusData(
      subnet_node_id=0,
      score=0,
    )
    return data


@dataclass
class ConsensusData:
  """
  Dataclass for subnet node info.
  """
  validator_id: int
  attests: list
  subnet_nodes: list
  prioritize_queue_node_id: int | None
  remove_queue_node_id: int | None
  data: list | None
  args: list | None

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "ConsensusData":
      """Converts substrate-interface SCALE object to ConsensusData dataclass."""
      return cls(**data_decoded.serialize())

@dataclass
class AllSubnetBootnodes:
  """
  Dataclass for subnet node info.
  """
  bootnodes: list
  node_bootnodes: list

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "AllSubnetBootnodes":
    """Fixes the values of the AllSubnetBootnodes object."""
    data_decoded["bootnodes"] = data_decoded["bootnodes"]
    data_decoded["node_bootnodes"] = data_decoded["node_bootnodes"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> Optional["AllSubnetBootnodes"]:
    """Returns a AllSubnetBootnodes object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return AllSubnetBootnodes._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.AllSubnetBootnodes)

    if decoded is None:
      return AllSubnetBootnodes._get_null()

    decoded = AllSubnetBootnodes.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["AllSubnetBootnodes"]:
    """Returns a list of AllSubnetBootnodes objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.AllSubnetBootnodes, is_vec=True, is_option=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      AllSubnetBootnodes.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _bootnodes_data_to_namespace(data) -> "AllSubnetBootnodes":
    """
    Converts a AllSubnetBootnodes object to a namespace.

    Args:
      rewards_data (AllSubnetBootnodes): The AllSubnetBootnodes object.

    Returns:
      AllSubnetBootnodes: The AllSubnetBootnodes object.
    """
    data = AllSubnetBootnodes(**data)

    return data

  @staticmethod
  def _get_null() -> "AllSubnetBootnodes":
    data = AllSubnetBootnodes(
      bootnodes=[],
      node_bootnodes=[],
    )
    return data

@dataclass
class SubnetNodeStakeInfo:
  subnet_id: int
  subnet_node_id: int
  hotkey: str
  balance: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "SubnetNodeStakeInfo":
    """Fixes the values of the SubnetNodeStakeInfo object."""
    data_decoded["subnet_id"] = data_decoded["subnet_id"]
    data_decoded["subnet_node_id"] = data_decoded["subnet_node_id"]
    data_decoded["hotkey"] = data_decoded["hotkey"]
    data_decoded["balance"] = data_decoded["balance"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> Optional["SubnetNodeStakeInfo"]:
    """Returns a SubnetNodeStakeInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return SubnetNodeStakeInfo._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.SubnetNodeStakeInfo)

    if decoded is None:
      return SubnetNodeStakeInfo._get_null()

    decoded = SubnetNodeStakeInfo.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["SubnetNodeStakeInfo"]:
    """Returns a list of SubnetNodeStakeInfo objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.SubnetNodeStakeInfo, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      SubnetNodeStakeInfo.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_node_stake_info_data_to_namespace(data) -> "SubnetNodeStakeInfo":
    """
    Converts a SubnetNodeStakeInfo object to a namespace.

    Args:
      rewards_data (SubnetNodeStakeInfo): The SubnetNodeStakeInfo object.

    Returns:
      SubnetNodeStakeInfo: The SubnetNodeStakeInfo object.
    """
    data = SubnetNodeStakeInfo(**data)

    return data

  @staticmethod
  def _get_null() -> "SubnetNodeStakeInfo":
    data = SubnetNodeStakeInfo(
      subnet_id=0,
      subnet_node_id=0,
      hotkey="000000000000000000000000000000000000000000000000",
      balance=0
    )
    return data

@dataclass
class DelegateStakeInfo:
  subnet_id: int
  shares: int
  balance: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "DelegateStakeInfo":
    """Fixes the values of the DelegateStakeInfo object."""
    data_decoded["subnet_id"] = data_decoded["subnet_id"]
    data_decoded["shares"] = data_decoded["shares"]
    data_decoded["balance"] = data_decoded["balance"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> Optional["DelegateStakeInfo"]:
    """Returns a DelegateStakeInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return DelegateStakeInfo._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.DelegateStakeInfo)

    if decoded is None:
      return DelegateStakeInfo._get_null()

    decoded = DelegateStakeInfo.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["DelegateStakeInfo"]:
    """Returns a list of DelegateStakeInfo objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.DelegateStakeInfo, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      DelegateStakeInfo.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_node_stake_info_data_to_namespace(data) -> "DelegateStakeInfo":
    """
    Converts a DelegateStakeInfo object to a namespace.

    Args:
      rewards_data (DelegateStakeInfo): The DelegateStakeInfo object.

    Returns:
      SubnetNoDelegateStakeInfodeStakeInfo: The DelegateStakeInfo object.
    """
    data = DelegateStakeInfo(**data)

    return data

  @staticmethod
  def _get_null() -> "DelegateStakeInfo":
    data = DelegateStakeInfo(
      subnet_id=0,
      shares=0,
      balance=0
    )
    return data

@dataclass
class NodeDelegateStakeInfo:
  subnet_id: int
  subnet_node_id: int
  shares: int
  balance: int

  @classmethod
  def fix_decoded_values(cls, data_decoded: Any) -> "NodeDelegateStakeInfo":
    """Fixes the values of the NodeDelegateStakeInfo object."""
    data_decoded["subnet_id"] = data_decoded["subnet_id"]
    data_decoded["shares"] = data_decoded["shares"]
    data_decoded["balance"] = data_decoded["balance"]

    return cls(**data_decoded)

  @classmethod
  def from_vec_u8(cls, vec_u8: List[int]) -> Optional["NodeDelegateStakeInfo"]:
    """Returns a NodeDelegateStakeInfo object from a ``vec_u8``."""

    if len(vec_u8) == 0:
      return NodeDelegateStakeInfo._get_null()

    decoded = from_scale_encoding(vec_u8, ChainDataType.NodeDelegateStakeInfo)

    if decoded is None:
      return NodeDelegateStakeInfo._get_null()

    decoded = NodeDelegateStakeInfo.fix_decoded_values(decoded)

    return decoded

  @classmethod
  def list_from_vec_u8(cls, vec_u8: List[int]) -> List["NodeDelegateStakeInfo"]:
    """Returns a list of NodeDelegateStakeInfo objects from a ``vec_u8``."""

    decoded_list = from_scale_encoding(
      vec_u8, ChainDataType.NodeDelegateStakeInfo, is_vec=True
    )
    if decoded_list is None:
      return []

    decoded_list = [
      NodeDelegateStakeInfo.fix_decoded_values(decoded) for decoded in decoded_list
    ]
    return decoded_list

  @staticmethod
  def _subnet_node_stake_info_data_to_namespace(data) -> "NodeDelegateStakeInfo":
    """
    Converts a NodeDelegateStakeInfo object to a namespace.

    Args:
      rewards_data (NodeDelegateStakeInfo): The NodeDelegateStakeInfo object.

    Returns:
      SubnetNoDelegateStakeInfodeStakeInfo: The NodeDelegateStakeInfo object.
    """
    data = NodeDelegateStakeInfo(**data)

    return data

  @staticmethod
  def _get_null() -> "NodeDelegateStakeInfo":
    data = NodeDelegateStakeInfo(
      subnet_id=0,
      subnet_node_id=0,
      shares=0,
      balance=0
    )
    return data
