import protobufjs from "protobufjs";
import fs from "fs";
import path from "path";

const schema = process.argv[2] || "ForwardMsg";
const protoRoot = path.resolve("streamlit/proto/streamlit/proto");

const root = new protobufjs.Root();
root.resolvePath = (origin, target) =>
  path.join(protoRoot, target.replace(/^.*streamlit\/proto\//, ""));

function decodeBase64(inputData) {
  try {
    const data = Buffer.from(inputData.trim(), "base64");
    root.loadSync(path.join(protoRoot, `${schema}.proto`));
    root.resolveAll();
    const MsgType = root.lookupType(schema);
    const decoded = MsgType.decode(data);
    console.log(JSON.stringify(decoded, null, 2));
  } catch (err) {
    console.error("❌ Decoder error:", err.message);
    process.exit(1);
  }
}

let inputData = "";
process.stdin.on("data", chunk => (inputData += chunk));
process.stdin.on("end", () => decodeBase64(inputData));