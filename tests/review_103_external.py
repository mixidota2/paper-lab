"""Non-browser HTTP reachability worker. Parent enforces a wall-clock budget by killing it."""
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request,urlopen


def check_url(url):
    """HEAD, with a small GET only for method-dependent 404/405/501 failures.

    Both attempts share the existing eight-second URL budget. The parent still
    enforces the total wall-clock budget, including stalled DNS or response reads.
    A successful request proves HTTP reachability only, never source correctness.
    """
    deadline = time.monotonic() + 8
    item = {'url': url, 'method': 'HEAD'}
    headers = {'User-Agent': 'paper-lab-link-review/1.0'}
    try:
        try:
            with urlopen(Request(url, method='HEAD', headers=headers), timeout=8) as r:
                item.update(head_status=r.status, status=r.status, final_url=r.url,
                            result='CONFIRMED HTTP reachability only')
                return item
        except HTTPError as e:
            item['head_status'] = e.code
            e.close()
            if e.code not in (404, 405, 501):
                raise
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('URL time budget exhausted before GET fallback')
        item.update(method='GET', fallback_method='GET')
        with urlopen(Request(url, method='GET', headers=headers), timeout=remaining) as r:
            # Do not download entire articles. Exiting the context closes the stream.
            r.read(1024)
            if time.monotonic() >= deadline:
                raise TimeoutError('URL time budget exhausted during GET fallback')
            item.update(status=r.status, final_url=r.url,
                        result='CONFIRMED HTTP reachability only')
    except Exception as e:
        if isinstance(e, HTTPError):
            item['status'] = e.code
            e.close()
        item.update(result='NOT CONFIRMED', error=str(e))
    return item


def worker(input_path,output_path):
    with Path(output_path).open('w') as output:
        for url in json.loads(Path(input_path).read_text()):
            output.write(json.dumps(check_url(url))+'\n');output.flush()


def bounded_check(urls,out,budget_seconds=45,command=None):
    """Worker owns no Chrome resources or descendants; even stalled DNS is terminated."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    urls=sorted(set(urls));inp=out/'urls.json';results=out/'completed.jsonl'
    inp.write_text(json.dumps(urls));start=time.monotonic();timed_out=False
    if budget_seconds<=0:
        summary={'budget_seconds':0,'elapsed_seconds':time.monotonic()-start,'timed_out':True,'worker_exit':None,'requested':len(urls),'completed':0,'worker_started':False}
        (out/'summary.json').write_text(json.dumps(summary,indent=2))
        return [{'url':u,'result':'NOT CONFIRMED','reason':'no external time budget remaining'} for u in urls],summary
    args=command if command is not None else [sys.executable,str(Path(__file__).resolve()),str(inp),str(results)]
    with (out/'worker.log').open('w') as log:
        proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
        try:
            proc.wait(timeout=max(0,budget_seconds-(time.monotonic()-start)))
        except subprocess.TimeoutExpired:
            timed_out=True;proc.kill();proc.wait(timeout=2)
        except BaseException:
            proc.kill();proc.wait(timeout=2);raise
    completed={}
    if results.exists():
        for line in results.read_text().splitlines():
            try:item=json.loads(line)
            except json.JSONDecodeError:continue  # Killed mid-record: leave this URL unconfirmed.
            if item.get('url') in urls:completed[item['url']]=item
    rows=[completed.get(u,{'url':u,'result':'NOT CONFIRMED','reason':'total time budget exhausted' if timed_out else 'worker did not complete URL'}) for u in urls]
    summary={'budget_seconds':budget_seconds,'elapsed_seconds':time.monotonic()-start,'timed_out':timed_out,'worker_exit':proc.returncode,'requested':len(urls),'completed':len(completed)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    return rows,summary

if __name__=='__main__':worker(*sys.argv[1:])
