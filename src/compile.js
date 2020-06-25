const path = require('path');
const fs = require('fs');
const parser = require('../huff/src/parser');

const modulesPath = path.posix.resolve(__dirname, './huff_modules');
const OUT_PATH = '../out/';

const minisigParsed = parser.parseFile('minisig.huff', modulesPath);

const minisig = parser.processMacro(
  'MAIN',
  0,
  [],
  minisigParsed.macros,
  minisigParsed.inputMap,
  minisigParsed.jumptables
).data.bytecode;

writeBin('minisig.bin', minisig);

console.log(`bytecode written to ${OUT_PATH}`);

function writeBin(filename, bytecode) {
  fs.writeFileSync(path.posix.resolve(__dirname, OUT_PATH + filename), bytecode);
}
