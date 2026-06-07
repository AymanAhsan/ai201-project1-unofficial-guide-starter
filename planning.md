
# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain chosen is learning ratings for Mathematics professors at CCNY. This knowledge is valuable for students (especially STEM majors) because professor quality strongly affects learning outcomes in challenging courses. Aggregating and summarizing student reviews makes it easier to compare instructors without manually visiting many pages.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1949151 |
| 2 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1583271 |
| 3 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1588752 |
| 4 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1751203 |
| 5 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/631569 |
| 6 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1023742 |
| 7 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1807944 |
| 8 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/221879 |
| 9 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1249262 |
| 10 | RateMyProfessors — sample professor | Student reviews and ratings | https://www.ratemyprofessors.com/professor/1913056 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** paragraph-based (split by individual review / paragraph)

**Overlap:** none (reviews are short and self-contained)

**Reasoning:** Reviews are short, opinionated paragraphs; splitting by paragraph preserves full review context and avoids slicing sentences across chunks.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 10

**Production tradeoff reflection:** For short, informal reviews this lightweight model balances cost and speed with reasonable semantic quality. If cost were not a constraint, consider larger embedding models trained on informal or user-generated text for improved nuance, at the expense of latency and cost.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Is John Adamski known as the best professor? | Yes — John Adamski is highly rated in reviews.
| 2 | Did Starshimer read the textbook for the first time mid class? | Yes — reviews indicate Starshimer was reading the textbook during class.
| 3 | What class is Strashimir Popvassilev good and bad for? | Good for Calculus 3; poor for Linear Algebra (per reviewer comments).
| 4 | Who has a higher overall rating, Anthony Paolillo or John Adamski? | John Adamski has a higher overall rating than Anthony Paolillo.
| 5 | Which professor does Zoom meetings on off days? | Doris Pichardo holds Zoom meetings on off days.

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Subjectivity and noise: Reviews are opinionated and inconsistent; aggregation may produce biased summaries.
2. Off-topic or ambiguous queries: Vague queries (e.g., "Which professor is best?") may retrieve mixed-professor content making synthesis difficult.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline — Unofficial Guide                     │
└─────────────────────────────────────────────────────────────────────────────┘

 ┌──────────────────────┐
 │   Document Ingestion │
 │                      │
 │  documents/          │
 │    reviews.txt       │
 │  (~781 reviews,      │
 │   scraped from       │
 │   RateMyProfessors)  │
 └──────────┬───────────┘
            │  raw text (--- delimited blocks)
            ▼
 ┌──────────────────────┐
 │      Chunking        │
 │                      │
 │  text_chunker.py     │
 │  strategy: paragraph │
 │  split on "---"      │
 │  overlap: none       │
 │  → 781 chunks        │
 │  → chunks.json       │
 └──────────┬───────────┘
            │  list of chunk dicts
            │  {chunk_id, text, professor,
            │   course, rating, difficulty}
            ▼
 ┌──────────────────────┐
 │      Embedding       │
 │                      │
 │  sentence-           │
 │  transformers        │
 │  all-MiniLM-L6-v2   │
 └──────────┬───────────┘
            │  384-dim vectors
            ▼
 ┌──────────────────────┐
 │     Vector Store     │
 │                      │
 │  ChromaDB            │
 │  (persistent,        │
 │   local)             │
 └──────────┬───────────┘
            │
    ┌───────┴────────┐
    │   User Query   │
    │  (natural lang)│
    └───────┬────────┘
            │  embed query → cosine similarity
            ▼
 ┌──────────────────────┐
 │      Retrieval       │
 │                      │
 │  top-k = 10 chunks   │
 │  by semantic         │
 │  similarity          │
 └──────────┬───────────┘
            │  retrieved chunks + query
            ▼
 ┌──────────────────────┐
 │      Generation      │
 │                      │
 │  Groq LLM            │
 │  grounded system     │
 │  prompt: answer only │
 │  from retrieved docs │
 └──────────┬───────────┘
            │
            ▼
      Final Answer
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

I used Claude to scrape reviews from the 10 specified RateMyProfessors URLs. I provided the URLs and the requirement to extract review text, professor name, course name, and overall rating. I verified the output by checking that the scraped data includes these fields for each review and matches the content on the source pages.

I also used Claude to generate the text chunking code in `text_chunker.py` based on the Chunking Strategy section. I provided the specific chunk size (paragraph-based) and overlap (none) requirements. I verified the output by running the chunking function on sample reviews and checking that chunks correspond to individual reviews without splitting sentences.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
