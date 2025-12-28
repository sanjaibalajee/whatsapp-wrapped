"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getJobStats } from "../actions";
import { getCachedStats, setCachedStats, clearCache } from "../lib/cache";

// Type definitions
interface SlideData {
  id: number;
  type: string;
  title: string;
  data: Record<string, unknown>;
}

interface SummaryData {
  groupName: string;
  totalMessages: number;
  activeDays: number;
  longestStreak: number;
  topChatter: { name: string; count: number } | null;
  peakHour: number;
  busiestDay: { date: string; count: number } | null;
  topEmoji: string;
  topWords: string[];
  topics: string[];
  brainRotScore: number;
  groupRoast: string;
}

// Slide configurations with diverse gradients and patterns
const slideStyles = [
  { gradient: "from-[#0a0a0a] via-[#0a0a0a] to-[#0a0a0a]", pattern: "none" }, // Intro - clean
  { gradient: "from-[#0a0a0a] via-[#0d1a15] to-[#0a0a0a]", pattern: "radial-top" }, // Overview - subtle green center
  { gradient: "from-[#0a0a0a] via-[#0a0a0a] to-[#1a0f14]", pattern: "glow-bottom" }, // Ranking - warm accent
  { gradient: "from-[#0a0a0a] via-[#0a1218] to-[#0a0a0a]", pattern: "dots" }, // Emoji - cool dots
  { gradient: "from-[#14100a] via-[#0a0a0a] to-[#0a0a0a]", pattern: "diagonal" }, // Activity - diagonal warmth
  { gradient: "from-[#0a0a0a] to-[#0a0a0a] via-[#0a1510]", pattern: "mesh" }, // Words - mesh pattern
  { gradient: "from-[#0a0a0a] via-[#0a0a0a] to-[#100a14]", pattern: "glow-center" }, // Signature - purple glow
  { gradient: "from-[#0a0a0a] via-[#10140a] to-[#0a0a0a]", pattern: "waves" }, // Dynamics - subtle waves
  { gradient: "from-[#0a0a14] via-[#0a0a0a] to-[#0a0a0a]", pattern: "corner-glow" }, // Fun stats - corner accent
  { gradient: "from-[#0a0a0a] via-[#1a0a10] to-[#0a0a0a]", pattern: "gradient-orb" }, // Brain rot - dramatic
  { gradient: "from-[#0a0a0a] via-[#0a0a0a] to-[#140a0a]", pattern: "fire" }, // Individual takes - fire effect
  { gradient: "from-[#0a0a0a] via-[#0a1a0f] to-[#0a0a0a]", pattern: "summary" }, // Summary - special
  { gradient: "from-[#0a0a0a] via-[#0a0a0a] to-[#0a100a]", pattern: "radial-bottom" }, // Outro - closing
];

// Pattern overlay component
function PatternOverlay({ type }: { type: string }) {
  if (type === "none") return null;

  if (type === "dots") {
    return (
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `radial-gradient(circle, #25D366 1px, transparent 1px)`,
          backgroundSize: '20px 20px',
        }}
      />
    );
  }

  if (type === "radial-top") {
    return (
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          background: `radial-gradient(ellipse at 50% 0%, #25D366 0%, transparent 60%)`,
        }}
      />
    );
  }

  if (type === "radial-bottom") {
    return (
      <div
        className="absolute inset-0 opacity-[0.05]"
        style={{
          background: `radial-gradient(ellipse at 50% 100%, #25D366 0%, transparent 50%)`,
        }}
      />
    );
  }

  if (type === "glow-bottom") {
    return (
      <div className="absolute inset-0">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#ff6b6b]/[0.03] rounded-full blur-[100px]" />
      </div>
    );
  }

  if (type === "glow-center") {
    return (
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9b59b6]/[0.04] rounded-full blur-[120px]" />
      </div>
    );
  }

  if (type === "diagonal") {
    return (
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `repeating-linear-gradient(45deg, #f39c12 0, #f39c12 1px, transparent 0, transparent 50%)`,
          backgroundSize: '30px 30px',
        }}
      />
    );
  }

  if (type === "mesh") {
    return (
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(#25D366 1px, transparent 1px),
            linear-gradient(90deg, #25D366 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }}
      />
    );
  }

  if (type === "waves") {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 20'%3E%3Cpath fill='none' stroke='%2325D366' stroke-width='0.5' d='M0 10 Q25 0 50 10 T100 10'/%3E%3C/svg%3E")`,
            backgroundSize: '100px 20px',
          }}
        />
      </div>
    );
  }

  if (type === "corner-glow") {
    return (
      <div className="absolute inset-0">
        <div className="absolute -top-20 -left-20 w-[400px] h-[400px] bg-[#3498db]/[0.04] rounded-full blur-[100px]" />
        <div className="absolute -bottom-20 -right-20 w-[300px] h-[300px] bg-[#25D366]/[0.03] rounded-full blur-[80px]" />
      </div>
    );
  }

  if (type === "gradient-orb") {
    return (
      <div className="absolute inset-0">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-[#e74c3c]/[0.05] rounded-full blur-[150px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-[#f39c12]/[0.04] rounded-full blur-[100px]" />
      </div>
    );
  }

  if (type === "fire") {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute bottom-0 left-0 right-0 h-1/2 opacity-[0.04]"
          style={{
            background: `linear-gradient(to top, #e74c3c 0%, #f39c12 30%, transparent 100%)`,
          }}
        />
      </div>
    );
  }

  if (type === "summary") {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1/3 opacity-[0.06]"
          style={{
            background: `linear-gradient(to bottom, #25D366 0%, transparent 100%)`,
          }}
        />
        <div className="absolute bottom-0 left-0 right-0 h-1/4 opacity-[0.04]"
          style={{
            background: `linear-gradient(to top, #25D366 0%, transparent 100%)`,
          }}
        />
      </div>
    );
  }

  return null;
}

