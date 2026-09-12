import process from 'node:process'
import { bytesToHex, hexToBytes, type Address, type Hex } from 'viem'

export type UserOperationLike = {
  sender: Address
  nonce: bigint
  callData: Hex
  callGasLimit: bigint
  verificationGasLimit: bigint
  preVerificationGas: bigint
  maxFeePerGas: bigint
  maxPriorityFeePerGas: bigint
  signature: Hex
  factory?: Address
  factoryData?: Hex
  paymaster?: Address
  paymasterVerificationGasLimit?: bigint
  paymasterPostOpGasLimit?: bigint
  paymasterData?: Hex
}

export type Mutation = {
  id: string
  rationale: string
  userOperation: UserOperationLike
}

const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000' as Address

function flipFirstByte(hex: Hex): Hex {
  const bytes = hexToBytes(hex)
  if (bytes.length === 0) return '0x01'
  bytes[0] ^= 0x01
  return bytesToHex(bytes)
}

export function mutateUserOperation(base: UserOperationLike): Mutation[] {
  const mutations: Mutation[] = []
  const add = (id: string, rationale: string, patch: Partial<UserOperationLike>) => {
    mutations.push({ id, rationale, userOperation: { ...base, ...patch } })
  }

  add('nonce-replay', 'Exercise replay protection with a previous nonce.', {
    nonce: base.nonce > 0n ? base.nonce - 1n : 0n,
  })
  add('nonce-future', 'Exercise nonce-gap handling with an unexpectedly large nonce.', {
    nonce: base.nonce + 1_000_000n,
  })
  add('empty-signature', 'Reject an unsigned UserOperation before execution.', { signature: '0x' })
  add('malformed-signature', 'Reject a one-byte signature rather than accepting malformed ERC-1271/ECDSA data.', {
    signature: '0x00',
  })
  add('signature-bitflip', 'Test signature-domain and signer validation against a minimally changed signature.', {
    signature: flipFirstByte(base.signature),
  })
  add('empty-calldata', 'Exercise authorization and execution behavior for empty account calldata.', { callData: '0x' })
  add('calldata-selector-bitflip', 'Probe dispatch/authorization boundaries by mutating the first calldata byte.', {
    callData: flipFirstByte(base.callData),
  })
  add('zero-call-gas', 'Exercise accounting and validation with no execution gas allowance.', { callGasLimit: 0n })
  add('zero-verification-gas', 'Exercise validation-gas accounting boundaries.', { verificationGasLimit: 0n })
  add('zero-preverification-gas', 'Exercise preVerificationGas assumptions.', { preVerificationGas: 0n })
  add('priority-fee-over-max-fee', 'Exercise fee-field consistency validation.', {
    maxPriorityFeePerGas: base.maxFeePerGas + 1n,
  })
  add('zero-factory', 'Exercise counterfactual-account handling with an invalid factory.', {
    factory: ZERO_ADDRESS,
    factoryData: '0x',
  })
  add('zero-paymaster', 'Exercise paymaster validation and zero-address handling.', {
    paymaster: ZERO_ADDRESS,
    paymasterVerificationGasLimit: 0n,
    paymasterPostOpGasLimit: 0n,
    paymasterData: '0x',
  })

  return mutations
}

function sample(): UserOperationLike {
  return {
    sender: '0x1111111111111111111111111111111111111111',
    nonce: 1n,
    callData: '0x12345678',
    callGasLimit: 250_000n,
    verificationGasLimit: 300_000n,
    preVerificationGas: 60_000n,
    maxFeePerGas: 20_000_000_000n,
    maxPriorityFeePerGas: 2_000_000_000n,
    signature: `0x${'11'.repeat(65)}` as Hex,
  }
}

function toJson(value: unknown): string {
  return JSON.stringify(value, (_key, item) => (typeof item === 'bigint' ? item.toString() : item), 2)
}

const corpus = mutateUserOperation(sample())
if (process.argv.includes('--self-test')) {
  const ids = new Set(corpus.map((entry) => entry.id))
  if (corpus.length < 10 || ids.size !== corpus.length) {
    throw new Error('Mutation corpus self-test failed')
  }
  console.log(`UserOperation mutator self-test passed (${corpus.length} mutations)`)
} else {
  console.log(toJson(corpus))
}
