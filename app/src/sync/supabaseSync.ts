import * as Y from 'yjs'
import { supabase } from '../db/supabase'

/**
 * Sync em segundo plano, append-only:
 *  - cada update local do Yjs é enfileirado e enviado em lote (debounce)
 *  - ao abrir/reconectar, baixa updates mais novos que o último visto
 *  - Realtime entrega updates de outros dispositivos ao vivo
 * Updates Yjs são idempotentes e comutativos: reenviar/reaplicar é seguro.
 */
export function startCloudSync(documentId: string, doc: Y.Doc) {
  if (!supabase) return () => {}
  const sb = supabase
  const REMOTE = Symbol('remote')
  const cursorKey = `cursor:${documentId}`
  let pending: Uint8Array[] = []
  let timer: ReturnType<typeof setTimeout> | undefined

  const flush = async () => {
    if (!pending.length || !navigator.onLine) return
    const merged = Y.mergeUpdates(pending)
    const { error } = await sb.from('doc_updates').insert({ document_id: documentId, update: toB64(merged) })
    if (!error) pending = [] // em erro mantém na fila e tenta depois
  }
  const onUpdate = (u: Uint8Array, origin: unknown) => {
    if (origin === REMOTE) return
    pending.push(u)
    clearTimeout(timer); timer = setTimeout(flush, 1500)
  }
  doc.on('update', onUpdate)

  const pull = async () => {
    const since = Number(localStorage.getItem(cursorKey) ?? 0)
    const { data } = await sb.from('doc_updates').select('id, update')
      .eq('document_id', documentId).gt('id', since).order('id')
    data?.forEach((row) => Y.applyUpdate(doc, fromB64(row.update), REMOTE))
    if (data?.length) localStorage.setItem(cursorKey, String(data.at(-1)!.id))
    // garante que o servidor tem tudo que só existe localmente (1ª sync)
    if (since === 0) { pending.push(Y.encodeStateAsUpdate(doc)); flush() }
  }
  pull()

  const channel = sb.channel(`doc:${documentId}`)
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'doc_updates', filter: `document_id=eq.${documentId}` },
      (p) => Y.applyUpdate(doc, fromB64((p.new as any).update), REMOTE))
    .subscribe()

  const online = () => { pull(); flush() }
  window.addEventListener('online', online)
  return () => { doc.off('update', onUpdate); clearTimeout(timer); flush(); sb.removeChannel(channel); window.removeEventListener('online', online) }
}

const toB64 = (u: Uint8Array) => btoa(String.fromCharCode(...u))
const fromB64 = (s: string) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0))
