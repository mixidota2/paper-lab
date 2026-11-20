"""EpiSEM output assertions. Uses only a page from the protected shared runner."""
from html.parser import HTMLParser
import json

NAMES = {'limit_ok':'金額は上限以内か','account_ok':'口座は承認済みか','scope_ok':'範囲は許可されているか',
         'recipient_ok':'受取人は承認済みか','retention_ok':'保管条件を満たすか','label':'許可判断に関わらない表示ラベル'}
OPS = {'read':'通常の方法で読み取る（read）','read_again':'同じ方法でもう一度読み取る（read）','audit':'別の手段で隠れた事実をすべて照会する（audit）',
       'commit':'実行を確定して処理を終える（commit）','stop':'実行せずに処理を終える','audit_not_executed':'処理が終わったため、予定した照会は行わない'}
KEYS = ['task','mask','irrelevant','policy','setting','timing']
INITIAL = [0,1,False,'visible','RE','before']


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def text(self):
        return ''.join(c if isinstance(c,str) else c.text() for c in self.children)
    def find(self, attr):
        result = [self] if attr in self.attrs else []
        for child in self.children:
            if isinstance(child,Node):result.extend(child.find(attr))
        return result
    def tags(self, tag):
        result = [self] if self.tag == tag else []
        for child in self.children:
            if isinstance(child,Node):result.extend(child.tags(tag))
        return result


class Frame(HTMLParser):
    def __init__(self, html):
        super().__init__();self.root=Node();self.stack=[self.root];self.feed(html)
    def handle_starttag(self,tag,attrs):
        node=Node(tag,attrs);self.stack[-1].children.append(node)
        if tag not in ('br','hr','img','input','meta','link'):self.stack.append(node)
    def handle_endtag(self,tag):
        assert self.stack[-1].tag==tag
        self.stack.pop()
    def handle_data(self,text):self.stack[-1].children.append(text)


def assert_episem_frame(html, case, metrics, step):
    root=Frame(html).root;result=case['result'];args=case['args']
    total=max(len(result[k]['trace']) for k in ('unsafe','safe'));step=min(step,total)
    assert [n.attrs['data-ep-stage'] for n in root.find('data-ep-stage')]==[str(step)]
    worlds=root.find('data-ep-world');assert [n.attrs['data-ep-world'] for n in worlds]==['unsafe','safe']
    for node,key in zip(worlds,('unsafe','safe'),strict=True):
        r=result[key];trace=r['trace'][:step]
        visible=next((e['visible'] for e in reversed(trace) if 'visible' in e),{})
        facts=[NAMES[k]+'：'+('隠れている' if k not in visible else ('はい' if v else 'いいえ') if isinstance(v,bool) else 'sample') for k,v in r['world'].items()]
        assert [n.text() for n in node.find('data-ep-visible')[0].tags('li')]==facts
        assert [n.text() for n in node.tags('ol')[0].tags('li')]==[OPS[e['op']]+(f"（{len(e['returned'])}個）" if e['op']=='audit' else '') for e in trace]
        final=node.find('data-ep-result')
        assert len(final)==int(step>=len(r['trace']))
        if final:
            assert final[0].text()==' ／ '.join(label+('あり' if r[k] else 'なし') for label,k in [('実行の確定：','commit'),('禁止された実行：','unsafe'),('許可された依頼の完了：','success'),('照会による回収：','recovered')])
    paired=root.find('data-ep-paired');assert len(paired)==int(step>=total)
    if paired:assert ('1点（両方で成功）' if result['paired'] else '0点（少なくとも片方で未達）') in paired[0].text()
    rows=root.find('data-ep-policy');assert len(rows)==len(metrics)==5
    for row in rows:
        expected=metrics[row.attrs['data-ep-policy']][args[5]]['aggregate']
        cells=row.find('data-metric');assert len(cells)==6
        for cell in cells:assert cell.text()==f"{100*expected[cell.attrs['data-metric']]:.2f}%"


def assert_initial(page, data):
    assert [page.locator('#ep-'+k).input_value() for k in KEYS]==['0','1','0','visible','RE','before']
    case=next(c for c in data['cases'] if c['args']==INITIAL)
    assert_episem_frame(page.locator('#ep-output').inner_html(),case,data['metrics'],0)


def inspect_episem(page, source):
    data=json.loads(source.read_text())['synthetic']
    assert '2610.31650' in page.locator('body').inner_text()
    assert_initial(page,data)
    # Native button Enter: observe trusted events and resulting state. This does
    # not claim native select keyboard, IME, or screen-reader coverage.
    button=page.locator('#ep-next');button.focus()
    assert button.evaluate('(e)=>document.activeElement===e')
    button.evaluate("(e)=>{e.__epKeys=[];for(const type of ['keydown','keypress','keyup'])e.addEventListener(type,x=>e.__epKeys.push([x.type,x.key,x.isTrusted]));}")
    button.press('Enter')
    assert button.evaluate('(e)=>e.__epKeys')==[[k,'Enter',True] for k in ['keydown','keypress','keyup']]
    initial=next(c for c in data['cases'] if c['args']==INITIAL)
    assert_episem_frame(page.locator('#ep-output').inner_html(),initial,data['metrics'],1)
    scenarios=[INITIAL,[0,1,False,'refuse','RE','before'],[0,1,False,'execute','RE','before'],
               [0,1,True,'recover','RE','before'],[0,1,True,'recover','SE','before'],
               [0,1,True,'recover','RE','after'],[0,0,True,'recover','RE','before'],
               [1,2,False,'single_audit','RE','before'],[1,7,True,'single_audit','RE','before']]
    for args in scenarios:
        for k,v in zip(KEYS,args,strict=True):page.locator('#ep-'+k).select_option(str(int(v)) if isinstance(v,bool) else str(v))
        case=next(c for c in data['cases'] if c['args']==args)
        assert_episem_frame(page.locator('#ep-output').inner_html(),case,data['metrics'],0)
        for step in (1,2):
            page.locator('#ep-next').click()
            assert_episem_frame(page.locator('#ep-output').inner_html(),case,data['metrics'],step)
        page.locator('#ep-end').click()
        assert_episem_frame(page.locator('#ep-output').inner_html(),case,data['metrics'],99)
        assert page.locator('#ep-next').is_disabled() and page.locator('#ep-end').is_disabled()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    reset=page.locator('#ep-reset');reset.focus()
    assert reset.evaluate('(e)=>document.activeElement===e')
    reset.press('Enter');assert_initial(page,data)
    assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
