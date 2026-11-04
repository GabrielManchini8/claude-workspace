import Dexie, { Table } from 'dexie'

/**
 * Dexie guarda METADADOS e índices (lista de docs, busca, backlinks).
 * O conteúdo em si vive no Y.Doc (y-indexeddb). Separar evita carregar
 * todos os canvases na RAM só para listar a sidebar.
 */
export interface DocMeta { documentId: string; title: string; kind: 'note' | 'board'; updatedAt: number; tags: string[] }
export interface Link { from: string; to: string } // [[wikilinks]] -> backlinks estilo Obsidian

class LocalDB extends Dexie {
  docs!: Table<DocMeta, string>
  links!: Table<Link, [string, string]>
  constructor() {
    super('mindvault')
    this.version(1).stores({ docs: 'documentId, updatedAt, *tags', links: '[from+to], to' })
  }
}
export const db = new LocalDB()
