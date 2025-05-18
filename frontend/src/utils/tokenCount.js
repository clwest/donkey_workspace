import { encoding_for_model } from "tiktoken";

let encoder;

export function countTokens(text, model = "text-embedding-3-small") {
  if (!encoder) {
    encoder = encoding_for_model(model);
  }

  return encoder.encode(text).length;
}
