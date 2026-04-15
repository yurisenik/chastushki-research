import { MvpWorkspace } from "@/components/mvp-workspace";

export default function Home() {
  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl p-6 md:p-10">
      <h1 className="mb-2 text-3xl font-bold">Chastushki MVP</h1>
      <p className="mb-6 text-sm text-gray-600">
        Сценарный ввод, пакетная генерация, быстрые доработки и история.
      </p>
      <MvpWorkspace />
    </main>
  );
}
