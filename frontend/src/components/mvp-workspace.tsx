"use client";

import { useState } from "react";

import { addFavorite, generatePack, getFavorites, getHistory, refinePack } from "@/lib/api";
import type { GeneratePackRequest, Pack } from "@/lib/types";
import { MvpForm } from "./mvp-form";

const ACTIONS = [
  { label: "Смешнее", value: "funnier" },
  { label: "Мягче", value: "softer" },
  { label: "Дерзче", value: "bolder" },
  { label: "Народнее", value: "folksier" },
  { label: "Короче", value: "shorter" },
  { label: "Еще", value: "more" },
];

export function MvpWorkspace() {
  const [currentPack, setCurrentPack] = useState<Pack | null>(null);
  const [history, setHistory] = useState<Pack[]>([]);
  const [favorites, setFavorites] = useState<Pack[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    const [historyResponse, favoritesResponse] = await Promise.all([getHistory(), getFavorites()]);
    setHistory(historyResponse.items);
    setFavorites(favoritesResponse.items);
  };

  const handleSubmit = async (payload: GeneratePackRequest) => {
    setError(null);
    try {
      const pack = await generatePack(payload);
      setCurrentPack(pack);
      await refresh();
    } catch {
      setError("Не удалось получить пачку. Проверьте backend URL.");
    }
  };

  const handleRefine = async (action: string) => {
    if (!currentPack) return;
    setError(null);
    try {
      const refined = await refinePack(currentPack.pack_id, action);
      setCurrentPack(refined);
      await refresh();
    } catch {
      setError("Не удалось доработать пачку.");
    }
  };

  const handleFavorite = async () => {
    if (!currentPack) return;
    await addFavorite(currentPack.pack_id);
    await refresh();
  };

  return (
    <section className="grid gap-6 md:grid-cols-2">
      <div className="space-y-4">
        <MvpForm onSubmit={handleSubmit} />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </div>
      <div className="space-y-4">
        <article className="rounded border p-4">
          <h2 className="mb-3 text-xl font-semibold">Результат</h2>
          {!currentPack ? (
            <p className="text-sm text-gray-500">Сначала сгенерируйте пачку.</p>
          ) : (
            <>
              <ul className="space-y-2 text-sm">
                {currentPack.candidates.map((candidate) => (
                  <li key={candidate.id} className="rounded bg-gray-50 p-2">
                    {candidate.text}
                  </li>
                ))}
              </ul>
              <div className="mt-3 flex flex-wrap gap-2">
                {ACTIONS.map((action) => (
                  <button
                    key={action.value}
                    type="button"
                    onClick={() => handleRefine(action.value)}
                    className="rounded border px-2 py-1 text-xs"
                  >
                    {action.label}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={handleFavorite}
                  className="rounded bg-black px-2 py-1 text-xs text-white"
                >
                  В избранное
                </button>
              </div>
            </>
          )}
        </article>
        <article className="rounded border p-4">
          <h3 className="mb-2 text-sm font-semibold">История</h3>
          <p className="text-xs text-gray-600">Паков: {history.length}</p>
        </article>
        <article className="rounded border p-4">
          <h3 className="mb-2 text-sm font-semibold">Избранное</h3>
          <p className="text-xs text-gray-600">Паков: {favorites.length}</p>
        </article>
      </div>
    </section>
  );
}
