"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Dithering } from "@paper-design/shaders-react";

interface Participant {
  name: string;
  selected: boolean;
  messageCount: number;
}

// Mock participants data
const mockParticipants: Participant[] = [
  { name: "Alex Johnson", selected: true, messageCount: 4523 },
  { name: "Sarah Miller", selected: true, messageCount: 3891 },
  { name: "Mike Chen", selected: true, messageCount: 2156 },
  { name: "Emma Wilson", selected: false, messageCount: 1834 },
  { name: "David Brown", selected: false, messageCount: 1245 },
  { name: "Lisa Garcia", selected: true, messageCount: 987 },
];

export default function SelectPage() {
  const router = useRouter();
  const [participants, setParticipants] = useState<Participant[]>(mockParticipants);

  useEffect(() => {
    // Check if user came from landing page
    const fileName = localStorage.getItem("wrappedFileName");
    if (!fileName) {
      router.push("/");
    }

    // Load saved participants if any
    const saved = localStorage.getItem("wrappedParticipants");
    if (saved) {
      setParticipants(JSON.parse(saved));
    }
  }, [router]);

  const toggleParticipant = (index: number) => {
    setParticipants((prev) => {
      const updated = prev.map((p, i) => (i === index ? { ...p, selected: !p.selected } : p));
      localStorage.setItem("wrappedParticipants", JSON.stringify(updated));
      return updated;
    });
  };

  const selectedCount = participants.filter((p) => p.selected).length;
  const allSelected = selectedCount === participants.length;

  const toggleAll = () => {
    setParticipants((prev) => {
      const updated = prev.map((p) => ({ ...p, selected: !allSelected }));
      localStorage.setItem("wrappedParticipants", JSON.stringify(updated));
      return updated;
    });
  };

  const handleContinue = () => {
    router.push("/wrapped");
  };

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
                <p className="text-zinc-500 text-xs">
                  {participant.messageCount.toLocaleString()} messages
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

        {/* Actions - Fixed at bottom */}
        <div className="pt-4 border-t border-[#2a2a2a]">
          <button
            onClick={handleContinue}
            disabled={selectedCount === 0}
            className={`w-full py-3.5 rounded-xl font-semibold transition-all ${
              selectedCount > 0
                ? "bg-[#25D366] text-white hover:bg-[#128C7E]"
                : "bg-[#2a2a2a] text-zinc-500 cursor-not-allowed"
            }`}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
