import { Tldraw, Editor, DefaultToolbar, DefaultToolbarContent, TldrawUiMenuItem, useEditor, useTools } from 'tldraw'
import 'tldraw/tldraw.css'
import { useYjsStore } from '../sync/useYjsStore'
import { ZoomControls, cameraOptions } from './zoom'
import { pickFiles, registerFileImporters } from '../import/importFiles'
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

function Toolbar() {
  const editor = useEditor()
  const tools = useTools()
  return (
    <DefaultToolbar>
      <DefaultToolbarContent />
      <TldrawUiMenuItem id="mindmap" label="Mapa mental" icon="mind-map" onSelect={() => { createMindMap(editor) }} />
      <TldrawUiMenuItem id="import" label="Importar arquivo (PDF, imagem, vídeo, texto, Word…)" icon="file"
        onSelect={async () => {
          const files = await pickFiles()
          if (files.length) await editor.putExternalContent({ type: 'files', files, point: editor.getViewportPageBounds().center })
        }} />
      {/* Imagens (png/jpg/svg) já são suportadas por arrastar/colar ou pela ferramenta de mídia */}
      <TldrawUiMenuItem {...tools['asset']} />
    </DefaultToolbar>
  )
}

function Overlays() {
  return <><MindNodeToolbar /><ZoomControls /></>
}

export function Board({ documentId }: { documentId: string }) {
  const store = useYjsStore(documentId, shapeUtils)
  return (
    <Tldraw
      store={store}
      shapeUtils={shapeUtils}
      getShapeVisibility={getShapeVisibility}
      cameraOptions={cameraOptions}
      components={{ Toolbar, InFrontOfTheCanvas: Overlays, ZoomMenu: null }}
      onMount={(editor) => {
        if (import.meta.env.DEV) (window as any).editor = editor
        const a = enablePenFriendlyDefaults(editor)
        const b = registerMindMapKeys(editor)
        registerFileImporters(editor)
        return () => { a(); b() }
      }}
    />
  )
}
