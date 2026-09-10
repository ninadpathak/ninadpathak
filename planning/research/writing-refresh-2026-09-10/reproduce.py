from pathlib import Path
import tempfile,subprocess,shutil,zipfile,json,platform
root=Path.cwd(); evidence=root/'planning/research/writing-refresh-2026-09-10'; fixture=root/'static/examples/writing-lab'
def run(args,cwd,name,expected=0):
 r=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
 text='$ '+' '.join(args)+'\n'+r.stdout+r.stderr+'\nexit='+str(r.returncode)+'\n'
 (evidence/name).write_text(text)
 assert r.returncode==expected,(name,r.returncode,text[-1500:])
 return text
with tempfile.TemporaryDirectory(prefix='writing-lab-before-') as td:
 p=Path(td)
 for name in ['webhook.mjs','check.mjs']:shutil.copy(fixture/name,p/name)
 shutil.copy(evidence/'before-service.mjs',p/'service.mjs')
 run(['node','check.mjs'],p,'aborted-upload-before.log',1)
with tempfile.TemporaryDirectory(prefix='writing-import-') as td:
 run(['node','--input-type=module','-e','import { verifyWebhook } from "@example/webhooks"'],td,'missing-import.log',1)
with tempfile.TemporaryDirectory(prefix='writing-lab-clean-') as td:
 p=Path(td)/'writing-lab';shutil.copytree(fixture,p)
 text=run(['node','check.mjs'],p,'clean-check.log')
 validation='Local fixture validation: 2026-09-10\nRuntime: '+subprocess.check_output(['node','--version'],text=True).strip()+'\nPlatform: '+platform.system()+' '+platform.machine()+'\nThird-party dependencies: none\nEnvironment: fresh temporary directory, loopback servers only\n\n'+text+'\nScope: synthetic fixture behavior; no human usability study or production claim.\n'
 (fixture/'validation.txt').write_text(validation)
 proc=subprocess.Popen(['node','service.mjs'],cwd=p,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  url=proc.stdout.readline().strip(); assert url.startswith('http://127.0.0.1:')
  checks=[]
  for name,args,code,status in [
   ('health',['--fail-with-body',url+'/health'],0,'{"status":"ok"}'),
   ('first',['-i',url+'/exports','-H','Content-Type: application/json','-H','Idempotency-Key: report-a','--data','{"format":"csv"}'],0,'202 Accepted'),
   ('drop',['-i',url+'/exports','-H','Content-Type: application/json','-H','Idempotency-Key: report-loss','-H','X-Fixture-Drop-Response: yes','--data','{"format":"csv"}'],52,'Empty reply from server'),
   ('retry',['-i',url+'/exports','-H','Content-Type: application/json','-H','Idempotency-Key: report-loss','--data','{"format":"csv"}'],0,'200 OK')]:
   r=subprocess.run(['curl','--max-time','5',*args],capture_output=True,text=True)
   assert r.returncode==code and status in r.stdout+r.stderr,(name,r)
   checks.append({'name':name,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
  (evidence/'manual-curl.json').write_text(json.dumps(checks,indent=2)+'\n')
 finally:
  proc.terminate();proc.wait(timeout=5)
zip_path=root/'static/examples/writing-lab.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(fixture.rglob('*')):
  if p.is_file():z.write(p,'writing-lab/'+str(p.relative_to(fixture)))
with tempfile.TemporaryDirectory(prefix='writing-archive-check-') as td:
 with zipfile.ZipFile(zip_path) as z:z.extractall(td)
 run(['node','check.mjs'],Path(td)/'writing-lab','archive-check.log')
print('Original import and aborted-upload failures retained; clean fixture, manual curl and final archive checks PASS.')
