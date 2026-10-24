# Synthetic access demonstration

All documents in this directory are fictional, AI-assisted demonstration
material under the project's MIT license. They are not upstream HTTPX guidance
or real organization policies. They contain no real users or secrets.

They are excluded by default. Explicitly select `ingest --include-synthetic`
to combine these two separately checksummed fixtures with the unchanged pinned
HTTPX sources. The `support` demo profile can retrieve them; `public` cannot.
A profile is selected by the trusted local CLI/server operator, never by model
output or document instructions. This simulates access and is not production
authentication; all fixtures are publicly visible in this repository.

The two version snapshots intentionally give different fictional orchidrelay
retry budgets: two attempts for 0.27.2 and three for 0.28.1. The isolated change
demo revises the latter to four, grants/revokes public access and deletes the
selected snapshot without changing these checked-in source files.
