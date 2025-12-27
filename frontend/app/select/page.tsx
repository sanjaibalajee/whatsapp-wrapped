"use client";

import { useState, useEffect, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Dithering } from "@paper-design/shaders-react";
import { startAnalysis, getJobStatus } from "../actions";
import { hasValidCache } from "../lib/cache";

interface Participant {
  name: string;
  selected: boolean;
}

export default function SelectPage() {
  const router = useRouter();
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we already have cached stats - redirect to wrapped
    if (hasValidCache()) {
      router.replace("/wrapped");
      return;
    }

    // Load participants from localStorage
    const storedParticipants = localStorage.getItem("wrappedParticipants");
    const storedJobId = localStorage.getItem("wrappedJobId");

    if (!storedParticipants || !storedJobId) {
      router.push("/");
      return;
    }

    setJobId(storedJobId);
    const names: string[] = JSON.parse(storedParticipants);
    setParticipants(names.map((name) => ({ name, selected: true })));
  }, [router]);

  const toggleParticipant = (index: number) => {
    setParticipants((prev) =>
      prev.map((p, i) => (i === index ? { ...p, selected: !p.selected } : p))
    );
  };

  const selectedCount = participants.filter((p) => p.selected).length;
  const allSelected = selectedCount === participants.length;

  const toggleAll = () => {
    setParticipants((prev) =>
      prev.map((p) => ({ ...p, selected: !allSelected }))
    );
  };

  const pollJobStatus = async (id: string) => {
    try {
      const status = await getJobStatus(id);
      setProgress(status.progress);
      setCurrentStep(status.current_step);

      if (status.status === "completed") {
        // Store job ID for stats page and navigate to wrapped
        localStorage.setItem("wrappedJobId", id);
        router.push("/wrapped");
      } else if (status.status === "failed") {
        setError("Analysis failed. Please try again.");
        setIsAnalyzing(false);
      } else {
        // Continue polling
        setTimeout(() => pollJobStatus(id), 1000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get status");
      setIsAnalyzing(false);
    }
  };

  const handleContinue = () => {
    if (!jobId || selectedCount === 0) return;

    const selectedMembers = participants
      .filter((p) => p.selected)
      .map((p) => p.name);

    startTransition(async () => {
      try {
        const response = await startAnalysis(jobId, selectedMembers);

        if (response.status === "pending") {
          setIsAnalyzing(true);
          setProgress(0);
          setCurrentStep("Starting analysis...");
          // Start polling
          pollJobStatus(jobId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Analysis failed");
      }
    });
  };

  // Show analyzing screen
  if (isAnalyzing) {
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
            speed={0.15}
          />
        </div>

        <div className="max-w-sm w-full text-center relative z-10">
          {/* Animated Logo */}
          <div className="w-20 h-20 mx-auto flex items-center justify-center mb-8">
            <svg
              className="w-20 h-20 animate-pulse"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#25D366"
              strokeWidth="0.8"
            >
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
          </div>

          <h1 className="text-2xl font-extrabold tracking-tight mb-2">
            Analyzing your chats...
          </h1>
          <p className="text-zinc-400 text-sm mb-8">{currentStep}</p>

          {/* Progress Bar */}
          <div className="w-full h-2 bg-[#2a2a2a] rounded-full overflow-hidden mb-4">
            <div
              className="h-full bg-[#25D366] transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-zinc-500 text-sm">{progress}% complete</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col px-4 py-6 relative overflow-hidden">
      {/* Dithering Background */}
      <div className="absolute inset-0 z-0 opacity-20">
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

      <div className="max-w-sm w-full mx-auto fade-in relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="text-center mb-6">
          <button
            onClick={() => router.push("/")}
            className="absolute left-0 top-0 p-2 text-zinc-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-xl font-extrabold tracking-tight">Who&apos;s in your Wrapped?</h1>
          <p className="text-zinc-500 text-sm mt-1">
            {selectedCount} of {participants.length} selected
          </p>
        </div>

        {/* Select All Toggle */}
        {participants.length > 0 && (
          <button
            onClick={toggleAll}
            className="flex items-center justify-between w-full px-4 py-3 mb-4 rounded-lg bg-[#1a1a1a]/80 border border-[#2a2a2a] text-sm"
          >
            <span className="text-zinc-300 font-medium">
              {allSelected ? "Deselect all" : "Select all"}
            </span>
            <div
              className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                allSelected
                  ? "border-[#25D366] bg-[#25D366]"
                  : "border-[#3a3a3a]"
              }`}
            >
              {allSelected && (
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </button>
        )}

        {/* Participants List */}
        <div className="space-y-2 mb-6 flex-1 overflow-y-auto">
          {participants.map((participant, index) => (
            <button
              key={participant.name}
              onClick={() => toggleParticipant(index)}
              className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all ${
                participant.selected
                  ? "bg-[#128C7E]/30 border border-[#128C7E]"
                  : "bg-[#1a1a1a]/80 border border-[#2a2a2a] hover:border-[#3a3a3a]"
              }`}
            >
              {/* Info */}
              <div className="flex-1 text-left">
                <p
                  className={`font-semibold text-sm ${
                    participant.selected ? "text-white" : "text-zinc-300"
                  }`}
                >
                  {participant.name}
                </p>
              </div>

              {/* Checkbox */}
              <div
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                  participant.selected
                    ? "border-[#128C7E] bg-[#128C7E]"
                    : "border-[#3a3a3a]"
                }`}
              >
                {participant.selected && (
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>

        {error && (
          <p className="text-red-400 text-sm mb-4 text-center">{error}</p>
        )}

        {/* Actions - Fixed at bottom */}
        <div className="pt-4 border-t border-[#2a2a2a]">
          <button
            onClick={handleContinue}
            disabled={selectedCount === 0 || isPending}
            className={`w-full py-3.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
              selectedCount > 0 && !isPending
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
                <span>Starting...</span>
              </>
            ) : (
              "Continue"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
