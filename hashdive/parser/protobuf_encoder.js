import protobufjs from "protobufjs";
import fs from "fs";
import path from "path";

const schemaArg = process.argv[2] || "BackMsg"; // e.g. "BackMsg"
const protoFile = schemaArg.endsWith(".proto") ? schemaArg : `${schemaArg}.proto`;
const messageType = schemaArg.replace(/\.proto$/, ""); // e.g. "BackMsg"

const protoRoot = path.resolve("streamlit/proto/streamlit/proto");
const root = new protobufjs.Root();
root.resolvePath = function (origin, target) {
  const cleanTarget = target.replace(/^.*streamlit\/proto\//, "");
  return path.join(protoRoot, cleanTarget);
};

root.loadSync(path.join(protoRoot, protoFile));
root.resolveAll();

const MsgType = root.lookupType(messageType); // <- use the message name

// Read JSON payload from stdin
const stdin = await new Promise((resolve) => {
  let data = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => (data += chunk));
  process.stdin.on("end", () => resolve(data));
});

const payload = JSON.parse(stdin.trim());
const err = MsgType.verify(payload);
if (err) throw Error(err);

const buffer = MsgType.encode(payload).finish();
process.stdout.write(buffer);