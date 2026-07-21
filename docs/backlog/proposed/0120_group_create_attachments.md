# agora-0120 — attachment refs on the /groups opening post

- **Status**: proposed
- **Origin**: continuum's adoption report for agora-0119 (dm 44, 2026-07-21):
  "pending-attachment carry-over uploads AFTER the room exists, so on the
  one-call path migrated files ride a follow-up fyi post rather than the
  opening post — if /groups ever accepts attachment refs in the create body,
  I fold same-day."

## Problem

`POST /groups` posts the opening message, and `PostMessage` already carries
`attachments` — but attachment blobs are CHANNEL-scoped (0091) and the
channel does not exist until the composite runs. A caller therefore cannot
upload the blobs first and pass refs: there is nowhere to upload them yet.
Clients that migrate a draft-with-files into a fresh group room must post
the files as a follow-up message instead of on the opening post.

## Sketch (not committed)

Blobs are content-addressed (sha256), so the natural mechanism is a
cross-channel ref: `/groups` accepts refs to blobs in a channel the CALLER
is a member of, and links (not copies) them into the new room. Security
surface to think through before building: a ref-link must not leak source
channel metadata, and the aggregate-budget accounting (per-channel blob
ceiling) must decide whether a linked blob charges the new channel, the old
one, or both. Alternative: a two-phase create (reserve name -> upload ->
commit) — heavier, probably not worth it for this one consumer.

## Adoption

continuum folds same-day once shipped (their words). Until then the
follow-up-post carry-over works and loses nothing but cosmetics.
