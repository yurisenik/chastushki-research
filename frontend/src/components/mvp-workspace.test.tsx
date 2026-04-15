import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MvpWorkspace } from "./mvp-workspace";

vi.mock("@/lib/api", () => ({
  generatePack: vi.fn(async () => ({
    pack_id: "pack-1",
    candidates: [{ id: "c1", text: "Тестовая частушка", score: 1, safe: true }],
    created_at: "2026-01-01T00:00:00Z",
  })),
  refinePack: vi.fn(async () => ({
    pack_id: "pack-2",
    source_pack_id: "pack-1",
    candidates: [{ id: "c2", text: "Уточненная частушка", score: 1, safe: true }],
    created_at: "2026-01-01T00:00:00Z",
  })),
  getHistory: vi.fn(async () => ({ items: [] })),
  getFavorites: vi.fn(async () => ({ items: [] })),
  addFavorite: vi.fn(async () => ({
    pack_id: "pack-1",
    candidates: [],
    created_at: "2026-01-01T00:00:00Z",
  })),
}));

describe("MvpWorkspace", () => {
  it("generates and renders candidate pack", async () => {
    render(<MvpWorkspace />);
    fireEvent.click(screen.getByRole("button", { name: "Сгенерировать пачку" }));

    await waitFor(() => {
      expect(screen.getByText("Тестовая частушка")).toBeInTheDocument();
    });
  });
});
