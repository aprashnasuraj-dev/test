import process from 'node:process'
import 'dotenv/config'
import { ens_normalize } from '@adraffy/ens-normalize'

type Result = {
  input: string
  normalized?: string
  idempotent?: boolean
  error?: string
}

const DEFAULT_CASES = [
  'RaFFY🚴‍♂️.eTh',
  'example.eth',
  'EXAMPLE.ETH',
  'e\u0301xample.eth',
  'éxample.eth',
  'раypal.eth',
  'paypaI.eth',
  'abc\u200d.eth',
  'abc\u200b.eth',
  'אabc.eth',
  'abcא.eth',
  '👨‍👩‍👧‍👦.eth',
  '🏴\u200d☠️.eth',
  `${'a'.repeat(63)}.eth`,
  `${'a'.repeat(64)}.eth`,
]

export function checkName(input: string): Result {
  try {
    const normalized = ens_normalize(input)
    const normalizedTwice = ens_normalize(normalized)
    return {
      input,
      normalized,
      idempotent: normalizedTwice === normalized,
    }
  } catch (error) {
    return {
      input,
      error: error instanceof Error ? error.message : String(error),
    }
  }
}

export function runCorpus(inputs: string[]): Result[] {
  return inputs.map(checkName)
}

const results = runCorpus(DEFAULT_CASES)
const broken = results.filter((result) => result.idempotent === false)

if (process.argv.includes('--self-test')) {
  if (broken.length > 0) {
    throw new Error(`ENS normalization idempotence failed for ${broken.length} case(s)`)
  }
  const valid = results.filter((result) => result.normalized !== undefined).length
  const rejected = results.filter((result) => result.error !== undefined).length
  console.log(`ENS normalizer self-test passed (${valid} accepted, ${rejected} rejected)`)
} else {
  console.log(JSON.stringify(results, null, 2))
}
