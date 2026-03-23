import CryptoJS from 'crypto-js';

const HASH_SALT = import.meta.env.VITE_HASH_SALT || 'super-secret-hash-key';

export function hashApiKey(apiKey: string): string {
  const saltedKey = apiKey + HASH_SALT;
  const hash = CryptoJS.SHA256(saltedKey).toString();
  return hash;
}
