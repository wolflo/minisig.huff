const path = require('path');
const fs = require('fs');
const parser = require('./huff/src/parser');

const modulesPath = path.posix.resolve(__dirname, './src/huff_modules');
const OUT_PATH = 'out/';

const minisigParsed = parser.parseFile('minisig.huff', modulesPath);

const runtime = parser.processMacro(
  'RUNTIME',
  0,
  [],
  minisigParsed.macros,
  minisigParsed.inputMap,
  minisigParsed.jumptables
).data.bytecode;

const runtimeShallow = parser.processMacro(
  'RUNTIME__SHALLOW',
  0,
  [],
  minisigParsed.macros,
  minisigParsed.jumptables,
).data.bytecode;

if(runtime.length !== runtimeShallow.length) throw "runtimeShallow incorrect length";

writeBin('minisig-runtime.bin', runtime);

console.log(`bytecode written to ${OUT_PATH}`);

function writeBin(filename, bytecode) {
  fs.writeFileSync(path.posix.resolve(__dirname, OUT_PATH + filename), bytecode);
}
