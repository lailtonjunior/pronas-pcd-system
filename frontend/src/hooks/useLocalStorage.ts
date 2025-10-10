// Arquivo: frontend/src/hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

function getStorageValue<T>(key: string, defaultValue: T): T {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem(key);
    if (saved !== null) {
      try {
        return JSON.parse(saved) as T;
      } catch (e) {
        console.error("Failed to parse localStorage value", e);
        return defaultValue;
      }
    }
  }
  return defaultValue;
}

export const useLocalStorage = <T>(key: string, defaultValue: T): [T, (value: T) => void] => {
  const [value, setValue] = useState<T>(() => {
    return getStorageValue(key, defaultValue);
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
};