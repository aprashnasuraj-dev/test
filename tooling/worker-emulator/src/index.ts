import type { Server } from 'node:http'
import express from 'express'
import { Miniflare } from 'miniflare'

type Finding = {
  id: 'worker-ssrf-loopback' | 'sendgrid-fail-open'
  reproduced: boolean
  detail: string
}

const SINK_HOST = '127.0.0.1'
const SINK_PORT = Number(process.env.SSRF_SINK_PORT ?? '8080')
const WORKER_HOST = '127.0.0.1'
const WORKER_PORT = Number(process.env.WORKER_EMULATOR_PORT ?? '8787')
const STRICT_SECURITY = process.env.SECURITY_STRICT === '1'
const SELF_TEST = process.argv.includes('--self-test')

function listen(app: express.Express, host: string, port: number): Promise<Server> {
  return new Promise((resolve, reject) => {
    const server = app.listen(port, host, () => resolve(server))
    server.once('error', reject)
  })
}

function close(server: Server | undefined): Promise<void> {
  if (!server) return Promise.resolve()
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()))
  })
}

async function main(): Promise<void> {
  const sinkApp = express()
  sinkApp.disable('x-powered-by')
  sinkApp.use(express.json({ limit: '64kb' }))
  sinkApp.use(express.urlencoded({ extended: true, limit: '64kb' }))

  let sinkHits = 0

  sinkApp.all('*', (req, res) => {
    sinkHits += 1
    console.warn('\n[SSRF-SINK EXFILTRATION DETECTED]')
    console.warn(`  Method:  ${req.method}`)
    console.warn(`  Path:    ${req.path}`)
    console.warn(`  Headers: ${JSON.stringify(req.headers)}`)
    console.warn(`  Query:   ${JSON.stringify(req.query)}`)
    res.status(200).json({ status: 'reached_internal_sink', path: req.path })
  })

  let sinkServer: Server | undefined
  let mf: Miniflare | undefined

  try {
    sinkServer = await listen(sinkApp, SINK_HOST, SINK_PORT)
    console.log(
      `[SSRF-SINK] Monitoring internal loopback on http://${SINK_HOST}:${SINK_PORT}`,
    )

    mf = new Miniflare({
      modules: true,
      host: WORKER_HOST,
      port: WORKER_PORT,
      cf: false,
      compatibilityDate: '2024-04-04',
      bindings: {
        SENDGRID_VERIFICATION_KEY:
          process.env.SENDGRID_VERIFICATION_KEY ?? '',
      },
      script: `
        export default {
          async fetch(request, env) {
            const url = new URL(request.url);

            if (url.pathname === '/og-image') {
              const avatarUrl = url.searchParams.get('avatarUrl');
              if (!avatarUrl) {
                return new Response('Missing avatarUrl parameter', { status: 400 });
              }

              try {
                const res = await fetch(avatarUrl);
                const text = await res.text();
                return new Response(
                  JSON.stringify({ status: 'fetched', bytes: text.length }),
                  { status: 200, headers: { 'Content-Type': 'application/json' } },
                );
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                return new Response(
                  JSON.stringify({ status: 'fetch_failed', error: message }),
                  { status: 500, headers: { 'Content-Type': 'application/json' } },
                );
              }
            }

            if (url.pathname === '/events/sendgrid') {
              const verificationKey = env.SENDGRID_VERIFICATION_KEY;
              const signature = request.headers.get(
                'X-Twilio-Email-Event-Webhook-Signature',
              );
              const timestamp = request.headers.get(
                'X-Twilio-Email-Event-Webhook-Timestamp',
              );

              if (!verificationKey || verificationKey.trim() === '') {
                console.warn(
                  '[WORKER ALERT] SENDGRID_VERIFICATION_KEY is unset; unauthenticated payload accepted.',
                );
                return new Response(
                  JSON.stringify({ status: 'accepted', fail_open: true }),
                  { status: 200, headers: { 'Content-Type': 'application/json' } },
                );
              }

              if (!signature || !timestamp) {
                return new Response(
                  JSON.stringify({ error: 'Missing signature headers' }),
                  { status: 401, headers: { 'Content-Type': 'application/json' } },
                );
              }

              return new Response(
                JSON.stringify({ status: 'verified', fail_open: false }),
                { status: 200, headers: { 'Content-Type': 'application/json' } },
              );
            }

            return new Response('Worker Emulator Running', { status: 200 });
          },
        };
      `,
    })

    await mf.ready
    const workerBaseUrl = `http://${WORKER_HOST}:${WORKER_PORT}`
    console.log(`[WORKER-EMULATOR] Miniflare sandbox active at ${workerBaseUrl}`)
    console.log('\n--- Executing Differential Vector Checks ---')

    console.log('\n[TEST 1] Testing SSRF reachability to internal loopback sink...')
    const internalTarget = `http://${SINK_HOST}:${SINK_PORT}/internal/metadata`
    const ssrfResponse = await fetch(
      `${workerBaseUrl}/og-image?avatarUrl=${encodeURIComponent(internalTarget)}`,
    )
    const ssrfBody = await ssrfResponse.text()
    const ssrfReproduced = ssrfResponse.status === 200 && sinkHits > 0
    console.log(
      `[TEST 1 RESULT] HTTP ${ssrfResponse.status}; sinkHits=${sinkHits}; body=${ssrfBody}`,
    )

    console.log('\n[TEST 2] Posting SendGrid webhook without signature headers...')
    const webhookResponse = await fetch(`${workerBaseUrl}/events/sendgrid`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([
        { event: 'delivered', email: 'audit-recipient@example.invalid' },
      ]),
    })
    const webhookText = await webhookResponse.text()
    let webhookBody: { fail_open?: boolean } = {}
    try {
      webhookBody = JSON.parse(webhookText) as { fail_open?: boolean }
    } catch {
      // The raw response is still emitted below for debugging.
    }
    const failOpenReproduced =
      webhookResponse.status === 200 && webhookBody.fail_open === true
    console.log(
      `[TEST 2 RESULT] HTTP ${webhookResponse.status}; body=${webhookText}`,
    )

    const findings: Finding[] = [
      {
        id: 'worker-ssrf-loopback',
        reproduced: ssrfReproduced,
        detail: ssrfReproduced
          ? 'Worker-controlled fetch reached the loopback sink.'
          : 'Loopback sink was not reached.',
      },
      {
        id: 'sendgrid-fail-open',
        reproduced: failOpenReproduced,
        detail: failOpenReproduced
          ? 'Webhook accepted an unsigned payload while the verification key was empty.'
          : 'Unsigned webhook payload was rejected.',
      },
    ]

    console.log('\n--- Security Harness Summary ---')
    for (const finding of findings) {
      console.log(
        `${finding.reproduced ? '[REPRODUCED]' : '[NOT REPRODUCED]'} ${finding.id}: ${finding.detail}`,
      )
    }

    if (SELF_TEST && findings.some((finding) => !finding.reproduced)) {
      throw new Error('Worker emulator self-test did not reproduce every built-in vector')
    }

    if (STRICT_SECURITY && findings.some((finding) => finding.reproduced)) {
      process.exitCode = 2
      console.error(
        '[STRICT SECURITY] One or more unsafe conditions were reproduced; failing the run.',
      )
    }
  } finally {
    await mf?.dispose()
    await close(sinkServer)
  }
}

main().catch((error) => {
  console.error('[WORKER-EMULATOR] Fatal error', error)
  process.exitCode = 1
})
