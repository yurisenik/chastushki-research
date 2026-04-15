import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MvpForm } from "./mvp-form";


describe("MvpForm", () => {
  it("submits scenario data to callback", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<MvpForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("Повод"), { target: { value: "свадьба" } });
    fireEvent.change(screen.getByLabelText("Про кого"), { target: { value: "молодожены" } });
    fireEvent.change(screen.getByLabelText("Факты"), { target: { value: "танцуют до утра" } });
    fireEvent.click(screen.getByRole("button", { name: "Сгенерировать пачку" }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        occasion: "свадьба",
        target: "молодожены",
        facts: ["танцуют до утра"],
      }),
    );
  });
});
