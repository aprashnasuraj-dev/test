import process from 'node:process'
import { isAddress, type Address, type Hex } from 'viem'

const RPC_URL = process.env.ANVIL_RPC_URL ?? 'http://127.0.0.1:8545'
let requestId = 0

async function rpc<T>(method: string, params: unknown[] = []): Promise<T> {
  const response = await fetch(RPC_URL, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: ++requestId, method, params }),
  })
  if (!response.ok) throw new Error(`RPC HTTP ${response.status}: ${response.statusText}`)
  const body = (await response.json()) as { result?: T; error?: { code: number; message: string } }
  if (body.error) throw new Error(`${method}: ${body.error.code} ${body.error.message}`)
  return body.result as T
}

function quantity(value: bigint): Hex {
  return `0x${value.toString(16)}` as Hex
}

export async function setBalance(address: Address, wei: bigint): Promise<void> {
  await rpc('anvil_setBalance', [address, quantity(wei)])
}

export async function setCode(address: Address, code: Hex): Promise<void> {
  await rpc('anvil_setCode', [address, code])
}

export async function setStorageAt(address: Address, slot: Hex, value: Hex): Promise<void> {
  await rpc('anvil_setStorageAt', [address, slot, value])
}

export async function impersonate(address: Address): Promise<void> {
  await rpc('anvil_impersonateAccount', [address])
}

export async function stopImpersonating(address: Address): Promise<void> {
  await rpc('anvil_stopImpersonatingAccount', [address])
}

async function main(): Promise<void> {
  if (process.argv.includes('--self-test')) {
    if (quantity(0n) !== '0x0' || quantity(255n) !== '0xff') throw new Error('Quantity encoder failed')
    console.log('State hydrator self-test passed')
    return
  }

  const chainId = await rpc<string>('eth_chainId')
  console.log(`Connected to ${RPC_URL}; chainId=${BigInt(chainId).toString()}`)

  const addressFlag = process.argv.indexOf('--address')
  const balanceFlag = process.argv.indexOf('--balance-wei')
  if (addressFlag !== -1 && balanceFlag !== -1) {
    const rawAddress = process.argv[addressFlag + 1]
    const rawBalance = process.argv[balanceFlag + 1]
    if (!rawAddress || !isAddress(rawAddress)) throw new Error('Invalid --address')
    if (!rawBalance) throw new Error('Missing --balance-wei value')
    await setBalance(rawAddress, BigInt(rawBalance))
    console.log(`Set balance for ${rawAddress} to ${rawBalance} wei`)
  }
}

await main()
