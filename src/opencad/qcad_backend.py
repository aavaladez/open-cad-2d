"""QCAD process adapter. Python holds disposable views, never authoritative geometry."""
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from .model import Point, Line, Circle, Layer
from .qcad_views import Arc,Polyline
from .commands import CommandBus,point

PIN = '4c830eb4d80285ca64b1f2c2dc0987f729344126'


class QcadDocument:
    def __init__(self, binary, source, qt):
        binary, source, qt = (Path(p).resolve() for p in (binary,source,qt))
        self.backend_paths = (binary,source,qt)
        if not binary.is_file():
            raise ValueError('Compilar el adaptador QCAD antes de abrir este modo')
        env = dict(os.environ)
        env['PATH'] = os.pathsep.join([str(source/'release'),str(source/'plugins'),str(qt/'bin'),env.get('PATH','')])
        env['QT_QPA_PLATFORM'] = 'offscreen'
        self.log = tempfile.TemporaryFile()
        self.reader = ThreadPoolExecutor(max_workers=1,thread_name_prefix='qcad-response')
        self.process = subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=self.log,env=env,text=True,encoding='utf-8',bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        self._depth = 0
        self._view = None
        self.id_map = {}
        try:
            identity = self.request('hello')
            if identity != dict(protocol=1,engine='qcad',revision=PIN):
                raise ValueError('Backend o protocolo QCAD no auditado')
        except Exception:
            self.close()
            raise

    def request(self, action, **arguments):
        if self.process.poll() is not None:
            raise RuntimeError('El proceso QCAD terminó; no se puede continuar editando')
        payload = json.dumps(dict(action=action,**arguments),allow_nan=False)
        if len(payload.encode('utf-8')) > 1_000_000:
            raise ValueError('Solicitud demasiado grande')
        try:
            self.process.stdin.write(payload+'\n'); self.process.stdin.flush()
            response = self.reader.submit(self.process.stdout.readline,4_000_001).result(timeout=15)
            if not response.endswith('\n') or len(response)>4_000_000:
                raise RuntimeError('Respuesta QCAD ausente o demasiado grande')
            data = json.loads(response)
        except Exception:
            self.close()
            raise
        if data.get('ok') is not True:
            raise ValueError(data.get('error','QCAD rechazó la operación'))
        self._view = data['document']
        return data.get('value')

    @property
    def entities(self):
        result = {}
        for item in self._view['entities']:
            i, layer = item['id'],item['layer']
            if item['type']=='LINE':
                result[i] = Line(i,Point(*item['start']),Point(*item['end']),layer)
            elif item['type']=='CIRCLE':
                result[i] = Circle(i,Point(*item['center']),item['radius'],layer)
            elif item['type']=='ARC':
                result[i] = Arc(i,Point(*item['center']),item['radius'],item['start_angle'],item['end_angle'],layer)
            elif item['type']=='LWPOLYLINE':
                result[i] = Polyline(i,tuple(Point(*p) for p in item['vertices']),item['closed'],layer)
            else:
                raise ValueError('Entidad no representable por la UI actual')
        return result

    @property
    def layers(self):
        return {v['name']:Layer(v['name'],v.get('display_color',v['color']),v['visible'],v['locked'])
                for v in self._view['layers']}

    @property
    def current_layer(self):
        return self._view['current_layer']

    @property
    def units(self):
        return self._view['units']

    @contextmanager
    def transaction(self):
        outer = self._depth==0
        if outer:
            self.request('begin'); self.id_map = {}
        self._depth += 1
        try:
            yield
            if outer:
                self.id_map = {int(k):v for k,v in self.request('commit').items()}
        except Exception:
            if outer and self.process.poll() is None:
                self.request('rollback')
            raise
        finally:
            self._depth -= 1

    @staticmethod
    def xyz(p):
        return [p.x,p.y,p.z]

    def add_line(self,a,b):
        return self.request('line',start=self.xyz(a),end=self.xyz(b))

    def add_circle(self,c,r):
        return self.request('circle',center=self.xyz(c),radius=r)

    def move(self,ids,delta):
        return self.request('move',ids=list(dict.fromkeys(ids)),delta=self.xyz(delta))

    def erase(self,ids):
        return self.request('erase',ids=list(dict.fromkeys(ids)))

    def layer(self,mode,name):
        return self.request('layer',mode=mode,name=name)

    def select(self,mode,a,b=None,tolerance=1):
        args=dict(mode=mode,a=self.xyz(a))
        if mode=='point': args['tolerance']=tolerance
        else: args['b']=self.xyz(b)
        return set(self.request('select',**args))

    def undo(self):
        return self.request('undo')

    def redo(self):
        return self.request('redo')

    def open_dxf(self,path):
        from .qcad_interop import open_document
        open_document(self,path)

    def save_dxf(self,path):
        from .qcad_interop import save_document
        save_document(self,path)

    def close(self):
        if getattr(self,'process',None) is not None:
            if self.process.poll() is None:
                self.process.stdin.close()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill(); self.process.wait(timeout=3)
            self.process.stdout.close()
        if getattr(self,'reader',None) is not None:
            self.reader.shutdown(wait=False,cancel_futures=True)
        if getattr(self,'log',None) is not None:
            self.log.close()


