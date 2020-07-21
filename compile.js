const fs = require('fs');
const path = require('path');
const parser = require('./huff/src/parser');

const modulesPath = path.posix.resolve(__dirname, './src/huff_modules');
const OUT_PATH = 'out/';

const msigParsed = parser.parseFile('minisig.huff', modulesPath);
const constructorParsed = parser.parseFile('constructor.huff', modulesPath)

const runtimeShallow = parser.processMacro(
  'RUNTIME',
  0,
  [ '00' ],
  msigParsed.macros,
  msigParsed.inputMap,
  msigParsed.jumptables
).data.bytecode;

const constructorShallow = parser.processMacro(
  'CONSTRUCTOR',
  0,
  [ '00' ],
  constructorParsed.macros,
  constructorParsed.inputMap,
  constructorParsed.jumptables
).data.bytecode;

check(lenBytes(runtimeShallow) <= 255, "bad runtime length estimate");
check(lenBytes(constructorShallow) <= 255, "bad constructor length estimate");

const runtime = parser.processMacro(
  'RUNTIME',
  0,
  [ lenBytes(runtimeShallow).toString() ],
  msigParsed.macros,
  msigParsed.inputMap,
  msigParsed.jumptables
).data.bytecode;

const constructor = parser.processMacro(
  'CONSTRUCTOR',
  0,
  [ lenBytes(constructorShallow).toString() ],
  constructorParsed.macros,
  constructorParsed.inputMap,
  constructorParsed.jumptables
).data.bytecode;

check(lenBytes(runtime) === lenBytes(runtimeShallow), "bad runtime length");
check(lenBytes(constructor) === lenBytes(constructorShallow), "bad runtime length");

const initCode = runtime + constructor
writeBin('minisig-runtime.bin', runtime);
writeBin('minisig-init.bin', initCode);
console.log(`bytecode written to ${OUT_PATH}`);
console.log(`init size        : ${lenBytes(initCode)} bytes`);
console.log(`runtime size     : ${lenBytes(runtime)} bytes`);
console.log(`constructor size : ${lenBytes(constructor)} bytes`);

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
