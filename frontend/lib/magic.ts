import { Magic } from "magic-sdk";

let magic: Magic | null = null;

export function getMagic(): Magic {
  if (typeof window === "undefined") {
    throw new Error("Magic can only be used in the browser");
  }
  if (!magic) {
    magic = new Magic(process.env.NEXT_PUBLIC_MAGIC_PUBLISHABLE_KEY!);
  }
  return magic;
}
