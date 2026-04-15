"use client";

import { useState } from "react";

import type { GeneratePackRequest } from "@/lib/types";

type MvpFormProps = {
  onSubmit: (payload: GeneratePackRequest) => Promise<void> | void;
};

export function MvpForm({ onSubmit }: MvpFormProps) {
  const [occasion, setOccasion] = useState("день рождения");
  const [target, setTarget] = useState("друг");
  const [facts, setFacts] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload: GeneratePackRequest = {
      occasion,
      target,
      facts: facts
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      tone: "funny",
      boldness: 2,
      safe_mode: true,
      count: 6,
    };
    await onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded border p-4">
      <div>
        <label htmlFor="occasion" className="mb-1 block text-sm font-medium">
          Повод
        </label>
        <input
          id="occasion"
          value={occasion}
          onChange={(event) => setOccasion(event.target.value)}
          className="w-full rounded border px-3 py-2"
        />
      </div>
      <div>
        <label htmlFor="target" className="mb-1 block text-sm font-medium">
          Про кого
        </label>
        <input
          id="target"
          value={target}
          onChange={(event) => setTarget(event.target.value)}
          className="w-full rounded border px-3 py-2"
        />
      </div>
      <div>
        <label htmlFor="facts" className="mb-1 block text-sm font-medium">
          Факты
        </label>
        <input
          id="facts"
          value={facts}
          onChange={(event) => setFacts(event.target.value)}
          placeholder="через запятую"
          className="w-full rounded border px-3 py-2"
        />
      </div>
      <button type="submit" className="rounded bg-black px-4 py-2 text-white">
        Сгенерировать пачку
      </button>
    </form>
  );
}
