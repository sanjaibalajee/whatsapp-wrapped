"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Mock story data
const mockStories = [
  {
    id: 1,
    gradient: "gradient-1",
    title: "Your 2025 in WhatsApp",
    subtitle: "Let's see what you've been up to...",
    stat: null,
    statLabel: null,
  },
  {
    id: 2,
    gradient: "gradient-2",
    title: "Total Messages",
    subtitle: "You sent a LOT of messages this year",
    stat: "47,832",
    statLabel: "messages exchanged",
  },
  {
    id: 3,
    gradient: "gradient-3",
    title: "Most Active Day",
    subtitle: "December 31st was your busiest",
    stat: "1,247",
    statLabel: "messages on New Year's Eve",
  },
  {
    id: 4,
    gradient: "gradient-4",
    title: "Night Owl",
    subtitle: "You love those late night chats",
    stat: "2:47 AM",
    statLabel: "your most active hour",
  },
  {
    id: 5,
    gradient: "gradient-5",
    title: "Top Chatter",
    subtitle: "Your #1 conversation partner",
    stat: "Sarah Miller",
    statLabel: "12,456 messages together",
  },
  {
    id: 6,
    gradient: "gradient-1",
    title: "Media Shared",
    subtitle: "Pictures, videos, and voice notes",
    stat: "2,341",
    statLabel: "media files shared",
  },
  {
    id: 7,
    gradient: "gradient-2",
    title: "Favorite Emoji",
    subtitle: "You really love this one",
    stat: "😂",
    statLabel: "used 3,421 times",
  },
  {
    id: 8,
    gradient: "gradient-3",
    title: "Voice Notes",
    subtitle: "Sometimes typing isn't enough",
    stat: "127",
    statLabel: "voice notes sent",
  },
  {
    id: 9,
    gradient: "gradient-4",
    title: "Longest Streak",
    subtitle: "You chatted every single day",
    stat: "89 days",
    statLabel: "consecutive days chatting",
  },
  {
    id: 10,
    gradient: "gradient-5",
    title: "That's a Wrap!",
    subtitle: "Thanks for an amazing 2025",
    stat: null,
    statLabel: "Share your Wrapped with friends",
  },
];

export default function WrappedPage() {
  const router = useRouter();
  const [currentStory, setCurrentStory] = useState(0);

  useEffect(() => {
    // Load saved story position
    const savedStory = localStorage.getItem("wrappedCurrentStory");
    if (savedStory) {
      setCurrentStory(parseInt(savedStory));
    }
  }, []);

  const handleNextStory = () => {
    if (currentStory < mockStories.length - 1) {
      const next = currentStory + 1;
      setCurrentStory(next);
      localStorage.setItem("wrappedCurrentStory", next.toString());
    }
  };

  const handlePrevStory = () => {
    if (currentStory > 0) {
      const prev = currentStory - 1;
      setCurrentStory(prev);
      localStorage.setItem("wrappedCurrentStory", prev.toString());
    }
  };

  const handleStoryClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const width = rect.width;

    if (x < width / 3) {
      handlePrevStory();
    } else {
      handleNextStory();
    }
  };

  const handleClose = () => {
    localStorage.removeItem("wrappedCurrentStory");
    router.push("/");
  };

  const story = mockStories[currentStory];

  return (
    <div className="h-screen w-screen bg-[#0a0a0a] overflow-hidden">
      <div
        className={`relative w-full h-full overflow-hidden ${story.gradient} cursor-pointer`}
        onClick={handleStoryClick}
      >
        {/* Progress Bars */}
        <div className="absolute top-4 left-4 right-4 flex gap-1 z-10">
          {mockStories.map((_, index) => (
            <div
              key={index}
              className="flex-1 h-1 rounded-full bg-white/30 overflow-hidden"
            >
              <div
                className={`h-full bg-white transition-all ${
                  index < currentStory
                    ? "w-full"
                    : index === currentStory
                    ? "story-progress"
                    : "w-0"
                }`}
                key={`progress-${currentStory}-${index}`}
              />
            </div>
          ))}
        </div>

        {/* Close Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleClose();
          }}
          className="absolute top-12 right-4 w-8 h-8 rounded-full bg-black/30 flex items-center justify-center z-10 hover:bg-black/50 transition-all"
        >
          <svg
            className="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center">
          <div className="slide-up" key={story.id}>
            {/* WhatsApp Logo for first and last story */}
            {(story.id === 1 || story.id === 10) && (
              <div className="w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                <svg
                  className="w-16 h-16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  strokeWidth="0.8"
                >
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
              </div>
            )}

            <h2 className="text-2xl font-extrabold text-white mb-3 tracking-tight">
              {story.title}
            </h2>
            <p className="text-white/70 mb-8 font-medium text-base">{story.subtitle}</p>

            {story.stat && (
              <div className="count-up">
                <p
                  className={`font-extrabold text-white mb-2 ${
                    story.stat.length > 10 ? "text-4xl" : "text-6xl"
                  }`}
                >
                  {story.stat}
                </p>
                <p className="text-white/60 text-sm font-medium">{story.statLabel}</p>
              </div>
            )}

            {/* Share button on last story */}
            {story.id === 10 && (
              <button className="mt-8 px-8 py-3 bg-[#25D366] text-white font-semibold rounded-xl hover:bg-[#128C7E] transition-all">
                Share Your Wrapped
              </button>
            )}
          </div>
        </div>

        {/* Navigation hints */}
        <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-2 text-white/40 text-xs">
          <span>Tap left/right to navigate</span>
        </div>

        {/* Story counter */}
        <div className="absolute bottom-4 left-0 right-0 text-center text-white/30 text-xs">
          {currentStory + 1} / {mockStories.length}
        </div>
      </div>
    </div>
  );
}
