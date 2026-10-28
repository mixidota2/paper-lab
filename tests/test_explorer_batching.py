"""Offline gate tests; no browser behavior or runtime-speed claim."""
import ast,copy,json,subprocess
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
import review_103 as m
BASELINE='48e2c5a425f06bc753a41c8072085885757cf7d2'
FRAME={'bars':[{'label':'a','value':20},{'label':'b','value':None}], 'lines':[{'values':[0,5,10]},{'values':[20,10,0]}],'note':'initial'}
AXES={'start':3,'caption':'period'}
def dom():return {'bars':[{'strongs':['20'],'widths':['100%']},{'strongs':['推定不能'],'widths':[]}], 'tables':[{'head':[], 'rows':[{'heads':['a'],'cells':['20']},{'heads':['b'],'cells':['推定不能']}]},{'head':['t','x','y'],'rows':[{'heads':['3'],'cells':['0','20']},{'heads':['4'],'cells':['5','10']},{'heads':['5'],'cells':['10','0']}]}], 'lines':['48,204 268,160 488,116','48,28 268,116 488,204'], 'text':'period', 'expectedWidths':['100%',None]}
def checks(d):m.assert_explorer_bars(d,FRAME);m.assert_explorer_widths(d,FRAME);m.assert_explorer_lines(d,FRAME,AXES)

def test_expected_raw_values_pass():checks(dom())

@pytest.mark.parametrize('mutation',range(20))
def test_missing_extra_duplicate_stale_and_wrong_values_fail(mutation):
 d=dom()
 if mutation==0:d['bars'].pop()
 if mutation==1:d['bars'].append(copy.deepcopy(d['bars'][0]))
 if mutation==2:d['bars'][0]['strongs'].append('20')
 if mutation==3:d['bars'][0]['strongs']=['19']
 if mutation==4:d['bars'][1]['widths']=['0%']
 if mutation==5:d['tables'].append(copy.deepcopy(d['tables'][0]))
 if mutation==6:d['tables'][0]['rows'].pop()
 if mutation==7:d['tables'][0]['rows'][0]['heads']=['wrong']
 if mutation==8:d['tables'][0]['rows'][0]['cells']=['20','20']
 if mutation==9:d['bars'][0]['widths']=['99%']
 if mutation==10:d['bars'][0]['widths']=['100%','100%']
 if mutation==11:d['lines'].append(d['lines'][0])
 if mutation==12:d['lines'][0]='48,204 268,161 488,116'
 if mutation==13:d['lines'][0]='48,204 268,160'
 if mutation==14:d['tables'][1]['rows'][1]['cells']=['5']
 if mutation==15:d['tables'][1]['rows'][1]['cells']=['6','10']
 if mutation==16:d['tables'][1]['rows'][1]['heads']=[]
 if mutation==17:d['tables'][1]['rows'][1]['heads']=['4','4']
 if mutation==18:d['tables'][1]['head'].append('extra')
 if mutation==19:d['text']='wrong caption'
 with pytest.raises(AssertionError):checks(d)


