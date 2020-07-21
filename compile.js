const fs = require('fs');
const path = require('path');
const parser = require('./huff/src/parser');

const modulesPath = path.posix.resolve(__dirname, './src/huff_modules');
const OUT_PATH = 'out/';

const msigParsed = parser.parseFile('minisig.huff', modulesPath);

const runtimeShallow = parser.processMacro(
  'RUNTIME',
  0,
  [ '00' ],
  msigParsed.macros,
  msigParsed.inputMap,
  msigParsed.jumptables
).data.bytecode;

check(lenBytes(runtimeShallow) <= 255, "bad runtime length estimate");

const runtime = parser.processMacro(
  'RUNTIME',
  0,
  [ lenBytes(runtimeShallow).toString() ],
  msigParsed.macros,
  msigParsed.inputMap,
  msigParsed.jumptables
).data.bytecode;

check(lenBytes(runtime) === lenBytes(runtimeShallow), "bad runtime length");

writeBin('minisig-runtime.bin', runtime);
console.log(`bytecode written to ${OUT_PATH}`);

function lenBytes(str) {
  return trimBytes(str).length / 2
}

function trimBytes(str) {
  if (str.length % 2 !== 0) {
    throw 'ERR: These aint bytes'
  }
  return str.replace(/^0x/,'')
}

function check(pred, err) {
  if (!pred) throw err;
}

function writeBin(filename, bytecode) {
  fs.writeFileSync(path.posix.resolve(__dirname, OUT_PATH + filename), bytecode);
}
