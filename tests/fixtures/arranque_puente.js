/* Preparación del proceso de prueba, separada del plazo de una orden. */
const assert = require('node:assert/strict');
async function preparar(base, id, solicitar = fetch) {
  const respuesta = await solicitar(base + '/siguiente', {
    headers: {'X-Capri-Puente': id, Origin: 'chrome-extension://' + id},
    signal: AbortSignal.timeout(20000)
  });
  assert.equal(respuesta.status, 200);
  assert.equal((await respuesta.json()).tarea, null);
  const continuar = new Promise(resolve => process.stdin.once('data', resolve));
  process.stdout.write('CAPRI_LISTO\n');
  await continuar;
  process.stdin.destroy();
}
module.exports = {preparar};