// Number formatter
const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null) return "0";
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "K";
  return num.toLocaleString();
};

// Slide Components
function IntroSlide() {
  return (
    <div className="flex flex-col items-center justify-center h-full px-8 text-center">
      <div className="w-20 h-20 mx-auto mb-8 flex items-center justify-center animate-pulse">
        <svg
          className="w-20 h-20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="0.8"
        >
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
      </div>
      <h1 className="text-3xl font-extrabold text-white mb-4 tracking-tight">
        Your 2025 in WhatsApp
      </h1>
      <p className="text-white/70 text-lg font-medium">
        Let&apos;s see what you&apos;ve been up to...
      </p>
    </div>
  );
}

function OverviewSlide({ data }: { data: Record<string, unknown> }) {
  const totalMessages = (data.total_messages as number) || 0;
  const streak = data.streak as { longest_streak: number; total_active_days: number } | undefined;
  const totalImages = (data.total_images as number) || 0;
  const totalVideos = (data.total_videos as number) || 0;
  const totalStickers = (data.total_stickers as number) || 0;
  const totalMedia = totalImages + totalVideos + totalStickers;

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-6">
        This year you exchanged
      </p>

      <p className="text-8xl font-extrabold text-white mb-2 tracking-tight">
        {formatNumber(totalMessages)}
      </p>
      <p className="text-white/50 text-xl font-medium mb-10">
        messages
      </p>

      <div className="space-y-4 text-left">
        <p className="text-2xl text-white/80">
          <span className="text-[#25D366] font-bold">{streak?.total_active_days || 0}</span> active days
        </p>
        <p className="text-2xl text-white/80">
          <span className="text-[#25D366] font-bold">{totalMedia}</span> media shared
        </p>
        {streak && streak.longest_streak > 0 && (
          <p className="text-2xl text-white/80">
            <span className="text-[#25D366] font-bold">{streak.longest_streak}</span> day streak 🔥
          </p>
        )}
      </div>
    </div>
  );
}

