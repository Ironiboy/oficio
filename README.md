# oficio

[![tests](https://github.com/Ironiboy/oficio/actions/workflows/tests.yml/badge.svg)](https://github.com/Ironiboy/oficio/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Build Apple apps like a craftsperson, with Claude Code.**

*Oficio* is Spanish for *craft*: the skill of someone who knows their trade and takes pride in it. That's what
this plugin teaches Claude: **Uncle Bob's discipline, made executable**, applied to Swift and SwiftUI, with
numbers instead of opinions.

It wasn't written from a blog post. It grew out of months of building a real app: a read-later app for iOS and
macOS with on-device AI, Swift 6 and SwiftUI on the iOS 27 SDK. Every rule in it exists because something cost
us an afternoon. Every trap is verified against an installed SDK and dated.

## What you get

🔒 **Deterministic quality gates, not reviewer opinions.** Acceptance tests first (they must fail first), CRAP
≤ 8 per function, **zero surviving mutants**, a shape ratchet (file and function size, comments, duplication),
and zero warnings on every platform. Small Python scripts run them for you, and they only measure what you
touched, so you can adopt them on day one of a legacy codebase.

✅ **"Done" means proven.** Nothing is declared finished, fixed or faster without the command output that
shows it, in the same turn.

📏 **Decisions with numbers.** Benchmarks before changes, paired bootstrap intervals, a clear adoption rule, and
three judges when bias can creep in: development, a fresh single-use set, and human labels.

🚀 **State of the art, always.** A session-start hook diffs the frameworks in your installed SDK against your
project's list and tells Claude what's new. (We built it after Core AI landed in the SDK and almost slipped past us.)

🪤 **Traps we already fell into, so you don't have to.** SwiftData crashes that `try` can't catch, CloudKit
schema rules, `navigationDestination` capturing stale state, BGTaskScheduler failing silently, MainActor
isolation leaking into conformances, the iCloud Drive folder that hangs `xcodebuild`…

🧠 **On-device AI done right.** Foundation Models, Core AI and Core ML compared by measurement, graceful
degradation on every inference path, and a teacher → student pipeline for your own models (Dawid-Skene label
aggregation included).

🪙 **Fewer tokens, same quality.** What to cut (whole-file reads, unfiltered logs, idle agents, babysitting
long jobs) and what never to cut (reading the code you change, running the tests, the evidence).

## Install

As a Claude Code plugin (skill + session hook):

```
/plugin marketplace add Ironiboy/oficio
/plugin install oficio@oficio
```

That's it. The skill triggers on its own whenever you write, debug, measure, design or plan code in an Apple
project.

**Optional, per project:**

- Let the hook spot new SDK frameworks by saving today's list:
  ```bash
  mkdir -p .oficio && ls "$(xcrun --sdk macosx --show-sdk-path)/System/Library/Frameworks" \
    | sed 's/.framework//' > .oficio/sdk-frameworks.txt
  ```
- Use the gates in your repo: copy `skills/oficio/puertas-swift/` to `scripts/gates/` and set
  `OFICIO_PKG=YourAppKit`. See [its README](skills/oficio/puertas-swift/README.md).

## What's inside

```
skills/oficio/
  SKILL.md            the method, short on purpose (it's loaded every time)
  referencias/        the details, read only when needed: debugging, measuring, SwiftData & CloudKit,
                      concurrency, SwiftUI, design & accessibility, platform, on-device AI, networking,
                      shipping to the App Store, context & tokens
  puertas-swift/      the gates: crap, mutants, forma (Python 3 + Xcode toolchain), with their own tests
hooks/arranque.sh     four lines of essentials at session start, after /clear and after compaction
evals/                task evals and trigger queries, in Anthropic's skill-creator format
tests/                the skill tests itself: paths, sizes, manifests, hook, evals
```

## A note on language

The skill itself is written in **Spanish**: that's the language it was born in, and Claude follows it just as
well whatever language you work in. Replies come back in *your* language. An English edition of the skill text
is on the roadmap. Contributions welcome.

## Measuring the skill

Practice what you preach: the skill ships with its own evals. Run `evals/evals.json` with and without the skill
using Anthropic's [skill-creator](https://github.com/anthropics/skills), and `evals/disparo.json` with its
trigger-optimization loop. The repo's own tests run in CI on every push.

## Status

API notes verified against the macOS/iOS 27.2 SDK (November 2026). On a new SDK, re-verify them. The skill
itself insists on it.

## License

[MIT](LICENSE). Use it, fork it, make it yours.
