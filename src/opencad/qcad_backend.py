"""QCAD process adapter. Python holds disposable views, never authoritative geometry."""
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from .model import Point, Line, Circle, Layer
from .commands import CommandBus

PIN = '4c830eb4d80285ca64b1f2c2dc0987f729344126'


class QcadDocument:
    def __init__(self, binary, source, qt):
        binary, source, qt = (Path(p).resolve() for p in (binary,source,qt))
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

    def undo(self):
        return self.request('undo')

    def redo(self):
        return self.request('redo')

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
    def execute(self,name,*args):
        canonical = self.aliases.get(name.upper().removeprefix('_'),name.upper().removeprefix('_'))
        if canonical == 'LAYER':
            if len(args)!=2:
                raise ValueError('LAYER opción nombre')
            with self.document.transaction():
                result = self.document.layer(str(args[0]).upper(),str(args[1]))
        else:
            result = super().execute(name,*args)
        if self.document._depth==0 and canonical in ('LINE','CIRCLE'):
            def translate(value):
                if type(value) is int: return self.document.id_map.get(value,value)
                if isinstance(value,list): return [translate(v) for v in value]
                return value
            result = translate(result)
        return result
