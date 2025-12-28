"use client";

import { useState, useTransition, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Dithering } from "@paper-design/shaders-react";
import { uploadChat } from "./actions";
import { hasValidCache } from "./lib/cache";

export default function Home() {
  const router = useRouter();
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [showInstructions, setShowInstructions] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [checkingCache, setCheckingCache] = useState(true);

  // Check for cached data on mount
  useEffect(() => {
    if (hasValidCache()) {
      router.replace("/wrapped");
    } else {
      setCheckingCache(false);
    }
  }, [router]);

  // Show nothing while checking cache to prevent flash
  if (checkingCache) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
        <div className="w-8 h-8 border-2 border-[#25D366] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const maxSize = 20 * 1024 * 1024; // 20MB
      if (selectedFile.size > maxSize) {
        setError("File size exceeds 20MB limit");
        return;
      }
      if (!selectedFile.name.endsWith(".txt")) {
        setError("Only .txt files are allowed");
        return;
      }
      setFileName(selectedFile.name);
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleContinue = () => {
    if (!file) return;

    startTransition(async () => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("year", "2025");

      const result = await uploadChat(formData);

      if (!result.success) {
        setError(result.error);
        return;
      }

      if (result.data.status === "awaiting_selection") {
        // Store job data in localStorage
        localStorage.setItem("wrappedJobId", result.data.job_id);
        localStorage.setItem("wrappedParticipants", JSON.stringify(result.data.participants));
        router.push("/select");
      }
    });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8 relative overflow-hidden">
      {/* Dithering Background */}
      <div className="absolute inset-0 z-0 opacity-30">
        <Dithering
          width="100%"
          height="100%"
          colorBack="#0a0a0a"
          colorFront="#25D366"
          shape="simplex"
          type="4x4"
          size={3}
          scale={0.6}
          speed={0.08}
        />
      </div>
      <div className="max-w-sm w-full text-center fade-in relative z-10">
        {/* Logo & Title */}
        <div className="mb-6">
          <div className="w-16 h-16 mx-auto flex items-center justify-center mb-4">
            <svg
              className="w-16 h-16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#25D366"
              strokeWidth="0.8"
            >
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight whitespace-nowrap">
            WhatsApp Wrapped <span className="text-[#25D366]">2025</span>
          </h1>
          <p className="text-zinc-400 mt-3 text-sm sm:text-base font-medium">
            Discover your group&apos;s year in review.
            <br />
            <span className="text-zinc-500">Who texted the most? Your top emojis? Find out.</span>
          </p>
        </div>

        {/* Upload Section */}
        <div className="space-y-3 mb-4">
          <label className="block">
            <div
              className={`border-2 border-dashed rounded-xl px-4 py-5 cursor-pointer transition-all ${
                fileName
                  ? "border-[#25D366] bg-[#25D366]/10"
                  : "border-[#2a2a2a] hover:border-[#25D366]/50 hover:bg-[#1a1a1a]"
              }`}
            >
              <input
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isPending}
              />
              {fileName ? (
                <div className="flex items-center justify-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#25D366] flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <div className="text-left">
                    <p className="text-[#25D366] font-medium text-sm">{fileName}</p>
                    <p className="text-zinc-500 text-xs">Tap to change</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#2a2a2a] flex items-center justify-center flex-shrink-0 pulse-animation">
                    <svg
                      className="w-5 h-5 text-[#25D366]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                      />
                    </svg>
                  </div>
                  <div className="text-left">
                    <p className="text-zinc-200 font-medium text-sm">
                      Upload chat export
                    </p>
                    <p className="text-zinc-500 text-xs">.txt file only (max 20MB)</p>
                  </div>
                </div>
              )}
            </div>
          </label>

          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}

          <button
            onClick={handleContinue}
            disabled={!fileName || isPending}
            className={`w-full py-3.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
              fileName && !isPending
                ? "bg-[#25D366] text-white hover:bg-[#128C7E]"
                : "bg-[#2a2a2a] text-zinc-500 cursor-not-allowed"
            }`}
          >
            {isPending ? (
              <>
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Processing...</span>
              </>
            ) : (
              "See Your Wrapped"
            )}
          </button>
        </div>

        {/* Collapsible Instructions */}
        <div className="mb-6">
          <button
            onClick={() => setShowInstructions(!showInstructions)}
            className="flex items-center justify-center gap-2 text-zinc-400 hover:text-zinc-300 transition-colors mx-auto text-sm"
          >
            <span>How do I export my chat?</span>
            <svg
              className={`w-4 h-4 transition-transform ${showInstructions ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showInstructions && (
            <div className="mt-4 bg-[#1a1a1a] rounded-xl p-4 text-left border border-[#2a2a2a] fade-in">
              <ol className="space-y-2.5 text-zinc-300 text-[13px]">
                <li className="flex gap-2.5">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#25D366]/20 text-[#25D366] flex items-center justify-center text-[10px] font-bold">
                    1
                  </span>
                  <span>Open the WhatsApp chat you want to analyze</span>
                </li>
                <li className="flex gap-2.5">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#25D366]/20 text-[#25D366] flex items-center justify-center text-[10px] font-bold">
                    2
                  </span>
                  <span>Tap the three dots menu (⋮) in the top right</span>
                </li>
                <li className="flex gap-2.5">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#25D366]/20 text-[#25D366] flex items-center justify-center text-[10px] font-bold">
                    3
                  </span>
                  <span>Select &quot;More&quot; → &quot;Export chat&quot;</span>
                </li>
                <li className="flex gap-2.5">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#25D366]/20 text-[#25D366] flex items-center justify-center text-[10px] font-bold">
                    4
                  </span>
                  <span>Choose &quot;Without media&quot; for faster export</span>
                </li>
                <li className="flex gap-2.5">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#25D366]/20 text-[#25D366] flex items-center justify-center text-[10px] font-bold">
                    5
                  </span>
                  <span>Save the .txt file and upload above</span>
                </li>
              </ol>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex flex-col items-center gap-1 text-zinc-500 text-xs">
          <div>
            <span>made by </span>
            <a
              href="https://sanjaibalajee.me/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-300 hover:text-white transition-colors underline underline-offset-2"
            >
              sanjai balajee
            </a>
          </div>
          <a
            href="https://github.com/sanjaibalajee"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors underline underline-offset-2"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            <span>github</span>
          </a>
        </div>
      </div>
    </div>
  );
}