@pytest.mark.parametrize('mode',['correct','stale-frame','stale-bars','stale-lines','local-as-global','global-as-local'])
def test_distinct_frames_and_scales_reject_stale_or_confused_dom(monkeypatch,mode):
 calls=[]
 second={'bars':[{'label':'c','value':10},{'label':'d','value':None}],
         'lines':[{'values':[2,4,6]},{'values':[12,8,4]}],'note':'second'}
 frames=[FRAME,second]
 def second_dom():
  return {'bars':[{'strongs':['10'],'widths':['50%']},{'strongs':['推定不能'],'widths':[]}],
          'tables':[{'head':[],'rows':[{'heads':['c'],'cells':['10']},{'heads':['d'],'cells':['推定不能']}]},
                    {'head':['t','x','y'],'rows':[{'heads':['3'],'cells':['2','12']},{'heads':['4'],'cells':['4','8']},{'heads':['5'],'cells':['6','4']}]}],
          'lines':['48,174.6666666667 268,145.3333333333 488,116','48,28 268,86.6666666667 488,145.3333333333'],
          'text':'period','expectedWidths':[]}
 class Control:
  def __init__(self,p,kind):self.p,self.kind=p,kind
  def text_content(self):return json.dumps({'frames':frames,'default':0} if self.kind=='[data-results]' else AXES)
  def evaluate(self,*args):pass
  def input_value(self):return str(self.p.index)
  def inner_text(self):return frames[self.p.index]['note']
  def get_attribute(self,key):assert key=='aria-pressed';return str(self.p.local).lower()
  def click(self):
   if self.kind=='reset':self.p.index=0;calls.append(('reset',))
   else:self.p.local=not self.p.local;calls.append(('scale',self.p.index,self.p.local))
 class Panel:
  index=0;local=False
  def locator(self,s):return Control(self,s)
  def get_by_role(self,role,name,exact):return Control(self,'reset' if name=='初期条件に戻す' else 'scale')
  def evaluate(self,script,widths):
   assert script==m.EXPLORER_DOM
   calls.append(('snapshot',self.index,self.local,tuple(widths)))
   raw=dom() if self.index==0 else second_dom()
   # Actual values come from a state fixture, never from expectedWidths.
   actual='100%' if self.index==0 or self.local else '50%'
   if self.index==1:
    if mode=='stale-frame':raw=dom()
    if mode=='stale-bars':
     raw['bars']=dom()['bars'];raw['tables'][0]=dom()['tables'][0]
    if mode=='stale-lines':
     raw['lines']=dom()['lines'];raw['tables'][1]=dom()['tables'][1]
    if mode=='local-as-global' and not self.local:actual='100%'
    if mode=='global-as-local' and self.local:actual='50%'
   raw['bars'][0]['widths']=[actual]
   # This mock only serializes expectations. It does not execute EXPLORER_DOM
   # or prove Chromium/CSSOM behavior; real protected CI remains required.
   raw['expectedWidths']=[None if v is None else f'{v:g}%' for v in widths]
   return raw
 p=Panel()
 class Panels:
  def all(self):return [p]
 class Page:
  def locator(self,s):assert s=='[data-interactive=explorer]';return Panels()
 def change(control,index):p.index=index;calls.append(('change',index))
 monkeypatch.setattr(m,'change',change)
 if mode!='correct':
  with pytest.raises(AssertionError):m.explorer_checks(Page())
  snapshots=[c for c in calls if c[0]=='snapshot' and c[1]==1]
  assert snapshots, 'Must reach the distinct second frame before rejection'
  if mode in ('stale-frame','stale-bars'):assert snapshots[-1]==('snapshot',1,False,())
  elif mode=='local-as-global':assert snapshots[-1]==('snapshot',1,False,(50.0,None))
  elif mode=='global-as-local':assert snapshots[-1]==('snapshot',1,True,(100.0,None))
  else:assert snapshots[-1]==('snapshot',1,False,()) and len(snapshots)==4
  assert ('reset',) not in calls
  return
 m.explorer_checks(Page())
 assert [c for c in calls if c[0]=='snapshot']==[
  ('snapshot',0,False,()),('snapshot',0,False,(100.0,None)),('snapshot',0,True,(100.0,None)),('snapshot',0,False,()),
  ('snapshot',1,False,()),('snapshot',1,False,(50.0,None)),('snapshot',1,True,(100.0,None)),('snapshot',1,False,())]
 assert calls[-1]==('reset',) and not p.local and p.index==0


@pytest.mark.parametrize('before,after', [(BASELINE,'3de77f7935af428a93028b17f5c14db7f8adcffb'),('01630c64451ac82f795bda53707f877ce16bd5fe','09c7b989582d93d76744f5821d25a6b20f7fa0ed')])
def test_only_explorer_block_changed(before,after):
 old=ast.parse(subprocess.check_output(['git','show',before+':tests/review_103.py'],cwd=ROOT,text=True));new=ast.parse(subprocess.check_output(['git','show',after+':tests/review_103.py'],cwd=ROOT,text=True))
 names={'explorer_checks','explorer_dom','assert_explorer_bars','assert_explorer_widths','assert_explorer_lines'}
 def strip(tree):return ast.dump(ast.Module(body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name in names) and not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXPLORER_DOM' for t in n.targets))],type_ignores=[]))
 assert strip(old)==strip(new)  # all guards, screenshots, case/semantic plans, time budgets unchanged

 # Both historical patches changed only explorer collection; integration must
 # retain their identical complete explorer block, including every assertion.
 def block(tree):return ast.dump(ast.Module(body=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name in names) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXPLORER_DOM' for t in n.targets))],type_ignores=[]))
 assert block(new)==block(ast.parse((ROOT/'tests/review_103.py').read_text()))
