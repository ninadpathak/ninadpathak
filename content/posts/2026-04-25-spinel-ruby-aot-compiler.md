---
title: "Matz's Ruby AOT Compiler: How Spinel Differs from YJIT/MJIT and What It Means for Production Ruby"
date: "2026-04-25"
slug: "spinel-ruby-aot-compiler"
description: "Spinel compiles Ruby to standalone native binaries with 11.6x speedups over miniruby. I dug into the architecture to understand why AOT beats JIT for long-running services."
tags: ["ruby", "compilers", "performance", "yjit", "aot"]
status: published
---

Matz released Spinel on March 25, 2026. Within 24 hours it had 1,000 stars on GitHub. The HN thread had 87 comments and a score of 331. I cloned the repo and spent a weekend reading the code. This is what I found.

## The fundamental difference: AOT vs JIT

YJIT and MJIT are JIT compilers. They run inside the Ruby process, profiling method calls at runtime and compiling hot paths on the fly. Spinel is an ahead-of-time compiler. It produces a standalone native binary before the program ever runs. This distinction matters enormously for production deployment.

A JIT compiler pays a warm-up cost every time a process starts. YJIT typically needs several thousand iterations before it identifies and compiles the hot paths in your application. MJIT has a similar problem: it compiles methods to native code in the background, but the first requests to a freshly forked worker still hit the interpreter. Spinel eliminates warm-up entirely. The compilation happens once, at build time. Your Puma worker starts fast and stays fast.

AOT compilation also changes the deployment model. A Spinel binary has no runtime dependencies. It needs only libc and libm. A Docker image that runs CRuby with YJIT needs to ship the entire Ruby interpreter, the JVM for MJIT's C extension compilation, and all the supporting libraries. A Spinel binary is a single file you drop onto a bare Linux machine.

## The architecture: Ruby to C to native

Spinel transforms Ruby source through three stages:

```
Ruby (.rb) → spinel_parse → AST text → spinel_codegen → C source → cc -O2 → Native binary
```

The parser uses Prism (the same parser Ruby 3.0 adopted). Spinel ships with a C binary (`spinel_parse`) that links libprism directly, so you do not need CRuby installed to parse. The fallback path uses the Prism gem with CRuby.

The compiler backend (`spinel_codegen.rb`) is 21,109 lines of Ruby written in a restricted subset Spinel itself can compile: classes, `def`, `attr_accessor`, `if`/`case`/`while`, `each`/`map`/`select`, `yield`, `begin`/`rescue`. No metaprogramming, no `eval`, no `require` in the backend. This self-hosting property is how Matz verified the compiler itself works correctly: the bootstrap loop generates identical C output whether running on CRuby or on a previously compiled Spinel binary.

The runtime lives in a single header file (`lib/sp_runtime.h`, 581 lines) plus `lib/sp_bigint.c` (5,394 lines) for arbitrary precision integers. The linker pulls only the parts the program actually uses.

## Whole-program type inference

Spinel's headline performance claim is ~11.6x faster than miniruby across 55 benchmarks. The geometric mean across 28 computation-heavy benchmarks is even higher. The mechanism driving these speedups is whole-program type inference.

YJIT and MJIT operate under runtime constraints. They do not know what types will flow through a method until the program actually runs. They use guards and type speculation to handle polymorphic code. Spinel analyzes the entire program before execution. It propagates types from call sites to method definitions, builds a call graph, and emits specialized C code for each concrete type combination it encounters.

The result is direct, unboxed operations in generated C. A method that always receives two integers generates C code that calls `sp_add_int_int` directly. No method dispatch, no virtual machine lookup, no garbage collection for those values. The trade-off mirrors what I described in my post on [prompt caching](/articles/prompt-caching-what-it-is-and-when-the-math-works): the upfront cost of analysis pays back across all subsequent executions, whether that analysis is compile-time type inference or runtime token KV cache management.

