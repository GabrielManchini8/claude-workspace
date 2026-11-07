# Bibliotecas de conexões (BIM / CAD)

Bibliotecas de fabricantes para tubos e conexões. Os arquivos ficam em subpastas aqui
(`tigre/`, `amanco/`, `pipestd/`) quando forem baixados.

**Situação (nov/2026):** a rede da sessão de nuvem bloqueia esses três sites, então nenhum
arquivo foi baixado automaticamente. Baixe pelo navegador e coloque na subpasta, ou libere
os domínios na rede do ambiente de nuvem (veja abaixo).

| Biblioteca | O que oferece | Formato | Login | Link |
|---|---|---|---|---|
| Tigre BIM | Plugins e catálogos para Revit e AutoCAD (hidrossanitário, elétrico, PPCI). Gratuito. | Plugin Windows (Revit/AutoCAD, não LT) | Não indicado | https://www.tigre.com.br/tigre-bim |
| Amanco Wavin BIM | Famílias Revit por linha: Água Fria (Soldável), Esgoto, PBA, CPVC FlowGuard, PEX, PPR, Gás, Elétrica, Caixas d'Água, Ramal Predial, Coletores, AquaCell, QuickStream, BIAX, K5, BlazeMaster | Revit (RFA) | Há área de login; confirmar por linha | https://bim.amanco.com.br/librerias-bim/ |
| pipestd | Bloco dinâmico de conexões PVC Classe 8.5 (curvas, tês, reduções, luvas, tampões). Não é de fabricante. | DWG (`PVC-Pipe-And-Fitting-Dynamic-Block.dwg`) | Não indicado | https://pipestd.com/pvc-pipe-fitting-class-8-5-dynamic-block/ |

Manual BIM da Amanco (link direto visto na página):
https://bim.amanco.com.br/wp-content/uploads/2023/11/Manual-BIM-Atualizacao-Set.2022.pdf.zip

## Como usar aqui

- **DWG/DXF** (pipestd, catálogos AutoCAD): DWG precisa ser convertido para DXF antes
  (ODA File Converter, gratuito, ou "Salvar como DXF" no AutoCAD). DXF abre no FreeCAD
  e em Python com `ezdxf` (já vem com o draftwright).
- **RFA** (Revit): formato fechado; só abre no Revit. Para usar aqui, exporte do Revit
  para IFC ou DWG.
- **IFC**: abre no FreeCAD (módulo BIM).

## Liberar o download na nuvem

Adicione `tigre.com.br`, `bim.amanco.com.br` e `pipestd.com` em *Allowed domains* do
ambiente de nuvem (Project settings → Cloud environment → Add cloud environment).
Guia: https://code.claude.com/docs/en/cloud-environments#network-access
Respeite os termos de uso de cada fabricante.
