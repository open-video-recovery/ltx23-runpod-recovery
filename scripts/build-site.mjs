import { mkdir, copyFile } from 'node:fs/promises';
await mkdir('dist',{recursive:true});
for(const name of ['index.html','telemetry.js','admin-stats.html']) {
  await copyFile(name,'dist/'+name);
}
