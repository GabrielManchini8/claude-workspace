import { Tldraw, Editor, DefaultToolbar, DefaultToolbarContent, TldrawUiMenuItem, useEditor, useTools } from 'tldraw'
import 'tldraw/tldraw.css'
import { useYjsStore } from '../sync/useYjsStore'
import { importPdfToCanvas } from '../pdf/importPdf'
import { MindNodeUtil, createMindMap, getShapeVisibility } from '../mindmap/MindNodeShape'
import { MindNodeToolbar, registerMindMapKeys } from '../mindmap/MindMapUI'

const shapeUtils = [MindNodeUtil]

/**
 * Caneta: o tldraw já usa PointerEvents com `pressure`, então Apple Pencil,
 * S-Pen e canetas Wacom/Surface têm traço sensível à pressão nativamente.
 * `isPenMode` faz o dedo navegar (pan/zoom) e só a caneta desenhar
 * ("palm rejection") — ativado automaticamente na 1ª vez que uma caneta toca.
 */
function enablePenFriendlyDefaults(editor: Editor) {
  editor.updateInstanceState({ isGridMode: false })
  const onPointer = (e: PointerEvent) => {
    if (e.pointerType === 'pen' && !editor.getInstanceState().isPenMode) {
      editor.updateInstanceState({ isPenMode: true })
      editor.setCurrentTool('draw')
    }
  }
  window.addEventListener('pointerdown', onPointer, { capture: true })
  return () => window.removeEventListener('pointerdown', onPointer, { capture: true })
}

function pickFile(accept: string): Promise<File | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = accept
    input.onchange = () => resolve(input.files?.[0] ?? null)
    input.click()
  })
}

function Toolbar() {
  const editor = useEditor()
  const tools = useTools()
  return (
    <DefaultToolbar>
      <DefaultToolbarContent />
      <TldrawUiMenuItem id="mindmap" label="Mapa mental" icon="mind-map" onSelect={() => { createMindMap(editor) }} />
      <TldrawUiMenuItem
        id="import-pdf"
        label="Importar PDF"
        icon="file"
        onSelect={async () => {
          const file = await pickFile('application/pdf')
          if (file) await importPdfToCanvas(editor, file)
        }}
      />
      {/* Imagens (png/jpg/svg) já são suportadas por arrastar/colar ou pela ferramenta de mídia */}
      <TldrawUiMenuItem {...tools['asset']} />
    </DefaultToolbar>
  )
}

export function Board({ documentId }: { documentId: string }) {
  const store = useYjsStore(documentId, shapeUtils)
  return (
    <Tldraw
      store={store}
      shapeUtils={shapeUtils}
      getShapeVisibility={getShapeVisibility}
      components={{ Toolbar, InFrontOfTheCanvas: MindNodeToolbar }}
      onMount={(editor) => {
        if (import.meta.env.DEV) (window as any).editor = editor
        const a = enablePenFriendlyDefaults(editor)
        const b = registerMindMapKeys(editor)
        return () => { a(); b() }
      }}
    />
  )
}
