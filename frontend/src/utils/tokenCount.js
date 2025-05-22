import { encoding_for_model } from "tiktoken";

export const EMBEDDING_MODEL = "text-embedding-3-small";
let encoder;

export function countTokens(text, model = EMBEDDING_MODEL) {
  if (!encoder) {
    encoder = encoding_for_model(model);
  }

  return encoder.encode(text).length;
}