Value-type promotion extends this further. Classes with eight or fewer scalar fields and no inheritance are promoted to C structs allocated on the stack. A five-field Point class goes from 85ms of allocations to 2ms when the compiler can prove it never escapes the local scope. Programs that use only such value types emit no garbage collector at all.

I saw this play out in the benchmarks. The `life` benchmark (Conway's Game of Life) runs 86.7x faster than miniruby. The `ackermann` benchmark runs 74.8x faster. These are programs with no I/O, no external dependencies, and deeply recursive call trees. Whole-program inference eliminates the entire Ruby VM overhead.

## What Spinel does not support

No eval, no `instance_eval`, no `class_eval`. No `send`, no `method_missing`, no `define_method`. These restrictions are not accidental. Dynamic dispatch and metaprogramming make static type inference impossible or unsound. Spinel chooses soundness: if it cannot prove the type, it does not compile that path.

No threads. `Thread` and `Mutex` are absent. Fiber is supported (via `ucontext_t`), but parallel threads are not. The GC is mark-and-sweep with non-recursive marking, which means it does not pause the world during collection the way a stop-the-world collector would.

UTF-8 and ASCII only. No encoding support for other character sets.

## What this means for production Ruby

CRuby with YJIT is the right choice for web servers where you want the flexibility of the full Ruby ecosystem, gems that use `eval`, and the ability to dynamically reload code in development. Spinel is for programs that run for hours or days doing computation-heavy work, where startup time matters, and where you want a single deployable binary.

I think of the trade-off this way: if your Ruby program is a long-running service that spends most of its time executing a known set of hot paths, Spinel's self-hosting AOT compilation will outperform YJIT after the first hour. If you have short-lived processes that fork frequently ( Puma workers restarting every few minutes), the JIT warm-up cost amortizes poorly and Spinel wins immediately.

The constraint that matters most is the no-metaprogramming rule. Rails uses `define_method` extensively. Many gems use `eval` for ERB templates or DSL parsing. Spinel will not compile a Rails application today. It works for standalone programs, scripts with clear type signatures, and computation-heavy utilities that do not need runtime feature flags.

## The self-hosting bootstrap loop

Spinel compiles its own backend. The bootstrap chain confirms correctness:

```
CRuby + spinel_parse.rb → AST
CRuby + spinel_codegen.rb → gen1.c → bin1
bin1 + AST → gen2.c → bin2
bin2 + AST → gen3.c
gen2.c == gen3.c   # loop closed
```

When `gen2.c` and `gen3.c` are byte-for-byte identical, the compiler is self-hosting correctly. Matz runs this check in the Makefile under `make bootstrap`. The `-Werror` flag on the generated C code ensures that any warnings in the bootstrap compiler become build failures, surfacing regressions immediately.

## Where Spinel fits in the Ruby performance landscape

Ruby 3.2 shipped YJIT and improved MJIT. Both are production-ready and part of the standard toolchain. Spinel is not a replacement for either. It is a different point in the design space: static analysis beats dynamic profiling when you can afford to know your program completely before execution. My post on [LLM token budgets](/articles/llm-token-budgets-cost-control) covers how the cost-per-token math shapes deployment decisions. Spinel's deployment model is a direct analog at the language runtime level.

If you want to understand the memory trade-offs that drive performance in this class of tooling, I wrote about [KV cache eviction strategies](/articles/kv-cache-eviction-accuracy) in the context of LLM inference. The core idea (managing a finite memory budget with importance-aware eviction) applies equally to how Spinel manages its value-type stack allocation versus heap allocation.

For a broader view of how compilation strategies affect runtime performance, my post on [speculative decoding](/articles/speculative-decoding-explained) covers how draft models and verification loops exploit memory-bandwidth trade-offs. Spinel's approach exploits a similar insight: the cost of interpretation is so high that compiling ahead of time pays back immediately for compute-bound programs.
