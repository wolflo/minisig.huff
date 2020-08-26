const fs = require('fs');
const path = require('path');
const parser = require('./huff/src/parser');

const modulesPath = path.posix.resolve(__dirname, './src');
const OUT_PATH = 'out/';

const msigParsed = parser.parseFile('minisig.huff', modulesPath);
const constructorParsed = parser.parseFile('constructor.huff', modulesPath)

const runtimeShallow = parser.processMacro(
  'RUNTIME',
  0,
  [ '0xaa' ],
  msigParsed.macros,
  msigParsed.inputMap,
  msigParsed.jumptables
).data.bytecode;

const constructorShallow = parser.processMacro(
  'CONSTRUCTOR',
  0,
  [ '0xaaaa', '0xaa' ],
  constructorParsed.macros,
  constructorParsed.inputMap,
  constructorParsed.jumptables
).data.bytecode;

check(lenBytes(runtimeShallow) <= 255, 'bad runtime length estimate');
check(
  lenBytes(constructorShallow) > 255 &&
  lenBytes(constructorShallow) <= 65525,
  'bad constructor length estimate'
);

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
  [ lenBytes(constructorShallow).toString(), lenBytes(runtime).toString() ],
  constructorParsed.macros,
  constructorParsed.inputMap,
  constructorParsed.jumptables
).data.bytecode;

check(lenBytes(runtime) === lenBytes(runtimeShallow), 'bad runtime length');
check(lenBytes(constructor) === lenBytes(constructorShallow), 'bad constructor length');

const bytecode = constructor + runtime
writeBin('minisig-runtime.bin', runtime);
writeBin('minisig.bin', bytecode);
console.log(`bytecode written to ${OUT_PATH}`);
console.log(`deploy size      : ${lenBytes(bytecode)} bytes`);
console.log(`runtime size     : ${lenBytes(runtime)} bytes`);
console.log(`constructor size : ${lenBytes(constructor)} bytes`);

const dummmyConstructorArgs = '000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000003000000000000000000000000aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa000000000000000000000000bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb000000000000000000000000ffffffffffffffffffffffffffffffffffffffff'
const initCode = bytecode + dummmyConstructorArgs;
writeBin('minisig-cstr.bin', constructor);
writeBin('minisig-init.bin', initCode);

const populatedVals = '00000000000000000000000000000000000000000000000000000000000000026edd5fb8f80f6e3e748e6da8ed3048cd085077429aa0a80a7994c1b59363470f00000000000000000000000000000000000000000000000000000000000000030000000000000000000000001eEE1d40A057D50C84a7bD5632e553eDf4beb93b00000000000000000000000070BBEd4c4D037e89E1e606997C0E5671f7c38D7f0000000000000000000000009b410c059f3b0E0B45A747a34D4Bf5431c282921';
const populatedCode = runtime + populatedVals;
writeBin('minisig-runtime-populated.bin', populatedCode);

function lenBytes(str) {
  return trimBytes(str).length / 2
}

function trimBytes(str) {
  check(str.length % 2 === 0, `ERR: These aint bytes: ${str}`);
  return str.replace(/^0x/,'')
}

function check(pred, err) {
  if (!pred) throw err;
}

function writeBin(filename, bytecode) {
  fs.writeFileSync(path.posix.resolve(__dirname, OUT_PATH + filename), bytecode);
}
