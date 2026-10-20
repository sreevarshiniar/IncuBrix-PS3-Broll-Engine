"""Run a JSONL file of API test cases and store response evidence. Each line: {"name":..., "payload":...}."""
import argparse, json, time
from pathlib import Path
import requests

def main():
    p=argparse.ArgumentParser(); p.add_argument('input',type=Path); p.add_argument('--base-url',default='http://localhost:8000'); p.add_argument('--out',type=Path,default=Path('test-pack/batch-results.json')); args=p.parse_args()
    results=[]
    for line in args.input.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        case=json.loads(line); started=time.time()
        try:
            r=requests.post(args.base_url.rstrip('/')+'/api/v1/broll/jobs',json=case['payload'],headers={'Idempotency-Key':f"batch-{case.get('name','case')}-{len(results)}"},timeout=30)
            body=r.json(); item={'name':case.get('name'),'http_status':r.status_code,'response':body,'elapsed_seconds':round(time.time()-started,3)}
            if r.status_code==202 and body.get('job_id'):
                for _ in range(600):
                    status=requests.get(args.base_url.rstrip('/')+f"/api/v1/jobs/{body['job_id']}",timeout=20).json()
                    if status.get('status') in ('succeeded','failed'): break
                    time.sleep(1)
                item['final_status']=status
            results.append(item)
        except Exception as e: results.append({'name':case.get('name'),'error':str(e),'elapsed_seconds':round(time.time()-started,3)})
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(results,indent=2),encoding='utf-8'); print(f'Wrote {len(results)} cases to {args.out}')
if __name__=='__main__': main()
