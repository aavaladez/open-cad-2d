"""Validated private recovery copies from acknowledged QCAD snapshots only."""
import hashlib,json,os,tempfile,uuid
from copy import deepcopy
from pathlib import Path
from .qcad_interop import write_snapshot,inspect_dxf,native_inventory,equivalent
from .qcad_backend import PIN


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RecoveryStore:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=True)
        self.session=uuid.uuid4().hex
        self._generations=[]

    def checkpoint(self,document):
        if document._confirmed_view is None: raise ValueError('No hay documento QCAD confirmado para respaldar')
        view=deepcopy(document._confirmed_view)
        if view.get('transaction_active') is not False: raise ValueError('No respaldar cambios sin confirmar')
        folder=self.root/self.session; folder.mkdir(exist_ok=True)
        generation=uuid.uuid4().hex
        drawing=folder/(generation+'.dxf'); metadata=folder/(generation+'.json')
        # New immutable generation, metadata published only after validation.
        with tempfile.TemporaryDirectory(prefix='.writing-',dir=folder) as work:
            temporary=Path(work)/'confirmed.dxf'; write_snapshot(view,temporary)
            os.replace(temporary,drawing)
        record=dict(format=1,engine='qcad',qcad_revision=PIN,dxf=drawing.name,sha256=digest(drawing),
            source=document.file_path,entities=len(view['entities']),history_preserved=False,lisp_state_preserved=False)
        try:
            with tempfile.TemporaryDirectory(prefix='.manifest-',dir=folder) as work:
                pending=Path(work)/'record.json'
                with pending.open('x',encoding='utf-8') as handle:
                    json.dump(record,handle,ensure_ascii=False,indent=2); handle.flush(); os.fsync(handle.fileno())
                os.replace(pending,metadata)
        except OSError:
            drawing.unlink(missing_ok=True)
            raise
        self._generations.append((metadata,drawing))
        # Retain two acknowledged generations from this store instance only.
        # Never enumerate/delete unknown files, prior sessions or user drawings.
        while len(self._generations)>2:
            old_metadata,old_drawing=self._generations[0]
            if old_metadata.resolve().parent!=folder or old_drawing.resolve().parent!=folder:
                raise ValueError('Ruta de retención fuera de la sesión propia')
            old_metadata.unlink(missing_ok=True); old_drawing.unlink(missing_ok=True)
            self._generations.pop(0)
        return metadata

    def read(self,metadata):
        metadata=Path(metadata).resolve()
        if self.root not in metadata.parents or metadata.suffix!='.json' or not metadata.is_file() or metadata.stat().st_size>65536:
            raise ValueError('Respaldo local propio de hasta64KB requerido')
        value=json.loads(metadata.read_text(encoding='utf-8'))
        if not isinstance(value,dict) or value.get('format')!=1 or value.get('engine')!='qcad' or value.get('qcad_revision')!=PIN:
            raise ValueError('Formato/pin de respaldo incompatible')
        name=value.get('dxf')
        if not isinstance(name,str) or len(name)!=36 or not name.endswith('.dxf') or any(c not in '0123456789abcdef' for c in name[:-4]):
            raise ValueError('Nombre de generación de respaldo inválido')
        drawing=(metadata.parent/name).resolve()
        if drawing.parent!=metadata.parent or not drawing.is_file() or drawing.stat().st_size>20_000_000 or digest(drawing)!=value.get('sha256'):
            raise ValueError('Respaldo ausente/modificado; restauración cancelada')
        inventory=inspect_dxf(drawing)
        if len(inventory['entities'])!=value.get('entities'): raise ValueError('Inventario de respaldo incompatible')
        return drawing,value,inventory

    def restore(self,document,metadata):
        drawing,record,expected=self.read(metadata)
        # open_dxf promotes a candidate only after native/independent validation;
        # it can replace either a live process or this document's failed process.
        document.open_dxf(drawing); equivalent(expected,native_inventory(document._view))
        # Source is informational only: never open, write, or execute it implicitly.
        document.file_path=None
        return record


def default_root():
    explicit=os.environ.get('OPENCAD_RECOVERY_DIR')
    if explicit:return Path(explicit)
    if os.name=='nt':return Path(os.environ['LOCALAPPDATA'])/'OPEN-CAD-2D'/'recovery'
    return Path(os.environ.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))/'open-cad-2d'/'recovery'