function RankingSlide({ data }: { data: Record<string, unknown> }) {
  const rankings = (data.rankings as Array<{ name: string; count: number }>) || [];
  const topThree = rankings.slice(0, 3);
  const rest = rankings.slice(3, 7);

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-8">
        Top Chatters
      </p>

      {/* Podium for top 3 */}
      <div className="flex items-end justify-center gap-3 mb-8 w-full max-w-sm">
        {/* 2nd place */}
        {topThree[1] && (
          <div className="flex flex-col items-center w-24">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-2 text-xl font-bold text-white/70">
              2
            </div>
            <p className="text-white/70 font-semibold text-sm truncate w-full">{topThree[1].name}</p>
            <p className="text-white/40 text-xs">{formatNumber(topThree[1].count)}</p>
            <div className="w-full h-20 bg-white/10 rounded-t-xl mt-2" />
          </div>
        )}

        {/* 1st place */}
        {topThree[0] && (
          <div className="flex flex-col items-center w-28">
            <div className="w-14 h-14 rounded-full bg-[#25D366] flex items-center justify-center mb-2 text-2xl">
              👑
            </div>
            <p className="text-white font-bold text-base truncate w-full">{topThree[0].name}</p>
            <p className="text-[#25D366] text-sm font-semibold">{formatNumber(topThree[0].count)}</p>
            <div className="w-full h-28 bg-[#25D366]/20 rounded-t-xl mt-2" />
          </div>
        )}

        {/* 3rd place */}
        {topThree[2] && (
          <div className="flex flex-col items-center w-24">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-2 text-xl font-bold text-white/70">
              3
            </div>
            <p className="text-white/70 font-semibold text-sm truncate w-full">{topThree[2].name}</p>
            <p className="text-white/40 text-xs">{formatNumber(topThree[2].count)}</p>
            <div className="w-full h-14 bg-white/10 rounded-t-xl mt-2" />
          </div>
        )}
      </div>

      {/* Rest of rankings */}
      {rest.length > 0 && (
        <div className="w-full max-w-xs space-y-3">
          {rest.map((person, idx) => (
            <div key={person.name} className="flex items-center gap-3">
              <span className="text-white/30 text-lg font-bold w-6">{idx + 4}</span>
              <span className="text-white/70 text-base flex-1 text-left truncate">{person.name}</span>
              <span className="text-white/40 text-sm">{formatNumber(person.count)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EmojiSlide({ data }: { data: Record<string, unknown> }) {
  const groupTopEmojis = (data.group_top_emojis as Array<[string, number]>) || [];
  const topEmoji = groupTopEmojis[0];

  return (
    <div className="flex flex-col items-center justify-center h-full px-8 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-6">
        Your favorite emoji
      </p>

      {topEmoji && (
        <>
          <p className="text-[120px] leading-none mb-4">{topEmoji[0]}</p>
          <p className="text-white/50 text-lg mb-10">
            used <span className="text-[#25D366] font-bold">{formatNumber(topEmoji[1])}</span> times
          </p>
        </>
      )}

      <div className="space-y-3">
        {groupTopEmojis.slice(1, 5).map((item, idx) => (
          <p key={idx} className="text-xl text-white/60">
            <span className="text-3xl mr-3">{item[0]}</span>
            <span className="text-white/40">{formatNumber(item[1])}</span>
          </p>
        ))}
      </div>
    </div>
  );
}

function ActivitySlide({ data }: { data: Record<string, unknown> }) {
  const peakHour = data.peak_hour as number | undefined;
  const busiestDay = data.busiest_day as { date: string; count: number } | undefined;
  const dailyDistribution = (data.daily_distribution as Record<string, number>) || {};

  // Convert 24h to 12h format
  const formatHour = (hour: number | undefined): string => {
    if (hour === undefined) return "--";
    if (hour === 0) return "12 AM";
    if (hour === 12) return "12 PM";
    if (hour < 12) return `${hour} AM`;
    return `${hour - 12} PM`;
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const maxDaily = Math.max(...Object.values(dailyDistribution), 1);
  const busiestDayOfWeek = days.reduce((max, day) =>
    (dailyDistribution[day] || 0) > (dailyDistribution[max] || 0) ? day : max
  , days[0]);

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-8">
        Peak Activity
      </p>

      <p className="text-6xl font-extrabold text-white mb-2">
        {formatHour(peakHour)}
      </p>
      <p className="text-white/50 text-lg mb-10">your peak hour</p>

      <div className="space-y-4 text-left">
        <p className="text-2xl text-white/80">
          <span className="text-[#25D366] font-bold">{busiestDayOfWeek}</span> is your busiest day
        </p>
        {busiestDay && (
          <>
            <p className="text-2xl text-white/80">
              <span className="text-[#25D366] font-bold">{formatNumber(busiestDay.count)}</span> msgs on{" "}
              <span className="text-[#25D366] font-bold">
                {new Date(busiestDay.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </p>
          </>
        )}
      </div>

      {/* Simple day indicators */}
      <div className="flex gap-3 mt-10">
        {days.map((day) => {
          const count = dailyDistribution[day] || 0;
          const opacity = 0.2 + (count / maxDaily) * 0.8;
          return (
            <div key={day} className="text-center">
              <p
                className="text-[#25D366] text-sm font-bold"
                style={{ opacity }}
              >
                {day.slice(0, 2)}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WordsSlide({ data }: { data: Record<string, unknown> }) {
  const topWords = (data.top_words as Array<[string, number]>) || [];
  const topics = (data.topics as string[]) || [];

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-8">
        Most used words
      </p>

      <div className="space-y-3 mb-10">
        {topWords.slice(0, 6).map((item, idx) => {
          const sizes = ["text-5xl", "text-4xl", "text-3xl", "text-2xl", "text-xl", "text-lg"];
          const opacities = [1, 0.85, 0.7, 0.6, 0.5, 0.4];
          return (
            <p
              key={`${item[0]}-${idx}`}
              className={`${sizes[idx]} font-bold text-white`}
              style={{ opacity: opacities[idx] }}
            >
              {item[0]} <span className="text-[#25D366] text-sm font-normal ml-2">{formatNumber(item[1])}</span>
            </p>
          );
        })}
      </div>

      {topics.length > 0 && (
        <div className="text-left">
          <p className="text-white/40 text-sm mb-3">Hot topics</p>
          <div className="space-y-2">
            {topics.slice(0, 4).map((topic, idx) => (
              <p key={topic} className="text-white/70 text-lg">
                <span className="text-[#25D366] mr-3">{idx + 1}.</span>
                {topic}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SignatureWordsSlide({
  entries,
  pageIndex,
  totalPages,
}: {
  entries: Array<[string, string[]]>;
  pageIndex: number;
  totalPages: number;
}) {
  const PEOPLE_PER_PAGE = 5;
  const startIndex = pageIndex * PEOPLE_PER_PAGE;
  const pageEntries = entries.slice(startIndex, startIndex + PEOPLE_PER_PAGE);
  const isMultiPage = totalPages > 1;

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-1">
        Signature Words
      </p>
      <p className="text-white/40 text-xs mb-6">
        Words unique to each person
        {isMultiPage && <span className="text-white/30"> • {pageIndex + 1}/{totalPages}</span>}
      </p>

      <div className="w-full max-w-sm space-y-4">
        {pageEntries.map(([name, words]) => (
          <div key={name} className="flex items-start gap-3 text-left">
            <p className="text-white font-bold text-sm shrink-0 min-w-[80px]">{name}</p>
            <p className="text-[#25D366]/80 text-sm">
              {words.slice(0, 3).join(", ")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ConvoDynamicsSlide({ data }: { data: Record<string, unknown> }) {
  const starters = (data.starters as string[]) || [];
  const killers = (data.killers as string[]) || [];

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-10">
        Conversation Dynamics
      </p>

      {starters.length > 0 && (
        <div className="mb-10">
          <p className="text-white/40 text-sm uppercase tracking-wider mb-2">Conversation Starter</p>
          <p className="text-4xl font-extrabold text-white">{starters[0]}</p>
          <p className="text-white/50 text-sm mt-2">Always kicks off the chat 💬</p>
        </div>
      )}

      {killers.length > 0 && (
        <div>
          <p className="text-white/40 text-sm uppercase tracking-wider mb-2">Conversation Ender</p>
          <p className="text-4xl font-extrabold text-white">{killers[0]}</p>
          <p className="text-white/50 text-sm mt-2">Usually has the last word 🎤</p>
        </div>
      )}
    </div>
  );
}

function FunStatsSlide({ data }: { data: Record<string, unknown> }) {
  const doubleTexter = data.double_texter as [string, number] | null;
  const linkSharer = data.link_sharer as [string, number] | null;
  const questionAsker = data.question_asker as [string, number] | null;

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#25D366] text-sm font-semibold uppercase tracking-widest mb-10">
        Fun Stats
      </p>

      <div className="space-y-8 text-left w-full max-w-sm">
        {doubleTexter && (
          <div>
            <p className="text-white/40 text-sm mb-1">Double Texter 💬</p>
            <p className="text-3xl font-bold text-white">{doubleTexter[0]}</p>
            <p className="text-[#25D366] text-lg">{formatNumber(doubleTexter[1])} times</p>
          </div>
        )}

        {questionAsker && (
          <div>
            <p className="text-white/40 text-sm mb-1">Question Asker ❓</p>
            <p className="text-3xl font-bold text-white">{questionAsker[0]}</p>
            <p className="text-[#25D366] text-lg">{formatNumber(questionAsker[1])} questions</p>
          </div>
        )}

        {linkSharer && (
          <div>
            <p className="text-white/40 text-sm mb-1">Link Sharer 🔗</p>
            <p className="text-3xl font-bold text-white">{linkSharer[0]}</p>
            <p className="text-[#25D366] text-lg">{formatNumber(linkSharer[1])} links</p>
          </div>
        )}
      </div>
    </div>
  );
}

function BrainRotSlide({ data }: { data: Record<string, unknown> }) {
  const brainrotScore = (data.brainrot_score as number) || 0;
  const groupRoast = (data.group_roast as string) || "";

  // Get score color and label
  const getScoreStyle = (score: number) => {
    if (score >= 80) return { color: "text-red-400", label: "Terminal", emoji: "🧠💀" };
    if (score >= 60) return { color: "text-orange-400", label: "Severe", emoji: "🧠🔥" };
    if (score >= 40) return { color: "text-yellow-400", label: "Moderate", emoji: "🧠⚡" };
    if (score >= 20) return { color: "text-green-400", label: "Mild", emoji: "🧠✨" };
    return { color: "text-blue-400", label: "Healthy", emoji: "🧠💚" };
  };

  const scoreStyle = getScoreStyle(brainrotScore);

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#e74c3c] text-sm font-semibold uppercase tracking-widest mb-6">
        Brain Rot Score
      </p>

      <p className="text-6xl mb-2">{scoreStyle.emoji}</p>

      <p className={`text-8xl font-black ${scoreStyle.color} mb-2`}>
        {brainrotScore}
      </p>
      <p className={`text-xl font-bold ${scoreStyle.color} uppercase tracking-wider mb-8`}>
        {scoreStyle.label}
      </p>

      {groupRoast && (
        <div className="max-w-sm">
          <p className="text-white/40 text-xs uppercase tracking-wider mb-3">The Verdict</p>
          <p className="text-white/80 text-lg leading-relaxed italic">
            &quot;{groupRoast}&quot;
          </p>
        </div>
      )}
    </div>
  );
}

function IndividualRoastsSlide({
  roasts,
  pageIndex
}: {
  roasts: Array<{ name: string; roast: string }>;
  pageIndex: number;
}) {
  const ROASTS_PER_PAGE = 5;
  const startIndex = pageIndex * ROASTS_PER_PAGE;
  const pageRoasts = roasts.slice(startIndex, startIndex + ROASTS_PER_PAGE);

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center">
      <p className="text-[#f39c12] text-sm font-semibold uppercase tracking-widest mb-2">
        What We Think About You
      </p>
      <p className="text-white/30 text-xs mb-8">
        {pageIndex + 1} of {Math.ceil(roasts.length / ROASTS_PER_PAGE)}
      </p>

      <div className="space-y-6 w-full max-w-sm overflow-y-auto max-h-[65vh]">
        {pageRoasts.map(({ name, roast }, idx) => (
          <div key={name} className="text-left">
            <p className="text-[#f39c12] font-bold text-lg mb-2">{name}</p>
            <p className="text-white/70 text-sm leading-relaxed">
              {roast}
            </p>
            {idx < pageRoasts.length - 1 && (
              <div className="mt-6 h-px bg-white/10" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function SummarySlide({ data }: { data: SummaryData }) {
  const [copied, setCopied] = useState(false);

  const formatHour = (hour: number): string => {
    if (hour === 0) return "12 AM";
    if (hour === 12) return "12 PM";
    if (hour < 12) return `${hour} AM`;
    return `${hour - 12} PM`;
  };

  const getScoreStyle = (score: number) => {
    if (score >= 80) return { color: "#ef4444", bg: "from-red-500/20 to-red-600/5" };
    if (score >= 60) return { color: "#f97316", bg: "from-orange-500/20 to-orange-600/5" };
    if (score >= 40) return { color: "#eab308", bg: "from-yellow-500/20 to-yellow-600/5" };
    return { color: "#22c55e", bg: "from-green-500/20 to-green-600/5" };
  };

  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || window.location.origin;
    const shareUrl = baseUrl;
    const shareText = `Check out my WhatsApp Wrapped 2025! ${formatNumber(data.totalMessages)} messages, Brain Rot Score: ${data.brainRotScore} 🧠`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'WhatsApp Wrapped 2025',
          text: shareText,
          url: shareUrl,
        });
      } catch {
        // User cancelled
      }
    } else {
      // Fallback: copy link
      await navigator.clipboard.writeText(`${shareText}\n${shareUrl}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const scoreStyle = getScoreStyle(data.brainRotScore);

  return (
    <div className="flex flex-col h-full px-6 py-2 relative overflow-hidden">
      {/* Minimal Header */}
      <div className="text-center mb-1">
        <p className="text-[#25D366] text-[9px] font-bold uppercase tracking-[0.2em]">Wrapped</p>
      </div>

      {/* Hero Section - Big Impact */}
      <div className="flex-1 flex flex-col justify-center -mt-4">
        {/* Year */}
        <p className="text-[56px] font-black text-white leading-none tracking-tighter text-center">
          2025
        </p>

        {/* Group Name */}
        <p className="text-white/40 text-xs text-center mt-1 mb-4 truncate px-4">
          {data.groupName}
        </p>

        {/* The Big Number */}
        <div className="text-center mb-5">
          <p className="text-[#25D366] text-5xl font-black tracking-tight">
            {formatNumber(data.totalMessages)}
          </p>
          <p className="text-white/60 text-xs mt-1">messages exchanged</p>
        </div>

        {/* Quick Stats Row */}
        <div className="flex justify-center gap-6 mb-5">
          <div className="text-center">
            <p className="text-white text-xl font-bold">{data.activeDays}</p>
            <p className="text-white/40 text-[9px] uppercase tracking-wider">days</p>
          </div>
          <div className="text-center">
            <p className="text-white text-xl font-bold">{data.longestStreak}<span className="text-sm ml-0.5">🔥</span></p>
            <p className="text-white/40 text-[9px] uppercase tracking-wider">streak</p>
          </div>
          <div className="text-center">
            <p className="text-2xl">{data.topEmoji || "💬"}</p>
            <p className="text-white/40 text-[9px] uppercase tracking-wider">vibe</p>
          </div>
        </div>

        {/* Highlights - No Cards, Just Text */}
        <div className="space-y-1.5 mb-4">
          {data.topChatter && (
            <p className="text-center text-white/70 text-xs">
              <span className="text-white font-semibold">{data.topChatter.name}</span> led with{" "}
              <span className="text-[#25D366] font-semibold">{formatNumber(data.topChatter.count)}</span> messages
            </p>
          )}
          <p className="text-center text-white/70 text-xs">
            Most active at <span className="text-white font-semibold">{formatHour(data.peakHour)}</span>
            {data.busiestDay && (
              <>, peaked on <span className="text-white font-semibold">
                {new Date(data.busiestDay.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span></>
            )}
          </p>
          {/* What the chat was about */}
          {(data.topWords.length > 0 || data.topics.length > 0) && (
            <div className="text-center pt-1">
              <p className="text-white/40 text-[9px] uppercase tracking-wider mb-0.5">you talked about</p>
              <p className="text-white/80 text-xs">
                {[...new Set([...data.topics.slice(0, 2), ...data.topWords.slice(0, 3)])].slice(0, 4).join(", ")}
              </p>
            </div>
          )}
        </div>

        {/* Brain Rot Card - The One Card That Matters */}
        <div className={`bg-gradient-to-br ${scoreStyle.bg} backdrop-blur-sm rounded-xl p-3 mx-auto w-full max-w-[260px]`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">
                {data.brainRotScore >= 80 ? "💀" : data.brainRotScore >= 60 ? "🔥" : data.brainRotScore >= 40 ? "⚡" : "✨"}
              </span>
              <div>
                <p className="text-white/50 text-[9px] uppercase tracking-wider">Brain Rot</p>
                <p className="text-white font-medium text-xs">Score</p>
              </div>
            </div>
            <p className="text-4xl font-black" style={{ color: scoreStyle.color }}>
              {data.brainRotScore}
            </p>
          </div>
          {data.groupRoast && (
            <p className="text-white/60 text-[10px] italic leading-relaxed border-t border-white/10 pt-2">
              &quot;{data.groupRoast}&quot;
            </p>
          )}
        </div>
      </div>

      {/* Share Button - Bottom Right, Small */}
      <button
        onClick={handleShare}
        className="absolute bottom-2 right-2 p-2 text-white/40 hover:text-[#25D366] transition-all"
        title="Share"
      >
        {copied ? (
          <svg className="w-5 h-5 text-[#25D366]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        )}
      </button>
    </div>
  );
}

function OutroSlide({ onNewWrapped }: { onNewWrapped: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-8 text-center">
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

      <h2 className="text-3xl font-extrabold text-white mb-3 tracking-tight">
        That&apos;s a Wrap!
      </h2>
      <p className="text-white/50 text-lg mb-8">
        Thanks for an amazing 2025
      </p>

      <div className="space-y-3">
        <button className="w-full px-8 py-3.5 border-2 border-[#25D366] text-[#25D366] font-semibold rounded-xl hover:bg-[#25D366]/10 transition-all">
          Share Your Wrapped
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onNewWrapped();
          }}
          className="w-full px-8 py-3 text-white/40 font-medium text-sm hover:text-white/60 transition-all"
        >
          Try Another Chat
        </button>
      </div>

      <p className="text-white/30 text-xs mt-6">
        made by{" "}
        <a
          href="https://sanjaibalajee.me"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-white/50 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          sanjai balajee
        </a>
      </p>
    </div>
  );
}

// Types for expanded slides
interface VirtualSlide {
  type: "intro" | "outro" | "regular" | "brain_rot" | "individual_roasts" | "signature_words" | "summary";
  slideData?: SlideData;
  roasts?: Array<{ name: string; roast: string }>;
  roastPageIndex?: number;
  signatureEntries?: Array<[string, string[]]>;
  signaturePageIndex?: number;
  signatureTotalPages?: number;
  summaryData?: SummaryData;
}

// Helper to extract summary data from all slides
function extractSummaryData(slides: SlideData[], metadata?: Record<string, unknown>): SummaryData {
  const summary: SummaryData = {
    groupName: (metadata?.group_name as string) || "Your Chat",
    totalMessages: 0,
    activeDays: 0,
    longestStreak: 0,
    topChatter: null,
    peakHour: 0,
    busiestDay: null,
    topEmoji: "",
    topWords: [],
    topics: [],
    brainRotScore: 0,
    groupRoast: "",
  };

  for (const slide of slides) {
    switch (slide.type) {
      case "overview": {
        summary.totalMessages = (slide.data.total_messages as number) || 0;
        const streak = slide.data.streak as { longest_streak: number; total_active_days: number } | undefined;
        if (streak) {
          summary.activeDays = streak.total_active_days || 0;
          summary.longestStreak = streak.longest_streak || 0;
        }
        break;
      }
      case "ranking": {
        const rankings = slide.data.rankings as Array<{ name: string; count: number }> | undefined;
        if (rankings && rankings.length > 0) {
          summary.topChatter = { name: rankings[0].name, count: rankings[0].count };
        }
        break;
      }
      case "emojis": {
        const emojis = slide.data.group_top_emojis as Array<[string, number]> | undefined;
        if (emojis && emojis.length > 0) {
          summary.topEmoji = emojis[0][0];
        }
        break;
      }
      case "activity": {
        summary.peakHour = (slide.data.peak_hour as number) || 0;
        summary.busiestDay = slide.data.busiest_day as { date: string; count: number } | null;
        break;
      }
      case "words": {
        const words = slide.data.top_words as Array<[string, number]> | undefined;
        if (words) {
          summary.topWords = words.slice(0, 3).map(w => w[0]);
        }
        summary.topics = (slide.data.topics as string[]) || [];
        break;
      }
      case "ai_roasts": {
        summary.brainRotScore = (slide.data.brainrot_score as number) || 0;
        summary.groupRoast = (slide.data.group_roast as string) || "";
        break;
      }
    }
  }

  return summary;
}

// Helper to process slides and expand data into multiple virtual slides
function processSlides(slides: SlideData[], metadata?: Record<string, unknown>): VirtualSlide[] {
  const ROASTS_PER_PAGE = 5;
  const SIGNATURE_WORDS_PER_PAGE = 5;
  const virtualSlides: VirtualSlide[] = [{ type: "intro" }];

  for (const slide of slides) {
    if (slide.type === "chat_graph") continue; // Skip chat_graph

    if (slide.type === "ai_roasts") {
      // Add brain rot slide
      virtualSlides.push({ type: "brain_rot", slideData: slide });

      // Get individual roasts
      const individualRoasts = slide.data.individual_roasts as Record<string, string> | undefined;
      if (individualRoasts) {
        const roastsArray = Object.entries(individualRoasts).map(([name, roast]) => ({ name, roast }));
        const numPages = Math.ceil(roastsArray.length / ROASTS_PER_PAGE);

        for (let i = 0; i < numPages; i++) {
          virtualSlides.push({
            type: "individual_roasts",
            roasts: roastsArray,
            roastPageIndex: i,
          });
        }
      }
    } else if (slide.type === "signature_words") {
      // Handle signature words pagination
      const perPerson = (slide.data.per_person as Record<string, string[]>) || {};
      const entries = Object.entries(perPerson) as Array<[string, string[]]>;
      const numPages = Math.ceil(entries.length / SIGNATURE_WORDS_PER_PAGE);

      for (let i = 0; i < numPages; i++) {
        virtualSlides.push({
          type: "signature_words",
          signatureEntries: entries,
          signaturePageIndex: i,
          signatureTotalPages: numPages,
        });
      }
    } else {
      virtualSlides.push({ type: "regular", slideData: slide });
    }
  }

  // Add summary slide before outro
  const summaryData = extractSummaryData(slides, metadata);
  virtualSlides.push({ type: "summary", summaryData });

  virtualSlides.push({ type: "outro" });
  return virtualSlides;
}

export default function WrappedPage() {
  const router = useRouter();
  const [currentStory, setCurrentStory] = useState(0);
  const [virtualSlides, setVirtualSlides] = useState<VirtualSlide[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const totalSlides = virtualSlides.length;

  useEffect(() => {
    const loadStats = async () => {
      // First, try to load from cache
      const cached = getCachedStats();
      if (cached && cached.stats?.slides) {
        const statsData = cached.stats as { slides: SlideData[]; metadata?: Record<string, unknown> };
        const metadata = statsData.metadata || cached.metadata;
        setVirtualSlides(processSlides(statsData.slides, metadata));
        setLoading(false);
        return;
      }

      // No cache, try to fetch from API
      const jobId = localStorage.getItem("wrappedJobId");
      if (!jobId) {
        router.push("/");
        return;
      }

      try {
        const response = await getJobStats(jobId);
        const statsData = response.stats as { slides: SlideData[]; metadata?: Record<string, unknown> };
        const metadata = statsData.metadata || (response.metadata as Record<string, unknown>);

        // Cache the stats for future visits
        setCachedStats(statsData, metadata, jobId);

        setVirtualSlides(processSlides(statsData.slides, metadata));
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load stats");
        setLoading(false);
      }
    };

    loadStats();
  }, [router]);

  const handleNextStory = () => {
    if (currentStory < totalSlides - 1) {
      setCurrentStory((prev) => prev + 1);
    }
  };

  const handlePrevStory = () => {
    if (currentStory > 0) {
      setCurrentStory((prev) => prev - 1);
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

  const handleNewWrapped = () => {
    clearCache();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin w-8 h-8 mx-auto text-[#25D366]" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-white/50 mt-4 text-sm">Loading your Wrapped...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center px-8">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="px-6 py-2 bg-[#25D366] text-white rounded-xl"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const currentVirtualSlide = virtualSlides[currentStory];
  const currentStyle = slideStyles[currentStory % slideStyles.length];

  // Render based on virtual slide type
  const renderCurrentSlide = () => {
    if (!currentVirtualSlide) return null;

    switch (currentVirtualSlide.type) {
      case "intro":
        return <IntroSlide />;
      case "outro":
        return <OutroSlide onNewWrapped={handleNewWrapped} />;
      case "brain_rot":
        return currentVirtualSlide.slideData ? <BrainRotSlide data={currentVirtualSlide.slideData.data} /> : null;
      case "individual_roasts":
        return currentVirtualSlide.roasts ? (
          <IndividualRoastsSlide roasts={currentVirtualSlide.roasts} pageIndex={currentVirtualSlide.roastPageIndex || 0} />
        ) : null;
      case "signature_words":
        return currentVirtualSlide.signatureEntries ? (
          <SignatureWordsSlide
            entries={currentVirtualSlide.signatureEntries}
            pageIndex={currentVirtualSlide.signaturePageIndex || 0}
            totalPages={currentVirtualSlide.signatureTotalPages || 1}
          />
        ) : null;
      case "summary":
        return currentVirtualSlide.summaryData ? (
          <SummarySlide data={currentVirtualSlide.summaryData} />
        ) : null;
      case "regular":
        if (!currentVirtualSlide.slideData) return null;
        const slide = currentVirtualSlide.slideData;
        switch (slide.type) {
          case "overview":
            return <OverviewSlide data={slide.data} />;
          case "ranking":
            return <RankingSlide data={slide.data} />;
          case "emojis":
            return <EmojiSlide data={slide.data} />;
          case "activity":
            return <ActivitySlide data={slide.data} />;
          case "words":
            return <WordsSlide data={slide.data} />;
          case "convo_dynamics":
            return <ConvoDynamicsSlide data={slide.data} />;
          case "fun_stats":
            return <FunStatsSlide data={slide.data} />;
          default:
            return (
              <div className="flex flex-col items-center justify-center h-full px-8 text-center">
                <h2 className="text-2xl font-bold text-white">{slide.title}</h2>
              </div>
            );
        }
      default:
        return null;
    }
  };

  const isSummarySlide = currentVirtualSlide?.type === "summary";

  return (
    <div className="h-screen w-screen bg-[#0a0a0a] overflow-hidden">
      <div
        className={`relative w-full h-full overflow-hidden cursor-pointer transition-all duration-500 ${
          isSummarySlide ? '' : `bg-gradient-to-br ${currentStyle.gradient}`
        }`}
        style={isSummarySlide ? {
          backgroundImage: 'url(/bg.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        } : undefined}
        onClick={handleStoryClick}
      >
        {/* Blur overlay for summary slide */}
        {isSummarySlide && (
          <div className="absolute inset-0 bg-black/70 backdrop-blur-md z-0" />
        )}

        {/* Subtle pattern overlay - not for summary */}
        {!isSummarySlide && <PatternOverlay type={currentStyle.pattern} />}

        {/* Progress Bars */}
        <div className="absolute top-4 left-4 right-4 flex gap-1 z-10">
          {Array.from({ length: totalSlides }, (_, index) => (
            <div
              key={index}
              className="flex-1 h-0.5 rounded-full bg-white/20 overflow-hidden"
            >
              <div
                className={`h-full bg-white transition-all duration-300 ${
                  index < currentStory
                    ? "w-full"
                    : index === currentStory
                    ? "w-full"
                    : "w-0"
                }`}
              />
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="absolute inset-0 z-10 pt-16 pb-16" key={currentStory}>
          <div className="h-full slide-up">
            {renderCurrentSlide()}
          </div>
        </div>

        {/* Watermark - visible on summary slide */}
        {isSummarySlide && (
          <div className="absolute bottom-4 right-4 text-right z-20">
            <p className="text-sm font-bold">
              <span className="text-white">#</span>
              <span className="text-[#25D366]">WhatsApp</span>
              <span className="text-white">Wrapped2025</span>
            </p>
            <p className="text-white/40 text-xs">made by sanjai</p>
          </div>
        )}

        {/* Story counter - hidden on summary slide */}
        {!isSummarySlide && (
          <div className="absolute bottom-4 left-0 right-0 text-center text-white/20 text-xs">
            {currentStory + 1} / {totalSlides}
          </div>
        )}
      </div>
    </div>
  );
}