class QcadCommandBus(CommandBus):
    def __init__(self,document,aliases=None):
        super().__init__(document)
        for name,alias in [('COPY','CO'),('ROTATE','RO'),('SCALE','SC'),('ARC','A'),('PLINE','PL'),('TRIM','TR'),('EXTEND','EX'),('OFFSET','O')]:
            self.definitions[name]={'aliases':[alias],'variant':'native subset'}; self.aliases[alias]=name
        if aliases is not None: self.set_aliases(aliases)

    def edit_properties(self,ids,changes):
        with self.document.transaction():
            self.document.request('properties',ids=sorted(ids),changes=changes)

    def execute(self,name,*args):
        canonical = self.aliases.get(name.upper().removeprefix('_'),name.upper().removeprefix('_'))
        if canonical in ('TRIM','EXTEND'):
            if len(args) not in (3,4): raise ValueError(canonical+' límites-IDs objetivo-ID punto [tolerancia-pick]')
            targets=self.ids(args[1])
            if len(targets)!=1: raise ValueError('Un objetivo por operación TRIM/EXTEND')
            with self.document.transaction():
                result=self.document.request(canonical.lower(),boundaries=self.ids(args[0]),id=targets[0],
                    picked=self.document.xyz(point(args[2])),tolerance=float(args[3]) if len(args)==4 else 1e-6)
        elif canonical=='OFFSET':
            if len(args)!=3: raise ValueError('OFFSET ID distancia punto-del-lado')
            targets=self.ids(args[0])
            if len(targets)!=1: raise ValueError('Un objetivo por OFFSET')
            with self.document.transaction():
                result=self.document.request('offset',id=targets[0],distance=float(args[1]),side=self.document.xyz(point(args[2])))
        elif canonical=='ARC':
            if len(args)==3:
                arguments=dict(points=[self.document.xyz(point(p)) for p in args])
            elif len(args)==5 and str(args[0]).upper()=='CENTER':
                arguments=dict(center=self.document.xyz(point(args[1])),radius=float(args[2]),
                    start_angle=float(args[3]),end_angle=float(args[4]))
            else: raise ValueError('ARC punto-inicial punto-intermedio punto-final | ARC CENTER centro radio grados-inicio grados-fin')
            with self.document.transaction(): result=self.document.request('arc',**arguments)
        elif canonical=='PLINE':
            closed=bool(args and str(args[-1]).upper() in ('C','CLOSE'))
            points=args[:-1] if closed else args
            if len(points)<(3 if closed else 2): raise ValueError('PLINE punto punto [punto ...] [CLOSE]')
            with self.document.transaction():
                result=self.document.request('pline',vertices=[self.document.xyz(point(p)) for p in points],closed=closed)
        elif canonical in ('COPY','ROTATE','SCALE'):
            required=2 if canonical=='COPY' else 3
            if len(args)!=required: raise ValueError(canonical+' IDs y vector, o IDs punto-base valor')
            arguments=dict(ids=self.ids(args[0]))
            if canonical=='COPY': arguments['delta']=self.document.xyz(point(args[1]))
            else: arguments.update(base=self.document.xyz(point(args[1])),amount=float(args[2]))
            with self.document.transaction(): result=self.document.request(canonical.lower(),**arguments)
        elif canonical == 'LAYER':
            if len(args)!=2:
                raise ValueError('LAYER opción nombre')
            with self.document.transaction():
                result = self.document.layer(str(args[0]).upper(),str(args[1]))
        else:
            result = super().execute(name,*args)
        if self.document._depth==0 and canonical in ('LINE','CIRCLE','COPY','ARC','PLINE','TRIM','EXTEND','OFFSET'):
            def translate(value):
                if type(value) is int: return self.document.id_map.get(value,value)
                if isinstance(value,list): return [translate(v) for v in value]
                return value
            result = translate(result)
        return result
